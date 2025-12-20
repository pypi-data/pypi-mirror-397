"""
Code Scalpel MCP Server - Real MCP Protocol Implementation.

This server implements the Model Context Protocol (MCP) specification using
the official Python SDK. It exposes Code Scalpel's analysis tools to any
MCP-compliant client (Claude Desktop, Cursor, etc.).

Transports:
- stdio: Default. Client spawns server as subprocess. Best for local use.
- streamable-http: Network deployment. Requires explicit --transport flag.

Usage:
    # stdio (default)
    python -m code_scalpel.mcp.server

    # HTTP transport for network access
    python -m code_scalpel.mcp.server --transport streamable-http --port 8080

Security:
    - Code is PARSED, never executed (ast.parse only)
    - Maximum code size enforced
    - HTTP transport binds to 127.0.0.1 by default
"""

from __future__ import annotations

import ast
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from code_scalpel import SurgicalExtractor

from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP, Context

# [20251216_FEATURE] v2.5.0 - Unified sink detection MCP tool
from code_scalpel.symbolic_execution_tools.unified_sink_detector import (
    UnifiedSinkDetector,
)

# [20251218_BUGFIX] Import version from package instead of hardcoding
from code_scalpel import __version__


# [20251215_BUGFIX] Configure logging to stderr only to prevent stdio transport corruption
# When using stdio transport, stdout must contain ONLY valid JSON-RPC messages.
# Any logging to stdout will corrupt the protocol stream.
def _configure_logging(transport: str = "stdio"):
    """Configure logging based on transport type."""
    root_logger = logging.getLogger()

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Always log to stderr to avoid corrupting stdio transport
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # Set level based on environment
    level = logging.DEBUG if os.environ.get("SCALPEL_DEBUG") else logging.WARNING
    handler.setLevel(level)
    root_logger.setLevel(level)
    root_logger.addHandler(handler)


# Setup logging (default to stderr)
logger = logging.getLogger(__name__)

# Maximum code size to prevent resource exhaustion
MAX_CODE_SIZE = 100_000

# Project root for resources (default to current directory)
PROJECT_ROOT = Path.cwd()

# [20251215_FEATURE] v2.0.0 - Roots capability for file system boundaries
# Client-specified allowed directories. If empty, PROJECT_ROOT is used.
ALLOWED_ROOTS: list[Path] = []

# Caching enabled by default
CACHE_ENABLED = os.environ.get("SCALPEL_CACHE_ENABLED", "1") != "0"


def _is_path_allowed(path: Path) -> bool:
    """
    Check if a path is within allowed roots.

    [20251215_FEATURE] v2.0.0 - Security boundary enforcement

    Args:
        path: Path to validate

    Returns:
        True if path is within allowed roots, False otherwise
    """
    resolved = path.resolve()

    # If no roots specified, use PROJECT_ROOT
    roots_to_check = ALLOWED_ROOTS if ALLOWED_ROOTS else [PROJECT_ROOT]

    for root in roots_to_check:
        try:
            resolved.relative_to(root.resolve())
            return True
        except ValueError:
            continue

    return False


def _validate_path_security(path: Path) -> Path:
    """
    Validate path is within allowed roots and return resolved path.

    [20251215_FEATURE] v2.0.0 - Security validation with helpful errors

    Args:
        path: Path to validate

    Returns:
        Resolved path if valid

    Raises:
        PermissionError: If path is outside allowed roots
    """
    resolved = path.resolve()

    if not _is_path_allowed(resolved):
        roots_str = ", ".join(str(r) for r in (ALLOWED_ROOTS or [PROJECT_ROOT]))
        raise PermissionError(
            f"Access denied: {path} is outside allowed roots.\n"
            f"Allowed roots: {roots_str}\n"
            f"Set roots via the roots/list capability or SCALPEL_ROOT environment variable."
        )


async def _fetch_and_cache_roots(ctx: Context | None) -> list[Path]:
    """
    Fetch roots from client via MCP context and cache in ALLOWED_ROOTS.

    [20251215_FEATURE] v2.0.0 - Dynamic roots capability support

    This function requests the list of allowed filesystem roots from the
    MCP client. Roots define the boundaries where the server can operate.

    Args:
        ctx: MCP Context object (from tool execution)

    Returns:
        List of allowed root paths

    Note:
        If ctx is None or client doesn't support roots, returns PROJECT_ROOT.
        Roots are cached in ALLOWED_ROOTS global for subsequent calls.
    """
    global ALLOWED_ROOTS

    if ctx is None:
        return [PROJECT_ROOT]

    try:
        # Request roots from client via MCP protocol
        roots = await ctx.list_roots()

        if roots:
            # Convert file:// URIs to Path objects
            ALLOWED_ROOTS = []
            for root in roots:
                uri = str(root.uri)
                if uri.startswith("file://"):
                    # Handle file:// URIs (e.g., file:///home/user/project)
                    # Remove 'file://' prefix and handle Windows paths
                    path_str = uri[7:]  # Remove 'file://'
                    # Windows paths may have extra slash: file:///C:/path
                    if len(path_str) >= 3 and path_str[0] == "/" and path_str[2] == ":":
                        path_str = path_str[1:]  # Remove leading /
                    ALLOWED_ROOTS.append(Path(path_str))
                else:
                    # Non-file URIs - log warning but try as path
                    logger.warning(f"Non-file root URI: {uri}")
                    ALLOWED_ROOTS.append(Path(uri))

            logger.debug(f"Updated ALLOWED_ROOTS from client: {ALLOWED_ROOTS}")
            return ALLOWED_ROOTS
        else:
            return [PROJECT_ROOT]

    except Exception as e:
        # Client may not support roots capability
        logger.debug(f"Could not fetch roots from client: {e}")
        return [PROJECT_ROOT]


# ============================================================================
# CACHING
# ============================================================================


def _get_cache():
    """Get the analysis cache (lazy initialization)."""
    if not CACHE_ENABLED:
        return None
    try:
        from code_scalpel.utilities.cache import get_cache

        return get_cache()
    except ImportError:
        logger.warning("Cache module not available")
        return None


# ============================================================================
# STRUCTURED OUTPUT MODELS
# ============================================================================


class FunctionInfo(BaseModel):
    """Information about a function."""

    name: str = Field(description="Function name")
    lineno: int = Field(description="Line number where function starts")
    end_lineno: int | None = Field(
        default=None, description="Line number where function ends"
    )
    is_async: bool = Field(default=False, description="Whether function is async")


class ClassInfo(BaseModel):
    """Information about a class."""

    name: str = Field(description="Class name")
    lineno: int = Field(description="Line number where class starts")
    end_lineno: int | None = Field(
        default=None, description="Line number where class ends"
    )
    methods: list[str] = Field(
        default_factory=list, description="Method names in class"
    )


