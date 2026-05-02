# ssh-shell-mcp

> **AI-native SSH orchestration for security engineers, DevSecOps, and sysadmins.**  
> 57+ MCP tools. Async. Audited. Built on [AsyncSSH](https://asyncssh.readthedocs.io/) + [FastMCP](https://github.com/jlowin/fastmcp).

[![CI](https://github.com/jaguar999paw-droid/ssh-shell-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/jaguar999paw-droid/ssh-shell-mcp/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-compatible-brightgreen)](https://modelcontextprotocol.io/)

---

## What it does

`ssh-shell-mcp` turns any SSH-accessible host into a fully agentic target. Connect Claude (or any MCP-compatible AI agent) to your infrastructure, then let the agent execute commands, triage incidents, orchestrate fleets, manage tunnels, and audit operations — all over SSH, with no credentials in prompts and a full audit trail.

```
┌─────────────┐       MCP (stdio/HTTP)      ┌──────────────────┐
│  Claude /   │ ◄──────────────────────────► │  ssh-shell-mcp   │
│  AI Agent   │                              │  (this server)   │
└─────────────┘                              └────────┬─────────┘
                                                      │  AsyncSSH
                                          ┌───────────┼───────────┐
                                       web01       db01       jump01
```

---

## Why ssh-shell-mcp?

| Feature | ssh-shell-mcp | Ansible | Fabric | Paramiko |
|---|:---:|:---:|:---:|:---:|
| AI agent / MCP native | ✅ | ❌ | ❌ | ❌ |
| Async connection pool | ✅ | ❌ | ❌ | ❌ |
| Built-in audit log | ✅ | partial | ❌ | ❌ |
| Security policy gate | ✅ | ❌ | ❌ | ❌ |
| Persistent shell sessions | ✅ | ❌ | ❌ | ❌ |
| Live SOCKS5 / tunnel mgmt | ✅ | ❌ | ❌ | ❌ |
| Zero-dependency config | ✅ | ❌ | ❌ | ✅ |
| Fleet health checks | ✅ | ✅ | ❌ | ❌ |

---

## Use Cases

### 🔵 Blue Team / Incident Response
- Ask Claude to `ssh_journalctl` across all production hosts for a suspicious PID, then `ssh_kill` it
- Run `ssh_health_check_fleet` to instantly see which hosts went dark after an incident
- Use `ssh_operation_history` + `ssh_audit_stats` to reconstruct what an agent did during triage
- `ssh_playbook_on_group` to push a hardened `sshd_config` to the entire `linux` host group

### 🔴 Red Team / Authorized Testing (own systems only)
- `ssh_socks_proxy` through a jump host for proxychains-style traffic routing
- `ssh_port_forward` to expose internal services for enumeration during authorized assessments
- `ssh_reverse_tunnel` to create C2-style callbacks on lab environments
- `ssh_tmux_send` to drive interactive sessions from an AI agent

### ⚙️ DevSecOps / Fleet Automation
- Rolling deployments with `ssh_rolling` — zero-downtime, stop-on-failure
- Push secrets via `ssh_run_with_env` — never in command strings
- `ssh_sync` config directories, then `ssh_playbook` to restart affected services
- Group hosts by `tags` (e.g. `web`, `database`, `staging`) and broadcast commands to each tier

---

## Quickstart

```bash
git clone https://github.com/jaguar999paw-droid/ssh-shell-mcp.git
cd ssh-shell-mcp

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp config.example.json config.json   # fill in your hosts
python server.py --transport stdio
```

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ssh-shell": {
      "command": "/path/to/ssh-shell-mcp/.venv/bin/python",
      "args": ["server.py", "--transport", "stdio"],
      "env": {
        "SSH_HOSTS_YAML": "/path/to/ssh-shell-mcp/config/hosts.yaml"
      }
    }
  }
}
```

---

## 🚀 Non-Docker Setup (Complete Guide)

For users who prefer **native installation** without Docker, follow these step-by-step instructions.

### Prerequisites

Before starting, ensure you have:

- **Python 3.10 or higher** — Check: `python3 --version`
- **pip** (Python package manager) — Check: `pip3 --version`
- **SSH client** — Usually pre-installed on macOS/Linux; on Windows, install [Git Bash](https://gitforwindows.org/) or [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
- **SSH keys** — Have an SSH public key in `~/.ssh/id_ed25519` (or `id_rsa`). [Generate one](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) if needed.
- **SSH-accessible hosts** — At least one remote server you can connect to via SSH

### Step 1: Clone the Repository

```bash
git clone https://github.com/jaguar999paw-droid/ssh-shell-mcp.git
cd ssh-shell-mcp
```

### Step 2: Create a Virtual Environment

Isolate dependencies in a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

**On Windows (Git Bash):**
```bash
source .venv/Scripts/activate
```

**On Windows (PowerShell):**
```bash
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` appear in your shell prompt.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

This installs:
- `asyncssh` — Async SSH library
- `mcp` & `fastmcp` — Model Context Protocol framework
- `pyyaml` — Configuration file parsing
- `pytest` — Testing framework

### Step 4: Configure Your SSH Hosts

Create a configuration file defining which SSH targets to connect to:

```bash
cp config.example.json config.json
```

Edit `config.json` with your SSH hosts:

```json
{
  "hosts": {
    "web01": {
      "host": "192.168.1.100",
      "port": 22,
      "user": "deploy",
      "key_path": "~/.ssh/id_ed25519",
      "tags": ["web", "production"]
    },
    "db01": {
      "host": "192.168.1.200",
      "port": 22,
      "user": "deploy",
      "key_path": "~/.ssh/id_ed25519",
      "tags": ["database", "production"]
    },
    "localhost": {
      "host": "127.0.0.1",
      "port": 22,
      "user": "$(whoami)",
      "key_path": "~/.ssh/id_ed25519",
      "tags": ["local", "testing"]
    }
  }
}
```

**Key fields:**
- `host` — IP address or domain of the SSH server
- `port` — SSH port (default: 22)
- `user` — SSH username
- `key_path` — Path to your SSH private key (e.g. `~/.ssh/id_ed25519`)
- `tags` — Arbitrary labels for grouping hosts (e.g. web, database, production)

### Step 5: Test SSH Connectivity

Before connecting via MCP, verify SSH works:

```bash
ssh -i ~/.ssh/id_ed25519 deploy@192.168.1.100 'echo "✓ SSH works!"'
```

If you get `Permission denied`, check:
- SSH key file permissions: `chmod 600 ~/.ssh/id_ed25519`
- SSH server is running on the target host
- User credentials are correct in `config.json`
- Firewall isn't blocking port 22

### Step 6: Start the Server

Run the server in **stdio mode** (for Claude Desktop):

```bash
python server.py --transport stdio
```

You should see:
```
[ssh-shell-mcp] INFO Starting MCP server in stdio mode
[ssh-shell-mcp] INFO Loaded config from config.json
[ssh-shell-mcp] INFO Registered 3 hosts: web01, db01, localhost
```

The server is now ready to accept MCP connections. Leave this terminal open.

### Step 7: Connect to Claude Desktop

In a **new terminal**, find the full path to your Python executable:

```bash
which python  # or 'python' depending on your setup
# Output: /Users/you/projects/ssh-shell-mcp/.venv/bin/python
```

Copy the path (e.g., `/Users/you/projects/ssh-shell-mcp/.venv/bin/python`).

Edit your Claude Desktop configuration file:

**On macOS:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**On Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

**On Windows:**
```bash
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Add or update the `mcpServers` section:

