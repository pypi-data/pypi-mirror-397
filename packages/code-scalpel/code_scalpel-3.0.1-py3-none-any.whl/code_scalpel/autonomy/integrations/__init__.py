"""
Code Scalpel Autonomy Integrations - Framework-specific integrations.

[20251217_FEATURE] Framework integrations for LangGraph, CrewAI, and AutoGen.
"""

from .langgraph import create_scalpel_fix_graph, ScalpelState
from .crewai import create_scalpel_fix_crew
from .autogen import create_scalpel_autogen_agents

__all__ = [
    "create_scalpel_fix_graph",
    "ScalpelState",
    "create_scalpel_fix_crew",
    "create_scalpel_autogen_agents",
]
