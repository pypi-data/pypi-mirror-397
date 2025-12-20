"""
Tamper-Resistant Audit Logging.

# [20251216_FEATURE] v2.5.0 Guardian - Tamper-resistant audit trail

This module provides cryptographically-signed, append-only audit logging
to ensure all security events are recorded and verifiable.
"""

import json
import hmac
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .exceptions import TamperDetectedError


class AuditLog:
    """
    Tamper-resistant audit logging with HMAC signatures.

    # [20251216_FEATURE] v2.5.0 Guardian P0

    Features:
    - Append-only log file (no deletion or modification)
    - HMAC-SHA256 signatures for each event
    - Integrity verification
    - Tamper detection
    """

    def __init__(self, log_path: str = ".code-scalpel/audit.log"):
        """
        Initialize audit log.

        Args:
            log_path: Path to audit log file
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record_event(
        self, event_type: str, severity: str, details: Dict[str, Any]
    ) -> None:
        """
        Record security event to tamper-resistant log.

        # [20251216_FEATURE] v2.5.0 Guardian P0 - Event signing

        Uses append-only file with cryptographic signatures.

        Args:
            event_type: Type of security event
            severity: Event severity (LOW, MEDIUM, HIGH, CRITICAL)
            details: Event details dictionary
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details,
        }

        # Sign event
        signature = self._sign_event(event)
        event["signature"] = signature

        # Append to log (append-only)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(event) + "\n")

    def _sign_event(self, event: Dict[str, Any]) -> str:
        """
        Sign event with HMAC-SHA256.

        # [20251216_FEATURE] v2.5.0 Guardian P0 - HMAC signing

        Args:
            event: Event dictionary (without signature)

        Returns:
            HMAC-SHA256 signature as hex string
        """
        # Use secret key stored securely (environment variable, keyring, etc.)
        secret = os.environ.get("SCALPEL_AUDIT_SECRET", "default-secret")

        message = json.dumps(event, sort_keys=True)
        signature = hmac.new(
            secret.encode(), message.encode(), hashlib.sha256
        ).hexdigest()

        return signature

    def verify_integrity(self) -> bool:
        """
        Verify audit log has not been tampered with.

        # [20251216_FEATURE] v2.5.0 Guardian P0 - Integrity verification

        Returns:
            True if log is intact, raises TamperDetectedError if tampered

        Raises:
            TamperDetectedError: If log tampering is detected
        """
        if not self.log_path.exists():
            return True

        with open(self.log_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    event = json.loads(line)
                    signature = event.pop("signature", None)

                    if signature is None:
                        raise TamperDetectedError(
                            f"Audit log entry missing signature at line {line_num}"
                        )

                    # Verify signature
                    expected_signature = self._sign_event(event)
                    if signature != expected_signature:
                        raise TamperDetectedError(
                            f"Audit log tampering detected at timestamp: {event.get('timestamp', 'unknown')}, line {line_num}"
                        )
                except json.JSONDecodeError:
                    raise TamperDetectedError(
                        f"Audit log corrupted at line {line_num}: invalid JSON"
                    )

        return True

    def get_events(
        self, event_type: str = None, severity: str = None, limit: int = None
    ) -> list:
        """
        Retrieve events from audit log.

        Args:
            event_type: Filter by event type (optional)
            severity: Filter by severity (optional)
            limit: Maximum number of events to return (optional)

        Returns:
            List of events matching filters
        """
        if not self.log_path.exists():
            return []

        events = []
        with open(self.log_path, "r") as f:
            for line in f:
                try:
                    event = json.loads(line)

                    # Apply filters
                    if event_type and event.get("event_type") != event_type:
                        continue
                    if severity and event.get("severity") != severity:
                        continue

                    events.append(event)

                    if limit and len(events) >= limit:
                        break

                except json.JSONDecodeError:
                    continue

        return events
