# Autonomy Module - Speculative Execution (Sandboxed)

**Last Updated:** December 17, 2025  
**Version:** v2.2.0+  
**Status:** Stable

## Overview

The autonomy module provides tools for testing proposed code changes in isolated sandbox environments before applying them to the main codebase. This enables "try before you apply" workflows that minimize risk of breaking changes.

## Features

### Core Capabilities

- **Isolated Sandbox Execution**: Creates temporary project copy with full isolation
- **Resource Limits**: Enforces CPU, memory, and disk limits
- **Network Blocking**: Disables network access by default
- **Filesystem Isolation**: Changes never affect main codebase
- **Multi-Mode Support**: Process-level or container-level isolation
- **Side Effect Detection**: Monitors for unintended side effects

### Execution Modes

1. **Process Mode** (default): Uses subprocess with resource limits
2. **Container Mode**: Full Docker container isolation (requires Docker)

## Quick Start

```python
from code_scalpel.autonomy import SandboxExecutor, FileChange

# Initialize executor
executor = SandboxExecutor(
    isolation_level="process",  # or "container"
    network_enabled=False,
    max_memory_mb=512,
    max_cpu_seconds=60
)

# Define changes to test
changes = [
    FileChange(
        relative_path="src/module.py",
        operation="modify",
        new_content="def fixed_func():\n    return 42\n"
    )
]

# Test changes in sandbox
result = executor.execute_with_changes(
    project_path="/path/to/project",
    changes=changes,
    test_command="pytest",
    lint_command="ruff check",
    build_command="python -m build"
)

# Check results
if result.success:
    print("[COMPLETE] Safe to apply changes")
else:
    print("[FAILED] Changes introduce failures")
```

## API Reference

### SandboxExecutor

Main class for executing code changes in isolated environments.

**Constructor:**
```python
SandboxExecutor(
    isolation_level: str = "process",  # "process" or "container"
    network_enabled: bool = False,
    max_memory_mb: int = 512,
    max_cpu_seconds: int = 60,
    max_disk_mb: int = 100
)
```

**Methods:**
- `execute_with_changes()`: Apply changes and run tests in sandbox

### FileChange

Represents a file modification to apply in sandbox.

```python
FileChange(
    relative_path: str,      # Path relative to project root
    operation: str,          # "create", "modify", or "delete"
    new_content: str | None  # New file content (for create/modify)
)
```

### SandboxResult

Result of sandbox execution.

**Attributes:**
- `success: bool` - Overall success status
- `build_success: bool` - Build command success
- `test_results: list[ExecutionTestResult]` - Test execution results
- `lint_results: list[LintResult]` - Linter findings
- `side_effects_detected: bool` - Side effect detection status
- `execution_time_ms: int` - Total execution time
- `stdout: str` - Standard output
- `stderr: str` - Standard error

## Security Guarantees

The sandbox provides multiple layers of security:

1. **Filesystem Isolation**: All changes occur in temporary directory
2. **Network Blocking**: Network access disabled by default (configurable)
3. **Resource Limits**: CPU, memory, and disk quotas enforced
4. **Process Isolation**: Subprocesses cannot affect parent
5. **Side Effect Detection**: Monitors for blocked operations

## Examples

See `examples/sandbox_example.py` for a complete working example.

## Testing

Run tests:
```bash
pytest tests/test_sandbox.py -v
```

Coverage: 100% (32 tests, all passing)

## Change Tags

All code includes `[20251217_FEATURE]` tags indicating the implementation date and type.

## Integration

The autonomy module integrates with:
- Project analysis tools (project_crawler.py)
- Security analysis (policy module)
- Symbolic execution tools
- MCP server (future)

## Known Limitations

1. **Container Mode**: Requires Docker installation
2. **Resource Limits**: Linux/Unix only (Windows has limited support)
3. **Side Effect Detection**: Best-effort monitoring
4. **Test Parsing**: Currently simple pattern matching (can be enhanced)

## Future Enhancements

Planned for v3.0.0 "Autonomy":
- Enhanced test result parsing
- Integration with error-to-diff system
- Automatic fix suggestion
- Caching for repeated executions
- Multi-language project support

## Contributing

When adding features:
1. Add comprehensive tests (maintain 100% coverage)
2. Use `[YYYYMMDD_TYPE]` change tags
3. Follow existing code style (black + ruff)
4. Update this README

## License

Part of Code Scalpel, MIT License.
