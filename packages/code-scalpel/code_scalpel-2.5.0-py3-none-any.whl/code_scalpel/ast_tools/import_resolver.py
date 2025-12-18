"""
Import Resolution Engine for Cross-File Analysis.

[20251213_FEATURE] v1.5.1 - Cross-file import resolution

This module provides comprehensive import resolution capabilities for Python projects,
enabling cross-file analysis by building an accurate picture of how modules connect.

Key features:
- Build import graph showing module dependencies
- Detect and report circular imports gracefully
- Resolve symbols across file boundaries
- Support relative imports and __init__.py packages
- Topological sort for safe analysis order

Example:
    >>> from code_scalpel.ast_tools.import_resolver import ImportResolver
    >>> resolver = ImportResolver("/path/to/project")
    >>> resolver.build()
    >>> module, symbol = resolver.resolve_symbol("views", "get_user")
    >>> print(f"Found {symbol.name} in {module}")
"""

import ast
import os
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict

from code_scalpel.cache import AnalysisCache, ParallelParser, IncrementalAnalyzer


logger = logging.getLogger(__name__)


# [20251214_FEATURE] Top-level parse fn for parallel workers (picklable on Windows spawn)
def _parse_for_imports(file_path: Path) -> Tuple[str, ast.AST]:
    with file_path.open("r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    return source, tree


# [20251214_FEATURE] Import types for classification including dynamic/framework imports
class ImportType:
    """Classification of import statement types."""

    DIRECT = "direct"  # import module
    FROM = "from"  # from module import name
    RELATIVE = "relative"  # from . import name or from ..module import name
    WILDCARD = "wildcard"  # from module import *
    ALIASED = "aliased"  # import module as alias
    DYNAMIC = "dynamic"  # importlib.import_module()
    DUNDER = "dunder"  # __import__()
    LAZY = "lazy"  # Detected but not yet resolved
    FRAMEWORK = "framework"  # [20251214_FEATURE] Framework-discovered imports (e.g., Django INSTALLED_APPS, Flask blueprints)


@dataclass
class ImportInfo:
    """
    Information about a single import statement.

    Attributes:
        module: The module being imported from (e.g., "os.path")
        name: The specific name being imported (e.g., "join")
        alias: Optional alias for the import (e.g., "pjoin")
        import_type: Type of import (direct, from, relative, etc.)
        level: Relative import level (0 for absolute, 1 for ., 2 for .., etc.)
        line: Line number in source file
        file: Source file path
    """

    module: str
    name: str
    alias: Optional[str] = None
    import_type: str = ImportType.DIRECT
    level: int = 0
    line: int = 0
    file: str = ""

    @property
    def effective_name(self) -> str:
        """Get the name as it appears in the importing module's namespace."""
        return self.alias if self.alias else self.name

    @property
    def full_path(self) -> str:
        """Get the fully qualified import path."""
        if self.module and self.name != "*":
            return f"{self.module}.{self.name}"
        return self.module or self.name


class DynamicImportVisitor(ast.NodeVisitor):
    """Visitor to extract dynamic imports and track local string variables."""

    def __init__(self, resolver, module_name: str, file_path: str):
        self.resolver = resolver
        self.module_name = module_name
        self.file_path = file_path
        self.local_vars: Dict[str, str] = {}  # var_name -> string_value

    def visit_Assign(self, node: ast.Assign) -> None:
        """Track string assignments: x = 'module'."""
        # Only handle simple assignments: x = "string"
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            val = node.value.value
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.local_vars[target.id] = val
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check for dynamic import calls."""
        # importlib.import_module(arg)
        if self.resolver._is_import_module_call(node):
            self._handle_import(node, ImportType.DYNAMIC)

        # __import__(arg)
        elif self.resolver._is_dunder_import(node):
            self._handle_import(node, ImportType.DUNDER)

        self.generic_visit(node)

    def _handle_import(self, node: ast.Call, import_type: str) -> None:
        """Process a dynamic import call."""
        target_module = self._resolve_arg(node)

        if target_module:
            self.resolver._add_dynamic_import(
                self.module_name,
                target_module,
                node.lineno,
                self.file_path,
                import_type,
            )
        else:
            # Variable or complex expression - mark as lazy/unknown
            self.resolver._add_dynamic_import(
                self.module_name, "?", node.lineno, self.file_path, ImportType.LAZY
            )

    def _resolve_arg(self, node: ast.Call) -> Optional[str]:
        """Resolve the first argument to a string (literal or variable)."""
        if not node.args:
            return None

        arg = node.args[0]

        # Case 1: String literal
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value

        # Case 2: Variable reference
        if isinstance(arg, ast.Name) and arg.id in self.local_vars:
            return self.local_vars[arg.id]

        return None

    def _extract_string_iterable(self, node: ast.AST) -> List[str]:
        """Extract string values from a list/tuple literal."""
        strings: List[str] = []
        if isinstance(node, (ast.List, ast.Tuple)):
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    strings.append(elt.value)
        return strings


@dataclass
class SymbolDefinition:
    """
    Definition of a symbol (function, class, variable) in a module.

    Attributes:
        name: Symbol name
        symbol_type: Type of symbol (function, class, variable, method)
        file: File where symbol is defined
        module: Module name (Python import path)
        line: Line number of definition
        end_line: End line of definition (if available)
        docstring: Docstring if present
        signature: Function/method signature if applicable
    """

    name: str
    symbol_type: str
    file: str
    module: str
    line: int
    end_line: Optional[int] = None
    docstring: Optional[str] = None
    signature: Optional[str] = None


@dataclass
class CircularImport:
    """
    Information about a detected circular import.

    Attributes:
        cycle: List of modules forming the cycle (e.g., ["a", "b", "c", "a"])
        files: List of file paths involved
        severity: How problematic this cycle is ("warning" or "error")
    """

    cycle: List[str]
    files: List[str]
    severity: str = "warning"

    def __str__(self) -> str:
        return " -> ".join(self.cycle)


@dataclass
class ImportGraphResult:
    """
    Result of building the import graph.

    Attributes:
        success: Whether the build completed successfully
        modules: Number of modules analyzed
        imports: Total number of imports found
        circular_imports: List of detected circular import cycles
        errors: List of errors encountered during analysis
        warnings: List of warnings (non-fatal issues)
    """

    success: bool = True
    modules: int = 0
    imports: int = 0
    circular_imports: List[CircularImport] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ImportResolver:
    """
    Build and query module import relationships for a Python project.

    This class handles:
    - Walking the project file tree
    - Parsing Python imports from AST
    - Building dependency graph (adjacency list)
    - Detecting circular imports
    - Resolving symbols to their source modules
    - Topological sorting for safe analysis order

    Example:
        >>> resolver = ImportResolver("/myproject")
        >>> result = resolver.build()
        >>> if result.success:
        ...     module, symbol = resolver.resolve_symbol("views", "get_user")
        ...     print(f"Found in {module}: {symbol}")
        ... else:
        ...     print(f"Build failed: {result.errors}")

    Scope Limitations (v1.5.1):
    - from module import func (direct imports)
    - import module (module imports)
    - from . import sibling (relative imports)
    - from ..package import module (parent imports)
    - from module import * (wildcard imports - partial resolution)
    - importlib.import_module() (dynamic imports - skipped)
    - __import__() (dynamic imports - skipped)
    - sys.path manipulation (too complex - skipped)
    """

    # Directories to skip during file crawling
    SKIP_DIRS = {
        ".git",
        ".venv",
        "venv",
        "env",
        ".env",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        ".tox",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "htmlcov",
        ".coverage",
        "site-packages",
    }

    def __init__(self, project_root: Union[str, Path]):
        """
        Initialize the import resolver.

        Args:
            project_root: Absolute path to the project root directory
        """
        self.project_root = Path(project_root).resolve()

        # [20251214_FEATURE] Reusable parse cache + parallel parser and incremental graph
        self._parse_cache: AnalysisCache[Tuple[str, ast.AST]] = AnalysisCache()
        self._parallel_parser: ParallelParser[Tuple[str, ast.AST]] = ParallelParser(
            cache=self._parse_cache
        )
        self._incremental: IncrementalAnalyzer[Tuple[str, ast.AST]] = (
            IncrementalAnalyzer(self._parse_cache)
        )

        # Core data structures
        self.edges: Dict[str, Set[str]] = defaultdict(
            set
        )  # module -> {imported_modules}
        self.reverse_edges: Dict[str, Set[str]] = defaultdict(
            set
        )  # module -> {modules that import it}
        self.imports: Dict[str, List[ImportInfo]] = defaultdict(
            list
        )  # module -> [ImportInfo]
        self.symbols: Dict[str, Dict[str, SymbolDefinition]] = (
            {}
        )  # module -> {name: SymbolDefinition}
        self.file_to_module: Dict[str, str] = {}  # file_path -> module_name
        self.module_to_file: Dict[str, str] = {}  # module_name -> file_path

        # Analysis state
        self._built = False
        self._circular_imports: List[CircularImport] = []
        self._errors: List[str] = []
        self._warnings: List[str] = []

    def build(self) -> ImportGraphResult:
        """
        Build the import graph by analyzing all Python files in the project.

        This method:
        1. Crawls all Python files in the project
        2. Parses imports and definitions from each file
        3. Builds the dependency graph
        4. Detects circular imports

        Returns:
            ImportGraphResult with build statistics and any errors/warnings
        """
        self._reset()

        try:
            # Phase 1: Discover all Python files and map to modules
            python_files = list(self._iter_python_files())
            for file_path in python_files:
                module_name = self._path_to_module(file_path)
                self.file_to_module[str(file_path)] = module_name
                self.module_to_file[module_name] = str(file_path)

            # Phase 2: Parse each file (parallel) for imports and definitions
            parsed, parse_errors = self._parallel_parser.parse_files(
                python_files, parse_fn=_parse_for_imports
            )
            for err_path in parse_errors:
                self._warnings.append(
                    f"Error analyzing {err_path}: parallel parse failed"
                )

            for file_path in python_files:
                parsed_entry = parsed.get(str(file_path.resolve()))
                self._analyze_file(file_path, parsed_entry)

            # Phase 3: Detect circular imports
            self._detect_circular_imports()

            # Phase 4: Record dependencies for incremental updates
            self._record_dependencies()

            self._built = True

            return ImportGraphResult(
                success=len(self._errors) == 0,
                modules=len(self.module_to_file),
                imports=sum(len(imps) for imps in self.imports.values()),
                circular_imports=self._circular_imports,
                errors=self._errors,
                warnings=self._warnings,
            )

        except Exception as e:
            self._errors.append(f"Build failed: {e}")
            return ImportGraphResult(
                success=False,
                errors=self._errors,
                warnings=self._warnings,
            )

    def _reset(self) -> None:
        """Reset all internal state for a fresh build."""
        self.edges.clear()
        self.reverse_edges.clear()
        self.imports.clear()
        self.symbols.clear()
        self.file_to_module.clear()
        self.module_to_file.clear()
        self._built = False
        self._circular_imports.clear()
        self._errors.clear()
        self._warnings.clear()

    def _iter_python_files(self):
        """
        Iterate over all Python files in the project.

        Yields:
            Path objects for each .py file, skipping hidden and ignored directories
        """
        for root, dirs, files in os.walk(self.project_root):
            # Filter out directories to skip
            dirs[:] = [
                d for d in dirs if d not in self.SKIP_DIRS and not d.startswith(".")
            ]

            for file in files:
                if file.endswith(".py"):
                    yield Path(root) / file

    def _path_to_module(self, file_path: Path) -> str:
        """
        Convert a file path to a Python module name.

        Args:
            file_path: Path to a .py file

        Returns:
            Module name (e.g., "src.models.user")
        """
        try:
            rel_path = file_path.relative_to(self.project_root)
        except ValueError:
            # File is outside project root
            return file_path.stem

        # Convert path to module name
        parts = list(rel_path.parts)

        # Remove .py extension from last part
        if parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]

        # Handle __init__.py -> package name
        if parts[-1] == "__init__":
            parts = parts[:-1]

        # Handle empty (project root __init__.py)
        if not parts:
            return "__root__"

        return ".".join(parts)

    def _module_to_path(
        self, module_name: str, from_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Convert a module name to a file path.

        Args:
            module_name: Python module name (e.g., "src.models.user")
            from_file: File where the import occurs (for relative imports)

        Returns:
            File path if found, None otherwise
        """
        # Check if we already have this module mapped
        if module_name in self.module_to_file:
            return self.module_to_file[module_name]

        # Try to find the file
        parts = module_name.split(".")

        # Try as a module file
        module_path = self.project_root / "/".join(parts)
        if (module_path.with_suffix(".py")).exists():
            return str(module_path.with_suffix(".py"))

        # Try as a package __init__.py
        init_path = module_path / "__init__.py"
        if init_path.exists():
            return str(init_path)

        return None

    def _analyze_file(
        self, file_path: Path, parsed: Optional[Tuple[str, ast.AST]] = None
    ) -> None:
        """
        Analyze a single Python file for imports and definitions.

        Args:
            file_path: Path to the .py file to analyze
            parsed: Optional (source, AST) pre-parsed tuple
        """
        rel_path = str(file_path.relative_to(self.project_root))
        module_name = self.file_to_module.get(str(file_path), rel_path)

        try:
            if parsed:
                source, tree = parsed
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source)

            # Extract imports
            self._extract_imports(tree, module_name, rel_path)

            # [20251214_FEATURE] Extract dynamic imports
            self._extract_dynamic_imports(tree, module_name, rel_path)

            # [20251214_FEATURE] Extract framework-derived imports (e.g., Django INSTALLED_APPS)
            self._extract_framework_imports(tree, module_name, rel_path)

            # Extract definitions (functions, classes)
            self._extract_definitions(tree, module_name, rel_path)

        except SyntaxError as e:
            self._warnings.append(f"Syntax error in {rel_path}: {e}")
        except Exception as e:
            self._warnings.append(f"Error analyzing {rel_path}: {e}")

    def _record_dependencies(self) -> None:
        """Populate incremental dependency graph mapping files to dependents."""
        for module_name, targets in self.edges.items():
            source_path = self.module_to_file.get(module_name)
            if not source_path:
                continue
            for target_module in targets:
                target_path = self.module_to_file.get(target_module)
                if target_path:
                    self._incremental.record_dependency(source_path, target_path)

    def _extract_imports(self, tree: ast.AST, module_name: str, file_path: str) -> None:
        """
        Extract all imports from an AST.

        Args:
            tree: Parsed AST
            module_name: Name of the module being analyzed
            file_path: Path to the source file
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # import x, y, z
                for alias in node.names:
                    import_info = ImportInfo(
                        module=alias.name,
                        name=alias.name,
                        alias=alias.asname,
                        import_type=(
                            ImportType.ALIASED if alias.asname else ImportType.DIRECT
                        ),
                        level=0,
                        line=node.lineno,
                        file=file_path,
                    )
                    self.imports[module_name].append(import_info)

                    # Add edge: this module imports that module
                    imported_module = alias.name.split(".")[0]
                    if imported_module in self.module_to_file or self._is_local_module(
                        imported_module
                    ):
                        self.edges[module_name].add(imported_module)
                        self.reverse_edges[imported_module].add(module_name)

            elif isinstance(node, ast.ImportFrom):
                # from x import y, z
                base_module = node.module or ""
                level = node.level  # 0=absolute, 1=., 2=.., etc.

                # Resolve relative imports
                if level > 0:
                    resolved_module = self._resolve_relative_import(
                        module_name, base_module, level
                    )
                else:
                    resolved_module = base_module

                for alias in node.names:
                    if alias.name == "*":
                        import_type = ImportType.WILDCARD
                    elif level > 0:
                        import_type = ImportType.RELATIVE
                    else:
                        import_type = ImportType.FROM

                    import_info = ImportInfo(
                        module=resolved_module,
                        name=alias.name,
                        alias=alias.asname,
                        import_type=import_type,
                        level=level,
                        line=node.lineno,
                        file=file_path,
                    )
                    self.imports[module_name].append(import_info)

                # Add edge to graph
                if resolved_module:
                    root_module = resolved_module.split(".")[0]
                    if root_module in self.module_to_file or self._is_local_module(
                        root_module
                    ):
                        self.edges[module_name].add(resolved_module)
                        self.reverse_edges[resolved_module].add(module_name)

    def _extract_dynamic_imports(
        self, tree: ast.AST, module_name: str, file_path: str
    ) -> None:
        """Extract dynamic imports (importlib, __import__) from an AST."""
        visitor = DynamicImportVisitor(self, module_name, file_path)
        visitor.visit(tree)

    # [20251214_FEATURE] Django/Flask framework import extraction
    def _extract_framework_imports(
        self, tree: ast.AST, module_name: str, file_path: str
    ) -> None:
        """Extract framework-derived imports such as Django INSTALLED_APPS and Flask blueprints."""
        blueprint_vars: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "INSTALLED_APPS":
                        apps = self._extract_string_iterable(node.value)
                        for app in apps:
                            self._add_framework_import(
                                module_name, app, getattr(node, "lineno", 0), file_path
                            )

                # [20251214_FEATURE] Flask Blueprint detection: bp = Blueprint("name", __name__)
                if self._is_blueprint_ctor(node):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            blueprint_vars.add(target.id)

            # [20251214_FEATURE] Flask app.register_blueprint(bp)
            if isinstance(node, ast.Call) and self._is_register_blueprint_call(node):
                arg = node.args[0] if node.args else None
                target = None
                if isinstance(arg, ast.Name) and arg.id in blueprint_vars:
                    target = arg.id
                elif isinstance(arg, ast.Name):
                    target = arg.id  # fallback: unknown blueprint var
                if target:
                    self._add_framework_import(
                        module_name, target, getattr(node, "lineno", 0), file_path
                    )

    def _extract_string_iterable(self, node: ast.AST) -> List[str]:
        """Extract string values from a list/tuple literal."""
        strings: List[str] = []
        if isinstance(node, (ast.List, ast.Tuple)):
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    strings.append(elt.value)
        return strings

    def _is_import_module_call(self, node: ast.Call) -> bool:
        """Check if this is importlib.import_module()."""
        if isinstance(node.func, ast.Attribute):
            return (
                node.func.attr == "import_module"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "importlib"
            )
        return False

    def _is_dunder_import(self, node: ast.Call) -> bool:
        """Check if this is __import__()."""
        return isinstance(node.func, ast.Name) and node.func.id == "__import__"

    # [20251214_FEATURE] Flask Blueprint constructor detection
    def _is_blueprint_ctor(self, node: ast.AST) -> bool:
        """Check if assignment value is a Flask Blueprint(...) call."""
        if not isinstance(node, ast.Assign):
            return False
        call = node.value
        if not isinstance(call, ast.Call):
            return False
        func = call.func
        # Blueprint(...) or flask.Blueprint(...)
        if isinstance(func, ast.Name) and func.id == "Blueprint":
            return True
        if isinstance(func, ast.Attribute) and func.attr == "Blueprint":
            return True
        return False

    # [20251214_FEATURE] Flask register_blueprint detection
    def _is_register_blueprint_call(self, node: ast.Call) -> bool:
        """Check if this is app.register_blueprint(...)"""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "register_blueprint"
        return False

    def _add_dynamic_import(
        self,
        source_module: str,
        target_module: str,
        line: int,
        file_path: str,
        import_type: str,
    ) -> None:
        """Add a dynamic import to the graph."""
        import_info = ImportInfo(
            module=target_module,
            name="*",  # Dynamic imports usually import the whole module
            alias=None,
            import_type=import_type,
            level=0,
            line=line,
            file=file_path,
        )
        self.imports[source_module].append(import_info)

        # Add edge if it's a known module and not a lazy placeholder
        if target_module and target_module != "?":
            root_module = target_module.split(".")[0]
            if root_module in self.module_to_file or self._is_local_module(root_module):
                self.edges[source_module].add(target_module)
                self.reverse_edges[target_module].add(source_module)

    def _add_framework_import(
        self, source_module: str, target_module: str, line: int, file_path: str
    ) -> None:
        """Add a framework-derived import (e.g., Django INSTALLED_APPS)."""
        import_info = ImportInfo(
            module=target_module,
            name="*",
            alias=None,
            import_type=ImportType.FRAMEWORK,
            level=0,
            line=line,
            file=file_path,
        )
        self.imports[source_module].append(import_info)

        # Add edge if local/known
        if target_module and target_module != "?":
            root_module = target_module.split(".")[0]
            if root_module in self.module_to_file or self._is_local_module(root_module):
                self.edges[source_module].add(target_module)
                self.reverse_edges[target_module].add(source_module)

    def _resolve_relative_import(
        self, from_module: str, import_module: str, level: int
    ) -> str:
        """
        Resolve a relative import to an absolute module path.

        Args:
            from_module: The module containing the import
            import_module: The module being imported (may be empty)
            level: Number of dots (1=., 2=.., etc.)

        Returns:
            Resolved absolute module path
        """
        if not from_module:
            return import_module

        parts = from_module.split(".")

        # Go up 'level' directories
        if level > len(parts):
            self._warnings.append(
                f"Relative import level {level} exceeds package depth in {from_module}"
            )
            level = len(parts)

        base_parts = parts[:-level] if level > 0 else parts

        if import_module:
            return (
                ".".join(base_parts + [import_module]) if base_parts else import_module
            )
        else:
            return ".".join(base_parts) if base_parts else ""

    def _is_local_module(self, module_name: str) -> bool:
        """Check if a module name refers to a local (project) module."""
        # Check if any known module starts with this name
        for known_module in self.module_to_file.keys():
            if known_module == module_name or known_module.startswith(
                f"{module_name}."
            ):
                return True
        return False

    def _extract_definitions(
        self, tree: ast.AST, module_name: str, file_path: str
    ) -> None:
        """
        Extract symbol definitions (functions, classes) from an AST.

        Args:
            tree: Parsed AST
            module_name: Name of the module
            file_path: Path to the source file
        """
        self.symbols[module_name] = {}

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip nested functions (already covered by their parent)
                if self._is_top_level(node, tree):
                    symbol = SymbolDefinition(
                        name=node.name,
                        symbol_type=(
                            "async_function"
                            if isinstance(node, ast.AsyncFunctionDef)
                            else "function"
                        ),
                        file=file_path,
                        module=module_name,
                        line=node.lineno,
                        end_line=getattr(node, "end_lineno", None),
                        docstring=ast.get_docstring(node),
                        signature=self._get_function_signature(node),
                    )
                    self.symbols[module_name][node.name] = symbol

            elif isinstance(node, ast.ClassDef):
                if self._is_top_level(node, tree):
                    symbol = SymbolDefinition(
                        name=node.name,
                        symbol_type="class",
                        file=file_path,
                        module=module_name,
                        line=node.lineno,
                        end_line=getattr(node, "end_lineno", None),
                        docstring=ast.get_docstring(node),
                    )
                    self.symbols[module_name][node.name] = symbol

                    # Also extract methods
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            method_name = f"{node.name}.{item.name}"
                            method_symbol = SymbolDefinition(
                                name=method_name,
                                symbol_type="method",
                                file=file_path,
                                module=module_name,
                                line=item.lineno,
                                end_line=getattr(item, "end_lineno", None),
                                docstring=ast.get_docstring(item),
                                signature=self._get_function_signature(item),
                            )
                            self.symbols[module_name][method_name] = method_symbol

    def _is_top_level(self, node: ast.AST, tree: ast.Module) -> bool:
        """Check if a node is at the top level of a module."""
        return node in tree.body

    def _get_function_signature(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> str:
        """Extract the function signature as a string."""
        args = []

        # Regular args
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                try:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                except Exception:
                    pass
            args.append(arg_str)

        # *args
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")

        # **kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        signature = f"({', '.join(args)})"

        # Return annotation
        if node.returns:
            try:
                signature += f" -> {ast.unparse(node.returns)}"
            except Exception:
                pass

        return signature

    def _detect_circular_imports(self) -> None:
        """
        Detect circular imports in the dependency graph.

        Uses DFS-based cycle detection (Tarjan's algorithm variant).
        """
        visited = set()
        rec_stack = set()
        path = []

        def dfs(module: str) -> bool:
            """DFS to find cycles, returns True if cycle found."""
            visited.add(module)
            rec_stack.add(module)
            path.append(module)

            for neighbor in self.edges.get(module, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]

                    # Get file paths for the cycle
                    files = [
                        self.module_to_file.get(m, f"<unknown:{m}>") for m in cycle
                    ]

                    self._circular_imports.append(
                        CircularImport(
                            cycle=cycle,
                            files=files,
                            severity="warning",
                        )
                    )
                    return True

            path.pop()
            rec_stack.remove(module)
            return False

        # Run DFS from each unvisited module
        for module in list(self.edges.keys()):
            if module not in visited:
                dfs(module)

    def has_circular_imports(self) -> bool:
        """Check if any circular imports were detected."""
        return len(self._circular_imports) > 0

    def get_circular_imports(self) -> List[CircularImport]:
        """Get all detected circular imports."""
        return self._circular_imports.copy()

    def resolve_symbol(
        self, from_module: str, symbol_name: str
    ) -> Tuple[Optional[str], Optional[SymbolDefinition]]:
        """
        Resolve a symbol to its source module and definition.

        Args:
            from_module: Module where the symbol is being used
            symbol_name: Name of the symbol to resolve

        Returns:
            Tuple of (source_module, SymbolDefinition) or (None, None) if not found
        """
        if not self._built:
            raise RuntimeError("Must call build() before resolve_symbol()")

        # 1. Check if it's defined locally in from_module
        if from_module in self.symbols and symbol_name in self.symbols[from_module]:
            return from_module, self.symbols[from_module][symbol_name]

        # 2. Check imports from from_module
        for imp in self.imports.get(from_module, []):
            if imp.effective_name == symbol_name:
                # Found the import, now find the definition
                target_module = imp.module
                if imp.name != "*" and imp.name != symbol_name:
                    # It's an alias or the import is for a different name
                    search_name = imp.name
                else:
                    search_name = symbol_name

                # Look in the target module
                if target_module in self.symbols:
                    if search_name in self.symbols[target_module]:
                        return target_module, self.symbols[target_module][search_name]

                # Try submodule
                full_module = (
                    f"{target_module}.{search_name}" if target_module else search_name
                )
                if full_module in self.symbols:
                    # The symbol might be a module itself
                    return full_module, None

        # 3. Check wildcard imports
        for imp in self.imports.get(from_module, []):
            if imp.import_type == ImportType.WILDCARD:
                target_module = imp.module
                if (
                    target_module in self.symbols
                    and symbol_name in self.symbols[target_module]
                ):
                    return target_module, self.symbols[target_module][symbol_name]

        return None, None

    def get_importers(self, module_name: str) -> Set[str]:
        """
        Get all modules that import the given module.

        Args:
            module_name: Module to find importers for

        Returns:
            Set of module names that import this module
        """
        return self.reverse_edges.get(module_name, set()).copy()

    def get_imports(self, module_name: str) -> Set[str]:
        """
        Get all modules imported by the given module.

        Args:
            module_name: Module to find imports for

        Returns:
            Set of module names imported by this module
        """
        return self.edges.get(module_name, set()).copy()

    def topological_sort(self) -> List[str]:
        """
        Return modules in topological order (dependencies first).

        This order is safe for analyzing modules because a module's
        dependencies will always be analyzed before the module itself.

        Returns:
            List of module names in topological order

        Raises:
            ValueError: If circular imports prevent topological sort
        """
        if not self._built:
            raise RuntimeError("Must call build() before topological_sort()")

        if self._circular_imports:
            # Still try to provide an order, just warn
            self._warnings.append(
                "Topological sort may be incomplete due to circular imports"
            )

        # Kahn's algorithm for topological sort
        in_degree = defaultdict(int)
        for module in self.edges:
            if module not in in_degree:
                in_degree[module] = 0
            for dep in self.edges[module]:
                in_degree[dep] = in_degree.get(dep, 0)

        # Calculate in-degrees
        for module, deps in self.edges.items():
            for dep in deps:
                in_degree[dep] += 1

        # Start with modules that have no dependencies
        queue = [m for m, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            module = queue.pop(0)
            result.append(module)

            for dep in self.edges.get(module, []):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        # Add any remaining modules (those in cycles)
        remaining = set(self.module_to_file.keys()) - set(result)
        result.extend(remaining)

        return result

    def get_module_info(self, module_name: str) -> Optional[Dict]:
        """
        Get detailed information about a module.

        Args:
            module_name: Module to get info for

        Returns:
            Dictionary with module information or None if not found
        """
        if module_name not in self.module_to_file:
            return None

        return {
            "name": module_name,
            "file": self.module_to_file[module_name],
            "imports": list(self.edges.get(module_name, set())),
            "imported_by": list(self.reverse_edges.get(module_name, set())),
            "symbols": list(self.symbols.get(module_name, {}).keys()),
            "import_count": len(self.imports.get(module_name, [])),
        }

    def get_all_symbols(self) -> Dict[str, List[SymbolDefinition]]:
        """
        Get all symbols defined in the project.

        Returns:
            Dictionary mapping module names to lists of SymbolDefinitions
        """
        return {
            module: list(symbols.values()) for module, symbols in self.symbols.items()
        }

    def find_symbol(self, symbol_name: str) -> List[Tuple[str, SymbolDefinition]]:
        """
        Find all definitions of a symbol across the project.

        Args:
            symbol_name: Name of the symbol to find

        Returns:
            List of (module_name, SymbolDefinition) tuples
        """
        results = []
        for module, symbols in self.symbols.items():
            if symbol_name in symbols:
                results.append((module, symbols[symbol_name]))
        return results

    def generate_mermaid(self) -> str:
        """
        Generate a Mermaid diagram of the import graph.

        Returns:
            Mermaid diagram string
        """
        lines = ["graph TD"]

        # Create node IDs
        node_ids = {}
        for i, module in enumerate(sorted(self.module_to_file.keys())):
            node_id = f"N{i}"
            node_ids[module] = node_id
            # Escape module name for Mermaid
            safe_name = module.replace(".", "_")
            lines.append(f"    {node_id}[{safe_name}]")

        # Add edges
        for module, deps in self.edges.items():
            if module not in node_ids:
                continue
            for dep in deps:
                if dep in node_ids:
                    lines.append(f"    {node_ids[module]} --> {node_ids[dep]}")

        # Highlight circular imports
        for circular in self._circular_imports:
            for i in range(len(circular.cycle) - 1):
                from_mod = circular.cycle[i]
                to_mod = circular.cycle[i + 1]
                if from_mod in node_ids and to_mod in node_ids:
                    # Style circular edges differently
                    lines.append(
                        f"    {node_ids[from_mod]} -.->|cycle| {node_ids[to_mod]}"
                    )

        return "\n".join(lines)
