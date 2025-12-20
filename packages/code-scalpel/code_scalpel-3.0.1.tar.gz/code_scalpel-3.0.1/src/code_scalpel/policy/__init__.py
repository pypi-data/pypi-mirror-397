"""
Change Budgeting and Blast Radius Control for Code Scalpel.

[20251216_FEATURE] P0 feature for limiting scope of agent modifications
to prevent runaway changes.

This module provides:
- Operation tracking (files, lines, complexity)
- Budget constraint validation
- Policy-based enforcement (default, critical files)
- Clear violation reporting with actionable feedback
"""

from .change_budget import (
    Operation,
    FileChange,
    BudgetViolation,
    BudgetDecision,
    ChangeBudget,
    load_budget_config,
)

__all__ = [
    "Operation",
    "FileChange",
    "BudgetViolation",
    "BudgetDecision",
    "ChangeBudget",
    "load_budget_config",
]
