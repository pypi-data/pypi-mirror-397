"""
Cross-File Taint Tracking for Security Analysis.

[20251213_FEATURE] v1.5.1 - Cross-file taint flow analysis

This module extends the existing TaintTracker to track taint flow across
module boundaries, enabling detection of vulnerabilities that span multiple files.

Key features:
- Track taint through function calls across files
- Map tainted parameters to callers
- Build cross-module taint flow graphs
- Detect vulnerabilities in multi-file scenarios

Example:
    >>> from code_scalpel.symbolic_execution_tools.cross_file_taint import CrossFileTaintTracker
    >>> tracker = CrossFileTaintTracker("/path/to/project")
    >>> tracker.build()
    >>> results = tracker.analyze()
    >>> for vuln in results.vulnerabilities:
    ...     print(f"{vuln.vulnerability_type}: {vuln.flow_path}")
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Optional, Union, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum, auto

from ..ast_tools.import_resolver import ImportResolver, ImportInfo


class CrossFileTaintSource(Enum):
    """Sources of taint in cross-file analysis."""

    FUNCTION_PARAMETER = auto()  # Parameter from external caller
    RETURN_VALUE = auto()  # Return value from imported function
    GLOBAL_VARIABLE = auto()  # Imported global/constant
    CLASS_ATTRIBUTE = auto()  # Attribute from imported class
    MODULE_LEVEL = auto()  # Top-level code in imported module


class CrossFileSink(Enum):
    """Dangerous sinks for cross-file taint."""

    SQL_QUERY = auto()
    HTML_OUTPUT = auto()
    FILE_PATH = auto()
    SHELL_COMMAND = auto()
    EVAL = auto()
    DESERIALIZATION = auto()
    NETWORK_REQUEST = auto()
    TEMPLATE_RENDER = auto()


@dataclass
class TaintedParameter:
    """
    A function parameter that receives tainted data.

    Attributes:
        function_name: Name of the function
        parameter_name: Name of the parameter
        module: Module where function is defined
        file: File path
        line: Line number of function definition
        callers: Set of (module, line) where tainted calls occur
    """

    function_name: str
    parameter_name: str
    module: str
    file: str
    line: int
    callers: Set[Tuple[str, int]] = field(default_factory=set)


@dataclass
class CrossFileTaintFlow:
    """
    A taint flow path across files.

    Attributes:
        source_module: Module where taint originates
        source_function: Function where taint originates
        source_line: Line number of source
        sink_module: Module where sink is reached
        sink_function: Function where sink is reached
        sink_line: Line number of sink
        sink_type: Type of dangerous sink
        flow_path: List of (module, function, line) showing flow
        tainted_data: Description of the tainted data
    """

    source_module: str
    source_function: str
    source_line: int
    sink_module: str
    sink_function: str
    sink_line: int
    sink_type: CrossFileSink
    flow_path: List[Tuple[str, str, int]] = field(default_factory=list)
    tainted_data: str = ""

    def __hash__(self):
        return hash(
            (
                self.source_module,
                self.source_function,
                self.source_line,
                self.sink_module,
                self.sink_function,
                self.sink_line,
            )
        )


@dataclass
class CrossFileVulnerability:
    """
    A detected vulnerability that spans multiple files.

    Attributes:
        vulnerability_type: Type of vulnerability (e.g., SQL_INJECTION)
        severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW)
        cwe_id: CWE identifier
        flow: The taint flow that causes this vulnerability
        description: Human-readable description
        recommendation: How to fix
    """

    vulnerability_type: str
    severity: str
    cwe_id: str
    flow: CrossFileTaintFlow
    description: str
    recommendation: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "vulnerability_type": self.vulnerability_type,
            "severity": self.severity,
            "cwe_id": self.cwe_id,
            "source_file": self.flow.source_module,
            "source_line": self.flow.source_line,
            "sink_file": self.flow.sink_module,
            "sink_line": self.flow.sink_line,
            "description": self.description,
            "recommendation": self.recommendation,
            # [20251214_BUGFIX] Use descriptive variable names to satisfy lint clarity rules
            "flow_path": [
                {"module": module, "function": func, "line": line}
                for module, func, line in self.flow.flow_path
            ],
        }


@dataclass
class CrossFileTaintResult:
    """
    Result of cross-file taint analysis.

    Attributes:
        success: Whether analysis completed
        modules_analyzed: Number of modules analyzed
        functions_analyzed: Number of functions analyzed
        tainted_parameters: Parameters that receive tainted data
        taint_flows: All detected taint flows
        vulnerabilities: Detected vulnerabilities
        errors: Any errors during analysis
        warnings: Non-fatal warnings
    """

    success: bool = True
    modules_analyzed: int = 0
    functions_analyzed: int = 0
    tainted_parameters: List[TaintedParameter] = field(default_factory=list)
    taint_flows: List[CrossFileTaintFlow] = field(default_factory=list)
    vulnerabilities: List[CrossFileVulnerability] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# Known taint sources (function calls that return tainted data)
TAINT_SOURCES = {
    # Flask/Django request sources
    "request.args.get": CrossFileTaintSource.RETURN_VALUE,
    "request.form.get": CrossFileTaintSource.RETURN_VALUE,
    "request.data": CrossFileTaintSource.RETURN_VALUE,
    "request.json": CrossFileTaintSource.RETURN_VALUE,
    "request.cookies.get": CrossFileTaintSource.RETURN_VALUE,
    "request.headers.get": CrossFileTaintSource.RETURN_VALUE,
    "request.GET.get": CrossFileTaintSource.RETURN_VALUE,  # Django
    "request.POST.get": CrossFileTaintSource.RETURN_VALUE,  # Django
    # File operations
    "open": CrossFileTaintSource.RETURN_VALUE,
    "read": CrossFileTaintSource.RETURN_VALUE,
    "readline": CrossFileTaintSource.RETURN_VALUE,
    "readlines": CrossFileTaintSource.RETURN_VALUE,
    # Environment
    "os.environ.get": CrossFileTaintSource.RETURN_VALUE,
    "os.getenv": CrossFileTaintSource.RETURN_VALUE,
    # Command line
    "sys.argv": CrossFileTaintSource.GLOBAL_VARIABLE,
    "argparse.parse_args": CrossFileTaintSource.RETURN_VALUE,
    # Network
    "socket.recv": CrossFileTaintSource.RETURN_VALUE,
    "requests.get": CrossFileTaintSource.RETURN_VALUE,
    "requests.post": CrossFileTaintSource.RETURN_VALUE,
    # Database (result may be pre-tainted)
    "cursor.fetchone": CrossFileTaintSource.RETURN_VALUE,
    "cursor.fetchall": CrossFileTaintSource.RETURN_VALUE,
    "cursor.fetchmany": CrossFileTaintSource.RETURN_VALUE,
}

# Known dangerous sinks
DANGEROUS_SINKS = {
    # SQL
    "cursor.execute": CrossFileSink.SQL_QUERY,
    "execute": CrossFileSink.SQL_QUERY,
    "executemany": CrossFileSink.SQL_QUERY,
    "session.execute": CrossFileSink.SQL_QUERY,
    "db.execute": CrossFileSink.SQL_QUERY,
    "raw": CrossFileSink.SQL_QUERY,  # Django raw SQL
    # [20251215_BUGFIX] Spring/JPA SQL sinks aligned with taint_tracker coverage
    "createStatement": CrossFileSink.SQL_QUERY,
    "createQuery": CrossFileSink.SQL_QUERY,
    "createNativeQuery": CrossFileSink.SQL_QUERY,
    "entityManager.createQuery": CrossFileSink.SQL_QUERY,
    "entityManager.createNativeQuery": CrossFileSink.SQL_QUERY,
    "entityManager.createNamedQuery": CrossFileSink.SQL_QUERY,
    "entityManager.createStoredProcedureQuery": CrossFileSink.SQL_QUERY,
    "Query.setParameter": CrossFileSink.SQL_QUERY,
    "TypedQuery.setParameter": CrossFileSink.SQL_QUERY,
    "JpaRepository.findBy": CrossFileSink.SQL_QUERY,
    "JpaRepository.deleteBy": CrossFileSink.SQL_QUERY,
    "JpaRepository.removeBy": CrossFileSink.SQL_QUERY,
    "JdbcTemplate.batchUpdate": CrossFileSink.SQL_QUERY,
    "jdbcTemplate.query": CrossFileSink.SQL_QUERY,
    "jdbcTemplate.queryForObject": CrossFileSink.SQL_QUERY,
    "jdbcTemplate.queryForList": CrossFileSink.SQL_QUERY,
    "jdbcTemplate.update": CrossFileSink.SQL_QUERY,
    "jdbcTemplate.execute": CrossFileSink.SQL_QUERY,
    "namedParameterJdbcTemplate.query": CrossFileSink.SQL_QUERY,
    # File
    "open": CrossFileSink.FILE_PATH,
    "os.path.join": CrossFileSink.FILE_PATH,
    "pathlib.Path": CrossFileSink.FILE_PATH,
    "shutil.copy": CrossFileSink.FILE_PATH,
    "shutil.move": CrossFileSink.FILE_PATH,
    # Shell
    "os.system": CrossFileSink.SHELL_COMMAND,
    "os.popen": CrossFileSink.SHELL_COMMAND,
    "subprocess.run": CrossFileSink.SHELL_COMMAND,
    "subprocess.call": CrossFileSink.SHELL_COMMAND,
    "subprocess.Popen": CrossFileSink.SHELL_COMMAND,
    "commands.getoutput": CrossFileSink.SHELL_COMMAND,
    # Eval
    "eval": CrossFileSink.EVAL,
    "exec": CrossFileSink.EVAL,
    "compile": CrossFileSink.EVAL,
    # Deserialization
    "pickle.loads": CrossFileSink.DESERIALIZATION,
    "pickle.load": CrossFileSink.DESERIALIZATION,
    "yaml.load": CrossFileSink.DESERIALIZATION,
    "yaml.unsafe_load": CrossFileSink.DESERIALIZATION,
    "marshal.loads": CrossFileSink.DESERIALIZATION,
    # HTML/Template
    "render_template": CrossFileSink.TEMPLATE_RENDER,
    "render_template_string": CrossFileSink.TEMPLATE_RENDER,
    "Markup": CrossFileSink.HTML_OUTPUT,
    "render": CrossFileSink.TEMPLATE_RENDER,  # Django
    "jinja2.Template": CrossFileSink.TEMPLATE_RENDER,
    # Network
    "requests.get": CrossFileSink.NETWORK_REQUEST,
    "requests.post": CrossFileSink.NETWORK_REQUEST,
    "urllib.request.urlopen": CrossFileSink.NETWORK_REQUEST,
    "httpx.get": CrossFileSink.NETWORK_REQUEST,
}

# Map sink types to CWE IDs
SINK_TO_CWE = {
    CrossFileSink.SQL_QUERY: ("CWE-89", "SQL Injection"),
    CrossFileSink.HTML_OUTPUT: ("CWE-79", "Cross-Site Scripting (XSS)"),
    CrossFileSink.FILE_PATH: ("CWE-22", "Path Traversal"),
    CrossFileSink.SHELL_COMMAND: ("CWE-78", "Command Injection"),
    CrossFileSink.EVAL: ("CWE-94", "Code Injection"),
    CrossFileSink.DESERIALIZATION: ("CWE-502", "Insecure Deserialization"),
    CrossFileSink.NETWORK_REQUEST: ("CWE-918", "Server-Side Request Forgery"),
    CrossFileSink.TEMPLATE_RENDER: ("CWE-1336", "Template Injection"),
}


class CrossFileTaintTracker:
    """
    Track taint flow across multiple files in a Python project.

    This class builds on ImportResolver to understand how data flows
    between modules through function calls and imports.

    Example:
        >>> tracker = CrossFileTaintTracker("/myproject")
        >>> result = tracker.analyze()
        >>> for vuln in result.vulnerabilities:
        ...     print(f"{vuln.vulnerability_type} in {vuln.flow.sink_module}")

    Analysis Strategy:
    1. Build import graph (which modules import what)
    2. Identify taint sources in each module
    3. Track how tainted data flows to exported functions
    4. For each call site, check if arguments reach sinks
    5. Build full taint paths across module boundaries

    Limitations:
    - Static analysis only (no dynamic/runtime analysis)
    - May have false positives with complex control flow
    - Does not track taint through class inheritance well
    - Does not handle metaclasses or descriptors
    """

    def __init__(self, project_root: Union[str, Path]):
        """
        Initialize the cross-file taint tracker.

        Args:
            project_root: Absolute path to project root
        """
        self.project_root = Path(project_root).resolve()
        self.resolver = ImportResolver(project_root)

        # Analysis state
        self._built = False
        self._file_cache: Dict[str, str] = {}
        self._ast_cache: Dict[str, ast.AST] = {}

        # Taint tracking data structures
        self.function_taint_info: Dict[str, Dict[str, FunctionTaintInfo]] = {}
        self.module_taint_sources: Dict[str, List[TaintSourceInfo]] = {}
        self.call_graph: Dict[str, Set[CallInfo]] = defaultdict(set)

    def build(self) -> bool:
        """
        Build the import graph and prepare for analysis.

        Returns:
            True if build succeeded
        """
        result = self.resolver.build()
        self._built = result.success or len(result.warnings) > 0
        return self._built

    def analyze(
        self,
        entry_points: Optional[List[str]] = None,
        max_depth: int = 5,
    ) -> CrossFileTaintResult:
        """
        Perform cross-file taint analysis.

        Args:
            entry_points: Optional list of entry point files/functions
            max_depth: Maximum depth to follow taint flows

        Returns:
            CrossFileTaintResult with detected vulnerabilities
        """
        if not self._built:
            if not self.build():
                return CrossFileTaintResult(
                    success=False, errors=["Failed to build import graph"]
                )

        result = CrossFileTaintResult()

        try:
            # Phase 1: Analyze each module for local taint sources and sinks
            for module, file_path in self.resolver.module_to_file.items():
                self._analyze_module_taint(module, file_path, result)

            # [20251215_BUGFIX] v2.0.1 - Phase 1.5: Propagate returns_tainted through import chains
            # This handles multi-hop taint tracking (A->B->C) by iteratively re-analyzing
            self._propagate_taint_through_imports(result, max_iterations=max_depth)

            # Phase 2: Build call graph and track cross-module calls
            self._build_cross_module_calls(result)

            # Phase 3: Trace taint flows across modules
            self._trace_cross_file_flows(result, max_depth)

            # [20251215_BUGFIX] v2.0.1 - Phase 3.5: Create flows from local_sinks
            # This handles cases where tainted data reaches sinks within the same function
            self._create_flows_from_local_sinks(result)

            # Phase 4: Identify vulnerabilities from taint flows
            self._identify_vulnerabilities(result)

            result.modules_analyzed = len(self.resolver.module_to_file)
            result.success = True

        except Exception as e:
            result.errors.append(f"Analysis failed: {e}")
            result.success = False

        return result

    def _create_flows_from_local_sinks(self, result: CrossFileTaintResult) -> None:
        """
        [20251215_BUGFIX] v2.0.1 - Create taint flows from local_sinks.

        This handles cases where a tainted variable is used directly in a dangerous sink
        within the same function, especially when the taint comes from cross-file imports.
        """
        for module, func_infos in self.function_taint_info.items():
            for func_name, func_info in func_infos.items():
                for var_name, sink_info in func_info.local_sinks.items():
                    # Find the origin of the taint
                    source_module, source_func, source_line = self._trace_taint_origin(
                        module, func_name, var_name
                    )

                    flow = CrossFileTaintFlow(
                        source_module=source_module,
                        source_function=source_func,
                        source_line=source_line,
                        sink_module=module,
                        sink_function=func_name,
                        sink_line=sink_info.line,
                        sink_type=sink_info.sink_type,
                        flow_path=[
                            (source_module, source_func, source_line),
                            (module, func_name, sink_info.line),
                        ],
                        tainted_data=var_name,
                    )
                    result.taint_flows.append(flow)

    def _trace_taint_origin(
        self, module: str, func_name: str, var_name: str
    ) -> Tuple[str, str, int]:
        """
        [20251215_BUGFIX] v2.0.1 - Trace back to find where the taint originated.

        Returns (source_module, source_function, source_line).
        """
        # Look at the function and try to find where var_name got its taint
        # For now, return the current function as source (local taint)
        # A more sophisticated version would trace through the call graph

        func_info = self.function_taint_info.get(module, {}).get(func_name)
        if func_info:
            return (module, func_name, func_info.line)
        return (module, func_name, 0)

    def _propagate_taint_through_imports(
        self, result: CrossFileTaintResult, max_iterations: int = 5
    ) -> None:
        """
        [20251215_BUGFIX] v2.0.1 - Multi-pass propagation of returns_tainted through import chains.

        This handles cases like:
            source.py: get_user_input() -> returns request.args.get() [tainted]
            processor.py: process_input() -> returns source.get_user_input() [should be tainted]
            executor.py: execute() -> uses processor.process_input() in SQL [vulnerability]

        We iterate until no new taints are discovered (fixpoint).
        """
        for iteration in range(max_iterations):
            changed = False

            # For each module, re-analyze functions that call imported tainted functions
            for module, file_path in self.resolver.module_to_file.items():
                tree = self._get_file_ast(file_path)
                if not tree:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_info = self.function_taint_info.get(module, {}).get(
                            node.name
                        )
                        if func_info and not func_info.returns_tainted:
                            # Re-analyze with updated taint info
                            old_tainted_vars = len(func_info.tainted_variables)
                            visitor = FunctionTaintVisitor(func_info, self)
                            visitor.visit(node)

                            # Check if taint status changed
                            if (
                                func_info.returns_tainted
                                or len(func_info.tainted_variables) > old_tainted_vars
                            ):
                                changed = True

            # Fixpoint reached - no new taints discovered
            if not changed:
                break

    def _get_file_source(self, file_path: str) -> Optional[str]:
        """Get source code for a file with caching."""
        if file_path in self._file_cache:
            return self._file_cache[file_path]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            self._file_cache[file_path] = source
            return source
        except Exception:
            return None

    def _get_file_ast(self, file_path: str) -> Optional[ast.AST]:
        """Get parsed AST for a file with caching."""
        if file_path in self._ast_cache:
            return self._ast_cache[file_path]

        source = self._get_file_source(file_path)
        if not source:
            return None

        try:
            tree = ast.parse(source)
            self._ast_cache[file_path] = tree
            return tree
        except SyntaxError:
            return None

    def _analyze_module_taint(
        self, module: str, file_path: str, result: CrossFileTaintResult
    ) -> None:
        """
        Analyze a single module for taint sources and sinks.
        """
        tree = self._get_file_ast(file_path)
        if not tree:
            return

        # Initialize storage
        self.function_taint_info[module] = {}
        self.module_taint_sources[module] = []

        # Find all functions and their taint characteristics
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = self._analyze_function_taint(node, module, file_path)
                self.function_taint_info[module][node.name] = func_info
                result.functions_analyzed += 1

    def _analyze_function_taint(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        module: str,
        file_path: str,
    ) -> "FunctionTaintInfo":
        """
        Analyze a function for taint characteristics.

        Determines:
        - Which parameters are used in dangerous sinks
        - Which local variables are tainted
        - What the function returns (tainted or not)
        """
        info = FunctionTaintInfo(
            name=node.name,
            module=module,
            file=file_path,
            line=node.lineno,
        )

        # Get parameter names
        for arg in node.args.args:
            info.parameters.append(arg.arg)

        # Analyze function body for taint flows
        visitor = FunctionTaintVisitor(info, self)
        visitor.visit(node)

        return info

    def _build_cross_module_calls(self, result: CrossFileTaintResult) -> None:
        """
        Build the cross-module call graph.
        """
        for module, file_path in self.resolver.module_to_file.items():
            tree = self._get_file_ast(file_path)
            if not tree:
                continue

            imports = self.resolver.imports.get(module, [])

            # Find all call sites
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    call_info = self._analyze_call(node, module, imports)
                    if call_info and call_info.target_module:
                        self.call_graph[module].add(call_info)

    def _analyze_call(
        self,
        node: ast.Call,
        caller_module: str,
        imports: List[ImportInfo],
    ) -> Optional["CallInfo"]:
        """
        Analyze a function call to determine cross-module relationships.
        """
        # Get the callee name
        callee_name = self._get_callee_name(node)
        if not callee_name:
            return None

        # Check if this is an imported function
        for imp in imports:
            if imp.effective_name == callee_name or callee_name.startswith(
                f"{imp.effective_name}."
            ):
                # Found the import
                target_module = imp.module
                target_function = imp.name if imp.name != "*" else callee_name

                return CallInfo(
                    caller_module=caller_module,
                    caller_line=node.lineno,
                    target_module=target_module,
                    target_function=target_function,
                    arguments=self._extract_argument_names(node),
                )

        return None

    def _get_callee_name(self, node: ast.Call) -> Optional[str]:
        """Extract the callee name from a Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return None

    def _extract_argument_names(self, node: ast.Call) -> List[str]:
        """Extract argument names/values from a call."""
        args = []
        for arg in node.args:
            if isinstance(arg, ast.Name):
                args.append(arg.id)
            elif isinstance(arg, ast.Constant):
                args.append(repr(arg.value))
            else:
                args.append("<expr>")
        return args

    def _trace_cross_file_flows(
        self,
        result: CrossFileTaintResult,
        max_depth: int,
    ) -> None:
        """
        Trace taint flows across module boundaries.
        """
        # For each module with taint sources, trace where the taint goes
        for module, sources in self.module_taint_sources.items():
            for source in sources:
                self._trace_flow_from_source(source, module, result, max_depth)

        # For each exported function that receives external input,
        # check if parameters reach sinks
        for module, func_infos in self.function_taint_info.items():
            for func_name, func_info in func_infos.items():
                if func_info.parameters_reaching_sinks:
                    # This function has parameters that reach sinks
                    # Check all callers
                    for caller_module, calls in self.call_graph.items():
                        for call in calls:
                            if (
                                call.target_module == module
                                and call.target_function == func_name
                            ):
                                # Found a call to this function
                                # Check if caller passes tainted data
                                self._check_caller_taint(
                                    call, func_info, result, max_depth
                                )

    def _trace_flow_from_source(
        self,
        source: "TaintSourceInfo",
        module: str,
        result: CrossFileTaintResult,
        max_depth: int,
    ) -> None:
        """
        Trace taint flow from a specific source.
        """
        # BFS to find paths to sinks
        queue = deque()
        visited = set()

        queue.append(
            (module, source.variable, 0, [(module, source.function, source.line)])
        )

        while queue:
            current_module, current_var, depth, path = queue.popleft()

            if depth > max_depth:
                continue

            key = (current_module, current_var)
            if key in visited:
                continue
            visited.add(key)

            # Check if this variable reaches a sink in current module
            func_infos = self.function_taint_info.get(current_module, {})
            for func_name, func_info in func_infos.items():
                if current_var in func_info.local_sinks:
                    sink_info = func_info.local_sinks[current_var]
                    flow = CrossFileTaintFlow(
                        source_module=module,
                        source_function=source.function,
                        source_line=source.line,
                        sink_module=current_module,
                        sink_function=func_name,
                        sink_line=sink_info.line,
                        sink_type=sink_info.sink_type,
                        flow_path=path + [(current_module, func_name, sink_info.line)],
                        tainted_data=source.variable,
                    )
                    result.taint_flows.append(flow)

    def _check_caller_taint(
        self,
        call: "CallInfo",
        func_info: "FunctionTaintInfo",
        result: CrossFileTaintResult,
        max_depth: int,
    ) -> None:
        """
        Check if a caller passes tainted data to a function with sinks.
        """
        # Get caller's function taint info
        caller_funcs = self.function_taint_info.get(call.caller_module, {})

        # For each argument in the call
        for i, arg_name in enumerate(call.arguments):
            if i < len(func_info.parameters):
                param = func_info.parameters[i]

                # Check if this parameter reaches a sink
                if param in func_info.parameters_reaching_sinks:
                    sink_info = func_info.parameters_reaching_sinks[param]

                    # Check if the argument is tainted in the caller
                    for caller_func, caller_info in caller_funcs.items():
                        if arg_name in caller_info.tainted_variables:
                            # Found cross-file taint flow!
                            taint_param = TaintedParameter(
                                function_name=func_info.name,
                                parameter_name=param,
                                module=func_info.module,
                                file=func_info.file,
                                line=func_info.line,
                            )
                            taint_param.callers.add(
                                (call.caller_module, call.caller_line)
                            )
                            result.tainted_parameters.append(taint_param)

                            flow = CrossFileTaintFlow(
                                source_module=call.caller_module,
                                source_function=caller_func,
                                source_line=call.caller_line,
                                sink_module=func_info.module,
                                sink_function=func_info.name,
                                sink_line=sink_info.line,
                                sink_type=sink_info.sink_type,
                                flow_path=[
                                    (call.caller_module, caller_func, call.caller_line),
                                    (func_info.module, func_info.name, sink_info.line),
                                ],
                                tainted_data=arg_name,
                            )
                            result.taint_flows.append(flow)

    def _identify_vulnerabilities(self, result: CrossFileTaintResult) -> None:
        """
        Convert taint flows into vulnerability reports.
        """
        seen = set()

        for flow in result.taint_flows:
            # Deduplicate
            flow_key = (
                flow.source_module,
                flow.source_line,
                flow.sink_module,
                flow.sink_line,
            )
            if flow_key in seen:
                continue
            seen.add(flow_key)

            # Get CWE info
            cwe_id, vuln_name = SINK_TO_CWE.get(
                flow.sink_type, ("CWE-Unknown", "Unknown Vulnerability")
            )

            # Determine severity
            severity = self._determine_severity(flow)

            vuln = CrossFileVulnerability(
                vulnerability_type=vuln_name,
                severity=severity,
                cwe_id=cwe_id,
                flow=flow,
                description=self._generate_description(flow, vuln_name),
                recommendation=self._generate_recommendation(flow.sink_type),
            )
            result.vulnerabilities.append(vuln)

    def _determine_severity(self, flow: CrossFileTaintFlow) -> str:
        """Determine vulnerability severity."""
        high_severity_sinks = {
            CrossFileSink.SQL_QUERY,
            CrossFileSink.SHELL_COMMAND,
            CrossFileSink.EVAL,
            CrossFileSink.DESERIALIZATION,
        }

        if flow.sink_type in high_severity_sinks:
            return "HIGH"
        elif flow.sink_type in {CrossFileSink.FILE_PATH, CrossFileSink.TEMPLATE_RENDER}:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_description(self, flow: CrossFileTaintFlow, vuln_name: str) -> str:
        """Generate vulnerability description."""
        return (
            f"{vuln_name}: Tainted data '{flow.tainted_data}' flows from "
            f"{flow.source_module}:{flow.source_line} to dangerous sink at "
            f"{flow.sink_module}:{flow.sink_line}"
        )

    def _generate_recommendation(self, sink_type: CrossFileSink) -> str:
        """Generate remediation recommendation."""
        recommendations = {
            CrossFileSink.SQL_QUERY: "Use parameterized queries or ORM methods instead of string concatenation",
            CrossFileSink.HTML_OUTPUT: "Escape output using appropriate context-aware encoding",
            CrossFileSink.FILE_PATH: "Validate and sanitize file paths, use allowlists",
            CrossFileSink.SHELL_COMMAND: "Avoid shell commands with user input; use subprocess with list arguments",
            CrossFileSink.EVAL: "Never use eval/exec with user input",
            CrossFileSink.DESERIALIZATION: "Use safe serialization formats like JSON, validate before deserializing",
            CrossFileSink.NETWORK_REQUEST: "Validate and sanitize URLs, use allowlists for domains",
            CrossFileSink.TEMPLATE_RENDER: "Use auto-escaping templates, validate template names",
        }
        return recommendations.get(
            sink_type, "Review and sanitize user input before use"
        )

    def get_taint_graph_mermaid(self) -> str:
        """
        Generate a Mermaid diagram of cross-file taint flows.

        Returns:
            Mermaid diagram string
        """
        lines = ["graph LR"]

        # Add nodes for modules
        node_ids = {}
        for i, module in enumerate(self.resolver.module_to_file.keys()):
            node_id = f"M{i}"
            node_ids[module] = node_id
            safe_name = module.replace(".", "_")
            lines.append(f"    {node_id}[{safe_name}]")

        # Add edges for calls
        for caller, calls in self.call_graph.items():
            if caller not in node_ids:
                continue
            for call in calls:
                if call.target_module in node_ids:
                    lines.append(
                        f"    {node_ids[caller]} -->|{call.target_function}| {node_ids[call.target_module]}"
                    )

        return "\n".join(lines)