```json
{
  "mcpServers": {
    "ssh-shell": {
      "command": "/Users/you/projects/ssh-shell-mcp/.venv/bin/python",
      "args": ["server.py", "--transport", "stdio"],
      "env": {
        "SSH_HOSTS_YAML": "/Users/you/projects/ssh-shell-mcp/config/hosts.yaml"
      }
    }
  }
}
```

**Replace `/Users/you/projects/ssh-shell-mcp/` with your actual repository path.**

### Step 8: Restart Claude Desktop

Fully restart Claude Desktop for the new MCP server to load:

1. Quit Claude completely
2. Wait 2 seconds
3. Reopen Claude

You should see a **hammer icon** (🔨) or **settings gear** in the Claude interface — click it to verify the server loaded.

### Step 9: Test a Tool

In Claude, try:

```
Can you list the files in /tmp on web01?
```

Claude will use the `ssh_ls` tool to run `ls /tmp` on `web01` via SSH. Watch the terminal running `server.py` to see the command executed with full audit logging.

### Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'asyncssh'` | Ensure venv is activated: `source .venv/bin/activate` |
| `Permission denied (publickey)` | Check SSH key permissions: `chmod 600 ~/.ssh/id_ed25519` |
| `Could not open config file 'config.json'` | Verify `config.json` exists in the repo root: `ls config.json` |
| MCP server not showing in Claude | Restart Claude Desktop completely (not just app minimize) |
| `Connection refused` when testing SSH | Verify SSH server is running on target: `ssh web01 'echo ok'` |
| `Host key verification failed` | SSH host unknown. Accept the key: `ssh-keyscan -H 192.168.1.100 >> ~/.ssh/known_hosts` |

### Next Steps

- **Read the [tool reference](docs/tools.md)** for all 57 available tools
- **Review [SECURITY.md](SECURITY.md)** for production hardening
- **Check [CONTRIBUTING.md](CONTRIBUTING.md)** if you want to extend the server

---

## Tool Categories (57 tools)

