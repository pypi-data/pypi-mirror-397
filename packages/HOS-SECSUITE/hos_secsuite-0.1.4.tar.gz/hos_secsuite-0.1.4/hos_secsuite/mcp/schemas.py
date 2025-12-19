"""MCP Service Data Models"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union
from enum import Enum


class ServiceStatus(str, Enum):
    """Service status enum"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class ToolType(str, Enum):
    """Tool type enum"""
    SCAN = "scan"
    WEB = "web"
    NETWORK = "network"
    PROXY = "proxy"
    VULN = "vuln"
    REQUEST = "request"
    INFO = "info"
    FINGERPRINT = "fingerprint"
    CRYPTO = "crypto"
    WIRELESS = "wireless"
    DEFENSE = "defense"
    REPORT = "report"


class ToolCall(BaseModel):
    """Tool call request model"""
    type: str = Field(..., description="Tool type (e.g., 'nmap.scan', 'web.proxy.mitmproxy')")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    async_mode: bool = Field(default=False, description="Run in async mode")
    task_id: Optional[str] = Field(default=None, description="Task ID for tracking")


class ToolResult(BaseModel):
    """Tool result response model"""
    status: str = Field(..., description="Execution status (success, error, running)")
    task_id: str = Field(..., description="Task ID")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Tool execution result")
    error: Optional[str] = Field(default=None, description="Error message if status is error")
    progress: Optional[float] = Field(default=None, description="Progress percentage (0-100)")
    timestamp: float = Field(..., description="Result timestamp")


class ServiceInfo(BaseModel):
    """Service information model"""
    name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    status: ServiceStatus = Field(..., description="Service status")
    tools: List[str] = Field(default_factory=list, description="Available tools")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    code: int = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")


class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str = Field(..., description="Message type (tool_call, tool_result, status, error)")
    data: Union[ToolCall, ToolResult, ServiceInfo, ErrorResponse] = Field(..., description="Message data")


class ToolDescription(BaseModel):
    """Tool description model"""
    name: str = Field(..., description="Tool name")
    type: ToolType = Field(..., description="Tool type")
    description: str = Field(..., description="Tool description")
    options: Dict[str, Any] = Field(default_factory=dict, description="Tool options")
    requires_root: bool = Field(default=False, description="Whether tool requires root/admin privileges")
