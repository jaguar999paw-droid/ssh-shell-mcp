"""
Copilot SSH MCP bridge - Exposes ssh-shell-mcp to VS Code Copilot
Runs web_server.py and provides SSE endpoint for direct MCP integration
"""
import asyncio
import json
import logging
import subprocess
import sys
import os
import time
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

BASE_DIR = Path(__file__).parent
WEB_SERVER_SCRIPT = BASE_DIR / "web_server.py"
WEB_SERVER_URL = "http://localhost:8765"

logger = logging.getLogger("copilot_ssh_bridge")
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# FastMCP server for Copilot
mcp = FastMCP("copilot-ssh-shell")
client = httpx.AsyncClient(timeout=60.0)


@mcp.tool()
async def ssh_exec(host: str, command: str, timeout: int = 30) -> str:
    """Execute a command on a remote SSH host via Copilot.
    
    Args:
        host: Target hostname (e.g., 'web01')
        command: Shell command to execute
        timeout: Max seconds to wait (default 30)
    
    Returns:
        Command output and status
    """
    try:
        response = await client.post(
            f"{WEB_SERVER_URL}/api/ssh-shell-mcp/exec",
            json={"host": host, "command": command, "timeout": timeout}
        )
        data = response.json()
        if response.status_code == 200:
            return json.dumps(data.get("result"), indent=2)
        else:
            return f"Error: {data.get('detail', 'Unknown error')}"
    except Exception as e:
        return f"Connection failed: {e}. Make sure web server is running on {WEB_SERVER_URL}"


@mcp.tool()
async def ssh_list_hosts() -> str:
    """List all registered SSH hosts."""
    try:
        response = await client.post(
            f"{WEB_SERVER_URL}/api/ssh-shell-mcp/call",
            json={"tool": "ssh_list_hosts", "args": {}}
        )
        data = response.json()
        return json.dumps(data.get("result"), indent=2)
    except Exception as e:
        return f"Failed to list hosts: {e}"


@mcp.tool()
async def ssh_register_host(name: str, host: str, user: str = "root", 
                           port: int = 22, key_path: str = "", 
                           password: str = "") -> str:
    """Register a new SSH host for use in Copilot.
    
    Args:
        name: Unique host identifier (e.g., 'prod-web-01')
        host: IP address or hostname
        user: SSH username (default: root)
        port: SSH port (default: 22)
        key_path: Path to private key (~/.ssh/id_rsa)
        password: SSH password (if not using keys)
    """
    try:
        response = await client.post(
            f"{WEB_SERVER_URL}/api/ssh-shell-mcp/call",
            json={
                "tool": "ssh_register_host",
                "args": {
                    "name": name,
                    "host": host,
                    "user": user,
                    "port": port,
                    "key": key_path or None,
                    "password": password or None,
                    "tags": []
                }
            }
        )
        data = response.json()
        return data.get("result", "Host registered")
    except Exception as e:
        return f"Registration failed: {e}"


@mcp.tool()
async def ssh_process_list(host: str) -> str:
    """List running processes on a remote host."""
    try:
        response = await client.post(
            f"{WEB_SERVER_URL}/api/ssh-shell-mcp/call",
            json={
                "tool": "ssh_process_list",
                "args": {"host_name": host, "filter": ""}
            }
        )
        data = response.json()
        return json.dumps(data.get("result"), indent=2)
    except Exception as e:
        return f"Failed to list processes: {e}"


@mcp.tool()
async def ssh_system_info(host: str) -> str:
    """Get system information from a remote host."""
    try:
        response = await client.post(
            f"{WEB_SERVER_URL}/api/ssh-shell-mcp/call",
            json={
                "tool": "ssh_system_info",
                "args": {"host_name": host}
            }
        )
        data = response.json()
        return json.dumps(data.get("result"), indent=2)
    except Exception as e:
        return f"Failed to get system info: {e}"


@mcp.tool()
async def web_server_health() -> str:
    """Check if the ssh-shell-mcp web server is running."""
    try:
        response = await client.get(f"{WEB_SERVER_URL}/health")
        if response.status_code == 200:
            return f"✓ Web server running at {WEB_SERVER_URL}"
        else:
            return f"✗ Web server returned {response.status_code}"
    except Exception as e:
        return f"✗ Web server not responding: {e}"


async def startup():
    """Startup hook - ensure web server is running."""
    logger.info(f"Checking web server at {WEB_SERVER_URL}...")
    for attempt in range(5):
        try:
            response = await client.get(f"{WEB_SERVER_URL}/health", timeout=2)
            if response.status_code == 200:
                logger.info("✓ Web server is running")
                return
        except:
            if attempt < 4:
                logger.info(f"  Attempt {attempt+1}/5: Web server not ready, retrying...")
                await asyncio.sleep(1)
    
    logger.warning("⚠ Web server may not be running. Start it with:")
    logger.warning(f"  cd {BASE_DIR} && python web_server.py")


async def main():
    """Main entry point for Copilot MCP."""
    await startup()
    async with mcp:
        logger.info("Copilot SSH MCP bridge ready")
        await mcp.wait()


if __name__ == "__main__":
    asyncio.run(main())