class AnalysisResult(BaseModel):
    """Result of code analysis."""

    success: bool = Field(description="Whether analysis succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    functions: list[str] = Field(description="List of function names found")
    classes: list[str] = Field(description="List of class names found")
    imports: list[str] = Field(description="List of import statements")
    function_count: int = Field(description="Total number of functions found")
    class_count: int = Field(description="Total number of classes found")
    complexity: int = Field(description="Cyclomatic complexity estimate")
    lines_of_code: int = Field(description="Total lines of code")
    issues: list[str] = Field(default_factory=list, description="Issues found")
    error: str | None = Field(default=None, description="Error message if failed")
    # v1.3.0: Detailed info with line numbers
    function_details: list[FunctionInfo] = Field(
        default_factory=list, description="Detailed function info with line numbers"
    )
    class_details: list[ClassInfo] = Field(
        default_factory=list, description="Detailed class info with line numbers"
    )


class VulnerabilityInfo(BaseModel):
    """Information about a detected vulnerability."""

    type: str = Field(description="Vulnerability type (e.g., SQL Injection)")
    cwe: str = Field(description="CWE identifier")
    severity: str = Field(description="Severity level")
    line: int | None = Field(default=None, description="Line number if known")
    description: str = Field(description="Description of the vulnerability")


class SecurityResult(BaseModel):
    """Result of security analysis."""

    success: bool = Field(description="Whether analysis succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    has_vulnerabilities: bool = Field(description="Whether vulnerabilities were found")
    vulnerability_count: int = Field(description="Number of vulnerabilities")
    risk_level: str = Field(description="Overall risk level")
    vulnerabilities: list[VulnerabilityInfo] = Field(
        default_factory=list, description="List of vulnerabilities"
    )
    taint_sources: list[str] = Field(
        default_factory=list, description="Identified taint sources"
    )
    error: str | None = Field(default=None, description="Error message if failed")


# [20251216_FEATURE] Unified sink detection result model
class UnifiedDetectedSink(BaseModel):
    """Detected sink with confidence and OWASP mapping."""

    pattern: str = Field(description="Sink pattern matched")
    sink_type: str = Field(description="Sink type classification")
    confidence: float = Field(description="Confidence score (0.0-1.0)")
    line: int = Field(default=0, description="Line number of sink occurrence")
    column: int = Field(default=0, description="Column offset of sink occurrence")
    code_snippet: str = Field(default="", description="Snippet around the sink")
    vulnerability_type: str | None = Field(
        default=None, description="Vulnerability category key"
    )
    owasp_category: str | None = Field(
        default=None, description="Mapped OWASP Top 10 category"
    )


class UnifiedSinkResult(BaseModel):
    """Result of unified polyglot sink detection."""

    success: bool = Field(description="Whether detection succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    language: str = Field(description="Language analyzed")
    sink_count: int = Field(description="Number of sinks detected")
    sinks: list[UnifiedDetectedSink] = Field(
        default_factory=list, description="Detected sinks meeting threshold"
    )
    coverage_summary: dict[str, Any] = Field(
        default_factory=dict, description="Summary of sink pattern coverage"
    )
    error: str | None = Field(default=None, description="Error message if failed")


class PathCondition(BaseModel):
    """A condition along an execution path."""

    condition: str = Field(description="The condition expression")
    is_satisfiable: bool = Field(description="Whether condition is satisfiable")


class ExecutionPath(BaseModel):
    """An execution path discovered by symbolic execution."""

    path_id: int = Field(description="Unique path identifier")
    conditions: list[str] = Field(description="Conditions along the path")
    final_state: dict[str, Any] = Field(description="Variable values at path end")
    reproduction_input: dict[str, Any] | None = Field(
        default=None, description="Input values that trigger this path"
    )
    is_reachable: bool = Field(description="Whether path is reachable")


class SymbolicResult(BaseModel):
    """Result of symbolic execution."""

    success: bool = Field(description="Whether analysis succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    paths_explored: int = Field(description="Number of execution paths explored")
    paths: list[ExecutionPath] = Field(
        default_factory=list, description="Discovered execution paths"
    )
    symbolic_variables: list[str] = Field(
        default_factory=list, description="Variables treated symbolically"
    )
    constraints: list[str] = Field(
        default_factory=list, description="Discovered constraints"
    )
    error: str | None = Field(default=None, description="Error message if failed")


class GeneratedTestCase(BaseModel):
    """A generated test case."""

    path_id: int = Field(description="Path ID this test covers")
    function_name: str = Field(description="Function being tested")
    inputs: dict[str, Any] = Field(description="Input values for this test")
    description: str = Field(description="Human-readable description")
    path_conditions: list[str] = Field(
        default_factory=list, description="Conditions that define this path"
    )


class TestGenerationResult(BaseModel):
    """Result of test generation."""

    success: bool = Field(description="Whether generation succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    function_name: str = Field(description="Function tests were generated for")
    test_count: int = Field(description="Number of test cases generated")
    test_cases: list[GeneratedTestCase] = Field(
        default_factory=list, description="Generated test cases"
    )
    pytest_code: str = Field(default="", description="Generated pytest code")
    unittest_code: str = Field(default="", description="Generated unittest code")
    error: str | None = Field(default=None, description="Error message if failed")


class RefactorSecurityIssue(BaseModel):
    """A security issue found in refactored code."""

    type: str = Field(description="Vulnerability type")
    severity: str = Field(description="Severity level")
    line: int | None = Field(default=None, description="Line number")
    description: str = Field(description="Issue description")
    cwe: str | None = Field(default=None, description="CWE identifier")


class RefactorSimulationResult(BaseModel):
    """Result of refactor simulation."""

    success: bool = Field(description="Whether simulation succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    is_safe: bool = Field(description="Whether the refactor is safe to apply")
    status: str = Field(description="Status: safe, unsafe, warning, or error")
    reason: str | None = Field(default=None, description="Reason if not safe")
    security_issues: list[RefactorSecurityIssue] = Field(
        default_factory=list, description="Security issues found"
    )
    structural_changes: dict[str, Any] = Field(
        default_factory=dict, description="Functions/classes added/removed"
    )
    warnings: list[str] = Field(default_factory=list, description="Warnings")
    error: str | None = Field(default=None, description="Error message if failed")


class CrawlFunctionInfo(BaseModel):
    """Information about a function from project crawl."""

    name: str = Field(description="Function name (qualified if method)")
    lineno: int = Field(description="Line number")
    complexity: int = Field(description="Cyclomatic complexity")


class CrawlClassInfo(BaseModel):
    """Information about a class from project crawl."""

    name: str = Field(description="Class name")
    lineno: int = Field(description="Line number")
    methods: list[CrawlFunctionInfo] = Field(
        default_factory=list, description="Methods in the class"
    )
    bases: list[str] = Field(default_factory=list, description="Base classes")


class CrawlFileResult(BaseModel):
    """Result of analyzing a single file during crawl."""

    path: str = Field(description="Relative path to the file")
    status: str = Field(description="success or error")
    lines_of_code: int = Field(default=0, description="Lines of code")
    functions: list[CrawlFunctionInfo] = Field(
        default_factory=list, description="Top-level functions"
    )
    classes: list[CrawlClassInfo] = Field(
        default_factory=list, description="Classes found"
    )
    imports: list[str] = Field(default_factory=list, description="Import statements")
    complexity_warnings: list[CrawlFunctionInfo] = Field(
        default_factory=list, description="High-complexity functions"
    )
    error: str | None = Field(default=None, description="Error if failed")


class CrawlSummary(BaseModel):
    """Summary statistics from project crawl."""

    total_files: int = Field(description="Total files scanned")
    successful_files: int = Field(description="Files analyzed successfully")
    failed_files: int = Field(description="Files that failed analysis")
    total_lines_of_code: int = Field(description="Total lines of code")
    total_functions: int = Field(description="Total functions found")
    total_classes: int = Field(description="Total classes found")
    complexity_warnings: int = Field(description="Number of high-complexity functions")


class ProjectCrawlResult(BaseModel):
    """Result of crawling an entire project."""

    success: bool = Field(description="Whether crawl succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    root_path: str = Field(description="Project root path")
    timestamp: str = Field(description="When the crawl was performed")
    summary: CrawlSummary = Field(description="Summary statistics")
    files: list[CrawlFileResult] = Field(
        default_factory=list, description="Analyzed files"
    )
    errors: list[CrawlFileResult] = Field(
        default_factory=list, description="Files with errors"
    )
    markdown_report: str = Field(default="", description="Markdown report")
    error: str | None = Field(default=None, description="Error if failed")


class SurgicalExtractionResult(BaseModel):
    """Result of surgical code extraction."""

    success: bool = Field(description="Whether extraction succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    name: str = Field(description="Name of extracted element")
    code: str = Field(description="Extracted source code")
    node_type: str = Field(description="Type: function, class, or method")
    line_start: int = Field(default=0, description="Starting line number")
    line_end: int = Field(default=0, description="Ending line number")
    dependencies: list[str] = Field(
        default_factory=list, description="Names of dependencies"
    )
    imports_needed: list[str] = Field(
        default_factory=list, description="Required import statements"
    )
    token_estimate: int = Field(default=0, description="Estimated token count")
    error: str | None = Field(default=None, description="Error if failed")


class ContextualExtractionResult(BaseModel):
    """Result of extraction with dependencies included."""

    success: bool = Field(description="Whether extraction succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    target_name: str = Field(description="Name of target element")
    target_code: str = Field(description="Target element source code")
    context_code: str = Field(description="Combined dependency source code")
    full_code: str = Field(description="Complete code block for LLM consumption")
    context_items: list[str] = Field(
        default_factory=list, description="Names of included dependencies"
    )
    total_lines: int = Field(default=0, description="Total lines in extraction")
    # v1.3.0: Line number information
    line_start: int = Field(default=0, description="Starting line number of target")
    line_end: int = Field(default=0, description="Ending line number of target")
    token_estimate: int = Field(default=0, description="Estimated token count")
    error: str | None = Field(default=None, description="Error if failed")

    # [20251216_FEATURE] v2.0.2 - JSX/TSX extraction metadata
    jsx_normalized: bool = Field(
        default=False, description="Whether JSX syntax was normalized"
    )
    is_server_component: bool = Field(
        default=False, description="Next.js Server Component (async)"
    )
    is_server_action: bool = Field(
        default=False, description="Next.js Server Action ('use server')"
    )
    component_type: str | None = Field(
        default=None, description="React component type: 'functional', 'class', or None"
    )


class PatchResultModel(BaseModel):
    """Result of a surgical code modification."""

    success: bool = Field(description="Whether the patch was applied successfully")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    file_path: str = Field(description="Path to the modified file")
    target_name: str = Field(description="Name of the modified symbol")
    target_type: str = Field(description="Type: function, class, or method")
    lines_before: int = Field(default=0, description="Lines in original code")
    lines_after: int = Field(default=0, description="Lines in replacement code")
    lines_delta: int = Field(default=0, description="Change in line count")
    backup_path: str | None = Field(default=None, description="Path to backup file")
    error: str | None = Field(default=None, description="Error message if failed")


# [20251212_FEATURE] v1.4.0 - New MCP tool models for enhanced AI context


class FileContextResult(BaseModel):
    """Result of get_file_context - file overview without full content."""

    success: bool = Field(description="Whether analysis succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    file_path: str = Field(description="Path to the analyzed file")
    language: str = Field(default="python", description="Detected language")
    line_count: int = Field(description="Total lines in file")
    functions: list[str] = Field(default_factory=list, description="Function names")
    classes: list[str] = Field(default_factory=list, description="Class names")
    imports: list[str] = Field(default_factory=list, description="Import statements")
    exports: list[str] = Field(
        default_factory=list, description="Exported symbols (__all__)"
    )
    complexity_score: int = Field(
        default=0, description="Overall cyclomatic complexity"
    )
    has_security_issues: bool = Field(
        default=False, description="Whether file has security issues"
    )
    summary: str = Field(default="", description="Brief description of file purpose")
    error: str | None = Field(default=None, description="Error message if failed")


class SymbolReference(BaseModel):
    """A single reference to a symbol."""

    file: str = Field(description="File path containing the reference")
    line: int = Field(description="Line number of the reference")
    column: int = Field(default=0, description="Column number")
    context: str = Field(description="Code snippet showing usage context")
    is_definition: bool = Field(
        default=False, description="Whether this is the definition"
    )


class SymbolReferencesResult(BaseModel):
    """Result of get_symbol_references - all usages of a symbol."""

    success: bool = Field(description="Whether search succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    symbol_name: str = Field(description="Name of the searched symbol")
    definition_file: str | None = Field(
        default=None, description="File where symbol is defined"
    )
    definition_line: int | None = Field(
        default=None, description="Line where symbol is defined"
    )
    references: list[SymbolReference] = Field(
        default_factory=list, description="All references found"
    )
    total_references: int = Field(default=0, description="Total reference count")
    error: str | None = Field(default=None, description="Error message if failed")


# ============================================================================
# MCP SERVER
# ============================================================================

mcp = FastMCP(
    name="Code Scalpel",
    instructions=f"""Code Scalpel v{__version__} - AI-powered code analysis tools:

**TOKEN-EFFICIENT EXTRACTION (READ):**
- extract_code: Surgically extract functions/classes/methods by FILE PATH.
  The SERVER reads the file - YOU pay ~50 tokens instead of ~10,000.
  Supports Python, JavaScript, TypeScript, Java, JSX, TSX (React components).
  Example: extract_code(file_path="/src/utils.py", target_type="function", target_name="calculate_tax")
  React: extract_code(file_path="/components/Button.tsx", target_type="function", target_name="Button", language="tsx")

**JSX/TSX EXTRACTION (v2.0.2):**
- Extract React components with full metadata
- Detects Server Components (Next.js async components)
- Detects Server Actions ('use server' directive)
- Normalizes JSX for consistent analysis
- Returns component_type: "functional" or "class"

**RESOURCE TEMPLATES (v2.0.2):**
Access code via URIs without knowing file paths:
- code:///python/utils/calculate_tax
- code:///typescript/components/UserCard
- code:///java/services.AuthService/authenticate

**SURGICAL MODIFICATION (WRITE):**
- update_symbol: Replace a function/class/method in a file with new code.
  YOU provide only the new symbol - the SERVER handles safe replacement.
  Example: update_symbol(file_path="/src/utils.py", target_type="function",
           target_name="calculate_tax", new_code="def calculate_tax(amount): ...")
  Creates backup, validates syntax, preserves surrounding code.

**ANALYSIS TOOLS:**
- analyze_code: Parse Python/Java code, extract structure (functions, classes, imports)
- security_scan: Detect vulnerabilities using taint analysis (SQL injection, XSS, etc.)
- symbolic_execute: Explore execution paths using symbolic execution
- generate_unit_tests: Generate pytest/unittest tests from symbolic execution paths
- simulate_refactor: Verify a code change is safe before applying it
- crawl_project: Crawl entire project directory, analyze all Python files

**WORKFLOW OPTIMIZATION:**
1. Use extract_code(file_path=...) to get ONLY the symbol you need
2. Modify the extracted code
3. Use update_symbol(file_path=..., new_code=...) to apply the change safely

Code is PARSED only, never executed.""",
)


def _validate_code(code: str) -> tuple[bool, str | None]:
    """Validate code before analysis."""
    if not code:
        return False, "Code cannot be empty"
    if not isinstance(code, str):
        return False, "Code must be a string"
    if len(code) > MAX_CODE_SIZE:
        return False, f"Code exceeds maximum size of {MAX_CODE_SIZE} characters"
    return True, None


def _count_complexity(tree: ast.AST) -> int:
    """Estimate cyclomatic complexity."""
    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
            complexity += len(node.values) - 1
    return complexity


def _analyze_java_code(code: str) -> AnalysisResult:
    """Analyze Java code using tree-sitter."""
    try:
        from code_scalpel.code_parser.java_parsers.java_parser_treesitter import (
            JavaParser,
        )

        parser = JavaParser()
        result = parser.parse(code)
        return AnalysisResult(
            success=True,
            functions=result["functions"],
            classes=result["classes"],
            imports=result["imports"],
            function_count=len(result["functions"]),
            class_count=len(result["classes"]),
            complexity=result["complexity"],
            lines_of_code=result["lines_of_code"],
            issues=result["issues"],
        )
    except ImportError:
        return AnalysisResult(
            success=False,
            functions=[],
            classes=[],
            imports=[],
            function_count=0,
            class_count=0,
            complexity=0,
            lines_of_code=0,
            error="Java support not available. Please install tree-sitter and tree-sitter-java.",
        )
    except Exception as e:
        return AnalysisResult(
            success=False,
            functions=[],
            classes=[],
            imports=[],
            function_count=0,
            class_count=0,
            complexity=0,
            lines_of_code=0,
            error=f"Java analysis failed: {str(e)}",
        )


def _analyze_code_sync(code: str, language: str = "python") -> AnalysisResult:
    """Synchronous implementation of analyze_code."""
    valid, error = _validate_code(code)
    if not valid:
        return AnalysisResult(
            success=False,
            functions=[],
            classes=[],
            imports=[],
            function_count=0,
            class_count=0,
            complexity=0,
            lines_of_code=0,
            error=error,
        )

    # Check cache first
    cache = _get_cache()
    cache_config = {"language": language}
    if cache:
        cached = cache.get(code, "analysis", cache_config)
        if cached is not None:
            logger.debug("Cache hit for analyze_code")
            # Convert dict back to AnalysisResult if needed
            if isinstance(cached, dict):
                return AnalysisResult(**cached)
            return cached

    if language.lower() == "java":
        result = _analyze_java_code(code)
        if cache and result.success:
            cache.set(code, "analysis", result.model_dump(), cache_config)
        return result

    try:
        tree = ast.parse(code)

        functions = []
        function_details = []
        classes = []
        class_details = []
        imports = []
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                function_details.append(
                    FunctionInfo(
                        name=node.name,
                        lineno=node.lineno,
                        end_lineno=getattr(node, "end_lineno", None),
                        is_async=False,
                    )
                )
                # Flag potential issues
                if len(node.name) < 2:
                    issues.append(f"Function '{node.name}' has very short name")
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(f"async {node.name}")
                function_details.append(
                    FunctionInfo(
                        name=node.name,
                        lineno=node.lineno,
                        end_lineno=getattr(node, "end_lineno", None),
                        is_async=True,
                    )
                )
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
                # Extract method names
                methods = [
                    n.name
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                class_details.append(
                    ClassInfo(
                        name=node.name,
                        lineno=node.lineno,
                        end_lineno=getattr(node, "end_lineno", None),
                        methods=methods,
                    )
                )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

        result = AnalysisResult(
            success=True,
            functions=functions,
            classes=classes,
            imports=imports,
            function_count=len(functions),
            class_count=len(classes),
            complexity=_count_complexity(tree),
            lines_of_code=len(code.splitlines()),
            issues=issues,
            function_details=function_details,
            class_details=class_details,
        )

        # Cache successful result
        if cache:
            cache.set(code, "analysis", result.model_dump(), cache_config)

        return result

    except SyntaxError as e:
        return AnalysisResult(
            success=False,
            functions=[],
            classes=[],
            imports=[],
            function_count=0,
            class_count=0,
            complexity=0,
            lines_of_code=0,
            error=f"Syntax error at line {e.lineno}: {e.msg}. Please check your code syntax.",
        )
    except Exception as e:
        return AnalysisResult(
            success=False,
            functions=[],
            classes=[],
            imports=[],
            function_count=0,
            class_count=0,
            complexity=0,
            lines_of_code=0,
            error=f"Analysis failed: {str(e)}",
        )


@mcp.tool()
async def analyze_code(code: str, language: str = "python") -> AnalysisResult:
    """
    Analyze source code structure.

    Use this tool to understand the high-level architecture (classes, functions, imports)
    of a file before attempting to edit it. This helps prevent hallucinating non-existent
    methods or classes.

    Args:
        code: Source code to analyze
        language: Language of the code ("python", "java")

    Returns:
        Structured analysis result with code metrics and structure
    """
    return await asyncio.to_thread(_analyze_code_sync, code, language)


def _security_scan_sync(
    code: Optional[str] = None, file_path: Optional[str] = None
) -> SecurityResult:
    """
    Synchronous implementation of security_scan.

    [20251214_FEATURE] v2.0.0 - Added file_path parameter support.
    """
    # Handle file_path parameter
    if file_path is not None:
        try:
            path = Path(file_path)
            if not path.exists():
                return SecurityResult(
                    success=False,
                    has_vulnerabilities=False,
                    vulnerability_count=0,
                    risk_level="unknown",
                    error=f"File not found: {file_path}",
                )
            if not path.is_file():
                return SecurityResult(
                    success=False,
                    has_vulnerabilities=False,
                    vulnerability_count=0,
                    risk_level="unknown",
                    error=f"Path is not a file: {file_path}",
                )
            code = path.read_text(encoding="utf-8")
        except Exception as e:
            return SecurityResult(
                success=False,
                has_vulnerabilities=False,
                vulnerability_count=0,
                risk_level="unknown",
                error=f"Failed to read file: {str(e)}",
            )

    if code is None:
        return SecurityResult(
            success=False,
            has_vulnerabilities=False,
            vulnerability_count=0,
            risk_level="unknown",
            error="Either 'code' or 'file_path' must be provided",
        )

    valid, error = _validate_code(code)
    if not valid:
        return SecurityResult(
            success=False,
            has_vulnerabilities=False,
            vulnerability_count=0,
            risk_level="unknown",
            error=error,
        )

    # Check cache first
    cache = _get_cache()
    if cache:
        cached = cache.get(code, "security")
        if cached is not None:
            logger.debug("Cache hit for security_scan")
            if isinstance(cached, dict):
                # Reconstruct VulnerabilityInfo objects
                if "vulnerabilities" in cached:
                    cached["vulnerabilities"] = [
                        VulnerabilityInfo(**v) for v in cached["vulnerabilities"]
                    ]
                return SecurityResult(**cached)
            return cached

    try:
        # Import here to avoid circular imports
        from code_scalpel.symbolic_execution_tools.security_analyzer import (
            SecurityAnalyzer,
        )

        analyzer = SecurityAnalyzer()
        result = analyzer.analyze(code).to_dict()

        vulnerabilities = []
        taint_sources = []

        for vuln in result.get("vulnerabilities", []):
            # Extract line number from sink_location tuple (line, col)
            sink_loc = vuln.get("sink_location")
            line_number = (
                sink_loc[0]
                if sink_loc and isinstance(sink_loc, (list, tuple))
                else None
            )

            vulnerabilities.append(
                VulnerabilityInfo(
                    type=vuln.get("type", "Unknown"),
                    cwe=vuln.get("cwe", "Unknown"),
                    severity=vuln.get("severity", "medium"),
                    line=line_number,
                    description=vuln.get("description", ""),
                )
            )

        for source in result.get("taint_sources", []):
            taint_sources.append(str(source))

        vuln_count = len(vulnerabilities)
        if vuln_count == 0:
            risk_level = "low"
        elif vuln_count <= 2:
            risk_level = "medium"
        elif vuln_count <= 5:
            risk_level = "high"
        else:
            risk_level = "critical"

        security_result = SecurityResult(
            success=True,
            has_vulnerabilities=vuln_count > 0,
            vulnerability_count=vuln_count,
            risk_level=risk_level,
            vulnerabilities=vulnerabilities,
            taint_sources=taint_sources,
        )

        # Cache successful result
        if cache:
            cache.set(code, "security", security_result.model_dump())

        return security_result

    except ImportError:
        # Fallback to basic pattern matching if SecurityAnalyzer not available
        return _basic_security_scan(code)
    except Exception as e:
        return SecurityResult(
            success=False,
            has_vulnerabilities=False,
            vulnerability_count=0,
            risk_level="unknown",
            error=f"Security scan failed: {str(e)}",
        )


# ==========================================================================
# [20251216_FEATURE] v2.5.0 - Unified sink detection MCP tool
# ==========================================================================


def _sink_coverage_summary(detector: UnifiedSinkDetector) -> dict[str, Any]:
    """Compute coverage summary across languages."""

    by_language: dict[str, int] = {}
    total_patterns = 0

    for vuln_sinks in detector.sinks.values():
        for lang, sink_list in vuln_sinks.items():
            by_language[lang] = by_language.get(lang, 0) + len(sink_list)
            total_patterns += len(sink_list)

    return {
        "total_patterns": total_patterns,
        "by_language": by_language,
    }


def _unified_sink_detect_sync(
    code: str, language: str, min_confidence: float
) -> UnifiedSinkResult:
    """Synchronous unified sink detection wrapper."""

    lang = (language or "").lower()

    if code is None or code.strip() == "":
        return UnifiedSinkResult(
            success=False,
            language=lang,
            sink_count=0,
            error="code is required",
            coverage_summary={},
        )

    if not 0.0 <= min_confidence <= 1.0:
        return UnifiedSinkResult(
            success=False,
            language=lang,
            sink_count=0,
            error="min_confidence must be between 0.0 and 1.0",
            coverage_summary={},
        )

    detector = UnifiedSinkDetector()
    try:
        detected = detector.detect_sinks(code, lang, min_confidence)
    except ValueError as e:
        return UnifiedSinkResult(
            success=False,
            language=lang,
            sink_count=0,
            error=str(e),
            coverage_summary=_sink_coverage_summary(detector),
        )

    sinks: list[UnifiedDetectedSink] = []
    for sink in detected:
        owasp = detector.get_owasp_category(sink.vulnerability_type)
        sinks.append(
            UnifiedDetectedSink(
                pattern=sink.pattern,
                sink_type=getattr(sink.sink_type, "name", str(sink.sink_type)),
                confidence=sink.confidence,
                line=sink.line,
                column=getattr(sink, "column", 0),
                code_snippet=getattr(sink, "code_snippet", ""),
                vulnerability_type=getattr(sink, "vulnerability_type", None),
                owasp_category=owasp,
            )
        )

    return UnifiedSinkResult(
        success=True,
        language=lang,
        sink_count=len(sinks),
        sinks=sinks,
        coverage_summary=_sink_coverage_summary(detector),
    )


@mcp.tool()
async def unified_sink_detect(
    code: str, language: str, min_confidence: float = 0.8
) -> UnifiedSinkResult:
    """
    Unified polyglot sink detection with confidence thresholds.

    [20251216_FEATURE] v2.5.0 "Guardian" - Expose unified sink detector via MCP.

    Args:
        code: Source code to analyze
        language: Programming language (python, java, typescript, javascript)
        min_confidence: Minimum confidence threshold (0.0-1.0)

    Returns:
        UnifiedSinkResult with detected sinks and coverage summary.
    """

    return await asyncio.to_thread(
        _unified_sink_detect_sync, code, language, min_confidence
    )


@mcp.tool()
async def security_scan(
    code: Optional[str] = None, file_path: Optional[str] = None
) -> SecurityResult:
    """
    Scan Python code for security vulnerabilities using taint analysis.

    Use this tool to audit code for security vulnerabilities before deploying
    or committing changes. It tracks data flow from sources to sinks.

    [20251214_FEATURE] v2.0.0 - Now accepts file_path parameter to scan files directly.

    Detects:
    - SQL Injection (CWE-89)
    - NoSQL Injection (CWE-943) - MongoDB
    - LDAP Injection (CWE-90)
    - Cross-Site Scripting (CWE-79)
    - Command Injection (CWE-78)
    - Path Traversal (CWE-22)
    - XXE - XML External Entity (CWE-611) [v1.4.0]
    - SSTI - Server-Side Template Injection (CWE-1336) [v1.4.0]
    - Hardcoded Secrets (CWE-798) - 30+ patterns
    - Weak Cryptography (CWE-327) - MD5, SHA-1 [v2.0.0]
    - Dangerous Patterns - shell=True, eval(), pickle [v2.0.0]

    Args:
        code: Python source code to scan (provide either code or file_path)
        file_path: Path to Python file to scan (provide either code or file_path)

    Returns:
        Security analysis result with vulnerabilities and risk assessment
    """
    return await asyncio.to_thread(_security_scan_sync, code, file_path)


def _basic_security_scan(code: str) -> SecurityResult:
    """Fallback security scan using pattern matching."""
    vulnerabilities = []
    taint_sources = []

    # Detect common dangerous patterns
    patterns = [
        (
            "execute(",
            "SQL Injection",
            "CWE-89",
            "Possible SQL injection via execute()",
        ),
        ("cursor.execute", "SQL Injection", "CWE-89", "SQL query execution detected"),
        ("os.system(", "Command Injection", "CWE-78", "os.system() call detected"),
        (
            "subprocess.call(",
            "Command Injection",
            "CWE-78",
            "subprocess.call() detected",
        ),
        ("eval(", "Code Injection", "CWE-94", "eval() call detected"),
        ("exec(", "Code Injection", "CWE-94", "exec() call detected"),
        (
            "render_template_string(",
            "XSS",
            "CWE-79",
            "Template injection risk",
        ),
    ]

    for line_num, line in enumerate(code.splitlines(), 1):
        for pattern, vuln_type, cwe, desc in patterns:
            if pattern in line:
                vulnerabilities.append(
                    VulnerabilityInfo(
                        type=vuln_type,
                        cwe=cwe,
                        severity="high" if "Injection" in vuln_type else "medium",
                        line=line_num,
                        description=desc,
                    )
                )

    # Detect taint sources
    source_patterns = ["request.args", "request.form", "input(", "sys.argv"]
    for pattern in source_patterns:
        if pattern in code:
            taint_sources.append(pattern)

    vuln_count = len(vulnerabilities)
    if vuln_count == 0:
        risk_level = "low"
    elif vuln_count <= 2:
        risk_level = "medium"
    else:
        risk_level = "high"

    return SecurityResult(
        success=True,
        has_vulnerabilities=vuln_count > 0,
        vulnerability_count=vuln_count,
        risk_level=risk_level,
        vulnerabilities=vulnerabilities,
        taint_sources=taint_sources,
    )


def _symbolic_execute_sync(code: str, max_paths: int = 10) -> SymbolicResult:
    """Synchronous implementation of symbolic_execute."""
    valid, error = _validate_code(code)
    if not valid:
        return SymbolicResult(
            success=False,
            paths_explored=0,
            error=error,
        )

    # Check cache first (symbolic execution is expensive!)
    cache = _get_cache()
    # [20251214_FEATURE] Include schema to bust caches when model format changes
    cache_config = {"max_paths": max_paths, "model_schema": "friendly_names_v20251214"}
    if cache:
        cached = cache.get(code, "symbolic", cache_config)
        if cached is not None:
            logger.debug("Cache hit for symbolic_execute")
            if isinstance(cached, dict):
                # Reconstruct ExecutionPath objects
                if "paths" in cached:
                    cached["paths"] = [ExecutionPath(**p) for p in cached["paths"]]
                return SymbolicResult(**cached)
            return cached

    try:
        # Import here to avoid circular imports
        from code_scalpel.symbolic_execution_tools import SymbolicAnalyzer
        from code_scalpel.symbolic_execution_tools.engine import PathStatus

        analyzer = SymbolicAnalyzer(max_loop_iterations=max_paths)
        result = analyzer.analyze(code)

        paths = []
        all_constraints = []
        for i, path in enumerate(result.paths):
            # PathResult has: path_id, status, constraints, variables, model
            # Convert Z3 constraints to string conditions
            conditions = [str(c) for c in path.constraints] if path.constraints else []
            all_constraints.extend(conditions)

            paths.append(
                ExecutionPath(
                    path_id=path.path_id,
                    conditions=conditions,
                    final_state=path.variables or {},
                    reproduction_input=path.model or {},
                    is_reachable=path.status == PathStatus.FEASIBLE,
                )
            )

        # If symbolic execution didn't find variables or constraints,
        # supplement with AST-based analysis
        symbolic_vars = (
            list(result.all_variables.keys()) if result.all_variables else []
        )
        constraints_list = list(set(all_constraints))

        if not symbolic_vars or not constraints_list:
            basic = _basic_symbolic_analysis(code)
            if not symbolic_vars and basic.symbolic_variables:
                symbolic_vars = basic.symbolic_variables
            if not constraints_list and basic.constraints:
                constraints_list = basic.constraints
            # Also use basic paths if symbolic found nothing
            if not paths and basic.paths:
                paths = basic.paths

        symbolic_result = SymbolicResult(
            success=True,
            paths_explored=len(paths) if paths else result.total_paths,
            paths=paths,
            symbolic_variables=symbolic_vars,
            constraints=constraints_list,
        )

        # Cache successful result
        if cache:
            cache.set(code, "symbolic", symbolic_result.model_dump(), cache_config)

        return symbolic_result

    except ImportError:
        # Fallback to basic path analysis
        return _basic_symbolic_analysis(code)
    except Exception as e:
        # If symbolic execution fails (e.g., unsupported AST nodes like f-strings),
        # fall back to basic AST-based analysis instead of returning an error
        logger.warning(f"Symbolic execution failed, using basic analysis: {e}")
        return _basic_symbolic_analysis(code)


@mcp.tool()
async def symbolic_execute(code: str, max_paths: int = 10) -> SymbolicResult:
    """
    Perform symbolic execution on Python code.

    Use this tool to explore execution paths and find bugs that static analysis misses.
    It treats variables as symbolic values and uses a Z3 solver to find inputs that
    trigger specific paths.

    Args:
        code: Python source code to analyze
        max_paths: Maximum number of paths to explore (default: 10)

    Returns:
        Symbolic execution result with discovered paths, constraints, and reproduction inputs
    """
    return await asyncio.to_thread(_symbolic_execute_sync, code, max_paths)


def _basic_symbolic_analysis(code: str) -> SymbolicResult:
    """Fallback symbolic analysis using AST inspection."""
    try:
        tree = ast.parse(code)

        # Count branches
        branch_count = 0
        symbolic_vars = []
        conditions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                branch_count += 1
                conditions.append(ast.unparse(node.test))
            elif isinstance(node, ast.While):
                branch_count += 1
                conditions.append(f"while: {ast.unparse(node.test)}")
            elif isinstance(node, ast.For):
                branch_count += 1
                if isinstance(node.target, ast.Name):
                    symbolic_vars.append(node.target.id)
            elif isinstance(node, ast.FunctionDef):
                for arg in node.args.args:
                    symbolic_vars.append(arg.arg)

        # Estimate paths (2^branches, capped)
        estimated_paths = min(2**branch_count, 10)

        paths = [
            ExecutionPath(
                path_id=i,
                conditions=conditions[: i + 1] if i < len(conditions) else conditions,
                final_state={},
                reproduction_input=None,
                is_reachable=True,
            )
            for i in range(estimated_paths)
        ]

        return SymbolicResult(
            success=True,
            paths_explored=estimated_paths,
            paths=paths,
            symbolic_variables=list(set(symbolic_vars)),
            constraints=conditions,
        )

    except Exception as e:
        return SymbolicResult(
            success=False,
            paths_explored=0,
            error=f"Basic analysis failed: {str(e)}",
        )


# ============================================================================
# TEST GENERATION
# ============================================================================


def _generate_tests_sync(
    code: str, function_name: str | None = None, framework: str = "pytest"
) -> TestGenerationResult:
    """Synchronous implementation of generate_unit_tests."""
    valid, error = _validate_code(code)
    if not valid:
        return TestGenerationResult(
            success=False,
            function_name=function_name or "unknown",
            test_count=0,
            error=error,
        )

    try:
        from code_scalpel.generators import TestGenerator

        generator = TestGenerator(framework=framework)
        result = generator.generate(code, function_name=function_name)

        test_cases = [
            GeneratedTestCase(
                path_id=tc.path_id,
                function_name=tc.function_name,
                inputs=tc.inputs,
                description=tc.description,
                path_conditions=tc.path_conditions,
            )
            for tc in result.test_cases
        ]

        return TestGenerationResult(
            success=True,
            function_name=result.function_name,
            test_count=len(test_cases),
            test_cases=test_cases,
            pytest_code=result.pytest_code,
            unittest_code=result.unittest_code,
        )

    except Exception as e:
        return TestGenerationResult(
            success=False,
            function_name=function_name or "unknown",
            test_count=0,
            error=f"Test generation failed: {str(e)}",
        )


@mcp.tool()
async def generate_unit_tests(
    code: str, function_name: str | None = None, framework: str = "pytest"
) -> TestGenerationResult:
    """
    Generate unit tests from code using symbolic execution.

    Use this tool to automatically create test cases that cover all execution paths
    in a function. Each test case includes concrete input values that trigger a
    specific path through the code.

    Args:
        code: Source code containing the function to test
        function_name: Name of function to generate tests for (auto-detected if None)
        framework: Test framework ("pytest" or "unittest")

    Returns:
        Test generation result with generated test code and test cases
    """
    return await asyncio.to_thread(_generate_tests_sync, code, function_name, framework)


# ============================================================================
# REFACTOR SIMULATION
# ============================================================================


def _simulate_refactor_sync(
    original_code: str,
    new_code: str | None = None,
    patch: str | None = None,
    strict_mode: bool = False,
) -> RefactorSimulationResult:
    """Synchronous implementation of simulate_refactor."""
    valid, error = _validate_code(original_code)
    if not valid:
        return RefactorSimulationResult(
            success=False,
            is_safe=False,
            status="error",
            error=f"Invalid original code: {error}",
        )

    if new_code is None and patch is None:
        return RefactorSimulationResult(
            success=False,
            is_safe=False,
            status="error",
            error="Must provide either 'new_code' or 'patch'",
        )

    try:
        from code_scalpel.generators import RefactorSimulator

        simulator = RefactorSimulator(strict_mode=strict_mode)
        result = simulator.simulate(
            original_code=original_code,
            new_code=new_code,
            patch=patch,
        )

        security_issues = [
            RefactorSecurityIssue(
                type=issue.type,
                severity=issue.severity,
                line=issue.line,
                description=issue.description,
                cwe=issue.cwe,
            )
            for issue in result.security_issues
        ]

        return RefactorSimulationResult(
            success=True,
            is_safe=result.is_safe,
            status=result.status.value,
            reason=result.reason,
            security_issues=security_issues,
            structural_changes=result.structural_changes,
            warnings=result.warnings,
        )

    except Exception as e:
        return RefactorSimulationResult(
            success=False,
            is_safe=False,
            status="error",
            error=f"Simulation failed: {str(e)}",
        )


@mcp.tool()
async def simulate_refactor(
    original_code: str,
    new_code: str | None = None,
    patch: str | None = None,
    strict_mode: bool = False,
) -> RefactorSimulationResult:
    """
    Simulate applying a code change and check for safety issues.

    Use this tool before applying AI-generated code changes to verify they don't
    introduce security vulnerabilities or break existing functionality.

    Provide either the new_code directly OR a unified diff patch.

    Args:
        original_code: The original source code
        new_code: The modified code to compare against (optional)
        patch: A unified diff patch to apply (optional)
        strict_mode: If True, treat warnings as unsafe

    Returns:
        Simulation result with safety verdict and any issues found
    """
    return await asyncio.to_thread(
        _simulate_refactor_sync, original_code, new_code, patch, strict_mode
    )


def _crawl_project_sync(
    root_path: str,
    exclude_dirs: list[str] | None = None,
    complexity_threshold: int = 10,
    include_report: bool = True,
) -> ProjectCrawlResult:
    """Synchronous implementation of crawl_project."""
    try:
        from code_scalpel.project_crawler import ProjectCrawler

        crawler = ProjectCrawler(
            root_path,
            exclude_dirs=frozenset(exclude_dirs) if exclude_dirs else None,
            complexity_threshold=complexity_threshold,
        )
        result = crawler.crawl()

        # Convert to Pydantic models
        def to_func_info(f) -> CrawlFunctionInfo:
            return CrawlFunctionInfo(
                name=f.qualified_name,
                lineno=f.lineno,
                complexity=f.complexity,
            )

        def to_class_info(c) -> CrawlClassInfo:
            return CrawlClassInfo(
                name=c.name,
                lineno=c.lineno,
                methods=[to_func_info(m) for m in c.methods],
                bases=c.bases,
            )

        def to_file_result(fr, root: str) -> CrawlFileResult:
            import os

            return CrawlFileResult(
                path=os.path.relpath(fr.path, root),
                status=fr.status,
                lines_of_code=fr.lines_of_code,
                functions=[to_func_info(f) for f in fr.functions],
                classes=[to_class_info(c) for c in fr.classes],
                imports=fr.imports,
                complexity_warnings=[to_func_info(f) for f in fr.complexity_warnings],
                error=fr.error,
            )

        summary = CrawlSummary(
            total_files=result.total_files,
            successful_files=len(result.files_analyzed),
            failed_files=len(result.files_with_errors),
            total_lines_of_code=result.total_lines_of_code,
            total_functions=result.total_functions,
            total_classes=result.total_classes,
            complexity_warnings=len(result.all_complexity_warnings),
        )

        files = [to_file_result(f, result.root_path) for f in result.files_analyzed]
        errors = [to_file_result(f, result.root_path) for f in result.files_with_errors]

        report = ""
        if include_report:
            report = crawler.generate_report(result)

        return ProjectCrawlResult(
            success=True,
            root_path=result.root_path,
            timestamp=result.timestamp,
            summary=summary,
            files=files,
            errors=errors,
            markdown_report=report,
        )

    except Exception as e:
        return ProjectCrawlResult(
            success=False,
            root_path=root_path,
            timestamp="",
            summary=CrawlSummary(
                total_files=0,
                successful_files=0,
                failed_files=0,
                total_lines_of_code=0,
                total_functions=0,
                total_classes=0,
                complexity_warnings=0,
            ),
            error=f"Crawl failed: {str(e)}",
        )


# --- Helper functions for extract_code (refactored for maintainability) ---


def _extraction_error(target_name: str, error: str) -> ContextualExtractionResult:
    """Create a standardized error result for extraction failures."""
    return ContextualExtractionResult(
        success=False,
        target_name=target_name,
        target_code="",
        context_code="",
        full_code="",
        error=error,
    )


async def _extract_polyglot(
    target_type: str,
    target_name: str,
    file_path: str | None,
    code: str | None,
    language: Any,
    include_token_estimate: bool,
) -> ContextualExtractionResult:
    """
    [20251214_FEATURE] v2.0.0 - Multi-language extraction using PolyglotExtractor.

    Handles extraction for JavaScript, TypeScript, and Java using tree-sitter
    and the Unified IR system.

    Args:
        target_type: "function", "class", or "method"
        target_name: Name of element to extract
        file_path: Path to source file
        code: Source code string (if file_path not provided)
        language: Language enum value
        include_token_estimate: Include token count estimate

    Returns:
        ContextualExtractionResult with extracted code
    """
    from code_scalpel.polyglot import PolyglotExtractor
    from code_scalpel.mcp.path_resolver import resolve_path

    if file_path is None and code is None:
        return _extraction_error(
            target_name, "Must provide either 'file_path' or 'code' argument"
        )

    try:
        # Create extractor from file or code
        if file_path is not None:
            resolved_path = resolve_path(file_path, str(PROJECT_ROOT))
            extractor = PolyglotExtractor.from_file(resolved_path, language)
        else:
            extractor = PolyglotExtractor(code, language=language)

        # Perform extraction
        result = extractor.extract(target_type, target_name)

        if not result.success:
            return _extraction_error(target_name, result.error or "Extraction failed")

        token_estimate = result.token_estimate if include_token_estimate else 0

        # [20251216_FEATURE] v2.0.2 - Include JSX/TSX metadata in result
        return ContextualExtractionResult(
            success=True,
            target_name=target_name,
            target_code=result.code,
            context_code="",  # Cross-file deps not yet supported for non-Python
            full_code=result.code,
            context_items=[],
            total_lines=result.end_line - result.start_line + 1,
            line_start=result.start_line,
            line_end=result.end_line,
            token_estimate=token_estimate,
            jsx_normalized=result.jsx_normalized,
            is_server_component=result.is_server_component,
            is_server_action=result.is_server_action,
            component_type=result.component_type,
        )
    except FileNotFoundError as e:
        return _extraction_error(target_name, str(e))
    except Exception as e:
        return _extraction_error(target_name, f"Polyglot extraction failed: {str(e)}")


def _create_extractor(
    file_path: str | None, code: str | None, target_name: str
) -> tuple["SurgicalExtractor | None", ContextualExtractionResult | None]:
    """
    Create a SurgicalExtractor from file_path or code.

    [20251214_FEATURE] v1.5.3 - Integrated PathResolver for intelligent path resolution

    Returns (extractor, None) on success, (None, error_result) on failure.
    """
    from code_scalpel import SurgicalExtractor
    from code_scalpel.mcp.path_resolver import resolve_path

    if file_path is None and code is None:
        return None, _extraction_error(
            target_name, "Must provide either 'file_path' or 'code' argument"
        )

    if file_path is not None:
        try:
            # [20251214_FEATURE] Use PathResolver for intelligent path resolution
            resolved_path = resolve_path(file_path, str(PROJECT_ROOT))
            return SurgicalExtractor.from_file(resolved_path), None
        except FileNotFoundError as e:
            # PathResolver provides helpful error messages
            return None, _extraction_error(target_name, str(e))
        except ValueError as e:
            return None, _extraction_error(target_name, str(e))
    else:
        try:
            return SurgicalExtractor(code), None
        except (SyntaxError, ValueError) as e:
            return None, _extraction_error(
                target_name, f"Syntax error in code: {str(e)}"
            )


def _extract_method(extractor: "SurgicalExtractor", target_name: str):
    """Extract a method, handling the ClassName.method_name parsing."""
    if "." not in target_name:
        return None, _extraction_error(
            target_name, "Method name must be 'ClassName.method_name' format"
        )
    class_name, method_name = target_name.rsplit(".", 1)
    return extractor.get_method(class_name, method_name), None


def _perform_extraction(
    extractor: "SurgicalExtractor",
    target_type: str,
    target_name: str,
    include_context: bool,
    include_cross_file_deps: bool,
    context_depth: int,
    file_path: str | None,
):
    """
    Perform the actual extraction based on target type and options.

    Returns (result, cross_file_result, error_result).
    """
    from code_scalpel.surgical_extractor import CrossFileResolution

    cross_file_result: CrossFileResolution | None = None

    # CROSS-FILE RESOLUTION PATH
    if include_cross_file_deps and file_path is not None:
        if target_type in ("function", "class"):
            cross_file_result = extractor.resolve_cross_file_dependencies(
                target_name=target_name,
                target_type=target_type,
                max_depth=context_depth,
            )
            return cross_file_result.target, cross_file_result, None
        else:
            # Method - fall back to regular extraction
            result, error = _extract_method(extractor, target_name)
            return result, None, error

    # INTRA-FILE CONTEXT PATH
    if target_type == "function":
        if include_context:
            return (
                extractor.get_function_with_context(
                    target_name, max_depth=context_depth
                ),
                None,
                None,
            )
        return extractor.get_function(target_name), None, None

    if target_type == "class":
        if include_context:
            return (
                extractor.get_class_with_context(target_name, max_depth=context_depth),
                None,
                None,
            )
        return extractor.get_class(target_name), None, None

    if target_type == "method":
        result, error = _extract_method(extractor, target_name)
        return result, None, error

    return (
        None,
        None,
        _extraction_error(
            target_name,
            f"Unknown target_type: {target_type}. Use 'function', 'class', or 'method'.",
        ),
    )


def _process_cross_file_context(cross_file_result) -> tuple[str, list[str]]:
    """Process cross-file resolution results into context_code and context_items."""
    if cross_file_result is None or not cross_file_result.external_symbols:
        return "", []

    external_parts = []
    external_names = []
    for sym in cross_file_result.external_symbols:
        external_parts.append(f"# From {sym.source_file}")
        external_parts.append(sym.code)
        external_names.append(f"{sym.name} ({sym.source_file})")

    context_code = "\n\n".join(external_parts)

    # Add unresolved imports as a comment
    if cross_file_result.unresolved_imports:
        unresolved_comment = "# Unresolved imports: " + ", ".join(
            cross_file_result.unresolved_imports
        )
        context_code = unresolved_comment + "\n\n" + context_code

    return context_code, external_names


def _build_full_code(
    imports_needed: list[str], context_code: str, target_code: str
) -> str:
    """Build the combined full_code for LLM consumption."""
    parts = []
    if imports_needed:
        parts.append("\n".join(imports_needed))
    if context_code:
        parts.append(context_code)
    parts.append(target_code)
    return "\n\n".join(parts)


@mcp.tool()
async def extract_code(
    target_type: str,
    target_name: str,
    file_path: str | None = None,
    code: str | None = None,
    language: str | None = None,
    include_context: bool = False,
    context_depth: int = 1,
    include_cross_file_deps: bool = False,
    include_token_estimate: bool = True,
    ctx: Context | None = None,
) -> ContextualExtractionResult:
    """
    Surgically extract specific code elements (functions, classes, methods).

    **TOKEN-EFFICIENT MODE (RECOMMENDED):**
    Provide `file_path` - the server reads the file directly. The Agent
    never sees the full file content, saving potentially thousands of tokens.

    **MULTI-LANGUAGE SUPPORT (v2.0.0):**
    Supports Python, JavaScript, TypeScript, and Java. Language is auto-detected
    from file extension, or specify explicitly with `language` parameter.

    **CROSS-FILE DEPENDENCIES:**
    Set `include_cross_file_deps=True` to automatically resolve imports.
    If your function uses `TaxRate` from `models.py`, this will extract
    `TaxRate` from `models.py` and include it in the response.

    **LEGACY MODE:**
    Provide `code` as a string - for when you already have code in context.

    Args:
        target_type: Type of element - "function", "class", or "method".
        target_name: Name of the element. For methods, use "ClassName.method_name".
        file_path: Path to the source file (TOKEN SAVER - server reads file).
        code: Source code string (fallback if file_path not provided).
        language: Language override: "python", "javascript", "typescript", "java".
                  If None, auto-detects from file extension.
        include_context: If True, also extract intra-file dependencies.
        context_depth: How deep to traverse dependencies (1=direct, 2=transitive).
        include_cross_file_deps: If True, resolve imports from external files.
        include_token_estimate: If True, include estimated token count.

    Returns:
        ContextualExtractionResult with extracted code and metadata.

    Example (Efficient - Agent sends ~50 tokens, receives ~200):
        extract_code(
            file_path="/project/src/utils.py",
            target_type="function",
            target_name="calculate_tax"
        )

    Example (JavaScript extraction):
        extract_code(
            file_path="/project/src/utils.js",
            target_type="function",
            target_name="calculateTax"
        )

    Example (Java method extraction):
        extract_code(
            file_path="/project/src/Calculator.java",
            target_type="method",
            target_name="Calculator.add"
        )

    Example (With cross-file dependencies):
        extract_code(
            file_path="/project/src/services/order.py",
            target_type="function",
            target_name="process_order",
            include_cross_file_deps=True
        )
    """
    # [20251215_FEATURE] v2.0.0 - Roots capability support
    # Fetch allowed roots from client for security boundary enforcement
    if ctx and file_path:
        await _fetch_and_cache_roots(ctx)

    from code_scalpel.surgical_extractor import ContextualExtraction, ExtractionResult
    from code_scalpel.polyglot import Language, detect_language

    # [20251214_FEATURE] v2.0.0 - Multi-language support
    # Determine language from parameter, file extension, or code content
    detected_lang = Language.AUTO
    if language:
        lang_map = {
            "python": Language.PYTHON,
            "javascript": Language.JAVASCRIPT,
            "js": Language.JAVASCRIPT,
            "jsx": Language.JAVASCRIPT,  # [20251216_FEATURE] JSX is JavaScript with JSX syntax
            "typescript": Language.TYPESCRIPT,
            "ts": Language.TYPESCRIPT,
            "tsx": Language.TYPESCRIPT,  # [20251216_FEATURE] TSX is TypeScript with JSX syntax
            "java": Language.JAVA,
        }
        detected_lang = lang_map.get(language.lower(), Language.AUTO)

    if detected_lang == Language.AUTO:
        detected_lang = detect_language(file_path, code)

    # [20251214_FEATURE] Route to polyglot extractor for non-Python languages
    if detected_lang != Language.PYTHON:
        return await _extract_polyglot(
            target_type=target_type,
            target_name=target_name,
            file_path=file_path,
            code=code,
            language=detected_lang,
            include_token_estimate=include_token_estimate,
        )

    # Python path - use existing SurgicalExtractor with full context support
    # Step 1: Create extractor
    extractor, error = _create_extractor(file_path, code, target_name)
    if error:
        return error

    try:
        # Step 2: Perform extraction
        result, cross_file_result, error = _perform_extraction(
            extractor,
            target_type,
            target_name,
            include_context,
            include_cross_file_deps,
            context_depth,
            file_path,
        )
        if error:
            return error

        # Step 3: Handle None result
        if result is None:
            return _extraction_error(
                target_name,
                f"{target_type.capitalize()} '{target_name}' not found in code",
            )

        # Step 4: Process result based on type
        if isinstance(result, ExtractionResult):
            if not result.success:
                return _extraction_error(
                    target_name,
                    result.error
                    or f"{target_type.capitalize()} '{target_name}' not found",
                )
            target_code = result.code
            total_lines = (
                result.line_end - result.line_start + 1 if result.line_end > 0 else 0
            )
            line_start = result.line_start
            line_end = result.line_end
            imports_needed = result.imports_needed

            # Handle cross-file context
            context_code, context_items = _process_cross_file_context(cross_file_result)

        elif isinstance(result, ContextualExtraction):
            if not result.target.success:
                return _extraction_error(
                    target_name,
                    result.target.error
                    or f"{target_type.capitalize()} '{target_name}' not found",
                )
            target_code = result.target.code
            context_items = result.context_items
            context_code = result.context_code
            total_lines = result.total_lines
            line_start = result.target.line_start
            line_end = result.target.line_end
            imports_needed = result.target.imports_needed
        else:
            return _extraction_error(
                target_name, f"Unexpected result type: {type(result).__name__}"
            )

        # Step 5: Build final response
        full_code = _build_full_code(imports_needed, context_code, target_code)
        token_estimate = len(full_code) // 4 if include_token_estimate else 0

        return ContextualExtractionResult(
            success=True,
            target_name=target_name,
            target_code=target_code,
            context_code=context_code,
            full_code=full_code,
            context_items=context_items,
            total_lines=total_lines,
            line_start=line_start,
            line_end=line_end,
            token_estimate=token_estimate,
        )

    except Exception as e:
        return _extraction_error(target_name, f"Extraction failed: {str(e)}")


@mcp.tool()
async def update_symbol(
    file_path: str,
    target_type: str,
    target_name: str,
    new_code: str,
    create_backup: bool = True,
) -> PatchResultModel:
    """
        Surgically replace a function, class, or method in a file with new code.

        This is the SAFE way to modify code - you provide only the new symbol,
        and the server handles:
        - Locating the exact symbol boundaries (including decorators)
        - Validating the replacement code syntax
        - Preserving all surrounding code exactly
        - Creating a backup before modification
        - Atomic write (prevents partial writes)

        Args:
            file_path: Path to the Python source file to modify.
            target_type: Type of element - "function", "class", or "method".
            target_name: Name of the element. For methods, use "ClassName.method_name".
            new_code: The complete new definition (including def/class line and body).
            create_backup: If True (default), create a .bak file before modifying.

        Returns:
            PatchResultModel with success status, line changes, and backup path.

        Example (Fix a function):
            update_symbol(
                file_path="/project/src/utils.py",
                target_type="function",
                target_name="calculate_tax",
                new_code='''def calculate_tax(amount, rate=0.1):
        \"\"\"Calculate tax with proper rounding.\"\"\"
        return round(amount * rate, 2)
    '''
            )

        Example (Update a method):
            update_symbol(
                file_path="/project/src/models.py",
                target_type="method",
                target_name="User.validate_email",
                new_code='''def validate_email(self, email):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    '''
            )

        Safety Features:
            - Backup created at {file_path}.bak (unless create_backup=False)
            - Syntax validation before any file modification
            - Atomic write prevents corruption on crash
            - Original indentation preserved
    """
    from code_scalpel.surgical_patcher import SurgicalPatcher

    # Validate inputs
    if not file_path:
        return PatchResultModel(
            success=False,
            file_path="",
            target_name=target_name,
            target_type=target_type,
            error="file_path is required",
        )

    if not new_code or not new_code.strip():
        return PatchResultModel(
            success=False,
            file_path=file_path,
            target_name=target_name,
            target_type=target_type,
            error="new_code cannot be empty",
        )

    if target_type not in ("function", "class", "method"):
        return PatchResultModel(
            success=False,
            file_path=file_path,
            target_name=target_name,
            target_type=target_type,
            error=f"Invalid target_type: {target_type}. Use 'function', 'class', or 'method'.",
        )

    # Load the file
    try:
        patcher = SurgicalPatcher.from_file(file_path)
    except FileNotFoundError:
        return PatchResultModel(
            success=False,
            file_path=file_path,
            target_name=target_name,
            target_type=target_type,
            error=f"File not found: {file_path}",
        )
    except ValueError as e:
        return PatchResultModel(
            success=False,
            file_path=file_path,
            target_name=target_name,
            target_type=target_type,
            error=str(e),
        )

    # Apply the patch based on target type
    try:
        if target_type == "function":
            result = patcher.update_function(target_name, new_code)
        elif target_type == "class":
            result = patcher.update_class(target_name, new_code)
        elif target_type == "method":
            if "." not in target_name:
                return PatchResultModel(
                    success=False,
                    file_path=file_path,
                    target_name=target_name,
                    target_type=target_type,
                    error="Method name must be 'ClassName.method_name' format",
                )
            class_name, method_name = target_name.rsplit(".", 1)
            result = patcher.update_method(class_name, method_name, new_code)
        else:
            # Should not reach here due to validation above
            return PatchResultModel(
                success=False,
                file_path=file_path,
                target_name=target_name,
                target_type=target_type,
                error=f"Unknown target_type: {target_type}",
            )

        if not result.success:
            return PatchResultModel(
                success=False,
                file_path=file_path,
                target_name=target_name,
                target_type=target_type,
                error=result.error,
            )

        # Save the changes
        backup_path = patcher.save(backup=create_backup)

        return PatchResultModel(
            success=True,
            file_path=file_path,
            target_name=target_name,
            target_type=target_type,
            lines_before=result.lines_before,
            lines_after=result.lines_after,
            lines_delta=result.lines_delta,
            backup_path=backup_path,
        )

    except Exception as e:
        return PatchResultModel(
            success=False,
            file_path=file_path,
            target_name=target_name,
            target_type=target_type,
            error=f"Patch failed: {str(e)}",
        )


@mcp.tool()
async def crawl_project(
    root_path: str | None = None,
    exclude_dirs: list[str] | None = None,
    complexity_threshold: int = 10,
    include_report: bool = True,
    ctx: Context | None = None,
) -> ProjectCrawlResult:
    """
    Crawl an entire project directory and analyze all Python files.

    Use this tool to get a comprehensive overview of a project's structure,
    complexity hotspots, and code metrics before diving into specific files.

    [20251215_FEATURE] v2.0.0 - Progress reporting for long-running operations.
    Reports progress as files are discovered and analyzed.

    Args:
        root_path: Path to project root (defaults to current working directory)
        exclude_dirs: Additional directories to exclude (common ones already excluded)
        complexity_threshold: Complexity score that triggers a warning (default: 10)
        include_report: Include a markdown report in the response (default: True)

    Returns:
        Project crawl result with file analysis, summary statistics, and optional report
    """
    if root_path is None:
        root_path = str(PROJECT_ROOT)

    # [20251215_FEATURE] v2.0.0 - Progress token support
    # Report initial progress
    if ctx:
        await ctx.report_progress(progress=0, total=100)

    result = await asyncio.to_thread(
        _crawl_project_sync,
        root_path,
        exclude_dirs,
        complexity_threshold,
        include_report,
    )

    # Report completion
    if ctx:
        await ctx.report_progress(progress=100, total=100)

    return result


# ============================================================================
# RESOURCES
# ============================================================================


@mcp.resource("scalpel://project/call-graph")
def get_project_call_graph() -> str:
    """
    Get the project-wide call graph.

    Returns a JSON adjacency list:
    {
        "file.py:caller_function": ["target_function", "other_file.py:target_function"]
    }

    Use this to trace function calls across files and understand dependencies.
    """
    import json
    from code_scalpel.ast_tools.call_graph import CallGraphBuilder

    builder = CallGraphBuilder(PROJECT_ROOT)
    graph = builder.build()
    return json.dumps(graph, indent=2)


@mcp.resource("scalpel://project/dependencies")
def get_project_dependencies() -> str:
    """
    Returns a list of project dependencies detected in configuration files.
    Use this to verify if libraries used in generated code actually exist in the project.
    """
    import json
    from code_scalpel.ast_tools.dependency_parser import DependencyParser

    parser = DependencyParser(str(PROJECT_ROOT))
    deps = parser.get_dependencies()
    return json.dumps(deps, indent=2)


@mcp.resource("scalpel://project/structure")
def get_project_structure() -> str:
    """
    Get the project directory structure as a JSON tree.

    Use this resource to understand the file layout of the project.
    It respects .gitignore if possible (simple implementation for now).
    """

    def build_tree(path: Path) -> dict[str, Any]:
        tree = {"name": path.name, "type": "directory", "children": []}
        try:
            # Sort directories first, then files
            items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            for item in items:
                # Skip hidden files/dirs and common ignore patterns
                if item.name.startswith(".") or item.name in [
                    "__pycache__",
                    "venv",
                    "node_modules",
                    "dist",
                    "build",
                ]:
                    continue

                if item.is_dir():
                    tree["children"].append(build_tree(item))
                else:
                    tree["children"].append({"name": item.name, "type": "file"})
        except PermissionError:
            pass
        return tree

    import json

    return json.dumps(build_tree(PROJECT_ROOT), indent=2)


@mcp.resource("scalpel://version")
def get_version() -> str:
    """Get Code Scalpel version information."""
    return f"""Code Scalpel v{__version__}

A precision toolkit for AI-driven code analysis.

Features:
- AST Analysis: Parse and analyze code structure
- Security Scanning: Taint-based vulnerability detection
- Symbolic Execution: Path exploration with Z3 solver

Supported Languages:
- Python (full support)
- JavaScript/TypeScript (planned v0.4.0)
"""


@mcp.resource("scalpel://health")
def get_health() -> str:
    """
    Health check endpoint for Docker and orchestration systems.

    [20251215_FEATURE] v2.0.0 - Added health endpoint for Docker health checks.

    Returns immediately with server status. Use this instead of SSE endpoint
    for health checks as SSE connections stay open indefinitely.

    Returns:
        JSON string with health status
    """
    import json

    return json.dumps(
        {
            "status": "healthy",
            "version": __version__,
            "project_root": str(PROJECT_ROOT),
        }
    )


@mcp.resource("scalpel://capabilities")
def get_capabilities() -> str:
    """Get information about Code Scalpel's capabilities."""
    return """# Code Scalpel Capabilities

## Tools

### analyze_code
Parses Python code and extracts:
- Function definitions (sync and async)
- Class definitions
- Import statements
- Cyclomatic complexity
- Lines of code

### security_scan
Detects vulnerabilities:
- SQL Injection (CWE-89)
- Cross-Site Scripting (CWE-79)
- Command Injection (CWE-78)
- Path Traversal (CWE-22)
- Code Injection (CWE-94)

Uses taint analysis to track data flow from sources to sinks.

### symbolic_execute
Explores execution paths:
- Treats function arguments as symbolic
- Uses Z3 SMT solver for constraint solving
- Identifies reachable/unreachable paths
- Reports path conditions

## Security Notes
- Code is PARSED, never executed
- Maximum code size: 100KB
- No filesystem access from analyzed code
- No network access from analyzed code
"""


# ============================================================================
# RESOURCE TEMPLATES - Dynamic URI-based Context
# [20251215_FEATURE] v2.0.0 - MCP Resource Templates for dynamic content access
# ============================================================================


@mcp.resource("scalpel://file/{path}")
def get_file_resource(path: str) -> str:
    """
    Read file contents by path (Resource Template).

    [20251215_FEATURE] v2.0.0 - Dynamic file access via URI template.

    This resource template allows clients to construct URIs dynamically
    to access any file within the allowed roots.

    Example URIs:
    - scalpel://file/src/main.py
    - scalpel://file/tests/test_utils.py

    Security: Path must be within allowed roots (PROJECT_ROOT or client-specified roots).

    Args:
        path: Relative or absolute path to the file

    Returns:
        File contents as text
    """
    from code_scalpel.mcp.path_resolver import resolve_path

    try:
        resolved = resolve_path(path, str(PROJECT_ROOT))
        file_path = Path(resolved)

        # Security check
        _validate_path_security(file_path)

        return file_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        return f"Error: {e}"
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error reading file: {e}"


@mcp.resource("scalpel://analysis/{path}")
def get_analysis_resource(path: str) -> str:
    """
    Get code analysis for a file by path (Resource Template).

    [20251215_FEATURE] v2.0.0 - Dynamic analysis access via URI template.

    Returns a JSON analysis including:
    - Functions and classes
    - Imports
    - Complexity metrics
    - Security warnings (if any)

    Example URIs:
    - scalpel://analysis/src/utils.py
    - scalpel://analysis/app/models.py

    Args:
        path: Path to the Python file to analyze

    Returns:
        JSON string with analysis results
    """
    import json
    from code_scalpel.mcp.path_resolver import resolve_path

    try:
        resolved = resolve_path(path, str(PROJECT_ROOT))
        file_path = Path(resolved)

        # Security check
        _validate_path_security(file_path)

        code = file_path.read_text(encoding="utf-8")

        # Run analysis
        result = _analyze_code_sync(code, "python")

        # Run quick security check
        security = _security_scan_sync(code)

        return json.dumps(
            {
                "file": str(file_path),
                "analysis": result.model_dump(),
                "security_summary": {
                    "has_vulnerabilities": security.has_vulnerabilities,
                    "vulnerability_count": security.vulnerability_count,
                    "risk_level": security.risk_level,
                },
            },
            indent=2,
        )
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)})
    except PermissionError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"Analysis failed: {e}"})


# [20251215_BUGFIX] Provide synchronous extraction helper for URI templates using SurgicalExtractor.
def _extract_code_sync(
    target_type: str,
    target_name: str,
    file_path: str | None,
    code: str | None = None,
    include_context: bool = True,
    include_token_estimate: bool = True,
) -> ContextualExtractionResult:
    from code_scalpel.surgical_extractor import SurgicalExtractor

    if not file_path and not code:
        return _extraction_error(
            target_name, "Must provide either 'file_path' or 'code' argument"
        )

    extractor = (
        SurgicalExtractor.from_file(file_path)
        if file_path is not None
        else SurgicalExtractor(code or "")
    )

    context = None
    if target_type == "class":
        target = extractor.get_class(target_name)
        if include_context:
            context = extractor.get_class_with_context(target_name)
    elif target_type == "method":
        if "." not in target_name:
            return _extraction_error(
                target_name, "Method targets must use Class.method format"
            )
        class_name, method_name = target_name.split(".", 1)
        target = extractor.get_method(class_name, method_name)
        if include_context:
            context = extractor.get_method_with_context(class_name, method_name)
    else:
        target = extractor.get_function(target_name)
        if include_context:
            context = extractor.get_function_with_context(target_name)

    if not target.success:
        return _extraction_error(target_name, target.error or "Extraction failed")

    context_code = context.context_code if context else ""
    context_items = context.context_items if context else (target.dependencies or [])
    full_code = context.full_code if context else target.code
    total_lines = (
        context.total_lines
        if context
        else (
            target.line_end - target.line_start + 1
            if target.line_end and target.line_start
            else max(1, full_code.count("\n") + 1)
        )
    )
    token_estimate = context.token_estimate if context and include_token_estimate else 0

    return ContextualExtractionResult(
        success=True,
        server_version=__version__,
        target_name=target_name,
        target_code=target.code,
        context_code=context_code,
        full_code=full_code,
        context_items=context_items,
        total_lines=total_lines,
        line_start=target.line_start,
        line_end=target.line_end,
        token_estimate=token_estimate,
        error=None,
    )


@mcp.resource("scalpel://symbol/{file_path}/{symbol_name}")
def get_symbol_resource(file_path: str, symbol_name: str) -> str:
    """
    Extract a specific symbol (function/class) from a file (Resource Template).

    [20251215_FEATURE] v2.0.0 - Surgical symbol extraction via URI template.

    This is more efficient than reading the entire file when you only
    need a specific function or class definition.

    Example URIs:
    - scalpel://symbol/src/utils.py/calculate_tax
    - scalpel://symbol/app/models.py/User
    - scalpel://symbol/services/auth.py/AuthService.validate

    Args:
        file_path: Path to the file
        symbol_name: Name of the function, class, or method (use Class.method for methods)

    Returns:
        JSON with extracted code and metadata
    """
    import json
    from code_scalpel.mcp.path_resolver import resolve_path

    try:
        resolved = resolve_path(file_path, str(PROJECT_ROOT))
        path = Path(resolved)

        # Security check
        _validate_path_security(path)

        # Determine target type
        if "." in symbol_name:
            target_type = "method"
        else:
            # Try to detect from code
            code = path.read_text(encoding="utf-8")
            tree = ast.parse(code)

            target_type = "function"
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == symbol_name:
                    target_type = "class"
                    break

        # Use extraction logic
        result = _extract_code_sync(
            target_type=target_type,
            target_name=symbol_name,
            file_path=str(path),
            include_context=True,
            include_token_estimate=True,
        )

        return json.dumps(result.model_dump(), indent=2)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)})
    except PermissionError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"Extraction failed: {e}"})


@mcp.resource("scalpel://security/{path}")
def get_security_resource(path: str) -> str:
    """
    Get security scan results for a file (Resource Template).

    [20251215_FEATURE] v2.0.0 - Security analysis via URI template.

    Returns detailed vulnerability information including:
    - Vulnerability type and CWE
    - Line numbers
    - Severity levels
    - Taint flow information

    Example URIs:
    - scalpel://security/src/api.py
    - scalpel://security/app/views.py

    Args:
        path: Path to the Python file to scan

    Returns:
        JSON string with security scan results
    """
    import json
    from code_scalpel.mcp.path_resolver import resolve_path

    try:
        resolved = resolve_path(path, str(PROJECT_ROOT))
        file_path = Path(resolved)

        # Security check
        _validate_path_security(file_path)

        # Run security scan
        result = _security_scan_sync(file_path=str(file_path))

        return json.dumps(result.model_dump(), indent=2)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)})
    except PermissionError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"Security scan failed: {e}"})


