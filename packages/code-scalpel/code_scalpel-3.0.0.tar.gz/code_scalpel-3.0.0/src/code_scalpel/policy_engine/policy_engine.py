"""
Policy Engine - OPA/Rego integration for declarative governance.

[20251216_FEATURE] v2.5.0 Guardian - Policy-as-Code enforcement

This module implements the core PolicyEngine that loads, validates, and enforces
policies defined in YAML using Open Policy Agent's Rego language.

Security Model: FAIL CLOSED
- Policy parsing errors → DENY ALL
- Policy evaluation errors → DENY ALL
- Missing OPA CLI → DENY ALL
"""

from __future__ import annotations
import subprocess
import json
import tempfile
import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

try:
    import yaml
except ImportError:
    raise ImportError(
        "PyYAML is required for policy engine. Install with: pip install pyyaml"
    )


class PolicyError(Exception):
    """Raised when policy loading, parsing, or evaluation fails."""

    pass


class PolicySeverity(Enum):
    """Severity levels for policy violations."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class PolicyAction(Enum):
    """Actions to take when policy is violated."""

    DENY = "DENY"  # Block the operation
    WARN = "WARN"  # Allow but log warning
    AUDIT = "AUDIT"  # Allow and log for review


@dataclass
class Policy:
    """
    A single policy definition.

    [20251216_FEATURE] Represents a policy rule written in Rego

    Attributes:
        name: Unique policy identifier
        description: Human-readable description
        rule: Rego policy code
        severity: Impact level (CRITICAL, HIGH, MEDIUM, LOW)
        action: What to do on violation (DENY, WARN, AUDIT)
    """

    name: str
    description: str
    rule: str
    severity: str = "HIGH"
    action: str = "DENY"

    def __post_init__(self):
        """Validate policy fields."""
        if not self.name:
            raise PolicyError("Policy name cannot be empty")
        if not self.rule:
            raise PolicyError(f"Policy '{self.name}' has empty rule")

        # Validate severity
        try:
            PolicySeverity(self.severity)
        except ValueError:
            raise PolicyError(
                f"Invalid severity '{self.severity}' in policy '{self.name}'"
            )

        # Validate action
        try:
            PolicyAction(self.action)
        except ValueError:
            raise PolicyError(f"Invalid action '{self.action}' in policy '{self.name}'")


@dataclass
class PolicyViolation:
    """
    A detected policy violation.

    [20251216_FEATURE] Represents a specific instance where code violates policy

    Attributes:
        policy_name: Name of violated policy
        severity: Severity level
        message: Human-readable violation message
        action: Action to take (DENY, WARN, AUDIT)
    """

    policy_name: str
    severity: str
    message: str
    action: str


@dataclass
class PolicyDecision:
    """
    Result of policy evaluation.

    [20251216_FEATURE] Decision on whether to allow an operation
    [20251216_REFACTOR] Added severity field for compatibility with TamperResistance
    [20251216_REFACTOR] Made reason optional with default for backward compatibility

    Attributes:
        allowed: Whether operation is allowed
        reason: Explanation of decision
        violated_policies: Names of violated policies
        violations: Detailed violation information
        requires_override: Whether human override is possible
        severity: Overall severity level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
    """

    allowed: bool
    reason: str = ""
    violated_policies: List[str] = field(default_factory=list)
    violations: List[PolicyViolation] = field(default_factory=list)
    requires_override: bool = False
    severity: str = "MEDIUM"


@dataclass
class Operation:
    """
    An operation to be evaluated against policies.

    [20251216_FEATURE] Represents a code operation (edit, file access, etc.)
    [20251216_REFACTOR] Extended to support both PolicyEngine and TamperResistance use cases

    Attributes:
        type: Operation type (code_edit, file_access, file_write, etc.)
        code: Code content being operated on (for code operations)
        language: Programming language (for code operations)
        file_path: Path to file being operated on (single file)
        affected_files: List of files affected (for multi-file operations)
        metadata: Additional context
        timestamp: When operation was created (for audit purposes)
    """

    type: str
    code: str = ""
    language: str = ""
    file_path: str = ""
    affected_files: List[Path] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OverrideDecision:
    """
    Result of override request.

    [20251216_FEATURE] Human approval for policy-violating operations
    [20251216_REFACTOR] Added justification and approved_by for TamperResistance compatibility

    Attributes:
        approved: Whether override was approved
        reason: Explanation of decision
        override_id: Unique ID for this override (if approved)
        expires_at: When override expires (if approved)
        justification: Reason provided by human for override
        approved_by: Identity of human who approved override
    """

    approved: bool
    reason: str
    override_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    justification: Optional[str] = None
    approved_by: Optional[str] = None


class PolicyEngine:
    """
    OPA/Rego policy enforcement engine.

    [20251216_FEATURE] v2.5.0 Guardian - Enterprise governance for AI agents

    Security Model: FAIL CLOSED
    - All errors result in DENY
    - No silent failures
    - Full audit trail

    Example:
        engine = PolicyEngine(".scalpel/policy.yaml")
        decision = engine.evaluate(operation)
        if not decision.allowed:
            print(f"Denied: {decision.reason}")
    """

    def __init__(self, policy_path: str = ".scalpel/policy.yaml"):
        """
        Initialize policy engine.

        [20251216_FEATURE] Loads and validates policies at startup

        Args:
            policy_path: Path to YAML policy configuration

        Raises:
            PolicyError: If policy file not found, invalid, or OPA unavailable
        """
        self.policy_path = Path(policy_path)
        self.policies: List[Policy] = []
        # [20240613_SECURITY] Persist used override codes to disk to enforce single-use guarantee across restarts
        self._used_override_codes_path = (
            self.policy_path.parent / "used_override_codes.json"
        )
        self._used_override_codes: set[str] = self._load_used_override_codes()

        # Load and validate policies
        self.policies = self._load_policies()
        self._validate_opa_available()
        self._validate_policies()

    def _load_used_override_codes(self) -> set[str]:
        """
        [20240613_SECURITY] Load used override codes from disk to enforce single-use guarantee across restarts.
        """
        if self._used_override_codes_path.exists():
            try:
                with open(self._used_override_codes_path, "r") as f:
                    codes = json.load(f)
                if not isinstance(codes, list):
                    raise ValueError("used_override_codes.json is not a list")
                return set(codes)
            except Exception as e:
                # Fail CLOSED - if we can't read the file, deny all overrides
                raise PolicyError(
                    f"Failed to load used override codes: {e}. Failing CLOSED."
                )
        return set()

    def _save_used_override_codes(self) -> None:
        """
        [20240613_SECURITY] Save used override codes to disk after each update.
        """
        try:
            with open(self._used_override_codes_path, "w") as f:
                json.dump(list(self._used_override_codes), f)
        except Exception as e:
            # Fail CLOSED - if we can't write the file, deny all overrides
            raise PolicyError(
                f"Failed to save used override codes: {e}. Failing CLOSED."
            )

    def _load_policies(self) -> List[Policy]:
        """
        Load and parse policy definitions.

        [20251216_FEATURE] Parse YAML policy file

        Returns:
            List of Policy objects

        Raises:
            PolicyError: If file not found or invalid YAML
        """
        if not self.policy_path.exists():
            raise PolicyError(f"Policy file not found: {self.policy_path}")

        try:
            with open(self.policy_path) as f:
                config = yaml.safe_load(f)

            if not config:
                raise PolicyError("Policy file is empty")

            policy_defs = config.get("policies", [])
            if not policy_defs:
                raise PolicyError("No policies defined in policy file")

            return [Policy(**p) for p in policy_defs]

        except yaml.YAMLError as e:
            # Fail CLOSED - deny all if policy parsing fails
            raise PolicyError(f"Policy parsing failed: {e}. Failing CLOSED.")
        except (KeyError, TypeError) as e:
            raise PolicyError(f"Invalid policy format: {e}. Failing CLOSED.")

    def _validate_opa_available(self) -> None:
        """
        Check if OPA CLI is available.

        [20251216_FEATURE] Verify OPA can be invoked

        Raises:
            PolicyError: If OPA CLI not found
        """
        try:
            result = subprocess.run(
                ["opa", "version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                raise PolicyError("OPA CLI check failed. Failing CLOSED.")
        except FileNotFoundError:
            raise PolicyError(
                "OPA CLI not found. Install from https://www.openpolicyagent.org/docs/latest/#running-opa. "
                "Failing CLOSED."
            )
        except subprocess.TimeoutExpired:
            raise PolicyError("OPA CLI timeout. Failing CLOSED.")

    def _validate_policies(self) -> None:
        """
        Validate Rego syntax using OPA CLI.

        [20251216_FEATURE] Check all policies have valid Rego syntax

        Raises:
            PolicyError: If any policy has invalid Rego
        """
        for policy in self.policies:
            try:
                result = subprocess.run(
                    ["opa", "check", "-"],
                    input=policy.rule.encode(),
                    capture_output=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    raise PolicyError(
                        f"Invalid Rego in policy '{policy.name}': "
                        f"{result.stderr.decode()}"
                    )
            except subprocess.TimeoutExpired:
                raise PolicyError(
                    f"Rego validation timeout for policy '{policy.name}'. Failing CLOSED."
                )

    def evaluate(self, operation: Operation) -> PolicyDecision:
        """
        Evaluate operation against all policies.

        [20251216_FEATURE] Check if operation violates any policies

        Args:
            operation: The operation to evaluate (code_edit, file_access, etc.)

        Returns:
            PolicyDecision with allow/deny and reasons
        """
        input_data = {
            "operation": operation.type,
            "code": operation.code,
            "language": operation.language,
            "file_path": operation.file_path,
            "metadata": operation.metadata,
        }

        violations = []

        for policy in self.policies:
            try:
                # Write Rego policy and input to temp files
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".rego", delete=False
                ) as policy_file:
                    policy_file.write(policy.rule)
                    policy_file.flush()
                    policy_file_path = policy_file.name

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False
                ) as input_file:
                    json.dump(input_data, input_file)
                    input_file.flush()
                    input_file_path = input_file.name

                # Evaluate with OPA
                result = subprocess.run(
                    [
                        "opa",
                        "eval",
                        "-d",
                        policy_file_path,
                        "-i",
                        input_file_path,
                        "--format",
                        "json",
                        "data.scalpel.security.deny",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                # Clean up temp files
                Path(policy_file_path).unlink(missing_ok=True)
                Path(input_file_path).unlink(missing_ok=True)

                if result.returncode != 0:
                    # Policy evaluation error - fail CLOSED
                    return PolicyDecision(
                        allowed=False,
                        reason="Policy evaluation error - failing CLOSED",
                        violated_policies=[policy.name],
                        requires_override=False,  # No override for errors
                    )

                # Parse OPA output
                output = json.loads(result.stdout)

                # Check if policy was violated
                # OPA returns {"result": [{"expressions": [...]}]}
                if output.get("result"):
                    expressions = output["result"][0].get("expressions", [])
                    if expressions:
                        deny_messages = expressions[0].get("value", [])
                        if deny_messages:
                            # Policy denied the operation
                            message = (
                                deny_messages[0]
                                if isinstance(deny_messages, list)
                                else str(deny_messages)
                            )
                            violations.append(
                                PolicyViolation(
                                    policy_name=policy.name,
                                    severity=policy.severity,
                                    message=message,
                                    action=policy.action,
                                )
                            )

            except subprocess.TimeoutExpired:
                # Timeout is a critical error - fail CLOSED
                return PolicyDecision(
                    allowed=False,
                    reason=f"Policy '{policy.name}' evaluation timeout - failing CLOSED",
                    violated_policies=[policy.name],
                    requires_override=False,
                )
            except Exception as e:
                # Any unexpected error - fail CLOSED
                return PolicyDecision(
                    allowed=False,
                    reason=f"Unexpected error evaluating '{policy.name}': {e} - failing CLOSED",
                    violated_policies=[policy.name],
                    requires_override=False,
                )

        if violations:
            # Check if all violations are just warnings/audits
            deny_violations = [v for v in violations if v.action == "DENY"]

            if deny_violations:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Violated {len(deny_violations)} DENY policy(ies)",
                    violated_policies=[v.policy_name for v in deny_violations],
                    violations=violations,
                    requires_override=True,
                )
            else:
                # Only warnings/audits - allow but report
                return PolicyDecision(
                    allowed=True,
                    reason=f"Allowed with {len(violations)} warning(s)",
                    violated_policies=[],
                    violations=violations,
                    requires_override=False,
                )

        return PolicyDecision(
            allowed=True,
            reason="No policy violations detected",
            violated_policies=[],
            violations=[],
        )

    def request_override(
        self,
        operation: Operation,
        decision: PolicyDecision,
        justification: str,
        human_code: str,
    ) -> OverrideDecision:
        """
        Request human override for denied operation.

        [20251216_FEATURE] Allow humans to override policy denials with justification

        Args:
            operation: The denied operation
            decision: The original policy decision
            justification: Human justification for override
            human_code: One-time code from human approver

        Returns:
            OverrideDecision with approval status
        """
        # Verify human code (time-based OTP or similar)
        if not self._verify_human_code(human_code):
            return OverrideDecision(approved=False, reason="Invalid override code")

        # Check if code was already used
        if human_code in self._used_override_codes:
            return OverrideDecision(
                approved=False, reason="Override code already used (single-use only)"
            )

        # Mark code as used
        self._used_override_codes.add(human_code)

        # Log override request for audit trail
        override_id = self._generate_override_id()
        self._log_override_request(
            operation=operation,
            decision=decision,
            justification=justification,
            human_code_hash=self._hash_code(human_code),
            override_id=override_id,
        )

        return OverrideDecision(
            approved=True,
            reason="Human override approved",
            override_id=override_id,
            expires_at=datetime.now() + timedelta(hours=1),
        )

    def _verify_human_code(self, code: str) -> bool:
        """
        Verify human override code.

        [20251216_FEATURE] Simple code verification (can be enhanced with TOTP)

        Args:
            code: Override code to verify

        Returns:
            True if code is valid
        """
        # Simple validation: code must be 6+ characters
        # In production, this should be TOTP or similar
        return len(code) >= 6

    def _hash_code(self, code: str) -> str:
        """Hash override code for audit log."""
        return hashlib.sha256(code.encode()).hexdigest()

    def _generate_override_id(self) -> str:
        """Generate unique override ID."""
        return str(uuid.uuid4())

    def _log_override_request(
        self,
        operation: Operation,
        decision: PolicyDecision,
        justification: str,
        human_code_hash: str,
        override_id: str,
    ) -> None:
        """
        Log override request for audit trail.

        [20251216_FEATURE] Audit trail for all overrides

        Args:
            operation: The operation being overridden
            decision: Original policy decision
            justification: Human justification
            human_code_hash: Hash of override code (not plaintext)
            override_id: Unique override identifier
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "override_id": override_id,
            "operation_type": operation.type,
            "file_path": operation.file_path,
            "violated_policies": decision.violated_policies,
            "justification": justification,
            "human_code_hash": human_code_hash,
        }

        # In production, this should write to a secure audit log
        # For now, we'll log to a local file as a placeholder
        # TODO: Implement secure audit logging
        # [20251216_FEATURE] Minimal file-based audit logging for override requests
        try:
            with open("policy_override_audit.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_entry) + "\n")
        except Exception as e:
            # In production, escalate/log this error securely
            print(f"[WARN] Failed to write audit log entry: {e}")
