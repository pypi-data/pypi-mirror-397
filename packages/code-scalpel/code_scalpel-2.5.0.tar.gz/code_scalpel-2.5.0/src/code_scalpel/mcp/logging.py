"""
[20251216_FEATURE] v2.2.0 - Structured MCP Logging and Analytics.

This module provides structured logging for MCP tool invocations with detailed
metrics tracking and analytics capabilities.

Features:
- Structured logging with contextual information
- Tool invocation tracking with timing
- Success/failure metrics
- Token savings tracking
- Error traces for debugging
- Analytics queries for usage patterns
"""

from __future__ import annotations

# [20251216_BUGFIX] Avoid self-import: explicitly import stdlib logging
import importlib
import traceback  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from datetime import datetime  # noqa: E402
from typing import Any, Dict, List, Optional  # noqa: E402

logging = importlib.import_module("logging")

try:
    import structlog

    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    structlog = None


# Configure structured logging if available
if STRUCTLOG_AVAILABLE:
    # Configure structlog with JSON rendering for production
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    mcp_logger = structlog.get_logger("code_scalpel.mcp")
else:
    # Fallback to standard logging if structlog not available
    mcp_logger = logging.getLogger("code_scalpel.mcp")
    mcp_logger.setLevel(logging.INFO)


@dataclass
class ToolInvocation:
    """
    [20251216_FEATURE] v2.2.0 - Record of a single MCP tool invocation.

    Attributes:
        tool_name: Name of the tool invoked
        timestamp: When the tool was invoked
        duration_ms: How long the tool took to execute (milliseconds)
        success: Whether the tool executed successfully
        error_type: Type of error if failed (None if success)
        error_message: Error message if failed
        params: Tool parameters (sanitized)
        metrics: Additional metrics (tokens_saved, lines_extracted, etc.)
    """

    tool_name: str
    timestamp: datetime
    duration_ms: float
    success: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)


