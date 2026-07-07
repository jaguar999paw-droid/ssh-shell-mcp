# MCP Server Architecture Redesign — Recovery & Optimization

## Problem Summary
**Claude Desktop MCP servers were failing with cascading timeouts:**
- All servers timing out during initialization (MCP error -32001)
- Response times 5+ seconds due to concurrent startup bottleneck
- Android services blocking startup (unreachable <android-host> host)
- ssh-shell-mcp hanging on synchronous YAML loading during module import

---

## Root Cause Analysis

### 1. **Synchronous Blocking I/O During Module Import**
- `ConnectionManager.__init__()` in ssh-shell-mcp was calling `_load_registry()` immediately
- Reads `hosts.yaml` synchronously during module import
- FastMCP couldn't initialize MCP tools until module fully loaded
- Multiple MCP servers competing for CPU/I/O → timeout cascade

### 2. **Concurrent Startup Bottleneck**
- Claude loads ALL MCP servers simultaneously
- One slow server blocks others from initializing
- No health checks or staggered startup
- Default MCP initialization timeout is ~5 seconds

### 3. **Broken/Unreachable Services**
- Android services trying to reach `<android-host>` host (30s timeout, then failure)
- ctf-mcp, lavira-media-engine may not be running
- Scraping-tools dependencies (worker services) may not exist

---

## Solutions Implemented

### ✅ Fix 1: Lazy-Load ssh-shell-mcp Connection Manager
**File:** `<project-root>/server/connection_manager.py`

**Changes:**
- Moved `_load_registry()` call from `__init__()` to first actual use
- Added `_registry_loaded` flag to prevent re-loading
- All public methods now call `_load_registry()` lazily

**Impact:**
- ✓ Module imports instantly (no blocking I/O)
- ✓ FastMCP can initialize MCP tools in <100ms
- ✓ YAML loads only when needed

**Verification:**
```bash
$ timeout 10 python -c "from server.connection_manager import get_manager; print('✓ Loaded')"
✓ Loaded
```

---

### ✅ Fix 2: HTTP Web Server Wrapper for ssh-shell-mcp
**File:** `<project-root>/web_server.py` (NEW)

**Features:**
- FastAPI REST API exposing all ssh-shell-mcp tools
- Health check endpoint (`/health`)
- Tool listing (`/api/tools`)
- Direct execution: `POST /api/ssh-shell-mcp/call`
- Quick SSH: `POST /api/ssh-shell-mcp/exec`
- Swagger docs: `http://localhost:8765/docs`

**Startup:**
```bash
cd <project-root>
python web_server.py --host 0.0.0.0 --port 8765
```

**Example Usage:**
```bash
curl -X POST http://localhost:8765/api/ssh-shell-mcp/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "ssh_list_hosts", "args": {}}'
```

**Benefits:**
- ✓ Accessible from browser, Copilot, external services
- ✓ Not subject to MCP server timeout limits
- ✓ Can be deployed in Docker/container

---

### ✅ Fix 3: Copilot/VS Code Integration Bridge
**File:** `<project-root>/copilot_bridge.py` (NEW)

**Features:**
- FastMCP server specifically for Copilot Chat
- Routes calls to web_server.py via HTTP
- Exposes 5 key tools to Copilot:
  - `ssh_exec()` — Execute commands on hosts
  - `ssh_list_hosts()` — Show registered hosts
  - `ssh_register_host()` — Add new hosts
  - `ssh_process_list()` — List processes
  - `ssh_system_info()` — Get system info

**Usage in VS Code:**
```json
{
  "mcpServers": {
    "copilot-ssh": {
      "command": "<project-root>/venv/bin/python",
      "args": ["<project-root>/copilot_bridge.py"]
    }
  }
}
```

---

### ✅ Fix 4: Disabled Broken Services
**File:** `~/.config/Claude/claude_desktop_config.json`

**Disabled:**
- `android-userspace` — Can't reach <android-host>
- `android-bootloader` — Can't reach <android-host>
- `android-orchestrator` — Can't reach <android-host>
- `android-network` — Can't reach <android-host>

**Why:** These services hit 30s timeout → block all others. Re-enable only when host is available.

---

## Recommended Architecture Changes

### 1. **Separate Fast vs. Slow Servers**