| # | Category | Tools |
|---|---|---|
| 1 | **Shell execution** | `ssh_run`, `ssh_run_batch`, `ssh_run_script`, `ssh_run_with_env`, `ssh_exec_retry` |
| 2 | **Persistent sessions** | `ssh_create_session`, `ssh_session_exec`, `ssh_session_read_buffer`, `ssh_close_session`, `ssh_session_list`, `ssh_session_set_env` |
| 3 | **File management** | `ssh_upload`, `ssh_download`, `ssh_ls`, `ssh_cat`, `ssh_write`, `ssh_rm`, `ssh_sync` |
| 4 | **Process management** | `ssh_ps`, `ssh_kill`, `ssh_start`, `ssh_background`, `ssh_monitor` |
| 5 | **System inspection** | `ssh_info`, `ssh_df`, `ssh_free`, `ssh_netstat`, `ssh_service`, `ssh_journalctl`, `ssh_docker` |
| 6 | **Fleet orchestration** | `ssh_parallel`, `ssh_rolling`, `ssh_group_exec`, `ssh_broadcast_batch`, `ssh_playbook`, `ssh_playbook_on_group` |
| 7 | **Tunnels & proxies** | `ssh_port_forward`, `ssh_reverse_tunnel`, `ssh_socks_proxy`, `ssh_close_tunnel`, `ssh_active_tunnels` |
| 8 | **Security controls** | `ssh_check_command`, `ssh_check_host_access`, `ssh_security_status` |
| 9 | **Host registry** | `ssh_register_host`, `ssh_list_hosts`, `ssh_remove_host`, `ssh_connection_status` |
| 10 | **Health & observability** | `ssh_ping_host`, `ssh_health_check_fleet`, `ssh_full_status`, `ssh_operation_history`, `ssh_audit_stats` |
| 11 | **tmux** | `ssh_tmux_new`, `ssh_tmux_send`, `ssh_tmux_list`, `ssh_tmux_kill` |

---

## Configuration

**`config/hosts.yaml`** — registers your SSH targets:

```yaml
hosts:
  web01:
    host: 192.168.1.100
    port: 22
    user: deploy
    key: ~/.ssh/id_ed25519
    tags: [web, production]

  db01:
    host: 192.168.1.200
    port: 22
    user: deploy
    key: ~/.ssh/id_ed25519
    tags: [database, production]
```

**`config/policies.yaml`** — security policy (host allowlist + command blocklist):

```yaml
policies:
  host_allowlist: []         # empty = all registered hosts permitted
  command_blocklist:
    - "rm -rf /"
    - "rm -rf /*"
    - "mkfs*"
    - ":(){:|:&};:"          # fork bomb
```

> **Never commit `hosts.yaml`** — it contains real credentials. It is already in `.gitignore`. Use `hosts.example.yaml` as a template.

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SSH_HOSTS_YAML` | Path to hosts config | `config/hosts.yaml` |
| `SSH_POLICIES_YAML` | Path to security policy config | `config/policies.yaml` |
| `SSH_MCP_LOG_DIR` | Directory for audit logs | `logs/` |
| `MCP_AUTH_TOKEN` | Bearer token for HTTP transport | _(none)_ |

---

## Security Design

- **Key-based auth only** — password auth is intentionally unsupported.
- **Policy gate on every tool** — `_gate()` checks host allowlist and command blocklist before any execution.
- **Full audit log** — every operation is recorded with host, command, result, and timestamp.
- **No outbound telemetry** — the server connects only to your configured SSH targets.
- **stdio default** — no network port opened on the MCP host by default.
- Running targets behind a VPN (e.g. Tailscale) is strongly recommended.

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

---

## Running Tests

```bash
# Integration tests — requires SSH server on localhost
TEST_USER=$USER TEST_KEY_PATH=~/.ssh/id_ed25519 pytest tests/ -v
```

Tests cover: exec, file transfer, persistent sessions, fleet orchestration, and tunnels.  
They use **real SSH connections** — no mocking.

---

## HTTP Transport (remote agents)

```bash
MCP_AUTH_TOKEN=your-secret python server.py --transport streamable_http --port 8000
```

The server exposes `/mcp` with Bearer token authentication. Suitable for remote AI agents over a private network.

---

## Project Structure

```
ssh-shell-mcp/
├── server.py              # MCP entrypoint — all 57 tools
├── server/
│   ├── connection_manager.py   # AsyncSSH connection pool
│   ├── session_manager.py      # Persistent shell sessions
│   ├── shell_engine.py         # Core command execution
│   ├── file_ops.py             # SFTP file operations
│   ├── process_manager.py      # Process lifecycle
│   ├── system_inspector.py     # System info, logs, Docker
│   ├── network_tools.py        # Tunnel manager
│   ├── orchestrator.py         # Multi-host execution
│   ├── audit.py                # Audit log
│   └── security.py             # Policy enforcement
├── config.example.json
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── SECURITY.md
```

---

For per-tool parameter documentation see [`docs/tools.md`](docs/tools.md).

---

## ⚠️ Legal Notice

This tool provides programmatic SSH access to remote systems. **Use only on systems you own or have explicit written authorization to access.** Unauthorized access to computer systems is illegal in most jurisdictions.

---

## 🔐 Cryptography Notice

This software uses the SSH protocol, which relies on cryptographic algorithms. Export, import, and use may be restricted in some jurisdictions. See the [Wassenaar Arrangement](https://www.wassenaar.org/) for reference.

---

## License

[Apache License 2.0](LICENSE)