class MCPAnalytics:
    """
    [20251216_FEATURE] v2.2.0 - Analytics engine for MCP tool usage.

    Tracks tool invocations, success rates, performance metrics, and provides
    query capabilities for usage analysis.
    """

    def __init__(self):
        """Initialize the analytics engine."""
        self._invocations: List[ToolInvocation] = []
        self._start_time = datetime.now()

    def record_invocation(self, invocation: ToolInvocation) -> None:
        """
        Record a tool invocation.

        Args:
            invocation: ToolInvocation record
        """
        self._invocations.append(invocation)

    def get_tool_usage_stats(self, time_range: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage statistics for MCP tools.

        Args:
            time_range: Optional time range filter (not implemented yet)

        Returns:
            Dictionary with usage statistics
        """
        if not self._invocations:
            return {
                "total_invocations": 0,
                "success_rate": 0.0,
                "most_used_tools": [],
                "avg_duration_ms": 0.0,
                "tokens_saved_total": 0,
            }

        # Count tool usage
        tool_counts: Dict[str, int] = {}
        for inv in self._invocations:
            tool_counts[inv.tool_name] = tool_counts.get(inv.tool_name, 0) + 1

        # Sort by usage
        most_used = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)

        # Calculate success rate
        successful = sum(1 for inv in self._invocations if inv.success)
        success_rate = successful / len(self._invocations)

        # Calculate average duration
        avg_duration = sum(inv.duration_ms for inv in self._invocations) / len(
            self._invocations
        )

        # Calculate tokens saved
        tokens_saved = sum(
            inv.metrics.get("tokens_saved", 0) for inv in self._invocations
        )

        return {
            "total_invocations": len(self._invocations),
            "success_rate": round(success_rate, 3),
            "most_used_tools": [tool for tool, _ in most_used[:5]],
            "avg_duration_ms": round(avg_duration, 2),
            "tokens_saved_total": tokens_saved,
            "tool_counts": tool_counts,
        }

    def get_tool_stats(self, tool_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary with tool-specific statistics
        """
        tool_invocations = [
            inv for inv in self._invocations if inv.tool_name == tool_name
        ]

        if not tool_invocations:
            return {
                "tool_name": tool_name,
                "total_invocations": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
            }

        successful = sum(1 for inv in tool_invocations if inv.success)
        success_rate = successful / len(tool_invocations)
        avg_duration = sum(inv.duration_ms for inv in tool_invocations) / len(
            tool_invocations
        )

        return {
            "tool_name": tool_name,
            "total_invocations": len(tool_invocations),
            "success_rate": round(success_rate, 3),
            "avg_duration_ms": round(avg_duration, 2),
            "failures": [
                {
                    "timestamp": inv.timestamp.isoformat(),
                    "error_type": inv.error_type,
                    "error_message": inv.error_message,
                }
                for inv in tool_invocations
                if not inv.success
            ][
                :10
            ],  # Last 10 failures
        }

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of errors encountered.

        Returns:
            Dictionary with error statistics
        """
        errors = [inv for inv in self._invocations if not inv.success]

        if not errors:
            return {
                "total_errors": 0,
                "error_rate": 0.0,
                "error_types": {},
            }

        # Count error types
        error_counts: Dict[str, int] = {}
        for inv in errors:
            if inv.error_type:
                error_counts[inv.error_type] = error_counts.get(inv.error_type, 0) + 1

        error_rate = len(errors) / len(self._invocations)

        return {
            "total_errors": len(errors),
            "error_rate": round(error_rate, 3),
            "error_types": error_counts,
            "recent_errors": [
                {
                    "tool": inv.tool_name,
                    "timestamp": inv.timestamp.isoformat(),
                    "error_type": inv.error_type,
                    "error_message": inv.error_message,
                }
                for inv in errors[-10:]  # Last 10 errors
            ],
        }


# Global analytics instance
_analytics = MCPAnalytics()


def get_analytics() -> MCPAnalytics:
    """
    Get the global analytics instance.

    Returns:
        MCPAnalytics instance
    """
    return _analytics


def log_tool_invocation(
    tool_name: str, params: Optional[Dict[str, Any]] = None, **kwargs
) -> None:
    """
    [20251216_FEATURE] v2.2.0 - Log MCP tool invocation start.

    Args:
        tool_name: Name of the tool being invoked
        params: Tool parameters (will be sanitized)
        **kwargs: Additional context to log
    """
    # Sanitize params (remove sensitive data)
    safe_params = _sanitize_params(params or {})

    if STRUCTLOG_AVAILABLE:
        mcp_logger.info("tool_invoked", tool=tool_name, params=safe_params, **kwargs)
    else:
        mcp_logger.info(
            f"Tool invoked: {tool_name}",
            extra={"tool": tool_name, "params": safe_params, **kwargs},
        )


def log_tool_success(
    tool_name: str,
    duration_ms: float,
    metrics: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> None:
    """
    [20251216_FEATURE] v2.2.0 - Log successful MCP tool execution.

    Args:
        tool_name: Name of the tool
        duration_ms: Execution duration in milliseconds
        metrics: Tool-specific metrics (tokens_saved, lines_extracted, etc.)
        **kwargs: Additional context to log
    """
    metrics = metrics or {}

    # Record invocation
    invocation = ToolInvocation(
        tool_name=tool_name,
        timestamp=datetime.now(),
        duration_ms=duration_ms,
        success=True,
        metrics=metrics,
    )
    _analytics.record_invocation(invocation)

    if STRUCTLOG_AVAILABLE:
        mcp_logger.info(
            "tool_success", tool=tool_name, duration_ms=duration_ms, **metrics, **kwargs
        )
    else:
        mcp_logger.info(
            f"Tool success: {tool_name} ({duration_ms:.2f}ms)",
            extra={"tool": tool_name, "duration_ms": duration_ms, **metrics, **kwargs},
        )


def log_tool_error(
    tool_name: str,
    error: Exception,
    duration_ms: Optional[float] = None,
    params: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> None:
    """
    [20251216_FEATURE] v2.2.0 - Log MCP tool execution error.

    Args:
        tool_name: Name of the tool
        error: Exception that occurred
        duration_ms: Execution duration in milliseconds (if available)
        params: Tool parameters (will be sanitized)
        **kwargs: Additional context to log
    """
    error_type = type(error).__name__
    error_message = str(error)
    error_trace = traceback.format_exc()

    # Record invocation
    invocation = ToolInvocation(
        tool_name=tool_name,
        timestamp=datetime.now(),
        duration_ms=duration_ms or 0.0,
        success=False,
        error_type=error_type,
        error_message=error_message,
        params=_sanitize_params(params or {}),
    )
    _analytics.record_invocation(invocation)

    if STRUCTLOG_AVAILABLE:
        mcp_logger.error(
            "tool_error",
            tool=tool_name,
            error=error_message,
            error_type=error_type,
            traceback=error_trace,
            duration_ms=duration_ms,
            **kwargs,
        )
    else:
        mcp_logger.error(
            f"Tool error: {tool_name} - {error_type}: {error_message}",
            extra={
                "tool": tool_name,
                "error": error_message,
                "error_type": error_type,
                "traceback": error_trace,
                "duration_ms": duration_ms,
                **kwargs,
            },
        )


def _sanitize_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize parameters to remove sensitive data.

    Args:
        params: Original parameters

    Returns:
        Sanitized parameters
    """
    # Keys that might contain sensitive data
    sensitive_keys = {
        "password",
        "secret",
        "token",
        "api_key",
        "access_token",
        "auth",
        "credentials",
        "key",
        "private_key",
    }

    sanitized = {}
    for key, value in params.items():
        key_lower = key.lower()
        # Check if key contains sensitive terms
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, str) and len(value) > 1000:
            # Truncate very long strings
            sanitized[key] = value[:100] + "... (truncated)"
        else:
            sanitized[key] = value

    return sanitized