@dataclass
class FunctionTaintInfo:
    """Information about taint characteristics of a function."""

    name: str
    module: str
    file: str
    line: int
    parameters: List[str] = field(default_factory=list)
    tainted_variables: Set[str] = field(default_factory=set)
    parameters_reaching_sinks: Dict[str, "SinkInfo"] = field(default_factory=dict)
    local_sinks: Dict[str, "SinkInfo"] = field(default_factory=dict)
    returns_tainted: bool = False


@dataclass
class SinkInfo:
    """Information about a dangerous sink."""

    sink_type: CrossFileSink
    line: int
    function_call: str


@dataclass
class TaintSourceInfo:
    """Information about a taint source in a module."""

    source_type: CrossFileTaintSource
    variable: str
    function: str
    line: int


@dataclass(frozen=True)
class CallInfo:
    """Information about a cross-module function call."""

    caller_module: str
    caller_line: int
    target_module: str
    target_function: str
    arguments: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        # Convert list to tuple for hashability
        if isinstance(self.arguments, list):
            object.__setattr__(self, "arguments", tuple(self.arguments))

    def __hash__(self):
        return hash(
            (
                self.caller_module,
                self.caller_line,
                self.target_module,
                self.target_function,
            )
        )


class FunctionTaintVisitor(ast.NodeVisitor):
    """
    AST visitor to analyze taint flow within a function.
    """

    def __init__(self, func_info: FunctionTaintInfo, tracker: CrossFileTaintTracker):
        self.func_info = func_info
        self.tracker = tracker
        self.current_var: Optional[str] = None

    def visit_Assign(self, node: ast.Assign) -> None:
        """Track variable assignments."""
        # Check if RHS is a taint source
        rhs_tainted = self._is_taint_source(node.value)

        if rhs_tainted:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.func_info.tainted_variables.add(target.id)

        # Check if assigning from a parameter
        if isinstance(node.value, ast.Name):
            if node.value.id in self.func_info.parameters:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.func_info.tainted_variables.add(target.id)

        # [20251215_BUGFIX] v2.0.1 - Check if assigning from a call to a tainted function
        if isinstance(node.value, ast.Call):
            callee = self._get_callee_name(node.value)
            if callee and self._is_imported_tainted_function(callee):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.func_info.tainted_variables.add(target.id)

        self.generic_visit(node)

    def _is_imported_tainted_function(self, callee: str) -> bool:
        """
        [20251215_BUGFIX] Check if a callee is an imported function that returns tainted data.

        This enables multi-hop taint tracking through import chains.
        """
        if not self.tracker:
            return False

        # Check if this function is imported
        module = self.func_info.module
        imports = self.tracker.resolver.imports.get(module, [])

        for imp in imports:
            if imp.effective_name == callee:
                # Found the import - check if target function returns tainted
                target_module = imp.module
                target_func = imp.name if imp.name != "*" else callee

                # Look up the function in our taint info
                target_funcs = self.tracker.function_taint_info.get(target_module, {})
                target_info = target_funcs.get(target_func)

                if target_info and target_info.returns_tainted:
                    return True

        return False

    def visit_Call(self, node: ast.Call) -> None:
        """Check for dangerous sinks."""
        callee = self._get_callee_name(node)

        if callee in DANGEROUS_SINKS:
            sink_type = DANGEROUS_SINKS[callee]

            # Check if any argument is tainted
            for i, arg in enumerate(node.args):
                tainted_vars_in_arg = self._extract_tainted_vars_from_arg(arg)

                for arg_name in tainted_vars_in_arg:
                    # Check if parameter or tainted variable
                    if arg_name in self.func_info.parameters:
                        self.func_info.parameters_reaching_sinks[arg_name] = SinkInfo(
                            sink_type=sink_type,
                            line=node.lineno,
                            function_call=callee,
                        )

                    if arg_name in self.func_info.tainted_variables:
                        self.func_info.local_sinks[arg_name] = SinkInfo(
                            sink_type=sink_type,
                            line=node.lineno,
                            function_call=callee,
                        )

        # [20251215_BUGFIX] v2.0.1 - Check for callback pattern
        # If a tainted variable is passed along with a function that has dangerous sinks,
        # the taint flows through the callback
        self._check_callback_taint_pattern(node)

        self.generic_visit(node)

    def _check_callback_taint_pattern(self, node: ast.Call) -> None:
        """
        [20251215_BUGFIX] v2.0.1 - Detect callback taint pattern.

        Pattern: with_callback(tainted_data, dangerous_callback)

        If:
        1. One argument is tainted (tainted_data)
        2. Another argument is a function name (dangerous_callback)
        3. That function has parameters_reaching_sinks

        Then the tainted data flows to the callback's sink.
        """
        if not self.tracker:
            return

        # Find tainted arguments and callback function arguments
        tainted_args = []
        callback_funcs = []

        for i, arg in enumerate(node.args):
            if isinstance(arg, ast.Name):
                # Check if this is a tainted variable
                if (
                    arg.id in self.func_info.tainted_variables
                    or arg.id in self.func_info.parameters
                ):
                    tainted_args.append((i, arg.id))
                # Check if this is a function name with dangerous sinks
                func_info = self._get_function_info_by_name(arg.id)
                if func_info and func_info.parameters_reaching_sinks:
                    callback_funcs.append((i, arg.id, func_info))

        # If we have both tainted args and callback functions, create a flow
        if tainted_args and callback_funcs:
            for _, tainted_var in tainted_args:
                for _, callback_name, callback_info in callback_funcs:
                    for (
                        param,
                        sink_info,
                    ) in callback_info.parameters_reaching_sinks.items():
                        # The tainted data flows through the callback to the sink
                        self.func_info.local_sinks[tainted_var] = SinkInfo(
                            sink_type=sink_info.sink_type,
                            line=node.lineno,
                            function_call=f"{callback_name} (callback)",
                        )

    def _get_function_info_by_name(
        self, func_name: str
    ) -> Optional["FunctionTaintInfo"]:
        """
        [20251215_BUGFIX] v2.0.1 - Look up function taint info by name.

        Checks both local module and imported functions.
        """
        if not self.tracker:
            return None

        # Check local module first
        local_funcs = self.tracker.function_taint_info.get(self.func_info.module, {})
        if func_name in local_funcs:
            return local_funcs[func_name]

        # Check imported functions
        imports = self.tracker.resolver.imports.get(self.func_info.module, [])
        for imp in imports:
            if imp.effective_name == func_name:
                target_funcs = self.tracker.function_taint_info.get(imp.module, {})
                return target_funcs.get(imp.name)

        return None

    def _extract_tainted_vars_from_arg(self, arg: ast.expr) -> List[str]:
        """
        [20251215_BUGFIX] v2.0.1 - Extract variable names from an argument expression.

        Handles:
        - Simple names: x
        - F-strings: f"SELECT * FROM users WHERE id = {user_id}"
        - BinOp string concatenation: "SELECT * FROM users WHERE id = " + user_id
        - Format strings: "SELECT * FROM users WHERE id = {}".format(user_id)
        """
        result = []

        if isinstance(arg, ast.Name):
            result.append(arg.id)
        elif isinstance(arg, ast.JoinedStr):
            # F-string - extract variables from FormattedValue nodes
            for value in arg.values:
                if isinstance(value, ast.FormattedValue):
                    if isinstance(value.value, ast.Name):
                        result.append(value.value.id)
        elif isinstance(arg, ast.BinOp):
            # String concatenation with +
            result.extend(self._extract_tainted_vars_from_arg(arg.left))
            result.extend(self._extract_tainted_vars_from_arg(arg.right))
        elif isinstance(arg, ast.Call):
            # Method call like "...".format(x, y) or str.format(...)
            callee = self._get_callee_name(arg)
            if callee and "format" in callee:
                for sub_arg in arg.args:
                    result.extend(self._extract_tainted_vars_from_arg(sub_arg))
        elif isinstance(arg, ast.Mod):
            # Old-style formatting: "..." % x
            result.extend(self._extract_tainted_vars_from_arg(arg))

        return result

    def visit_Return(self, node: ast.Return) -> None:
        """Check if function returns tainted data."""
        if node.value:
            if isinstance(node.value, ast.Name):
                if node.value.id in self.func_info.tainted_variables:
                    self.func_info.returns_tainted = True
                if node.value.id in self.func_info.parameters:
                    self.func_info.returns_tainted = True
            # [20251215_BUGFIX] v2.0.1 - Check if directly returning a taint source
            elif self._is_taint_source(node.value):
                self.func_info.returns_tainted = True
            # [20251215_BUGFIX] v2.0.1 - Check if returning a call to an imported tainted function
            elif isinstance(node.value, ast.Call):
                callee = self._get_callee_name(node.value)
                if callee and self._is_imported_tainted_function(callee):
                    self.func_info.returns_tainted = True
                # [20251215_BUGFIX] v2.0.1 - Check if returning a method call on a tainted variable
                # e.g., return data.strip() where data is tainted
                if self._is_method_on_tainted_var(node.value):
                    self.func_info.returns_tainted = True

        self.generic_visit(node)

    def _is_method_on_tainted_var(self, call_node: ast.Call) -> bool:
        """
        [20251215_BUGFIX] v2.0.1 - Check if a call is a method on a tainted variable.

        e.g., data.strip() where data is in tainted_variables
        """
        if isinstance(call_node.func, ast.Attribute):
            # Get the object the method is called on
            value = call_node.func.value
            if isinstance(value, ast.Name):
                return (
                    value.id in self.func_info.tainted_variables
                    or value.id in self.func_info.parameters
                )
        return False

    def _is_taint_source(self, node: ast.expr) -> bool:
        """Check if an expression is a taint source."""
        callee = self._get_callee_name_from_expr(node)
        return callee in TAINT_SOURCES

    def _get_callee_name(self, node: ast.Call) -> Optional[str]:
        """Get callee name from Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return None

    def _get_callee_name_from_expr(self, node: ast.expr) -> Optional[str]:
        """Get callee name from expression (for detecting taint sources)."""
        if isinstance(node, ast.Call):
            return self._get_callee_name(node)
        return None
