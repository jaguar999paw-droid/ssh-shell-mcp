"""
HTTP bridge for ssh-shell-mcp — Makes MCP tools available via REST API.
Allows integration with Copilot, browsers, and external services.

Usage:
    python web_server.py --host 0.0.0.0 --port 8765
    or via Docker: docker run -p 8765:8765 ssh-shell-mcp-web

API Example:
    POST http://localhost:8765/api/ssh-shell-mcp/call
    {
        "tool": "ssh_register_host",
        "args": {"name": "web01", "host": "192.168.1.10", "user": "deploy"}
    }
"""
import asyncio
import json
import logging
import os
import sys
import argparse
from pathlib import Path
from typing import Any, Dict

# FastAPI HTTP framework
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add parent to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from mcp.server.fastmcp import FastMCP
from server.shell_engine import (
    ssh_exec, ssh_exec_batch, ssh_exec_script, ssh_exec_with_env
)
from server.file_ops import (
    ssh_upload_file, ssh_download_file, ssh_list_directory,
    ssh_read_file, ssh_write_file, ssh_delete_file, ssh_sync_directory
)
from server.process_manager import (
    ssh_process_list, ssh_kill_process, ssh_start_process,
    ssh_background_process, ssh_monitor_process
)
from server.system_inspector import (
    ssh_system_info, ssh_disk_usage, ssh_memory_usage,
    ssh_network_status, ssh_service_status, ssh_logs, ssh_docker_status
)
from server.connection_manager import get_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s"
)
logger = logging.getLogger("ssh_web")

# Tool registry mapping
TOOLS = {
    # Connection management
    "ssh_register_host": None,  # Defer to get_manager()
    "ssh_list_hosts": None,
    "ssh_remove_host": None,
    "ssh_connection_status": None,
    
    # Shell execution
    "ssh_exec": ssh_exec,
    "ssh_exec_batch": ssh_exec_batch,
    "ssh_exec_script": ssh_exec_script,
    "ssh_exec_with_env": ssh_exec_with_env,
    
    # File operations
    "ssh_upload_file": ssh_upload_file,
    "ssh_download_file": ssh_download_file,
    "ssh_list_directory": ssh_list_directory,
    "ssh_read_file": ssh_read_file,
    "ssh_write_file": ssh_write_file,
    "ssh_delete_file": ssh_delete_file,
    "ssh_sync_directory": ssh_sync_directory,
    
    # Process management
    "ssh_process_list": ssh_process_list,
    "ssh_kill_process": ssh_kill_process,
    "ssh_start_process": ssh_start_process,
    "ssh_background_process": ssh_background_process,
    "ssh_monitor_process": ssh_monitor_process,
    
    # System inspection
    "ssh_system_info": ssh_system_info,
    "ssh_disk_usage": ssh_disk_usage,
    "ssh_memory_usage": ssh_memory_usage,
    "ssh_network_status": ssh_network_status,
    "ssh_service_status": ssh_service_status,
    "ssh_logs": ssh_logs,
    "ssh_docker_status": ssh_docker_status,
}

app = FastAPI(
    title="ssh-shell-mcp Web API",
    description="HTTP bridge for ssh-shell-mcp MCP server",
    version="1.0.0"
)

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ToolCall(BaseModel):
    tool: str
    args: Dict[str, Any]


class ToolResult(BaseModel):
    status: str
    result: Any
    error: str = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ssh-shell-mcp-web",
        "version": "1.0.0"
    }


@app.get("/api/tools")
async def list_tools():
    """List all available SSH tools."""
    return {
        "tools": list(TOOLS.keys()),
        "count": len(TOOLS)
    }


@app.post("/api/ssh-shell-mcp/call")
async def call_tool(call: ToolCall) -> ToolResult:
    """
    Call an ssh-shell-mcp tool via HTTP.
    
    Example:
        POST /api/ssh-shell-mcp/call
        {
            "tool": "ssh_register_host",
            "args": {"name": "web01", "host": "10.0.0.1"}
        }
    """
    if call.tool not in TOOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{call.tool}' not found. Available tools: {list(TOOLS.keys())}"
        )
    
    try:
        # Handle connection manager methods
        if call.tool == "ssh_register_host":
            result = get_manager().register_host(**call.args)
        elif call.tool == "ssh_list_hosts":
            result = get_manager().list_hosts()
        elif call.tool == "ssh_remove_host":
            result = get_manager().remove_host(**call.args)
        elif call.tool == "ssh_connection_status":
            result = get_manager().pool_status()
        else:
            func = TOOLS[call.tool]
            if asyncio.iscoroutinefunction(func):
                result = await func(**call.args)
            else:
                result = func(**call.args)
        
        return ToolResult(status="success", result=result)
    
    except Exception as e:
        logger.error(f"Tool call failed: {call.tool} - {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Tool execution failed: {str(e)}"
        )


@app.post("/api/ssh-shell-mcp/exec")
async def quick_exec(request: Request):
    """
    Quick SSH execution endpoint.
    
    JSON body:
        {
            "host": "web01",
            "command": "ls -la /var/log",
            "timeout": 30
        }
    """
    data = await request.json()
    host = data.get("host")
    command = data.get("command")
    timeout = data.get("timeout", 30)
    
    if not host or not command:
        raise HTTPException(
            status_code=400,
            detail="Required fields: host, command"
        )
    
    try:
        result = await ssh_exec(
            host_name=host,
            command=command,
            timeout=timeout
        )
        return ToolResult(status="success", result=result)
    except Exception as e:
        logger.error(f"Exec failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/docs")
async def api_docs():
    """OpenAPI documentation."""
    return {
        "title": "ssh-shell-mcp Web API",
        "endpoints": {
            "/health": "Health check",
            "/api/tools": "List available tools",
            "/api/ssh-shell-mcp/call": "Call any SSH tool",
            "/api/ssh-shell-mcp/exec": "Quick SSH execution",
            "/docs": "Interactive API documentation (Swagger)",
            "/redoc": "ReDoc documentation"
        },
        "example_curl": "curl -X POST http://localhost:8765/api/ssh-shell-mcp/call -H 'Content-Type: application/json' -d '{\"tool\": \"ssh_list_hosts\", \"args\": {}}'",
        "client_urls": {
            "copilot_mcp": "sse://localhost:8765/api/ssh-shell-mcp",
            "http_direct": "http://localhost:8765"
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="ssh-shell-mcp HTTP Web Server"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=8765, help="Bind port")
    parser.add_argument("--reload", action="store_true", help="Auto-reload on changes")
    args = parser.parse_args()
    
    logger.info(f"Starting ssh-shell-mcp web server on {args.host}:{args.port}")
    logger.info(f"API docs: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}/docs")
    
    uvicorn.run(
        "web_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
