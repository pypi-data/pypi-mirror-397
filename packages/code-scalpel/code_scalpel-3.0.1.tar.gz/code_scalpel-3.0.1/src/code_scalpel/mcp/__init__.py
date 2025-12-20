"""
Code Scalpel MCP Server - Model Context Protocol integration.

This module provides a fully MCP-compliant server that exposes Code Scalpel's
analysis capabilities through the official MCP protocol.

Supports:
- stdio transport (preferred for local integration)
- Streamable HTTP transport (for network deployment)

[20251216_FEATURE] v2.2.0 - Structured MCP Logging
- Tool invocation tracking with timing
- Success/failure metrics
- Analytics queries for usage patterns
"""

from .server import mcp, run_server

# [20251216_FEATURE] v2.2.0 - Structured logging
from .logging import (
    MCPAnalytics,
    ToolInvocation,
    log_tool_invocation,
    log_tool_success,
    log_tool_error,
    get_analytics,
    mcp_logger,
)

__all__ = [
    "mcp",
    "run_server",
    # [20251216_FEATURE] v2.2.0 - Logging exports
    "MCPAnalytics",
    "ToolInvocation",
    "log_tool_invocation",
    "log_tool_success",
    "log_tool_error",
    "get_analytics",
    "mcp_logger",
]