@mcp.resource("code:///{language}/{module}/{symbol}")
async def get_code_resource(language: str, module: str, symbol: str) -> str:
    """
    Access code elements via parameterized URI (Resource Template).

    [20251216_FEATURE] v2.0.2 - Universal code access via code:/// URIs.

    This resource template allows AI agents to access code elements by
    specifying language, module, and symbol without knowing exact file paths.

    URI Format:
        code:///{language}/{module}/{symbol}

    Examples:
        - code:///python/utils/calculate_tax
        - code:///typescript/components/UserCard
        - code:///javascript/services/auth/authenticate
        - code:///java/services.AuthService/validateToken

    Args:
        language: Programming language ("python", "javascript", "typescript", "java")
        module: Module name (e.g., "utils", "components/Button", "services.auth")
        symbol: Symbol name (function, class, or method with Class.method notation)

    Returns:
        JSON with extracted code, metadata, and JSX/TSX information
    """
    import json
    from code_scalpel.mcp.module_resolver import resolve_module_path, get_mime_type

    try:
        # Resolve module to file path
        file_path = resolve_module_path(language, module, PROJECT_ROOT)

        if file_path is None:
            return json.dumps(
                {
                    "error": f"Module '{module}' not found for language '{language}'",
                    "language": language,
                    "module": module,
                    "symbol": symbol,
                }
            )

        # Security check
        _validate_path_security(file_path)

        # [20251216_BUGFIX] Fallback type detection for uppercase function names
        # React components are often functions starting with uppercase (e.g., function Button)
        # Try class first for uppercase names, fall back to function if not found
        if "." in symbol:
            target_types_to_try = ["method"]
        elif symbol and symbol[0].isupper():
            # Uppercase: could be class OR function (React components)
            target_types_to_try = ["class", "function"]
        else:
            target_types_to_try = ["function"]

        # Extract the symbol using extract_code with fallback
        result = None
        last_error = None
        for target_type in target_types_to_try:
            result = await extract_code(
                target_type=target_type,
                target_name=symbol,
                file_path=str(file_path),
                language=language,
                include_context=True,
                include_token_estimate=True,
            )
            if result.success:
                break
            last_error = result.error

        if result is None or not result.success:
            return json.dumps(
                {
                    "error": last_error or "Extraction failed",
                    "language": language,
                    "module": module,
                    "symbol": symbol,
                }
            )

        # Return full result with metadata
        return json.dumps(
            {
                "uri": f"code:///{language}/{module}/{symbol}",
                "mimeType": get_mime_type(language),
                "code": result.full_code,
                "metadata": {
                    "file_path": str(file_path),
                    "language": language,
                    "module": module,
                    "symbol": symbol,
                    "line_start": result.line_start,
                    "line_end": result.line_end,
                    "token_estimate": result.token_estimate,
                    # JSX/TSX metadata
                    "jsx_normalized": result.jsx_normalized,
                    "is_server_component": result.is_server_component,
                    "is_server_action": result.is_server_action,
                    "component_type": result.component_type,
                },
            },
            indent=2,
        )

    except PermissionError as e:
        return json.dumps(
            {
                "error": str(e),
                "language": language,
                "module": module,
                "symbol": symbol,
            }
        )
    except Exception as e:
        return json.dumps(
            {
                "error": f"Resource access failed: {str(e)}",
                "language": language,
                "module": module,
                "symbol": symbol,
            }
        )


