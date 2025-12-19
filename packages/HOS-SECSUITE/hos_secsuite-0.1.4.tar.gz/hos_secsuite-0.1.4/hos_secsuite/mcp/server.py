"""MCP Service Server - FastAPI + WebSocket implementation"""

import asyncio
import uuid
import time
from typing import Dict, Any, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from hos_secsuite import registry, runner, __version__
from hos_secsuite.mcp.schemas import (
    ToolCall, ToolResult, ServiceInfo, ServiceStatus,
    ErrorResponse, WebSocketMessage, ToolDescription, ToolType
)


# Create FastAPI app
app = FastAPI(
    title="HOS SecSuite MCP Service",
    description="Model Context Protocol service for HOS SecSuite",
    version=__version__
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
active_connections: Set[WebSocket] = set()

# Task tracking
running_tasks: Dict[str, asyncio.Task] = {}


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Connect a client"""
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a client"""
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all clients"""
        for connection in self.active_connections:
            await connection.send_text(message)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send personal message to a client"""
        await websocket.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = WebSocketMessage(**data)
            
            if message.type == "tool_call":
                # Handle tool call
                tool_call = message.data
                result = await handle_tool_call(tool_call)
                
                # Send result back
                response_message = WebSocketMessage(
                    type="tool_result",
                    data=result
                )
                await manager.send_personal_message(
                    response_message.model_dump_json(),
                    websocket
                )
            elif message.type == "status":
                # Send service status
                service_info = get_service_info()
                response_message = WebSocketMessage(
                    type="status",
                    data=service_info
                )
                await manager.send_personal_message(
                    response_message.model_dump_json(),
                    websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        # Send error message
        error_response = ErrorResponse(
            error=str(e),
            code=500
        )
        error_message = WebSocketMessage(
            type="error",
            data=error_response
        )
        await manager.send_personal_message(
            error_message.model_dump_json(),
            websocket
        )
        manager.disconnect(websocket)


async def handle_tool_call(tool_call: ToolCall) -> ToolResult:
    """Handle tool call request
    
    Args:
        tool_call: Tool call request
        
    Returns:
        ToolResult: Tool execution result
    """
    # Generate task ID if not provided
    task_id = tool_call.task_id or str(uuid.uuid4())
    timestamp = time.time()
    
    try:
        # Get module from registry
        module_class = registry.get_module(tool_call.type)
        
        if tool_call.async_mode:
            # Run asynchronously
            task = asyncio.create_task(
                run_module_async(module_class, tool_call.arguments, task_id)
            )
            running_tasks[task_id] = task
            
            # Return running status
            return ToolResult(
                status="running",
                task_id=task_id,
                result=None,
                error=None,
                progress=0.0,
                timestamp=timestamp
            )
        else:
            # Run synchronously
            result = runner.run_module(
                module_class,
                sync=True,
                **tool_call.arguments
            )
            
            return ToolResult(
                status=result["status"],
                task_id=task_id,
                result=result,
                error=result.get("error"),
                progress=100.0,
                timestamp=timestamp
            )
    except KeyError:
        return ToolResult(
            status="error",
            task_id=task_id,
            result=None,
            error=f"Tool {tool_call.type} not found",
            progress=0.0,
            timestamp=timestamp
        )
    except Exception as e:
        return ToolResult(
            status="error",
            task_id=task_id,
            result=None,
            error=str(e),
            progress=0.0,
            timestamp=timestamp
        )


async def run_module_async(module_class, arguments: Dict[str, Any], task_id: str):
    """Run module asynchronously and update status"""
    timestamp = time.time()
    
    try:
        # Create module instance
        module_instance = module_class()
        
        # Set options
        for key, value in arguments.items():
            module_instance.set_option(key, value)
        
        # Run module
        result = await module_instance.run(**arguments)
        
        # Create result message
        result_message = WebSocketMessage(
            type="tool_result",
            data=ToolResult(
                status="success",
                task_id=task_id,
                result=result,
                error=None,
                progress=100.0,
                timestamp=time.time()
            )
        )
        
        # Broadcast result
        await manager.broadcast(result_message.model_dump_json())
    except Exception as e:
        # Create error message
        error_message = WebSocketMessage(
            type="tool_result",
            data=ToolResult(
                status="error",
                task_id=task_id,
                result=None,
                error=str(e),
                progress=0.0,
                timestamp=time.time()
            )
        )
        
        # Broadcast error
        await manager.broadcast(error_message.model_dump_json())
    finally:
        # Remove task from running tasks
        if task_id in running_tasks:
            del running_tasks[task_id]


@app.get("/", response_model=ServiceInfo)
async def get_service_status():
    """Get service status"""
    return get_service_info()


@app.post("/tools/call", response_model=ToolResult)
async def call_tool(tool_call: ToolCall):
    """Call a tool via REST API"""
    return await handle_tool_call(tool_call)


@app.get("/tools/list", response_model=Dict[str, ToolDescription])
async def list_tools():
    """List available tools"""
    tools = {}
    
    for module_name, module_class in registry.modules.items():
        # Determine tool type
        tool_type = ToolType.WEB
        if "scan" in module_name:
            tool_type = ToolType.SCAN
        elif "proxy" in module_name:
            tool_type = ToolType.PROXY
        elif "vuln" in module_name:
            tool_type = ToolType.VULN
        elif "request" in module_name:
            tool_type = ToolType.REQUEST
        elif "network" in module_name:
            tool_type = ToolType.NETWORK
        elif "info" in module_name:
            tool_type = ToolType.INFO
        elif "fingerprint" in module_name:
            tool_type = ToolType.FINGERPRINT
        elif "crypto" in module_name:
            tool_type = ToolType.CRYPTO
        elif "wireless" in module_name:
            tool_type = ToolType.WIRELESS
        elif "defense" in module_name:
            tool_type = ToolType.DEFENSE
        elif "report" in module_name:
            tool_type = ToolType.REPORT
        
        tools[module_name] = ToolDescription(
            name=module_name,
            type=tool_type,
            description=module_class.description,
            options=module_class.options,
            requires_root=module_class.requires_root
        )
    
    return tools


@app.get("/tools/{tool_name}", response_model=ToolDescription)
async def get_tool_info(tool_name: str):
    """Get tool information"""
    try:
        module_class = registry.get_module(tool_name)
        
        # Determine tool type
        tool_type = ToolType.WEB
        if "scan" in tool_name:
            tool_type = ToolType.SCAN
        elif "proxy" in tool_name:
            tool_type = ToolType.PROXY
        elif "vuln" in tool_name:
            tool_type = ToolType.VULN
        elif "request" in tool_name:
            tool_type = ToolType.REQUEST
        elif "network" in tool_name:
            tool_type = ToolType.NETWORK
        elif "info" in tool_name:
            tool_type = ToolType.INFO
        elif "fingerprint" in tool_name:
            tool_type = ToolType.FINGERPRINT
        elif "crypto" in tool_name:
            tool_type = ToolType.CRYPTO
        elif "wireless" in tool_name:
            tool_type = ToolType.WIRELESS
        elif "defense" in tool_name:
            tool_type = ToolType.DEFENSE
        elif "report" in tool_name:
            tool_type = ToolType.REPORT
        
        return ToolDescription(
            name=tool_name,
            type=tool_type,
            description=module_class.description,
            options=module_class.options,
            requires_root=module_class.requires_root
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")


@app.get("/tasks/{task_id}", response_model=ToolResult)
async def get_task_status(task_id: str):
    """Get task status"""
    if task_id in running_tasks:
        task = running_tasks[task_id]
        if task.done():
            try:
                result = task.result()
                return ToolResult(
                    status="success",
                    task_id=task_id,
                    result=result,
                    error=None,
                    progress=100.0,
                    timestamp=time.time()
                )
            except Exception as e:
                return ToolResult(
                    status="error",
                    task_id=task_id,
                    result=None,
                    error=str(e),
                    progress=0.0,
                    timestamp=time.time()
                )
        else:
            return ToolResult(
                status="running",
                task_id=task_id,
                result=None,
                error=None,
                progress=50.0,  # Estimated progress
                timestamp=time.time()
            )
    else:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


def get_service_info() -> ServiceInfo:
    """Get service information"""
    return ServiceInfo(
        name="HOS SecSuite MCP Service",
        version=__version__,
        status=ServiceStatus.RUNNING,
        tools=list(registry.modules.keys())
    )


def main():
    """Main entry point for MCP server"""
    # Initialize the framework
    registry.scan_modules()
    
    print(f"Starting HOS SecSuite MCP Service v{__version__}")
    print(f"Available tools: {len(registry.modules)}")
    
    # Run the server
    uvicorn.run(
        "hos_secsuite.mcp.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1
    )


if __name__ == "__main__":
    main()
