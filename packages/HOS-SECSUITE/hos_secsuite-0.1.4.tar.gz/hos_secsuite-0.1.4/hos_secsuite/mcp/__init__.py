"""MCP (Model Context Protocol) service for HOS SecSuite"""

from hos_secsuite.mcp.server import app
from hos_secsuite.mcp.schemas import ToolCall, ToolResult, ServiceStatus

__all__ = ["app", "ToolCall", "ToolResult", "ServiceStatus"]
