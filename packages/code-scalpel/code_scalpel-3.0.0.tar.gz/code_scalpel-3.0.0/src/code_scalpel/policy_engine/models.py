"""
Policy Engine Data Models - Additional models for Tamper Resistance.

# [20251216_FEATURE] v2.5.0 Guardian - Policy enforcement data structures

Note: Core models (Operation, PolicyDecision, OverrideDecision) are in policy_engine.py.
This module contains additional models for tamper resistance functionality.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class HumanResponse:
    """Represents a human's response to an override challenge."""

    code: str
    justification: str
    human_id: str
    timestamp: datetime = field(default_factory=datetime.now)
