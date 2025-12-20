"""
Policy Engine - Enterprise Governance for AI Agents.

[20251216_FEATURE] v2.5.0 Guardian - Policy-as-Code enforcement using OPA/Rego

This module provides declarative policy enforcement using Open Policy Agent's
Rego language for enterprise governance. It enables organizations to define
rules that agents must follow when modifying code.

Key Features:
- Declarative policy definitions in YAML
- Rego-based policy evaluation via OPA CLI
- Semantic code analysis (SQL injection, etc.)
- Fail CLOSED security model
- Human override with audit trail
- Tamper-resistant policy enforcement
- HMAC-signed audit logging
- TOTP-based human override system
- Policy file integrity verification

Example:
    from code_scalpel.policy_engine import PolicyEngine, Operation

    engine = PolicyEngine(".code-scalpel/policy.yaml")
    operation = Operation(
        type="code_edit",
        code="cursor.execute('SELECT * FROM users WHERE id=' + user_id)",
        language="python",
        file_path="app.py"
    )

    decision = engine.evaluate(operation)
    if not decision.allowed:
        print(f"Policy violation: {decision.reason}")
"""

# Policy Engine core
from .policy_engine import (
    PolicyEngine,
    Policy,
    PolicyDecision,
    PolicyViolation,
    Operation,
    OverrideDecision,
    PolicyError,
)

from .semantic_analyzer import SemanticAnalyzer

# Tamper Resistance (v2.5.0 Guardian P0)
from .tamper_resistance import TamperResistance
from .audit_log import AuditLog
from .exceptions import (
    PolicyEngineError,
    TamperDetectedError,
    PolicyModificationError,
    OverrideTimeoutError,
    InvalidOverrideCodeError,
)
from .models import HumanResponse

# [20250108_FEATURE] Cryptographic Policy Verification (v2.5.0 Guardian)
from .crypto_verify import (
    CryptographicPolicyVerifier,
    PolicyManifest,
    VerificationResult,
    SecurityError,
    verify_policy_integrity_crypto,
)

__all__ = [
    # Policy Engine core
    "PolicyEngine",
    "Policy",
    "PolicyDecision",
    "PolicyViolation",
    "Operation",
    "OverrideDecision",
    "PolicyError",
    "SemanticAnalyzer",
    # Tamper Resistance
    "TamperResistance",
    "AuditLog",
    # Cryptographic Verification (v2.5.0)
    "CryptographicPolicyVerifier",
    "PolicyManifest",
    "VerificationResult",
    "SecurityError",
    "verify_policy_integrity_crypto",
    # Exceptions
    "PolicyEngineError",
    "TamperDetectedError",
    "PolicyModificationError",
    "OverrideTimeoutError",
    "InvalidOverrideCodeError",
    # Models
    "HumanResponse",
]