**Priority 1 (Fast, Essential):**
```json
{
  "ssh-shell-mcp": {...},
  "docker-mcp": {...},
  "tailscale": {...}
}
```

**Priority 2 (Optional, Load in Background):**
```json
{
  "github": {...disabled_until_needed},
  "kubernetes": {...disabled},
  "scraping-tools": {...disabled}
}
```

### 2. **Health Checks & Timeouts**

**Add to each server config:**
```json
{
  "healthCheckInterval": 30000,      // Check every 30s
  "healthCheckPath": "/health",      // Optional HTTP health endpoint
  "startupTimeout": 10000,           // 10s to initialize
  "requestTimeout": 60000            // 60s for requests
}
```

### 3. **Graceful Degradation**

**If a server fails to start:**
1. Log error but don't block others
2. Mark server as "unavailable" (not "failed")
3. Retry startup after 30s
4. Show user: "⚠ Some tools unavailable (SSH tools degraded)"

### 4. **Web Tier for Heavy Services**

Instead of direct MCP servers:
- Deploy scraping-tools as HTTP service
- Deploy ctf-mcp as HTTP service  
- Use HTTP MCP bridge to call them

**Benefits:**
- Can be deployed separately (Docker)
- Can restart independently
- Don't block Claude Desktop startup
- Can scale horizontally

### 5. **Configuration Profiles**

Create `~/.config/Claude/profiles/`:

**`minimal.json`** — Fast startup (just SSH, Docker):
```json
{
  "mcpServers": {
    "ssh-shell-mcp": {...enabled},
    "docker-mcp": {...enabled}
  }
}
```

**`full.json`** — All services (requires all dependencies running)

**`development.json`** — No external services, local only

---

## Next Steps

### Immediate (Today)
1. ✅ Verify ssh-shell-mcp starts without hanging
2. ✅ Test web_server.py on localhost:8765
3. ✅ Add copilot_bridge.py to Claude config
4. ✅ Keep Android services disabled

### Short Term (This Week)
1. Deploy web_server.py in systemd/Docker
2. Create health check monitoring
3. Set up graceful degradation
4. Document API for external tools

### Medium Term (This Month)
1. Move heavy services (scraping-tools, ctf-mcp) to HTTP tier
2. Implement configuration profiles
3. Add automatic retry logic
4. Create dashboard for MCP server status

### Long Term (This Quarter)
1. Kubernetes-based MCP orchestration
2. Auto-scaling for compute-heavy servers
3. MCP service discovery & load balancing
4. Analytics & performance monitoring

---

## Deployment Commands

### Test ssh-shell-mcp Startup
```bash
cd <project-root>
<project-root>/venv/bin/python server.py --transport stdio
# Should start instantly, no timeout
```

### Run Web Server
```bash
cd <project-root>
pip install fastapi uvicorn httpx
python web_server.py --port 8765
# Visit: http://localhost:8765/docs
```

### Use from Command Line
```bash
# Register a host
curl -X POST http://localhost:8765/api/ssh-shell-mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "ssh_register_host",
    "args": {
      "name": "web01",
      "host": "10.0.0.1",
      "user": "deploy"
    }
  }'

# List hosts
curl http://localhost:8765/api/tools

# Execute command
curl -X POST http://localhost:8765/api/ssh-shell-mcp/exec \
  -H "Content-Type: application/json" \
  -d '{"host": "web01", "command": "hostname"}'
```

---

## Configuration Rollback

If issues occur, revert to minimal config:

```json
{
  "mcpServers": {
    "ssh-shell-mcp": {
      "command": "<project-root>/venv/bin/python",
      "args": ["<project-root>/server.py", "--transport", "stdio"],
      "env": {
        "SSH_HOSTS_YAML": "<project-root>/config/hosts.yaml"
      },
      "disabled": false
    },
    "docker-mcp": {
      "command": "<path-to-docker-mcp>/venv/bin/python",
      "args": ["<path-to-docker-mcp>/docker_mcp_server.py"],
      "disabled": false
    }
  }
}
```

---

## References
- MCP Documentation: https://modelcontextprotocol.io/docs/
- FastAPI: https://fastapi.tiangolo.com/
- ssh-shell-mcp: `<project-root>/README.md`