# ============================================================================
# PROMPTS
# ============================================================================


@mcp.prompt(title="Code Review")
def code_review_prompt(code: str) -> str:
    """Generate a comprehensive code review prompt."""
    return f"""Please analyze the following Python code and provide:

1. **Structure Analysis**: Identify functions, classes, and imports
2. **Security Review**: Check for potential vulnerabilities
3. **Quality Assessment**: Evaluate code quality and suggest improvements
4. **Edge Cases**: Identify potential edge cases and error conditions

Use the available Code Scalpel tools to gather detailed analysis:
- analyze_code: For structure and complexity
- security_scan: For vulnerability detection
- symbolic_execute: For path analysis

Code to review:
```python
{code}
```

Provide actionable recommendations for improvement."""


@mcp.prompt(title="Security Audit")
def security_audit_prompt(code: str) -> str:
    """Generate a security-focused audit prompt."""
    return f"""Perform a security audit of the following Python code.

Focus on:
1. **Input Validation**: Are all inputs properly validated?
2. **Injection Risks**: SQL, command, code injection vulnerabilities
3. **Authentication/Authorization**: Proper access controls
4. **Data Exposure**: Sensitive data handling
5. **Dependencies**: Known vulnerable patterns

Use security_scan tool to detect vulnerabilities automatically.

Code to audit:
```python
{code}
```

Provide a risk assessment and remediation steps for each finding."""


# ============================================================================
# WORKFLOW PROMPTS - Orchestrated Multi-Tool Workflows
# [20251215_FEATURE] v2.0.0 - Advanced workflow prompts combining tools + resources
# ============================================================================


@mcp.prompt(title="Refactor Function")
def refactor_function_prompt(
    file_path: str, function_name: str, refactor_goal: str
) -> str:
    """
    Safe refactoring workflow with validation.

    [20251215_FEATURE] v2.0.0 - Orchestrated refactor workflow.

    This prompt guides through a safe refactoring process:
    1. Extract the target function
    2. Analyze its structure and dependencies
    3. Simulate the refactor to verify safety
    4. Apply the change with backup

    Args:
        file_path: Path to the file containing the function
        function_name: Name of the function to refactor
        refactor_goal: Description of what the refactoring should achieve
    """
    return f"""# Safe Refactoring Workflow

## Target
- **File**: `{file_path}`
- **Function**: `{function_name}`
- **Goal**: {refactor_goal}

## Workflow Steps

### Step 1: Extract Current Implementation
First, use `extract_code` to get the current function:
```
extract_code(
    file_path="{file_path}",
    target_type="function",
    target_name="{function_name}",
    include_context=True,
    include_cross_file_deps=True
)
```

### Step 2: Analyze Dependencies
Check what depends on this function using `get_symbol_references`:
```
get_symbol_references(
    symbol_name="{function_name}",
    project_root="<project_root>"
)
```

### Step 3: Create Refactored Version
Based on the goal "{refactor_goal}", create the new implementation.
Ensure it maintains the same function signature if there are external callers.

### Step 4: Validate Safety
Before applying, use `simulate_refactor` to verify the change is safe:
```
simulate_refactor(
    original_code=<extracted_code>,
    new_code=<your_refactored_code>,
    strict_mode=True
)
```

### Step 5: Apply the Change
If simulation passes, use `update_symbol` to apply:
```
update_symbol(
    file_path="{file_path}",
    target_type="function",
    target_name="{function_name}",
    new_code=<your_refactored_code>,
    create_backup=True
)
```

## Safety Notes
- Always check the simulation result before applying
- A backup file (.bak) will be created
- If anything goes wrong, restore from backup

Please proceed with Step 1 to begin the refactoring process."""


