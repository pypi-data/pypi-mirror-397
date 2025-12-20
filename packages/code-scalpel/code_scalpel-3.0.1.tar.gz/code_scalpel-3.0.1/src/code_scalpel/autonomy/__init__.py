"""
[20251217_FEATURE] Autonomy module - v3.0.0 autonomous code repair features.

This module provides supervised autonomous code repair capabilities with
safety guarantees:

1. Error-to-Diff Engine: Converts error messages to actionable fix hints
   with confidence scoring and human review flagging.

2. Fix Loop Termination: Prevents infinite retry loops with hard limits,
   timeouts, and repeated error detection.

3. Mutation Test Gate: Prevents "hollow fixes" where tests pass because
   functionality was deleted, not because the bug was fixed.

4. Audit Trail: Cryptographically-hashed immutable audit log of all
   autonomous operations for compliance and debugging.

5. Framework Integrations: LangGraph state machines, CrewAI tools,
   and AutoGen function schemas for multi-agent workflows.

6. Sandboxed Execution: Speculative execution in isolated temp directories
   with automatic cleanup, resource limits, and side effect detection.

Features:
- Multi-language error parsing (Python, TypeScript, Java)
- Confidence-scored fix generation
- Bounded fix attempts with timeout
- Repeated error detection
- Human escalation on failure
- Full audit trail with SHA-256 hashing
- Hollow fix detection via mutation testing
- Speculative execution in isolated sandbox
- LangGraph, CrewAI, AutoGen integrations

Usage:
    from code_scalpel.autonomy import (
        ErrorToDiffEngine,
        ErrorAnalysis,
        FixLoop,
        MutationTestGate,
        AutonomyAuditTrail,
        SandboxExecutor,
    )

References:
- DEVELOPMENT_ROADMAP.md: v3.0.0 Autonomy specifications
- docs/: Architecture and design documentation
"""

# [20251217_FEATURE] Error-to-Diff Engine (primary exports)
from code_scalpel.autonomy.error_to_diff import (
    ErrorType,
    FixHint,
    ErrorAnalysis,
    ErrorToDiffEngine,
    ParsedError,
)

# [20251217_FEATURE] Fix Loop Termination
from code_scalpel.autonomy.fix_loop import (
    FixLoop,
    FixLoopResult,
    FixAttempt,
)

# [20251217_FEATURE] Mutation Test Gate
from code_scalpel.autonomy.mutation_gate import (
    MutationTestGate,
    MutationGateResult,
    MutationResult,
    Mutation,
    MutationType,
)

# [20251217_FEATURE] Audit Trail
from code_scalpel.autonomy.audit import (
    AuditEntry,
    AutonomyAuditTrail,
)

# [20251217_FEATURE] Sandboxed Execution
from code_scalpel.autonomy.sandbox import (
    SandboxExecutor as SandboxExecutorImpl,
    SandboxResult as SandboxResultImpl,
    FileChange,
    ExecutionTestResult,
    LintResult,
)

# [20251217_FEATURE] Stubs for external implementations (aliased to avoid conflicts)
from code_scalpel.autonomy.stubs import (
    ErrorAnalysis as StubErrorAnalysis,
    FixHint as StubFixHint,
    FileChange as StubFileChange,
    ExecutionTestResult as StubExecutionTestResult,
    SandboxResult as StubSandboxResult,
    SandboxExecutor as StubSandboxExecutor,
    ErrorToDiffEngine as StubErrorToDiffEngine,
)

__all__ = [
    # Error-to-Diff Engine (primary)
    "ErrorType",
    "FixHint",
    "ErrorAnalysis",
    "ErrorToDiffEngine",
    "ParsedError",
    # Fix Loop
    "FixLoop",
    "FixLoopResult",
    "FixAttempt",
    # Mutation Gate
    "MutationTestGate",
    "MutationGateResult",
    "MutationResult",
    "Mutation",
    "MutationType",
    # Audit Trail
    "AuditEntry",
    "AutonomyAuditTrail",
    # Sandbox (implementation)
    "SandboxExecutorImpl",
    "SandboxResultImpl",
    "FileChange",
    "ExecutionTestResult",
    "LintResult",
    # Stubs (for fix_loop/mutation_gate internal use)
    "StubErrorAnalysis",
    "StubFixHint",
    "StubFileChange",
    "StubExecutionTestResult",
    "StubSandboxResult",
    "StubSandboxExecutor",
    "StubErrorToDiffEngine",
]

# [20251217_FEATURE] Version indicator for autonomy module
__version__ = "3.0.0"