@mcp.prompt(title="Debug Vulnerability")
def debug_vulnerability_prompt(file_path: str, vulnerability_type: str = "any") -> str:
    """
    Security vulnerability investigation and remediation workflow.

    [20251215_FEATURE] v2.0.0 - Security debugging workflow.

    This prompt guides through investigating and fixing security issues:
    1. Scan for vulnerabilities
    2. Trace taint flow across files
    3. Identify the root cause
    4. Generate and validate fixes

    Args:
        file_path: Path to the file to investigate
        vulnerability_type: Type of vulnerability (sql_injection, xss, command_injection, etc.) or "any"
    """
    vuln_filter = (
        f"Focus specifically on **{vulnerability_type}** vulnerabilities."
        if vulnerability_type != "any"
        else "Check for all vulnerability types."
    )

    return f"""# Security Vulnerability Investigation

## Target
- **File**: `{file_path}`
- **Focus**: {vuln_filter}

## Investigation Workflow

### Step 1: Initial Security Scan
Run a security scan on the target file:
```
security_scan(file_path="{file_path}")
```

### Step 2: Cross-File Taint Analysis
If vulnerabilities are found, trace the taint flow across files:
```
cross_file_security_scan(
    project_root="<project_root>",
    entry_points=["{file_path}:<function_name>"],
    include_diagram=True
)
```

### Step 3: Understand the Data Flow
For each vulnerability found:
1. Identify the **taint source** (user input, request data, etc.)
2. Trace the flow through function calls
3. Find the **sink** where the vulnerability occurs

### Step 4: Extract Vulnerable Code
Use `extract_code` to get the vulnerable function(s):
```
extract_code(
    file_path="{file_path}",
    target_type="function",
    target_name="<vulnerable_function>",
    include_cross_file_deps=True
)
```

### Step 5: Generate Fix
Create a fixed version that:
- Adds proper input validation/sanitization
- Uses parameterized queries for SQL
- Escapes output for XSS
- Validates file paths for traversal

### Step 6: Validate Fix
Use `simulate_refactor` to ensure the fix:
- Doesn't introduce new vulnerabilities
- Preserves the function's behavior
```
simulate_refactor(
    original_code=<vulnerable_code>,
    new_code=<fixed_code>,
    strict_mode=True
)
```

### Step 7: Apply Fix
If validation passes, apply with `update_symbol`.

## Common Fixes by Vulnerability Type
- **SQL Injection**: Use parameterized queries, ORM methods
- **XSS**: HTML escape output, use template auto-escaping
- **Command Injection**: Use subprocess with list args, avoid shell=True
- **Path Traversal**: Use pathlib, validate against allowed directories

Please proceed with Step 1 to begin the investigation."""


@mcp.prompt(title="Analyze Codebase")
def analyze_codebase_prompt(project_description: str = "Python project") -> str:
    """
    Comprehensive codebase analysis workflow.

    [20251215_FEATURE] v2.0.0 - Full project analysis workflow.

    This prompt guides through a complete project analysis:
    1. Crawl and map the project structure
    2. Build call graphs
    3. Identify complexity hotspots
    4. Run security audit
    5. Generate improvement recommendations

    Args:
        project_description: Brief description of what the project does
    """
    return f"""# Comprehensive Codebase Analysis

## Project
{project_description}

## Analysis Workflow

### Step 1: Project Structure Overview
Start by understanding the project layout:
```
# Read the project structure resource
# URI: scalpel://project/structure
```

Then crawl for detailed metrics:
```
crawl_project(
    complexity_threshold=10,
    include_report=True
)
```

### Step 2: Dependency Analysis
Check project dependencies for vulnerabilities:
```
scan_dependencies(scan_vulnerabilities=True)
```

Also check internal dependencies:
```
# Read the dependencies resource
# URI: scalpel://project/dependencies
```

### Step 3: Call Graph Analysis
Understand how code flows through the project:
```
# Read the call graph resource
# URI: scalpel://project/call-graph
```

Or use the tool for specific functions:
```
get_call_graph(
    target_function="<main_entry_point>",
    include_diagram=True
)
```

### Step 4: Identify Hotspots
From the crawl results, identify:
1. **High Complexity Functions** (complexity > 10)
2. **Large Files** (> 500 lines)
3. **Deeply Nested Code**

For each hotspot, get detailed analysis:
```
# URI: scalpel://analysis/<file_path>
```

### Step 5: Security Assessment
Run cross-file security scan:
```
cross_file_security_scan(
    include_diagram=True,
    max_depth=5
)
```

### Step 6: Generate Report
Compile findings into:

1. **Architecture Overview**
   - Key modules and their responsibilities
   - Data flow patterns
   - External dependencies

2. **Quality Metrics**
   - Total lines of code
   - Average complexity
   - Test coverage (if detectable)

3. **Security Posture**
   - Vulnerabilities found
   - Risk level assessment
   - Remediation priorities

4. **Recommendations**
   - Refactoring candidates
   - Security fixes needed
   - Code quality improvements

Please proceed with Step 1 to begin the analysis."""


@mcp.prompt(title="Extract and Test")
def extract_and_test_prompt(file_path: str, function_name: str) -> str:
    """
    Extract a function and generate comprehensive tests.

    [20251215_FEATURE] v2.0.0 - Test generation workflow.

    This prompt guides through:
    1. Extracting a function with its dependencies
    2. Analyzing its execution paths
    3. Generating test cases that cover all paths
    4. Creating a test file

    Args:
        file_path: Path to the file containing the function
        function_name: Name of the function to test
    """
    return f"""# Extract and Generate Tests Workflow

## Target
- **File**: `{file_path}`
- **Function**: `{function_name}`

## Workflow Steps

### Step 1: Extract the Function
Get the function with all dependencies:
```
extract_code(
    file_path="{file_path}",
    target_type="function",
    target_name="{function_name}",
    include_context=True,
    include_cross_file_deps=True
)
```

### Step 2: Analyze Execution Paths
Run symbolic execution to discover all paths:
```
symbolic_execute(
    code=<extracted_code>,
    max_paths=20
)
```

### Step 3: Generate Test Cases
Create tests covering each path:
```
generate_unit_tests(
    code=<extracted_code>,
    function_name="{function_name}",
    framework="pytest"
)
```

### Step 4: Review Generated Tests
The generated tests will include:
- **Happy path tests**: Normal expected inputs
- **Edge case tests**: Boundary conditions
- **Error path tests**: Invalid inputs, exceptions

For each test case, verify:
1. The input values make sense for the path
2. The expected behavior is correct
3. Assertions are meaningful

### Step 5: Enhance Tests
Consider adding:
- **Property-based tests** for functions with numeric inputs
- **Mock tests** for external dependencies
- **Integration tests** if the function calls other modules

### Step 6: Create Test File
Save the tests to `tests/test_{function_name}.py`:
```python
# tests/test_{function_name}.py
import pytest
from {file_path.replace('/', '.').replace('.py', '')} import {function_name}

<generated_test_code>
```

### Step 7: Verify Tests Pass
Run the tests to ensure they work:
```bash
pytest tests/test_{function_name}.py -v
```

## Coverage Goals
- Aim for 100% branch coverage
- Each path from symbolic execution should have a test
- Edge cases should be explicitly tested

Please proceed with Step 1 to begin extracting the function."""


# ============================================================================
# v2.2.0 WORKFLOW PROMPTS - Guided Multi-Step Workflows
# [20251216_FEATURE] Feature 10: Workflow Prompts for common AI agent tasks
# ============================================================================


@mcp.prompt(title="Security Audit Workflow")
def security_audit_workflow_prompt(project_path: str) -> str:
    """
    [20251216_FEATURE] Guide an AI agent through a comprehensive security audit.

    This is a complete workflow prompt that guides through:
    1. Project structure analysis
    2. Vulnerability scanning
    3. Dependency checking
    4. Report generation

    Args:
        project_path: Path to the project root
    """
    return f"""## Security Audit Workflow for {project_path}

Follow these steps to perform a comprehensive security audit:

### Step 1: Project Analysis
Use `crawl_project` to understand the codebase structure:
```
crawl_project(
    project_root="{project_path}"
)
```

This will identify:
- All Python/JavaScript/TypeScript files
- Entry points and main modules
- Overall project structure

### Step 2: Vulnerability Scan
Use `security_scan` on each Python/JavaScript/TypeScript file discovered.
For each file with potential security issues:
```
security_scan(
    code=<file_contents>,
    filename=<file_path>
)
```

For multi-file taint analysis, use:
```
cross_file_security_scan(
    project_root="{project_path}",
    entry_point=<main_file>
)
```

### Step 3: Dependency Check
Use `scan_dependencies` to check for known CVEs:
```
scan_dependencies(
    project_path="{project_path}"
)
```

This checks:
- Python: requirements.txt, Pipfile, poetry.lock
- JavaScript/TypeScript: package.json, package-lock.json
- Known vulnerabilities from OSV database

### Step 4: Report Generation
Compile findings into a prioritized report with:

**CRITICAL** (Immediate action required):
- SQL Injection vulnerabilities
- Command Injection vulnerabilities
- Hardcoded secrets/credentials
- Known CVEs with exploit availability

**HIGH** (Address within 1 week):
- XSS vulnerabilities
- Path Traversal issues
- Insecure deserialization
- Authentication bypasses

**MEDIUM** (Address within 1 month):
- Information disclosure
- Weak cryptography
- Missing input validation

**LOW** (Nice to fix):
- Code quality issues
- Minor security improvements
- Best practice recommendations

For each finding, include:
- **Location**: File path and line number
- **Severity**: CRITICAL/HIGH/MEDIUM/LOW
- **Description**: What the vulnerability is
- **Impact**: What could go wrong
- **Remediation**: How to fix it
- **Code Example**: Show the vulnerable code and fixed version

Begin by running `crawl_project("{project_path}")` to start the audit.
"""


@mcp.prompt(title="Safe Refactor Workflow")
def safe_refactor_workflow_prompt(file_path: str, symbol_name: str) -> str:
    """
    [20251216_FEATURE] Guide an AI agent through a safe refactoring operation.

    This workflow ensures refactoring is done safely with validation:
    1. Extract current implementation
    2. Find all usages
    3. Plan changes
    4. Simulate refactor
    5. Apply changes (only if safe)

    Args:
        file_path: Path to the file containing the symbol
        symbol_name: Name of the function/class to refactor
    """
    return f"""## Safe Refactor Workflow for {symbol_name} in {file_path}

### Step 1: Extract Current Implementation
Use `extract_code` to get the current implementation:
```
extract_code(
    file_path="{file_path}",
    target_name="{symbol_name}",
    include_context=True
)
```

Review the extracted code to understand:
- Current function signature
- Dependencies (imports, other functions)
- Complexity and structure
- Existing patterns

### Step 2: Find All Usages
Use `get_symbol_references` to find all call sites:
```
get_symbol_references(
    symbol_name="{symbol_name}",
    project_root="<project_root>"
)
```

Document all locations where {symbol_name} is:
- Called/invoked
- Imported
- Referenced in type annotations
- Used in tests

### Step 3: Plan Changes
List all changes needed across files:

**Primary Changes** (in {file_path}):
- [ ] Function signature modifications
- [ ] Logic improvements
- [ ] Error handling updates
- [ ] Documentation updates

**Secondary Changes** (in dependent files):
- [ ] Update imports if renaming
- [ ] Update call sites if signature changes
- [ ] Update type annotations if types change
- [ ] Update tests to match new behavior

**Risk Assessment**:
- Breaking changes: YES/NO
- Number of dependent files: <count>
- Test coverage: <percentage>

### Step 4: Simulate Refactor
Use `simulate_refactor` to verify changes are safe:
```
simulate_refactor(
    original_code=<current_implementation>,
    new_code=<your_refactored_code>,
    strict_mode=True
)
```

The simulation will check:
- Function signature compatibility
- Return type consistency
- Exception handling preservation
- Side effect changes

**DO NOT PROCEED** if simulation fails or shows warnings.

### Step 5: Apply Changes
Only if simulation passes with no warnings:

For the primary file:
```
update_symbol(
    file_path="{file_path}",
    target_type="function",  # or "class"
    target_name="{symbol_name}",
    new_code=<your_refactored_code>,
    create_backup=True
)
```

For dependent files (if needed):
- Update each file manually or with update_symbol
- Update imports using extract_code + update_symbol
- Verify each change with simulation

### Step 6: Verify
After applying changes:

1. **Run Tests**:
   - Unit tests for {symbol_name}
   - Integration tests for dependent code
   - Full test suite if breaking changes

2. **Check Linters**:
   - Run static analysis tools
   - Check type checking (mypy, TypeScript)
   - Verify code formatting

3. **Review Changes**:
   - Use git diff to review all changes
   - Verify backup files were created
   - Check that all usages were updated

### Rollback Plan
If anything goes wrong:
1. Restore from .bak backup files
2. Run tests to verify rollback
3. Investigate what went wrong before retrying

### Safety Checklist
- [ ] Step 1: Current code extracted
- [ ] Step 2: All usages found
- [ ] Step 3: Changes planned and reviewed
- [ ] Step 4: Simulation passed
- [ ] Step 5: Changes applied with backups
- [ ] Step 6: Tests passing

Begin by running `extract_code(file_path="{file_path}", target_name="{symbol_name}")` to extract the current implementation.
"""


# ============================================================================
# v1.4.0 MCP TOOLS - Enhanced AI Context
# ============================================================================


def _get_file_context_sync(file_path: str) -> FileContextResult:
    """
    Synchronous implementation of get_file_context.

    [20251214_FEATURE] v1.5.3 - Integrated PathResolver for intelligent path resolution
    """
    from code_scalpel.mcp.path_resolver import resolve_path

    try:
        # [20251214_FEATURE] Use PathResolver for intelligent path resolution
        try:
            resolved_path = resolve_path(file_path, str(PROJECT_ROOT))
            path = Path(resolved_path)
        except FileNotFoundError as e:
            # PathResolver provides helpful error messages
            return FileContextResult(
                success=False,
                file_path=file_path,
                line_count=0,
                error=str(e),
            )

        code = path.read_text(encoding="utf-8")
        lines = code.splitlines()

        # Parse the code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return FileContextResult(
                success=False,
                file_path=str(path),
                line_count=len(lines),
                error=f"Syntax error at line {e.lineno}: {e.msg}",
            )

        functions = []
        classes = []
        imports = []
        exports = []
        complexity = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                # Only top-level functions
                if hasattr(node, "col_offset") and node.col_offset == 0:
                    functions.append(node.name)
                    complexity += _count_complexity_node(node)
            elif isinstance(node, ast.ClassDef):
                if hasattr(node, "col_offset") and node.col_offset == 0:
                    classes.append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
            elif isinstance(node, ast.Assign):
                # Check for __all__ exports
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List | ast.Tuple):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(
                                    elt.value, str
                                ):
                                    exports.append(elt.value)

        # Quick security check
        has_security_issues = False
        security_patterns = [
            "eval(",
            "exec(",
            "cursor.execute",
            "os.system(",
            "subprocess.call(",
        ]
        for pattern in security_patterns:
            if pattern in code:
                has_security_issues = True
                break

        # Generate summary based on content
        summary_parts = []
        if classes:
            summary_parts.append(f"{len(classes)} class(es)")
        if functions:
            summary_parts.append(f"{len(functions)} function(s)")
        if "flask" in code.lower() or "app.route" in code:
            summary_parts.append("Flask web application")
        elif "django" in code.lower():
            summary_parts.append("Django module")
        elif "test_" in path.name or "pytest" in code:
            summary_parts.append("Test module")

        summary = ", ".join(summary_parts) if summary_parts else "Python module"

        return FileContextResult(
            success=True,
            file_path=str(path),
            language="python",
            line_count=len(lines),
            functions=functions,
            classes=classes,
            imports=imports[:20],  # Limit to avoid token bloat
            exports=exports,
            complexity_score=complexity,
            has_security_issues=has_security_issues,
            summary=summary,
        )

    except Exception as e:
        return FileContextResult(
            success=False,
            file_path=file_path,
            line_count=0,
            error=f"Analysis failed: {str(e)}",
        )


def _count_complexity_node(node: ast.AST) -> int:
    """Count cyclomatic complexity for a single node."""
    complexity = 1  # Base complexity
    for child in ast.walk(node):
        if isinstance(child, ast.If | ast.While | ast.For | ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity


@mcp.tool()
async def get_file_context(file_path: str) -> FileContextResult:
    """
    Get a file overview without reading full content.

    [v1.4.0] Use this tool to quickly assess if a file is relevant to your task
    without consuming tokens on full content. Returns functions, classes, imports,
    complexity score, and security warnings.

    Why AI agents need this:
    - Quickly assess file relevance before extracting code
    - Understand file structure without token overhead
    - Make informed decisions about which functions to modify

    Args:
        file_path: Path to the Python file (absolute or relative to project root)

    Returns:
        FileContextResult with file overview and metadata
    """
    return await asyncio.to_thread(_get_file_context_sync, file_path)


def _get_symbol_references_sync(
    symbol_name: str, project_root: str | None = None
) -> SymbolReferencesResult:
    """Synchronous implementation of get_symbol_references."""
    try:
        root = Path(project_root) if project_root else PROJECT_ROOT

        if not root.exists():
            return SymbolReferencesResult(
                success=False,
                symbol_name=symbol_name,
                error=f"Project root not found: {root}",
            )

        references: list[SymbolReference] = []
        definition_file = None
        definition_line = None

        # Walk through all Python files
        for py_file in root.rglob("*.py"):
            # Skip common non-source directories
            if any(
                part.startswith(".")
                or part
                in ("__pycache__", "node_modules", "venv", ".venv", "dist", "build")
                for part in py_file.parts
            ):
                continue

            try:
                code = py_file.read_text(encoding="utf-8")
                lines = code.splitlines()
                tree = ast.parse(code)

                for node in ast.walk(tree):
                    # Check for function/class definitions
                    if isinstance(
                        node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
                    ):
                        if node.name == symbol_name:
                            rel_path = str(py_file.relative_to(root))
                            if definition_file is None:
                                definition_file = rel_path
                                definition_line = node.lineno

                            context = (
                                lines[node.lineno - 1]
                                if node.lineno <= len(lines)
                                else ""
                            )
                            references.append(
                                SymbolReference(
                                    file=rel_path,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    context=context.strip(),
                                    is_definition=True,
                                )
                            )

                    # Check for function calls
                    elif isinstance(node, ast.Call):
                        func = node.func
                        name = None
                        if isinstance(func, ast.Name):
                            name = func.id
                        elif isinstance(func, ast.Attribute):
                            name = func.attr

                        if name == symbol_name:
                            rel_path = str(py_file.relative_to(root))
                            line_no = getattr(node, "lineno", 0)
                            context = (
                                lines[line_no - 1] if 0 < line_no <= len(lines) else ""
                            )
                            references.append(
                                SymbolReference(
                                    file=rel_path,
                                    line=line_no,
                                    column=getattr(node, "col_offset", 0),
                                    context=context.strip(),
                                    is_definition=False,
                                )
                            )

                    # Check for name references
                    elif isinstance(node, ast.Name) and node.id == symbol_name:
                        rel_path = str(py_file.relative_to(root))
                        line_no = getattr(node, "lineno", 0)
                        context = (
                            lines[line_no - 1] if 0 < line_no <= len(lines) else ""
                        )
                        # Avoid duplicates from Call nodes
                        if not any(
                            r.file == rel_path and r.line == line_no for r in references
                        ):
                            references.append(
                                SymbolReference(
                                    file=rel_path,
                                    line=line_no,
                                    column=getattr(node, "col_offset", 0),
                                    context=context.strip(),
                                    is_definition=False,
                                )
                            )

            except (SyntaxError, UnicodeDecodeError):
                # Skip files that can't be parsed
                continue

        # Remove duplicates and sort
        seen = set()
        unique_refs = []
        for ref in references:
            key = (ref.file, ref.line, ref.is_definition)
            if key not in seen:
                seen.add(key)
                unique_refs.append(ref)

        unique_refs.sort(key=lambda r: (not r.is_definition, r.file, r.line))

        return SymbolReferencesResult(
            success=True,
            symbol_name=symbol_name,
            definition_file=definition_file,
            definition_line=definition_line,
            references=unique_refs[:100],  # Limit to prevent token overflow
            total_references=len(unique_refs),
        )

    except Exception as e:
        return SymbolReferencesResult(
            success=False,
            symbol_name=symbol_name,
            error=f"Search failed: {str(e)}",
        )


@mcp.tool()
async def get_symbol_references(
    symbol_name: str,
    project_root: str | None = None,
) -> SymbolReferencesResult:
    """
    Find all references to a symbol across the project.

    [v1.4.0] Use this tool before modifying a function, class, or variable to
    understand its usage across the codebase. Essential for safe refactoring.

    Why AI agents need this:
    - Safe refactoring: know all call sites before changing signatures
    - Impact analysis: understand blast radius of changes
    - No hallucination: real references, not guessed ones

    Args:
        symbol_name: Name of the function, class, or variable to search for
        project_root: Project root directory (default: server's project root)

    Returns:
        SymbolReferencesResult with definition location and all references
    """
    return await asyncio.to_thread(
        _get_symbol_references_sync, symbol_name, project_root
    )


# ============================================================================
# v1.5.0 MCP TOOLS - Project Intelligence
# ============================================================================


class DependencyVulnerability(BaseModel):
    """A vulnerability found in a dependency."""

    id: str = Field(description="CVE or GHSA identifier")
    summary: str = Field(description="Brief description of the vulnerability")
    severity: str = Field(
        description="Severity level: CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN"
    )
    package: str = Field(description="Affected package name")
    vulnerable_version: str = Field(description="The vulnerable version installed")
    fixed_version: str | None = Field(
        default=None, description="Version where vulnerability is fixed"
    )
    aliases: list[str] = Field(
        default_factory=list, description="Alternative identifiers (e.g., GHSA)"
    )
    references: list[str] = Field(
        default_factory=list, description="URLs with more information"
    )


class DependencyInfo(BaseModel):
    """Information about a single dependency."""

    name: str = Field(description="Package name")
    version: str = Field(description="Installed/required version")
    ecosystem: str = Field(description="Package ecosystem (PyPI, npm, etc.)")
    vulnerabilities: list[DependencyVulnerability] = Field(
        default_factory=list, description="Known vulnerabilities"
    )


class DependencyScanResult(BaseModel):
    """Result of dependency vulnerability scan."""

    success: bool = Field(description="Whether scan succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")
    total_dependencies: int = Field(description="Total number of dependencies scanned")
    vulnerable_count: int = Field(
        description="Number of dependencies with vulnerabilities"
    )
    total_vulnerabilities: int = Field(
        description="Total number of vulnerabilities found"
    )
    severity_summary: dict[str, int] = Field(
        default_factory=dict, description="Count by severity level"
    )
    dependencies: list[DependencyInfo] = Field(
        default_factory=list, description="All scanned dependencies"
    )
    error: str | None = Field(default=None, description="Error message if failed")


def _scan_dependencies_sync(
    project_root: str | None = None,
    include_dev: bool = False,
    scan_vulnerabilities: bool = True,
) -> DependencyScanResult:
    """
    Synchronous implementation of scan_dependencies.

    [20251213_FEATURE] v1.5.0 - Scan project dependencies for vulnerabilities.
    """
    from code_scalpel.ast_tools.dependency_parser import DependencyParser
    from code_scalpel.ast_tools.osv_client import OSVClient, OSVError

    try:
        root = Path(project_root) if project_root else PROJECT_ROOT

        if not root.exists():
            return DependencyScanResult(
                success=False,
                total_dependencies=0,
                vulnerable_count=0,
                total_vulnerabilities=0,
                error=f"Project root not found: {root}",
            )

        # Parse dependencies from project files
        parser = DependencyParser(str(root))
        raw_deps = parser.get_dependencies()

        dependencies: list[DependencyInfo] = []
        severity_summary: dict[str, int] = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "UNKNOWN": 0,
        }
        total_vulns = 0
        vulnerable_count = 0

        # Process each ecosystem
        for ecosystem, pkg_list in raw_deps.items():
            # Map ecosystem to OSV format
            osv_ecosystem = (
                "PyPI"
                if ecosystem == "python"
                else (
                    "npm"
                    if ecosystem == "javascript"
                    else "Maven" if ecosystem == "maven" else ecosystem
                )
            )

            for pkg in pkg_list:
                name = pkg.get("name", "")
                version = pkg.get("version", "*")
                is_dev = pkg.get("type") == "dev"

                if not name:
                    continue

                # Skip dev dependencies if not requested
                if is_dev and not include_dev:
                    continue

                dep_info = DependencyInfo(
                    name=name,
                    version=version,
                    ecosystem=osv_ecosystem,
                    vulnerabilities=[],
                )

                # Query OSV for vulnerabilities if enabled and version is specific
                if scan_vulnerabilities and version not in ("*", "", "latest"):
                    # Clean version string for OSV query
                    clean_version = version.lstrip(">=<~^")
                    if clean_version:
                        try:
                            client = OSVClient(timeout=5)
                            vulns = client.query_package(
                                name, clean_version, osv_ecosystem
                            )

                            for v in vulns:
                                dep_vuln = DependencyVulnerability(
                                    id=v.id,
                                    summary=v.summary,
                                    severity=v.severity,
                                    package=v.package,
                                    vulnerable_version=v.vulnerable_version,
                                    fixed_version=v.fixed_version,
                                    aliases=v.aliases,
                                    references=v.references,
                                )
                                dep_info.vulnerabilities.append(dep_vuln)
                                severity_summary[v.severity] = (
                                    severity_summary.get(v.severity, 0) + 1
                                )
                                total_vulns += 1
                        except OSVError:
                            # Continue scanning other dependencies even if one fails
                            pass

                if dep_info.vulnerabilities:
                    vulnerable_count += 1

                dependencies.append(dep_info)

        return DependencyScanResult(
            success=True,
            total_dependencies=len(dependencies),
            vulnerable_count=vulnerable_count,
            total_vulnerabilities=total_vulns,
            severity_summary=severity_summary,
            dependencies=dependencies,
        )

    except Exception as e:
        return DependencyScanResult(
            success=False,
            total_dependencies=0,
            vulnerable_count=0,
            total_vulnerabilities=0,
            error=f"Scan failed: {str(e)}",
        )


@mcp.tool()
async def scan_dependencies(
    project_root: str | None = None,
    include_dev: bool = False,
    scan_vulnerabilities: bool = True,
    ctx: Context | None = None,
) -> DependencyScanResult:
    """
    Scan project dependencies for known vulnerabilities.

    [v1.5.0] Use this tool to identify vulnerable dependencies before deployment.
    Parses requirements.txt, pyproject.toml, and package.json, then queries the
    OSV (Open Source Vulnerabilities) database for known CVEs.

    [20251215_FEATURE] v2.0.0 - Progress reporting for long-running operations.
    Reports progress during dependency parsing and vulnerability scanning.

    Why AI agents need this:
    - Security: Identify vulnerable packages before they become exploits
    - Compliance: Generate reports for security audits
    - Upgrade guidance: Know which versions fix vulnerabilities

    Args:
        project_root: Project root directory (default: server's project root)
        include_dev: Include development dependencies (default: False)
        scan_vulnerabilities: Query OSV for vulnerabilities (default: True)

    Returns:
        DependencyScanResult with dependency list and vulnerability details
    """
    # [20251215_FEATURE] v2.0.0 - Progress token support
    if ctx:
        await ctx.report_progress(progress=0, total=100)

    result = await asyncio.to_thread(
        _scan_dependencies_sync, project_root, include_dev, scan_vulnerabilities
    )

    if ctx:
        await ctx.report_progress(progress=100, total=100)

    return result


# ============================================================================
# [20251213_FEATURE] v1.5.0 - get_call_graph MCP Tool
# ============================================================================


class CallNodeModel(BaseModel):
    """Node in the call graph representing a function."""

    name: str = Field(description="Function name")
    file: str = Field(description="File path (relative) or '<external>'")
    line: int = Field(description="Line number (0 if unknown)")
    end_line: int | None = Field(default=None, description="End line number")
    is_entry_point: bool = Field(
        default=False, description="Whether function is an entry point"
    )


class CallEdgeModel(BaseModel):
    """Edge in the call graph representing a function call."""

    caller: str = Field(description="Caller function (file:name)")
    callee: str = Field(description="Callee function (file:name or external name)")


class CallGraphResultModel(BaseModel):
    """Result of call graph analysis."""

    nodes: list[CallNodeModel] = Field(
        default_factory=list, description="Functions in the graph"
    )
    edges: list[CallEdgeModel] = Field(
        default_factory=list, description="Call relationships"
    )
    entry_point: str | None = Field(
        default=None, description="Entry point used for filtering"
    )
    depth_limit: int | None = Field(default=None, description="Depth limit used")
    mermaid: str = Field(default="", description="Mermaid diagram representation")
    circular_imports: list[list[str]] = Field(
        default_factory=list, description="Detected import cycles"
    )
    error: str | None = Field(default=None, description="Error message if failed")


def _get_call_graph_sync(
    project_root: str | None,
    entry_point: str | None,
    depth: int,
    include_circular_import_check: bool,
) -> CallGraphResultModel:
    """Synchronous implementation of get_call_graph."""
    from code_scalpel.ast_tools.call_graph import CallGraphBuilder

    root_path = Path(project_root) if project_root else PROJECT_ROOT

    if not root_path.exists():
        return CallGraphResultModel(
            error=f"Project root not found: {root_path}",
        )

    try:
        builder = CallGraphBuilder(root_path)
        result = builder.build_with_details(entry_point=entry_point, depth=depth)

        # Convert dataclasses to Pydantic models
        nodes = [
            CallNodeModel(
                name=n.name,
                file=n.file,
                line=n.line,
                end_line=n.end_line,
                is_entry_point=n.is_entry_point,
            )
            for n in result.nodes
        ]

        edges = [CallEdgeModel(caller=e.caller, callee=e.callee) for e in result.edges]

        # Optionally check for circular imports
        circular_imports = []
        if include_circular_import_check:
            circular_imports = builder.detect_circular_imports()

        return CallGraphResultModel(
            nodes=nodes,
            edges=edges,
            entry_point=result.entry_point,
            depth_limit=result.depth_limit,
            mermaid=result.mermaid,
            circular_imports=circular_imports,
        )

    except Exception as e:
        return CallGraphResultModel(
            error=f"Call graph analysis failed: {str(e)}",
        )


@mcp.tool()
async def get_call_graph(
    project_root: str | None = None,
    entry_point: str | None = None,
    depth: int = 10,
    include_circular_import_check: bool = True,
) -> CallGraphResultModel:
    """
    Build a call graph showing function relationships in the project.

    [v1.5.0] Use this tool to understand code flow and function dependencies.
    Analyzes Python source files to build a static call graph with:
    - Line number tracking for each function
    - Entry point detection (main, CLI commands, routes)
    - Depth-limited traversal from any starting function
    - Mermaid diagram generation for visualization
    - Circular import detection

    Why AI agents need this:
    - Navigation: Quickly understand how functions connect
    - Impact analysis: See what breaks if you change a function
    - Refactoring: Identify tightly coupled code
    - Documentation: Generate visual diagrams of code flow

    Args:
        project_root: Project root directory (default: server's project root)
        entry_point: Starting function name (e.g., "main" or "app.py:main")
                    If None, includes all functions
        depth: Maximum depth to traverse from entry point (default: 10)
        include_circular_import_check: Check for circular imports (default: True)

    Returns:
        CallGraphResultModel with nodes, edges, Mermaid diagram, and any circular imports
    """
    return await asyncio.to_thread(
        _get_call_graph_sync,
        project_root,
        entry_point,
        depth,
        include_circular_import_check,
    )


# ============================================================================
# [20251216_FEATURE] v2.5.0 - get_graph_neighborhood MCP Tool
# ============================================================================


class NeighborhoodNodeModel(BaseModel):
    """A node in the neighborhood subgraph."""

    id: str = Field(description="Node ID (language::module::type::name)")
    depth: int = Field(description="Distance from center node (0 = center)")
    metadata: dict = Field(default_factory=dict, description="Additional node metadata")


class NeighborhoodEdgeModel(BaseModel):
    """An edge in the neighborhood subgraph."""

    from_id: str = Field(description="Source node ID")
    to_id: str = Field(description="Target node ID")
    edge_type: str = Field(description="Type of relationship")
    confidence: float = Field(description="Confidence score (0.0-1.0)")


class GraphNeighborhoodResult(BaseModel):
    """Result of k-hop neighborhood extraction."""

    success: bool = Field(description="Whether extraction succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")

    # Center node info
    center_node_id: str = Field(default="", description="ID of the center node")
    k: int = Field(default=0, description="Number of hops used")

    # Subgraph
    nodes: list[NeighborhoodNodeModel] = Field(
        default_factory=list, description="Nodes in the neighborhood"
    )
    edges: list[NeighborhoodEdgeModel] = Field(
        default_factory=list, description="Edges in the neighborhood"
    )
    total_nodes: int = Field(default=0, description="Number of nodes in subgraph")
    total_edges: int = Field(default=0, description="Number of edges in subgraph")

    # Truncation info
    max_depth_reached: int = Field(
        default=0, description="Maximum depth actually reached"
    )
    truncated: bool = Field(default=False, description="Whether graph was truncated")
    truncation_warning: str | None = Field(
        default=None, description="Warning if truncated"
    )

    # Mermaid diagram
    mermaid: str = Field(default="", description="Mermaid diagram of neighborhood")

    error: str | None = Field(default=None, description="Error message if failed")


def _generate_neighborhood_mermaid(
    nodes: list[NeighborhoodNodeModel],
    edges: list[NeighborhoodEdgeModel],
    center_node_id: str,
) -> str:
    """Generate Mermaid diagram for neighborhood."""
    lines = ["graph TD"]

    # Add nodes with depth-based styling
    for node in nodes:
        # Sanitize node ID for Mermaid
        safe_id = node.id.replace("::", "_").replace(".", "_").replace("-", "_")
        label = node.id.split("::")[-1] if "::" in node.id else node.id

        if node.depth == 0:
            # Center node - special styling
            lines.append(f'    {safe_id}["{label}"]:::center')
        elif node.depth == 1:
            lines.append(f'    {safe_id}["{label}"]:::depth1')
        else:
            lines.append(f'    {safe_id}["{label}"]:::depth2plus')

    # Add edges
    for edge in edges:
        from_safe = edge.from_id.replace("::", "_").replace(".", "_").replace("-", "_")
        to_safe = edge.to_id.replace("::", "_").replace(".", "_").replace("-", "_")
        lines.append(f"    {from_safe} --> {to_safe}")

    # Add style definitions
    lines.append("    classDef center fill:#f9f,stroke:#333,stroke-width:3px")
    lines.append("    classDef depth1 fill:#bbf,stroke:#333,stroke-width:2px")
    lines.append("    classDef depth2plus fill:#ddd,stroke:#333,stroke-width:1px")

    return "\n".join(lines)


@mcp.tool()
async def get_graph_neighborhood(
    center_node_id: str,
    k: int = 2,
    max_nodes: int = 100,
    direction: str = "both",
    min_confidence: float = 0.0,
    project_root: str | None = None,
) -> GraphNeighborhoodResult:
    """
    Extract k-hop neighborhood subgraph around a center node.

    [v2.5.0] Use this tool to prevent graph explosion when analyzing large
    codebases. Instead of loading the entire graph, extract only the nodes
    within k hops of a specific node.

    **Graph Pruning Formula:** N(v, k) = {u ∈ V : d(v, u) ≤ k}

    This extracts all nodes u where the shortest path from center v to u
    is at most k hops.

    **Truncation Protection:**
    If the neighborhood exceeds max_nodes, the graph is truncated and
    a warning is returned. This prevents memory exhaustion on dense graphs.

    Key capabilities:
    - Extract focused subgraph around any node
    - Control traversal depth with k parameter
    - Limit graph size with max_nodes
    - Filter by edge direction (incoming, outgoing, both)
    - Filter by minimum confidence score
    - Generate Mermaid visualization

    Why AI agents need this:
    - **Focused Analysis:** Analyze only relevant code, not entire codebase
    - **Memory Safety:** Prevent OOM on large graphs
    - **Honest Uncertainty:** Know when graph is incomplete

    Example:
        # Get 2-hop neighborhood around a function
        result = get_graph_neighborhood(
            center_node_id="python::services::function::process_order",
            k=2,
            max_nodes=50
        )
        if result.truncated:
            print(f"Warning: {result.truncation_warning}")

    Args:
        center_node_id: ID of the center node (format: language::module::type::name)
        k: Maximum hops from center (default: 2)
        max_nodes: Maximum nodes to include (default: 100)
        direction: "outgoing", "incoming", or "both" (default: "both")
        min_confidence: Minimum edge confidence to follow (default: 0.0)
        project_root: Project root directory (default: server's project root)

    Returns:
        GraphNeighborhoodResult with subgraph, truncation info, and Mermaid diagram
    """
    from code_scalpel.graph_engine import UniversalGraph

    root_path = Path(project_root) if project_root else PROJECT_ROOT

    if not root_path.exists():
        return GraphNeighborhoodResult(
            success=False,
            error=f"Project root not found: {root_path}",
        )

    # Validate parameters
    if k < 1:
        return GraphNeighborhoodResult(
            success=False,
            error="k must be at least 1",
        )

    if max_nodes < 1:
        return GraphNeighborhoodResult(
            success=False,
            error="max_nodes must be at least 1",
        )

    if direction not in ("outgoing", "incoming", "both"):
        return GraphNeighborhoodResult(
            success=False,
            error=f"direction must be 'outgoing', 'incoming', or 'both', got '{direction}'",
        )

    try:
        # Try to load existing graph from project
        # For now, we'll build a simple graph from the call graph
        from code_scalpel.ast_tools.call_graph import CallGraphBuilder

        builder = CallGraphBuilder(root_path)
        call_graph_result = builder.build_with_details(entry_point=None, depth=10)

        # Convert call graph to UniversalGraph
        from code_scalpel.graph_engine import (
            GraphNode,
            GraphEdge,
            UniversalNodeID,
            NodeType,
            EdgeType,
        )

        graph = UniversalGraph()

        # Add nodes
        for node in call_graph_result.nodes:
            node_id = UniversalNodeID(
                language="python",
                module=(
                    node.file.replace("/", ".").replace(".py", "")
                    if node.file != "<external>"
                    else "external"
                ),
                node_type=NodeType.FUNCTION,
                name=node.name,
                line=node.line,
            )
            graph.add_node(
                GraphNode(
                    id=node_id,
                    metadata={
                        "file": node.file,
                        "line": node.line,
                        "is_entry_point": node.is_entry_point,
                    },
                )
            )

        # Add edges
        for edge in call_graph_result.edges:
            # Parse caller/callee into node IDs
            caller_parts = edge.caller.split(":")
            callee_parts = edge.callee.split(":")

            caller_file = caller_parts[0] if len(caller_parts) > 1 else ""
            caller_name = caller_parts[-1]
            callee_file = callee_parts[0] if len(callee_parts) > 1 else ""
            callee_name = callee_parts[-1]

            caller_module = (
                caller_file.replace("/", ".").replace(".py", "")
                if caller_file
                else "unknown"
            )
            callee_module = (
                callee_file.replace("/", ".").replace(".py", "")
                if callee_file
                else "external"
            )

            caller_id = f"python::{caller_module}::function::{caller_name}"
            callee_id = f"python::{callee_module}::function::{callee_name}"

            graph.add_edge(
                GraphEdge(
                    from_id=caller_id,
                    to_id=callee_id,
                    edge_type=EdgeType.DIRECT_CALL,
                    confidence=0.9,
                    evidence="Direct function call",
                )
            )

        # Extract neighborhood
        result = graph.get_neighborhood(
            center_node_id=center_node_id,
            k=k,
            max_nodes=max_nodes,
            direction=direction,
            min_confidence=min_confidence,
        )

        if not result.success:
            return GraphNeighborhoodResult(
                success=False,
                error=result.error,
            )

        # Convert to response models
        nodes = []
        for node_id, depth in result.node_depths.items():
            node = result.subgraph.get_node(node_id) if result.subgraph else None
            nodes.append(
                NeighborhoodNodeModel(
                    id=node_id,
                    depth=depth,
                    metadata=node.metadata if node else {},
                )
            )

        edges = []
        if result.subgraph:
            for edge in result.subgraph.edges:
                edges.append(
                    NeighborhoodEdgeModel(
                        from_id=edge.from_id,
                        to_id=edge.to_id,
                        edge_type=edge.edge_type.value,
                        confidence=edge.confidence,
                    )
                )

        # Generate Mermaid diagram
        mermaid = _generate_neighborhood_mermaid(nodes, edges, center_node_id)

        return GraphNeighborhoodResult(
            success=True,
            center_node_id=center_node_id,
            k=k,
            nodes=nodes,
            edges=edges,
            total_nodes=result.total_nodes,
            total_edges=result.total_edges,
            max_depth_reached=result.max_depth_reached,
            truncated=result.truncated,
            truncation_warning=result.truncation_warning,
            mermaid=mermaid,
        )

    except Exception as e:
        return GraphNeighborhoodResult(
            success=False,
            error=f"Graph neighborhood extraction failed: {str(e)}",
        )


# ============================================================================
# [20251213_FEATURE] v1.5.0 - get_project_map MCP Tool
# ============================================================================


class ModuleInfo(BaseModel):
    """Information about a Python module/file."""

    path: str = Field(description="Relative file path")
    functions: list[str] = Field(
        default_factory=list, description="Function names in the module"
    )
    classes: list[str] = Field(
        default_factory=list, description="Class names in the module"
    )
    imports: list[str] = Field(default_factory=list, description="Import statements")
    entry_points: list[str] = Field(
        default_factory=list, description="Detected entry points"
    )
    line_count: int = Field(default=0, description="Number of lines in file")
    complexity_score: int = Field(default=0, description="Cyclomatic complexity score")


class PackageInfo(BaseModel):
    """Information about a Python package (directory with __init__.py)."""

    name: str = Field(description="Package name")
    path: str = Field(description="Relative path to package")
    modules: list[str] = Field(
        default_factory=list, description="Module names in package"
    )
    subpackages: list[str] = Field(default_factory=list, description="Subpackage names")


class ProjectMapResult(BaseModel):
    """Result of project map analysis."""

    project_root: str = Field(description="Absolute path to project root")
    total_files: int = Field(default=0, description="Total Python files")
    total_lines: int = Field(default=0, description="Total lines of code")
    languages: dict[str, int] = Field(
        default_factory=dict, description="Language breakdown by file count"
    )
    packages: list[PackageInfo] = Field(
        default_factory=list, description="Detected packages"
    )
    modules: list[ModuleInfo] = Field(
        default_factory=list, description="All modules analyzed"
    )
    entry_points: list[str] = Field(
        default_factory=list, description="All detected entry points"
    )
    circular_imports: list[list[str]] = Field(
        default_factory=list, description="Circular import cycles"
    )
    complexity_hotspots: list[str] = Field(
        default_factory=list, description="Files with high complexity"
    )
    mermaid: str = Field(default="", description="Mermaid diagram of package structure")
    error: str | None = Field(default=None, description="Error message if failed")


def _get_project_map_sync(
    project_root: str | None,
    include_complexity: bool,
    complexity_threshold: int,
    include_circular_check: bool,
) -> ProjectMapResult:
    """Synchronous implementation of get_project_map."""
    import ast
    from code_scalpel.ast_tools.call_graph import CallGraphBuilder

    root_path = Path(project_root) if project_root else PROJECT_ROOT

    if not root_path.exists():
        return ProjectMapResult(
            project_root=str(root_path),
            error=f"Project root not found: {root_path}",
        )

    try:
        modules: list[ModuleInfo] = []
        packages: dict[str, PackageInfo] = {}
        all_entry_points: list[str] = []
        complexity_hotspots: list[str] = []
        total_lines = 0

        # Entry point detection patterns
        entry_decorators = {
            "command",
            "main",
            "cli",
            "app",
            "route",
            "get",
            "post",
            "put",
            "delete",
        }

        def is_entry_point(func_node: ast.AST) -> bool:
            """Check if function is an entry point."""
            if func_node.name == "main":
                return True
            for dec in getattr(func_node, "decorator_list", []):
                dec_name = ""
                if isinstance(dec, ast.Name):
                    dec_name = dec.id
                elif isinstance(dec, ast.Attribute):
                    dec_name = dec.attr
                elif isinstance(dec, ast.Call):
                    if isinstance(dec.func, ast.Attribute):
                        dec_name = dec.func.attr
                    elif isinstance(dec.func, ast.Name):
                        dec_name = dec.func.id
                if dec_name in entry_decorators:
                    return True
            return False

        def calculate_complexity(tree: ast.AST) -> int:
            """Calculate cyclomatic complexity of a module."""
            complexity = 1  # Base complexity
            for node in ast.walk(tree):
                if isinstance(
                    node,
                    (
                        ast.If,
                        ast.While,
                        ast.For,
                        ast.AsyncFor,
                        ast.ExceptHandler,
                        ast.With,
                        ast.AsyncWith,
                        ast.Assert,
                        ast.comprehension,
                    ),
                ):
                    complexity += 1
                elif isinstance(node, (ast.And, ast.Or)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            return complexity

        # Collect all Python files
        python_files = list(root_path.rglob("*.py"))

        # Filter out common excluded directories
        exclude_patterns = {
            "__pycache__",
            ".git",
            "venv",
            ".venv",
            "env",
            ".env",
            "node_modules",
            "dist",
            "build",
            ".tox",
            ".pytest_cache",
            "htmlcov",
            ".mypy_cache",
        }

        for file_path in python_files:
            # Skip excluded directories
            if any(part in exclude_patterns for part in file_path.parts):
                continue

            rel_path = str(file_path.relative_to(root_path))

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()

                lines = code.count("\n") + 1
                total_lines += lines

                tree = ast.parse(code)

                # Extract module info
                functions = []
                classes = []
                imports = []
                entry_points = []

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions.append(node.name)
                        if is_entry_point(node):
                            entry_points.append(f"{rel_path}:{node.name}")
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)

                # Calculate complexity if requested
                complexity = 0
                if include_complexity:
                    complexity = calculate_complexity(tree)
                    if complexity >= complexity_threshold:
                        complexity_hotspots.append(
                            f"{rel_path} (complexity: {complexity})"
                        )

                all_entry_points.extend(entry_points)

                modules.append(
                    ModuleInfo(
                        path=rel_path,
                        functions=functions,
                        classes=classes,
                        imports=list(set(imports)),  # Dedupe
                        entry_points=entry_points,
                        line_count=lines,
                        complexity_score=complexity,
                    )
                )

                # Track packages
                parent = file_path.parent
                while parent != root_path and parent.exists():
                    init_file = parent / "__init__.py"
                    if init_file.exists():
                        pkg_path = str(parent.relative_to(root_path))
                        pkg_name = parent.name
                        if pkg_path not in packages:
                            packages[pkg_path] = PackageInfo(
                                name=pkg_name,
                                path=pkg_path,
                                modules=[],
                                subpackages=[],
                            )
                        # Add module to package
                        if rel_path not in packages[pkg_path].modules:
                            packages[pkg_path].modules.append(rel_path)
                    parent = parent.parent

            except Exception:
                # Skip files with errors
                continue

        # Organize package hierarchy
        pkg_list = list(packages.values())
        for pkg in pkg_list:
            for other_pkg in pkg_list:
                if (
                    other_pkg.path.startswith(pkg.path + "/")
                    and other_pkg.name not in pkg.subpackages
                ):
                    pkg.subpackages.append(other_pkg.name)

        # Check for circular imports
        circular_imports = []
        if include_circular_check:
            builder = CallGraphBuilder(root_path)
            circular_imports = builder.detect_circular_imports()

        # [20251213_FEATURE] Calculate language breakdown
        languages: dict[str, int] = {"python": len(modules)}
        # Also count other common file types
        for ext, lang in [
            (".js", "javascript"),
            (".ts", "typescript"),
            (".java", "java"),
            (".json", "json"),
            (".yaml", "yaml"),
            (".yml", "yaml"),
            (".md", "markdown"),
            (".html", "html"),
            (".css", "css"),
        ]:
            len(list(root_path.rglob(f"*{ext}")))
            # Exclude common ignored dirs
            actual_count = sum(
                1
                for f in root_path.rglob(f"*{ext}")
                if not any(p in exclude_patterns for p in f.parts)
            )
            if actual_count > 0:
                languages[lang] = languages.get(lang, 0) + actual_count

        # Generate Mermaid package diagram
        mermaid_lines = ["graph TD"]
        mermaid_lines.append("    subgraph Project")
        for i, mod in enumerate(modules[:50]):  # Limit to 50 modules
            mod_id = f"M{i}"
            label = mod.path.replace("/", "_").replace(".", "_")
            if mod.entry_points:
                mermaid_lines.append(
                    f'        {mod_id}[["{label}"]]'
                )  # Stadium for entry
            else:
                mermaid_lines.append(f'        {mod_id}["{label}"]')
        mermaid_lines.append("    end")

        return ProjectMapResult(
            project_root=str(root_path),
            total_files=len(modules),
            total_lines=total_lines,
            languages=languages,
            packages=pkg_list,
            modules=modules,
            entry_points=all_entry_points,
            circular_imports=circular_imports,
            complexity_hotspots=complexity_hotspots,
            mermaid="\n".join(mermaid_lines),
        )

    except Exception as e:
        return ProjectMapResult(
            project_root=str(root_path),
            error=f"Project map analysis failed: {str(e)}",
        )


@mcp.tool()
async def get_project_map(
    project_root: str | None = None,
    include_complexity: bool = True,
    complexity_threshold: int = 10,
    include_circular_check: bool = True,
) -> ProjectMapResult:
    """
    Generate a comprehensive map of the project structure.

    [v1.5.0] Use this tool to get a high-level overview of a codebase before diving in.
    Analyzes all Python files to provide:
    - Package and module structure
    - Function and class inventory per file
    - Entry point detection (main, CLI commands, routes)
    - Complexity hotspots (files that need attention)
    - Circular import detection
    - Mermaid diagram of project structure

    Why AI agents need this:
    - Orientation: Understand project structure before making changes
    - Navigation: Know where to find specific functionality
    - Risk assessment: Identify complex areas that need careful handling
    - Architecture: See how packages and modules are organized

    Args:
        project_root: Project root directory (default: server's project root)
        include_complexity: Calculate cyclomatic complexity (default: True)
        complexity_threshold: Threshold for flagging hotspots (default: 10)
        include_circular_check: Check for circular imports (default: True)

    Returns:
        ProjectMapResult with comprehensive project overview
    """
    return await asyncio.to_thread(
        _get_project_map_sync,
        project_root,
        include_complexity,
        complexity_threshold,
        include_circular_check,
    )


# ============================================================================
# [20251213_FEATURE] v1.5.1 - get_cross_file_dependencies MCP Tool
# ============================================================================


class ImportNodeModel(BaseModel):
    """Information about an import in the import graph."""

    module: str = Field(description="Module name (e.g., 'os', 'mypackage.utils')")
    import_type: str = Field(description="Import type: 'direct', 'from', or 'star'")
    names: list[str] = Field(
        default_factory=list, description="Imported names (for 'from' imports)"
    )
    alias: str | None = Field(default=None, description="Alias if import uses 'as'")
    line: int = Field(default=0, description="Line number of import")


class SymbolDefinitionModel(BaseModel):
    """Information about a symbol defined in a file."""

    name: str = Field(description="Symbol name")
    file: str = Field(description="File where symbol is defined (relative path)")
    line: int = Field(default=0, description="Line number of definition")
    symbol_type: str = Field(description="Type: 'function', 'class', or 'variable'")
    is_exported: bool = Field(default=False, description="Whether symbol is in __all__")


class ExtractedSymbolModel(BaseModel):
    """An extracted symbol with its code and dependencies."""

    name: str = Field(description="Symbol name")
    code: str = Field(description="Full source code of the symbol")
    file: str = Field(description="Source file (relative path)")
    line_start: int = Field(default=0, description="Starting line number")
    line_end: int = Field(default=0, description="Ending line number")
    dependencies: list[str] = Field(
        default_factory=list, description="Names of symbols this depends on"
    )
    # [20251216_FEATURE] v2.5.0 - Confidence decay for deep dependency chains
    depth: int = Field(default=0, description="Depth from original target (0 = target)")
    confidence: float = Field(
        default=1.0,
        description="Confidence score with decay applied (0.0-1.0). Formula: C_base × 0.9^depth",
    )
    low_confidence: bool = Field(
        default=False, description="True if confidence is below threshold (0.5)"
    )


class CrossFileDependenciesResult(BaseModel):
    """Result of cross-file dependency analysis."""

    success: bool = Field(description="Whether analysis succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")

    # Target symbol info
    target_name: str = Field(default="", description="Name of the analyzed symbol")
    target_file: str = Field(
        default="", description="File containing the target symbol"
    )

    # Dependency info
    extracted_symbols: list[ExtractedSymbolModel] = Field(
        default_factory=list,
        description="All symbols extracted (target + dependencies)",
    )
    total_dependencies: int = Field(
        default=0, description="Number of dependencies resolved"
    )
    unresolved_imports: list[str] = Field(
        default_factory=list, description="External imports that could not be resolved"
    )

    # Import graph info
    import_graph: dict[str, list[str]] = Field(
        default_factory=dict, description="Import graph: file -> list of imported files"
    )
    circular_imports: list[list[str]] = Field(
        default_factory=list, description="Detected circular import cycles"
    )

    # Combined code for AI consumption
    combined_code: str = Field(
        default="", description="All extracted code combined, ready for AI consumption"
    )
    token_estimate: int = Field(
        default=0, description="Estimated token count for combined code"
    )

    # Mermaid diagram
    mermaid: str = Field(
        default="", description="Mermaid diagram of import relationships"
    )

    # [20251216_FEATURE] v2.5.0 - Confidence decay tracking
    confidence_decay_factor: float = Field(
        default=0.9,
        description="Decay factor used: C_effective = C_base × decay_factor^depth",
    )
    low_confidence_count: int = Field(
        default=0, description="Number of symbols below confidence threshold (0.5)"
    )
    low_confidence_warning: str | None = Field(
        default=None, description="Warning message if low-confidence symbols detected"
    )

    error: str | None = Field(default=None, description="Error message if failed")


def _get_cross_file_dependencies_sync(
    project_root: str | None,
    target_file: str,
    target_symbol: str,
    max_depth: int,
    include_code: bool,
    include_diagram: bool,
    confidence_decay_factor: float = 0.9,
) -> CrossFileDependenciesResult:
    """Synchronous implementation of get_cross_file_dependencies."""
    from code_scalpel.ast_tools.import_resolver import ImportResolver
    from code_scalpel.ast_tools.cross_file_extractor import CrossFileExtractor

    root_path = Path(project_root) if project_root else PROJECT_ROOT

    if not root_path.exists():
        return CrossFileDependenciesResult(
            success=False,
            error=f"Project root not found: {root_path}",
        )

    # Resolve target file path
    target_path = Path(target_file)
    if not target_path.is_absolute():
        target_path = root_path / target_file

    if not target_path.exists():
        return CrossFileDependenciesResult(
            success=False,
            error=f"Target file not found: {target_path}",
        )

    try:
        # Build import graph
        resolver = ImportResolver(root_path)
        resolver.build()

        # Extract cross-file dependencies
        extractor = CrossFileExtractor(root_path)
        extractor.build()

        # [20251216_FEATURE] v2.5.0 - Pass confidence_decay_factor to extractor
        extraction_result = extractor.extract(
            str(target_path),
            target_symbol,
            depth=max_depth,
            confidence_decay_factor=confidence_decay_factor,
        )

        # Check for extraction errors
        if not extraction_result.success:
            return CrossFileDependenciesResult(
                success=False,
                error=f"Extraction failed: {'; '.join(extraction_result.errors)}",
            )

        # Build the list of all symbols (target + dependencies)
        all_symbols = []
        if extraction_result.target:
            all_symbols.append(extraction_result.target)
        all_symbols.extend(extraction_result.dependencies)

        # Convert extracted symbols to models
        extracted_symbols = []
        combined_parts = []

        # [20251216_FEATURE] v2.5.0 - Low confidence threshold
        LOW_CONFIDENCE_THRESHOLD = 0.5

        for sym in all_symbols:
            rel_file = (
                str(Path(sym.file).relative_to(root_path))
                if Path(sym.file).is_absolute()
                else sym.file
            )
            # [20251216_FEATURE] v2.5.0 - Include depth and confidence in symbol model
            extracted_symbols.append(
                ExtractedSymbolModel(
                    name=sym.name,
                    code=sym.code if include_code else "",
                    file=rel_file,
                    line_start=sym.line,  # ExtractedSymbol uses 'line' not 'line_start'
                    line_end=sym.end_line or 0,  # ExtractedSymbol uses 'end_line'
                    dependencies=list(sym.dependencies),
                    depth=sym.depth,
                    confidence=sym.confidence,
                    low_confidence=sym.confidence < LOW_CONFIDENCE_THRESHOLD,
                )
            )
            if include_code:
                combined_parts.append(f"# From {rel_file}")
                combined_parts.append(sym.code)

        combined_code = "\n\n".join(combined_parts) if include_code else ""

        # Use the extractor's combined code if available (includes proper ordering)
        if include_code and extraction_result.combined_code:
            combined_code = extraction_result.combined_code

        # Get unresolved imports from extraction result
        unresolved_imports = (
            extraction_result.module_imports
        )  # These are imports that couldn't be resolved

        # Build import graph dict (file -> list of imported files)
        # Uses resolver.imports which is Dict[module_name, List[ImportInfo]]
        import_graph = {}
        for module_name, imports in resolver.imports.items():
            # Get file path for this module
            if module_name in resolver.module_to_file:
                file_path = resolver.module_to_file[module_name]
                rel_path = (
                    str(Path(file_path).relative_to(root_path))
                    if Path(file_path).is_absolute()
                    else file_path
                )
            else:
                rel_path = module_name.replace(".", "/") + ".py"  # Best guess

            imported_files = []
            for imp in imports:
                # Try to resolve module to file using module_to_file mapping
                if imp.module in resolver.module_to_file:
                    resolved_file = resolver.module_to_file[imp.module]
                    resolved_rel = (
                        str(Path(resolved_file).relative_to(root_path))
                        if Path(resolved_file).is_absolute()
                        else resolved_file
                    )
                    if resolved_rel not in imported_files:
                        imported_files.append(resolved_rel)
            if imported_files:
                import_graph[rel_path] = imported_files

        # Detect circular imports using get_circular_imports()
        circular_import_objs = resolver.get_circular_imports()
        circular_import_lists = [
            ci.cycle for ci in circular_import_objs
        ]  # CircularImport uses 'cycle'

        # Generate Mermaid diagram
        mermaid = ""
        if include_diagram:
            mermaid = resolver.generate_mermaid()

        # Calculate token estimate (rough: 4 chars per token)
        token_estimate = len(combined_code) // 4 if combined_code else 0

        # Make target file relative
        target_rel = (
            str(target_path.relative_to(root_path))
            if target_path.is_absolute()
            else target_file
        )

        # [20251216_FEATURE] v2.5.0 - Build low confidence warning if needed
        low_confidence_warning = None
        if extraction_result.low_confidence_count > 0:
            low_conf_names = [
                s.name for s in extraction_result.get_low_confidence_symbols()[:5]
            ]
            low_confidence_warning = (
                f"⚠️ {extraction_result.low_confidence_count} symbol(s) have low confidence "
                f"(below 0.5): {', '.join(low_conf_names)}"
                + ("..." if extraction_result.low_confidence_count > 5 else "")
            )

        return CrossFileDependenciesResult(
            success=True,
            target_name=target_symbol,
            target_file=target_rel,
            extracted_symbols=extracted_symbols,
            total_dependencies=len(extracted_symbols) - 1,  # Exclude target itself
            unresolved_imports=unresolved_imports,  # Use local variable set from module_imports
            import_graph=import_graph,
            circular_imports=circular_import_lists,
            combined_code=combined_code,
            token_estimate=token_estimate,
            mermaid=mermaid,
            # [20251216_FEATURE] v2.5.0 - Confidence decay fields
            confidence_decay_factor=confidence_decay_factor,
            low_confidence_count=extraction_result.low_confidence_count,
            low_confidence_warning=low_confidence_warning,
        )

    except Exception as e:
        return CrossFileDependenciesResult(
            success=False,
            error=f"Cross-file dependency analysis failed: {str(e)}",
        )


@mcp.tool()
async def get_cross_file_dependencies(
    target_file: str,
    target_symbol: str,
    project_root: str | None = None,
    max_depth: int = 3,
    include_code: bool = True,
    include_diagram: bool = True,
    confidence_decay_factor: float = 0.9,
) -> CrossFileDependenciesResult:
    """
    Analyze and extract cross-file dependencies for a symbol.

    [v2.5.0] Use this tool to understand all dependencies a function/class needs
    from other files in the project. It recursively resolves imports and extracts
    the complete dependency chain with source code.

    **Confidence Decay (v2.5.0):**
    Deep dependency chains get exponentially decaying confidence scores.
    Formula: C_effective = 1.0 × confidence_decay_factor^depth

    | Depth | Confidence (factor=0.9) |
    |-------|------------------------|
    | 0     | 1.000 (target)         |
    | 1     | 0.900                  |
    | 2     | 0.810                  |
    | 5     | 0.590                  |
    | 10    | 0.349                  |

    Symbols with confidence < 0.5 are flagged as "low confidence".

    Key capabilities:
    - Resolve imports to their source files
    - Extract code for all dependent symbols
    - Detect circular import cycles
    - Generate import relationship diagrams
    - Provide combined code block ready for AI analysis
    - **Confidence scoring** for each symbol based on depth

    Why AI agents need this:
    - Complete Context: Get all code needed to understand a function
    - Safe Refactoring: Know what depends on what before making changes
    - Debugging: Trace data flow across file boundaries
    - Code Review: Understand the full impact of changes
    - **Honest Uncertainty**: Know when deep dependencies may be unreliable

    Example:
        # Analyze 'process_order' function in 'services/order.py'
        result = get_cross_file_dependencies(
            target_file="services/order.py",
            target_symbol="process_order",
            max_depth=5,
            confidence_decay_factor=0.9
        )
        # Check for low-confidence symbols
        if result.low_confidence_count > 0:
            print(f"Warning: {result.low_confidence_warning}")

    Args:
        target_file: Path to file containing the target symbol (relative to project root)
        target_symbol: Name of the function or class to analyze
        project_root: Project root directory (default: server's project root)
        max_depth: Maximum depth of dependency resolution (default: 3)
        include_code: Include full source code in result (default: True)
        include_diagram: Include Mermaid diagram of imports (default: True)
        confidence_decay_factor: Decay factor per depth level (default: 0.9).
                                 Lower values = faster decay. Range: 0.0-1.0

    Returns:
        CrossFileDependenciesResult with extracted symbols, dependency graph, combined code,
        and confidence scores for each symbol
    """
    return await asyncio.to_thread(
        _get_cross_file_dependencies_sync,
        project_root,
        target_file,
        target_symbol,
        max_depth,
        include_code,
        include_diagram,
        confidence_decay_factor,
    )


# ============================================================================
# [20251213_FEATURE] v1.5.1 - cross_file_security_scan MCP Tool
# ============================================================================


class TaintFlowModel(BaseModel):
    """Model for a taint flow across files."""

    source_function: str = Field(description="Function where taint originates")
    source_file: str = Field(description="File containing taint source")
    source_line: int = Field(default=0, description="Line number of taint source")
    sink_function: str = Field(description="Function where taint reaches sink")
    sink_file: str = Field(description="File containing sink")
    sink_line: int = Field(default=0, description="Line number of sink")
    flow_path: list[str] = Field(
        default_factory=list, description="Path: file:function -> file:function"
    )
    taint_type: str = Field(description="Type of taint source (e.g., 'request_input')")


class CrossFileVulnerabilityModel(BaseModel):
    """Model for a cross-file vulnerability."""

    type: str = Field(description="Vulnerability type (e.g., 'SQL Injection')")
    cwe: str = Field(description="CWE identifier")
    severity: str = Field(description="Severity: low, medium, high, critical")
    source_file: str = Field(description="File where taint originates")
    sink_file: str = Field(description="File where vulnerability manifests")
    description: str = Field(description="Human-readable description")
    flow: TaintFlowModel = Field(
        description="The taint flow that causes this vulnerability"
    )


class CrossFileSecurityResult(BaseModel):
    """Result of cross-file security analysis."""

    success: bool = Field(description="Whether analysis succeeded")
    server_version: str = Field(default=__version__, description="Code Scalpel version")

    # Summary
    files_analyzed: int = Field(default=0, description="Number of files analyzed")
    has_vulnerabilities: bool = Field(
        default=False, description="Whether vulnerabilities were found"
    )
    vulnerability_count: int = Field(
        default=0, description="Total vulnerabilities found"
    )
    risk_level: str = Field(default="low", description="Overall risk level")

    # Detailed findings
    vulnerabilities: list[CrossFileVulnerabilityModel] = Field(
        default_factory=list, description="Cross-file vulnerabilities found"
    )
    taint_flows: list[TaintFlowModel] = Field(
        default_factory=list, description="All taint flows detected"
    )

    # Entry points and sinks
    taint_sources: list[str] = Field(
        default_factory=list, description="Functions containing taint sources"
    )
    dangerous_sinks: list[str] = Field(
        default_factory=list, description="Functions containing dangerous sinks"
    )

    # Visualization
    mermaid: str = Field(default="", description="Mermaid diagram of taint flows")

    error: str | None = Field(default=None, description="Error message if failed")


def _cross_file_security_scan_sync(
    project_root: str | None,
    entry_points: list[str] | None,
    max_depth: int,
    include_diagram: bool,
) -> CrossFileSecurityResult:
    """Synchronous implementation of cross_file_security_scan."""
    from code_scalpel.symbolic_execution_tools.cross_file_taint import (
        CrossFileTaintTracker,
    )

    root_path = Path(project_root) if project_root else PROJECT_ROOT

    if not root_path.exists():
        return CrossFileSecurityResult(
            success=False,
            error=f"Project root not found: {root_path}",
        )

    try:
        tracker = CrossFileTaintTracker(root_path)
        result = tracker.analyze(entry_points=entry_points, max_depth=max_depth)

        # Helper to get file path from module name
        def get_file_for_module(module: str) -> str:
            """Get file path for a module, falling back to module name if not found."""
            file_path = tracker.resolver.module_to_file.get(module, module)
            if isinstance(file_path, Path):
                file_path = str(file_path)
            # Make relative if absolute
            try:
                p = Path(file_path)
                if p.is_absolute():
                    return str(p.relative_to(root_path))
            except (ValueError, TypeError):
                pass
            return file_path

        # Convert vulnerabilities to models
        vulnerabilities = []
        for vuln in result.vulnerabilities:
            # [20251215_BUGFIX] v2.0.1 - Use source_module not source_file
            source_file = get_file_for_module(vuln.flow.source_module)
            sink_file = get_file_for_module(vuln.flow.sink_module)

            flow_model = TaintFlowModel(
                source_function=vuln.flow.source_function,
                source_file=source_file,
                source_line=vuln.flow.source_line,
                sink_function=vuln.flow.sink_function,
                sink_file=sink_file,
                sink_line=vuln.flow.sink_line,
                flow_path=[
                    f"{get_file_for_module(m)}:{f}" for m, f, _ in vuln.flow.flow_path
                ],
                taint_type=str(
                    vuln.flow.sink_type.name
                    if hasattr(vuln.flow.sink_type, "name")
                    else vuln.flow.sink_type
                ),
            )
            vulnerabilities.append(
                CrossFileVulnerabilityModel(
                    type=vuln.vulnerability_type,
                    cwe=vuln.cwe_id,
                    severity=vuln.severity,
                    source_file=source_file,
                    sink_file=sink_file,
                    description=vuln.description,
                    flow=flow_model,
                )
            )

        # Convert taint flows to models
        taint_flows = []
        for flow in result.taint_flows:
            # [20251215_BUGFIX] v2.0.1 - Use source_module not source_file
            source_file = get_file_for_module(flow.source_module)
            sink_file = get_file_for_module(flow.sink_module)

            taint_flows.append(
                TaintFlowModel(
                    source_function=flow.source_function,
                    source_file=source_file,
                    source_line=flow.source_line,
                    sink_function=flow.sink_function,
                    sink_file=sink_file,
                    sink_line=flow.sink_line,
                    flow_path=[
                        f"{get_file_for_module(m)}:{f}" for m, f, _ in flow.flow_path
                    ],
                    taint_type=str(
                        flow.sink_type.name
                        if hasattr(flow.sink_type, "name")
                        else flow.sink_type
                    ),
                )
            )

        # Determine risk level
        vuln_count = len(vulnerabilities)
        if vuln_count == 0:
            risk_level = "low"
        elif vuln_count <= 2:
            risk_level = "medium"
        elif vuln_count <= 5:
            risk_level = "high"
        else:
            risk_level = "critical"

        # Generate Mermaid diagram
        mermaid = ""
        if include_diagram:
            mermaid = tracker.get_taint_graph_mermaid()

        # Extract taint sources from tracker's internal state
        taint_sources = []
        dangerous_sinks = []

        # Get taint sources if available
        if hasattr(tracker, "module_taint_sources"):
            for module, sources in tracker.module_taint_sources.items():
                for src in sources:
                    taint_sources.append(f"{module}:{src.function}")

        # Get sinks from taint flows
        for flow in result.taint_flows:
            sink_key = f"{flow.sink_function}"
            if sink_key not in dangerous_sinks:
                dangerous_sinks.append(sink_key)

        return CrossFileSecurityResult(
            success=True,
            files_analyzed=result.modules_analyzed,  # Use modules_analyzed
            has_vulnerabilities=vuln_count > 0,
            vulnerability_count=vuln_count,
            risk_level=risk_level,
            vulnerabilities=vulnerabilities,
            taint_flows=taint_flows,
            taint_sources=taint_sources,
            dangerous_sinks=dangerous_sinks,
            mermaid=mermaid,
        )

    except Exception as e:
        return CrossFileSecurityResult(
            success=False,
            error=f"Cross-file security analysis failed: {str(e)}",
        )


@mcp.tool()
async def cross_file_security_scan(
    project_root: str | None = None,
    entry_points: list[str] | None = None,
    max_depth: int = 5,
    include_diagram: bool = True,
    ctx: Context | None = None,
) -> CrossFileSecurityResult:
    """
    Perform cross-file security analysis tracking taint flow across module boundaries.

    [v1.5.1] Use this tool to detect vulnerabilities where tainted data crosses
    file boundaries before reaching a dangerous sink. This catches security
    issues that single-file analysis would miss.

    [20251215_FEATURE] v2.0.0 - Progress reporting for long-running operations.
    Reports progress during file discovery and taint analysis phases.

    Key capabilities:
    - Track taint flow through function calls across files
    - Detect vulnerabilities where source and sink are in different files
    - Identify all taint entry points (web inputs, file reads, etc.)
    - Map dangerous sinks (SQL execution, command execution, etc.)
    - Generate taint flow diagrams

    Detects cross-file patterns like:
    - User input in routes.py -> SQL execution in db.py (SQL Injection)
    - Request data in views.py -> os.system() in utils.py (Command Injection)
    - Form input in handlers.py -> open() in storage.py (Path Traversal)

    Why AI agents need this:
    - Defense in depth: Find vulnerabilities that span multiple files
    - Architecture review: Understand how untrusted data flows through the app
    - Code audit: Generate security reports for compliance
    - Risk assessment: Identify highest-risk code paths

    Args:
        project_root: Project root directory (default: server's project root)
        entry_points: Optional list of entry point functions to start from
                     (e.g., ["app.py:main", "routes.py:index"])
                     If None, analyzes all detected entry points
        max_depth: Maximum call depth to trace (default: 5)
        include_diagram: Include Mermaid diagram of taint flows (default: True)

    Returns:
        CrossFileSecurityResult with vulnerabilities, taint flows, and risk assessment
    """
    # [20251215_FEATURE] v2.0.0 - Progress token support
    # Report initial progress (discovery phase)
    if ctx:
        await ctx.report_progress(progress=0, total=100)

    result = await asyncio.to_thread(
        _cross_file_security_scan_sync,
        project_root,
        entry_points,
        max_depth,
        include_diagram,
    )

    # Report completion
    if ctx:
        await ctx.report_progress(progress=100, total=100)

    return result


# ============================================================================
# PATH VALIDATION (v1.5.3)
# ============================================================================


class PathValidationResult(BaseModel):
    """Result of path validation."""

    success: bool = Field(description="Whether all paths were accessible")
    accessible: list[str] = Field(
        default_factory=list, description="Paths that were successfully resolved"
    )
    inaccessible: list[str] = Field(
        default_factory=list, description="Paths that could not be resolved"
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Suggestions for resolving inaccessible paths"
    )
    workspace_roots: list[str] = Field(
        default_factory=list, description="Detected workspace root directories"
    )
    is_docker: bool = Field(
        default=False, description="Whether running in Docker container"
    )


def _validate_paths_sync(
    paths: list[str], project_root: str | None
) -> PathValidationResult:
    """Synchronous implementation of validate_paths."""
    from code_scalpel.mcp.path_resolver import PathResolver

    resolver = PathResolver()
    accessible, inaccessible = resolver.validate_paths(paths, project_root)

    suggestions = []
    if inaccessible:
        if resolver.is_docker:
            suggestions.append(
                "Running in Docker: Mount your project with -v /path/to/project:/workspace"
            )
            suggestions.append(
                "Example: docker run -v $(pwd):/workspace code-scalpel:latest"
            )
        else:
            suggestions.append(
                "Ensure files exist and use absolute paths or place in workspace roots:"
            )
            for root in resolver.workspace_roots[:3]:
                suggestions.append(f"  - {root}")
        suggestions.append("Set WORKSPACE_ROOT env variable to specify custom root")

    return PathValidationResult(
        success=len(inaccessible) == 0,
        accessible=accessible,
        inaccessible=inaccessible,
        suggestions=suggestions,
        workspace_roots=resolver.workspace_roots,
        is_docker=resolver.is_docker,
    )


@mcp.tool()
async def validate_paths(
    paths: list[str], project_root: str | None = None
) -> PathValidationResult:
    """
    Validate that paths are accessible before running file-based operations.

    [v1.5.3] Use this tool to check path accessibility before attempting
    file-based operations. Essential for Docker deployments where volume
    mounts must be configured correctly.

    Key capabilities:
    - Check if files are accessible from the MCP server
    - Detect Docker environment automatically
    - Provide actionable suggestions for fixing path issues
    - Report detected workspace roots
    - Generate Docker volume mount commands

    Why AI agents need this:
    - Prevent failures: Check paths before expensive operations
    - Debug deployment: Understand why paths aren't accessible
    - Guide users: Provide specific Docker mount commands
    - Environment awareness: Know if running in Docker vs local

    Common scenarios:
    - Before extract_code: Validate file exists and is accessible
    - Before crawl_project: Check project root is mounted
    - Troubleshooting: Help users configure Docker volumes

    Example:
        # Check if files are accessible
        result = validate_paths([
            "/home/user/project/main.py",
            "utils/helpers.py"
        ])

        if not result.success:
            print("Inaccessible:", result.inaccessible)
            print("Suggestions:", result.suggestions)

    Args:
        paths: List of file paths to validate
        project_root: Optional explicit project root directory

    Returns:
        PathValidationResult with accessible/inaccessible paths and suggestions
    """
    return await asyncio.to_thread(_validate_paths_sync, paths, project_root)


# ============================================================================
# POLICY VERIFICATION TOOL
# ============================================================================


# [20250108_FEATURE] v2.5.0 Guardian - Policy verification models
class PolicyVerificationResult(BaseModel):
    """Result of cryptographic policy verification."""

    success: bool = Field(description="Whether all policy files verified successfully")
    manifest_valid: bool = Field(
        default=False, description="Whether manifest signature is valid"
    )
    files_verified: int = Field(
        default=0, description="Number of files successfully verified"
    )
    files_failed: list[str] = Field(
        default_factory=list, description="List of files that failed verification"
    )
    error: str | None = Field(
        default=None, description="Error message if verification failed"
    )
    manifest_source: str | None = Field(
        default=None, description="Source of the policy manifest"
    )
    policy_dir: str | None = Field(
        default=None, description="Policy directory that was verified"
    )


def _verify_policy_integrity_sync(
    policy_dir: str | None = None,
    manifest_source: str = "file",
) -> PolicyVerificationResult:
    """
    Synchronous implementation of policy integrity verification.

    [20250108_FEATURE] v2.5.0 Guardian - Cryptographic verification
    """
    try:
        from code_scalpel.policy_engine import (
            CryptographicPolicyVerifier,
            SecurityError,
        )

        dir_path = policy_dir or ".code-scalpel"

        verifier = CryptographicPolicyVerifier(
            manifest_source=manifest_source,
            policy_dir=dir_path,
        )

        result = verifier.verify_all_policies()

        return PolicyVerificationResult(
            success=result.success,
            manifest_valid=result.manifest_valid,
            files_verified=result.files_verified,
            files_failed=result.files_failed,
            error=result.error,
            manifest_source=manifest_source,
            policy_dir=dir_path,
        )

    except SecurityError as e:
        return PolicyVerificationResult(
            success=False,
            error=str(e),
            manifest_source=manifest_source,
            policy_dir=policy_dir,
        )
    except Exception as e:
        return PolicyVerificationResult(
            success=False,
            error=f"Verification failed: {e}",
            manifest_source=manifest_source,
            policy_dir=policy_dir,
        )


@mcp.tool()
async def verify_policy_integrity(
    policy_dir: str | None = None,
    manifest_source: str = "file",
) -> PolicyVerificationResult:
    """
    Verify policy file integrity using cryptographic signatures.

    [v2.5.0] Use this tool to verify that policy files have not been tampered
    with since they were signed. This is essential for tamper-resistant
    governance in enterprise deployments.

    **Security Model: FAIL CLOSED**
    - Missing manifest → DENY ALL
    - Invalid signature → DENY ALL
    - Hash mismatch → DENY ALL

    **How it works:**
    1. Load policy manifest from configured source (git, env, file)
    2. Verify HMAC-SHA256 signature using secret key
    3. Verify SHA-256 hash of each policy file matches manifest
    4. Any failure results in security error

    **Bypass Prevention:**
    This addresses the 3rd party review feedback that file permissions
    (chmod 0444) can be bypassed. Even if an agent runs `chmod +w` and
    modifies a policy file, the hash verification will detect the change.

    Key capabilities:
    - Verify manifest signature integrity
    - Detect tampered policy files
    - Detect missing policy files
    - Report detailed verification status
    - Fail closed on any error

    Why AI agents need this:
    - **Trust Verification:** Confirm policies haven't been modified
    - **Audit Trail:** Verify policy integrity before operations
    - **Security Compliance:** Meet enterprise security requirements

    Example:
        # Verify policy integrity before operations
        result = verify_policy_integrity(policy_dir=".code-scalpel")

        if not result.success:
            print(f"SECURITY: {result.error}")
            # Fail closed - do not proceed
        else:
            print(f"Verified {result.files_verified} policy files")

    Args:
        policy_dir: Directory containing policy files (default: .code-scalpel)
        manifest_source: Where to load manifest from - "git", "env", or "file"
            - "git": Load from committed version in git history (most secure)
            - "env": Load from SCALPEL_POLICY_MANIFEST environment variable
            - "file": Load from local policy.manifest.json file

    Returns:
        PolicyVerificationResult with verification status and details

    Note:
        Requires SCALPEL_MANIFEST_SECRET environment variable to be set.
        This secret should be managed by administrators, not agents.
    """
    return await asyncio.to_thread(
        _verify_policy_integrity_sync, policy_dir, manifest_source
    )


# ============================================================================
# ENTRYPOINT
# ============================================================================


def run_server(
    transport: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 8080,
    allow_lan: bool = False,
    root_path: str | None = None,
    ssl_certfile: str | None = None,
    ssl_keyfile: str | None = None,
):
    """
    Run the Code Scalpel MCP server.

    Args:
        transport: Transport type - "stdio" or "streamable-http"
        host: Host to bind to (HTTP only)
        port: Port to bind to (HTTP only)
        allow_lan: Allow connections from LAN (disables host validation)
        root_path: Project root directory (default: current directory)
        ssl_certfile: Path to SSL certificate file for HTTPS (optional)
        ssl_keyfile: Path to SSL private key file for HTTPS (optional)

    Security Note:
        By default, the HTTP transport only allows connections from localhost.
        Use --allow-lan to enable LAN access. This disables DNS rebinding
        protection and allows connections from any host. Only use on trusted
        networks.

    HTTPS Note:
        [20251215_FEATURE] For production deployments (especially with Claude API),
        provide ssl_certfile and ssl_keyfile to enable HTTPS. Both must be specified
        for HTTPS to be enabled.
    """
    # [20251215_BUGFIX] Configure logging to stderr before anything else
    _configure_logging(transport)

    global PROJECT_ROOT
    if root_path:
        PROJECT_ROOT = Path(root_path).resolve()
        if not PROJECT_ROOT.exists():
            # Use stderr for warnings to avoid corrupting stdio transport
            print(
                f"Warning: Root path {PROJECT_ROOT} does not exist. Using current directory.",
                file=sys.stderr,
            )
            PROJECT_ROOT = Path.cwd()

    # [20251215_BUGFIX] Print to stderr for stdio transport
    output = sys.stderr if transport == "stdio" else sys.stdout
    print(f"Code Scalpel MCP Server v{__version__}", file=output)
    print(f"Project Root: {PROJECT_ROOT}", file=output)

    # [20251215_FEATURE] SSL/HTTPS support for production deployments
    use_https = ssl_certfile and ssl_keyfile
    if use_https:
        print(f"SSL/TLS: ENABLED (cert: {ssl_certfile})", file=output)
    else:
        if transport in ("streamable-http", "sse"):
            print(
                "SSL/TLS: DISABLED (use --ssl-cert and --ssl-key for HTTPS)",
                file=output,
            )

    if transport == "streamable-http" or transport == "sse":
        from mcp.server.transport_security import TransportSecuritySettings

        mcp.settings.host = host
        mcp.settings.port = port

        # [20251215_FEATURE] Configure SSL if certificates provided
        if use_https:
            mcp.settings.ssl_certfile = ssl_certfile
            mcp.settings.ssl_keyfile = ssl_keyfile
            protocol = "https"
        else:
            protocol = "http"

        if allow_lan or host == "0.0.0.0":  # nosec B104
            # [20251218_SECURITY] Intentional LAN binding for server functionality (B104)
            # Disable host validation for LAN access
            # WARNING: Only use on trusted networks!
            mcp.settings.transport_security = TransportSecuritySettings(
                enable_dns_rebinding_protection=False,
                allowed_hosts=["*"],
                allowed_origins=["*"],
            )
            print("WARNING: LAN access enabled. Host validation disabled.", file=output)
            print("Only use on trusted networks!", file=output)

        print(f"MCP endpoint: {protocol}://{host}:{port}/sse", file=output)

        # [20251215_FEATURE] Register HTTP health endpoint for Docker health checks
        _register_http_health_endpoint(mcp, host, port, ssl_certfile, ssl_keyfile)

        mcp.run(transport=transport)
    else:
        mcp.run()


def _register_http_health_endpoint(
    mcp_instance,
    host: str,
    port: int,
    ssl_certfile: str | None = None,
    ssl_keyfile: str | None = None,
):
    """
    Register a simple HTTP/HTTPS /health endpoint for Docker health checks.

    [20251215_FEATURE] v2.0.0 - HTTP health endpoint that returns immediately.
    [20251215_FEATURE] HTTPS support for production deployments.

    This endpoint is separate from the MCP protocol and provides a simple
    200 OK response for container orchestration health checks.
    """
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json

    use_https = ssl_certfile and ssl_keyfile

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = json.dumps(
                    {
                        "status": "healthy",
                        "version": __version__,
                        "transport": "https" if use_https else "http",
                    }
                )
                self.wfile.write(response.encode())
            else:
                # Let other paths fall through to MCP handler
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            # Suppress HTTP access logs to stderr
            pass

    def run_health_server():
        # Run on a different port (health_port = mcp_port + 1)
        health_port = port + 1
        try:
            server = HTTPServer((host, health_port), HealthHandler)

            # [20251215_FEATURE] Wrap with SSL if certificates provided
            if use_https:
                import ssl

                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(ssl_certfile, ssl_keyfile)
                server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
                protocol = "https"
            else:
                protocol = "http"

            logger.info(
                f"Health endpoint available at {protocol}://{host}:{health_port}/health"
            )
            server.serve_forever()
        except Exception as e:
            logger.warning(f"Could not start health server: {e}")

    # Start health server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Code Scalpel MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (HTTP only, default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind to (HTTP only, default: 8080)",
    )
    parser.add_argument(
        "--allow-lan",
        action="store_true",
        help="Allow LAN connections (disables host validation, use on trusted networks only)",
    )
    parser.add_argument(
        "--root",
        help="Project root directory for resources (default: current directory)",
    )
    # [20251215_FEATURE] SSL/TLS support for HTTPS
    parser.add_argument(
        "--ssl-cert",
        help="Path to SSL certificate file for HTTPS (required for production/Claude)",
    )
    parser.add_argument(
        "--ssl-key",
        help="Path to SSL private key file for HTTPS (required for production/Claude)",
    )

    args = parser.parse_args()
    run_server(
        transport=args.transport,
        host=args.host,
        port=args.port,
        allow_lan=args.allow_lan,
        root_path=args.root,
        ssl_certfile=args.ssl_cert,
        ssl_keyfile=args.ssl_key,
    )
