# ssh-shell-mcp

> **Production-grade SSH orchestration layer for AI agents.**
> Manage fleets of remote machines, deploy infrastructure, and orchestrate containers — all through MCP tools.

---

## Architecture Overview

```
ssh-shell-mcp/
├── server.py                  # MCP entrypoint — 40+ tools wired here
├── server/
│   ├── connection_manager.py  # SSH connection pool + host registry
│   ├── session_manager.py     # Persistent interactive shell sessions
│   ├── shell_engine.py        # One-off / batch / script execution
│   ├── file_ops.py            # SFTP file operations
│   ├── process_manager.py     # Remote process lifecycle
│   ├── system_inspector.py    # Infrastructure visibility
│   ├── network_tools.py       # SSH tunnels + port forwarding
│   ├── orchestrator.py        # Multi-host fleet operations
│   ├── security.py            # Policy enforcement + rate limiting
│   └── audit.py               # Structured audit logging
├── config/
│   ├── hosts.yaml             # Static host registry
│   └── policies.yaml          # Security policies
├── logs/
│   ├── server.log             # Application log
│   └── audit.jsonl            # Structured audit trail (JSON Lines)
├── tests/
│   └── test_ssh_mcp.py        # Integration tests (6 test classes)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Component Map

| Component | Responsibility |
|---|---|
| **ConnectionManager** | Pool of AsyncSSH connections, host YAML registry, key auth |
| **SessionManager** | Persistent PTY shells with sentinel-based output detection |
| **ShellEngine** | One-off exec, batch, streaming, script upload + run |
| **FileOps** | SFTP upload/download/read/write/delete/sync |
| **ProcessManager** | `ps`, `kill`, `nohup` background processes, monitoring |
| **SystemInspector** | `df`, `free`, `ss`, `systemctl`, `journalctl`, Docker |
| **NetworkTools** | AsyncSSH local/remote/dynamic (SOCKS5) tunnel manager |
| **Orchestrator** | Parallel, rolling, group-tagged, broadcast, playbooks |
| **Security** | Allowlists, blocklists, sliding-window rate limiter |
| **Audit** | JSONL audit trail + in-memory ring buffer for observability |

---

## Tool Reference (40 tools)

### Host Registry
| Tool | Description |
|---|---|
| `ssh_register_host` | Register a host dynamically (name, IP, user, key, tags) |
| `ssh_list_hosts` | List all registered hosts |
| `ssh_remove_host` | Remove a host from the registry |
| `ssh_connection_status` | Show pooled connection health |

### Persistent Sessions
| Tool | Description |
|---|---|
| `ssh_create_session` | Spawn a persistent PTY shell on a host |
| `ssh_session_exec` | Execute command in session (CWD + env persist) |
| `ssh_session_read_buffer` | Read buffered output from a session |
| `ssh_session_set_env` | Inject environment variable into session |
| `ssh_session_list` | List all active sessions |
| `ssh_close_session` | Terminate a session |

### Command Execution
| Tool | Description |
|---|---|
| `ssh_run` | Execute a single command (one-off) |
| `ssh_run_batch` | Execute a JSON array of commands sequentially |
| `ssh_run_script` | Upload and run a script (bash, python3, etc.) |
| `ssh_run_with_env` | Execute with injected environment variables |
| `ssh_exec_retry` | Execute with auto-retry on failure |

### File Operations
| Tool | Description |
|---|---|
| `ssh_upload` | Upload local file → remote via SFTP |
| `ssh_download` | Download remote file → local |
| `ssh_ls` | List remote directory |
| `ssh_cat` | Read remote file contents |
| `ssh_write` | Write content to remote file |
| `ssh_rm` | Delete remote file |
| `ssh_sync` | Recursively sync local dir → remote |

### Process Management
| Tool | Description |
|---|---|
| `ssh_ps` | List remote processes (optionally filtered) |
| `ssh_kill` | Send signal to remote PID |
| `ssh_start` | Start process (foreground or background) |
| `ssh_background` | Start named background process with PID tracking |
| `ssh_monitor` | Monitor resource usage of a PID |

### System Inspection
| Tool | Description |
|---|---|
| `ssh_info` | Full system info (OS, CPU, mem, IPs, uptime) |
| `ssh_df` | Disk usage |
| `ssh_free` | Memory usage |
| `ssh_netstat` | Network status, ports, interfaces, routes |
| `ssh_service` | Systemd service status |
| `ssh_journalctl` | Journal logs with optional service/time filter |
| `ssh_docker` | Docker containers and images |

### Multi-Host Orchestration
| Tool | Description |
|---|---|
| `ssh_parallel` | Same command on N hosts simultaneously |
| `ssh_rolling` | Sequential exec with configurable delay |
| `ssh_group_exec` | Execute on all hosts with a given tag |
| `ssh_broadcast_batch` | Broadcast a command sequence to N hosts |
| `ssh_playbook` | Run a named playbook on one host |
| `ssh_playbook_on_group` | Run a playbook across a tagged group |

### Tunnels & Port Forwarding
| Tool | Description |
|---|---|
| `ssh_port_forward` | Local forward: localhost → remote via SSH host |
| `ssh_reverse_tunnel` | Reverse: remote port → local service |
| `ssh_socks_proxy` | SOCKS5 dynamic proxy via SSH host |
| `ssh_close_tunnel` | Close a tunnel by ID |
| `ssh_active_tunnels` | List all active tunnels |

### Security
| Tool | Description |
|---|---|
| `ssh_security_status` | Show current policy in effect |
| `ssh_check_host_access` | Test if a host passes policy |
| `ssh_check_command` | Dry-run a command through security policy |

### Observability
| Tool | Description |
|---|---|
| `ssh_operation_history` | Recent audit log entries |
| `ssh_audit_stats` | Aggregate operation statistics |
| `ssh_full_status` | Complete snapshot: connections, sessions, tunnels, stats |
| `ssh_ping_host` | Test SSH reachability + latency |
| `ssh_health_check_fleet` | Ping all registered hosts in parallel |

### tmux Management
| Tool | Description |
|---|---|
| `ssh_tmux_new` | Create a remote tmux session |
| `ssh_tmux_send` | Send command to tmux + capture output |
| `ssh_tmux_list` | List tmux sessions on remote |
| `ssh_tmux_kill` | Kill a remote tmux session |

---

## Host Configuration (`config/hosts.yaml`)

```yaml
hosts:
  web01:
    host: 10.0.0.10
    port: 22
    user: root
    key: ~/.ssh/id_ed25519
    tags: [web, production]

  db01:
    host: 10.0.0.20
    user: ubuntu
    key: ~/.ssh/id_ed25519
    tags: [database, production]

  staging:
    host: 192.168.1.50
    port: 2222
    user: deploy
    key: ~/.ssh/staging_key
    tags: [staging]
```

All fields except `host` are optional. `tags` enable group operations via `ssh_group_exec` and `ssh_playbook_on_group`.

You can also register hosts dynamically at runtime:
```
ssh_register_host(name="new-server", host="10.0.0.99", user="root", key_path="~/.ssh/id_ed25519", tags="web,production")
```

---

## Security Model (`config/policies.yaml`)

| Feature | Default | Description |
|---|---|---|
| `host_allowlist` | empty (all) | Restrict to named hosts/patterns |
| `command_blocklist` | `rm -rf /`, `mkfs*` … | Block dangerous commands |
| `command_allowlist` | empty (all) | If set, only these commands run |
| `rate_limit_rps` | 20 | Max ops/second per host |
| `max_concurrent` | 50 | Connection pool size |
| `connection_timeout` | 30s | SSH connect timeout |
| `sandbox_users` | empty | Force per-host username |

All operations are logged to `logs/audit.jsonl`:
```json
{"timestamp":"2026-03-12T10:00:00Z","agent_id":"agent","host":"web01","operation":"exec","command":"docker ps","result":"0"}
```

---

## Deployment

### Option A — Direct (stdio, for Claude Desktop)

```bash
cd /path/to/ssh-shell-mcp
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python server.py --transport stdio
```

Add to `~/.config/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "ssh-shell-mcp": {
      "command": "/path/to/ssh-shell-mcp/venv/bin/python",
      "args": ["/path/to/ssh-shell-mcp/server.py", "--transport", "stdio"],
      "env": {
        "SSH_HOSTS_YAML": "/path/to/ssh-shell-mcp/config/hosts.yaml",
        "SSH_POLICIES_YAML": "/path/to/ssh-shell-mcp/config/policies.yaml",
        "SSH_MCP_LOG_DIR": "/path/to/ssh-shell-mcp/logs"
      }
    }
  }
}
```

### Option B — Docker (HTTP transport)

```bash
cd /path/to/ssh-shell-mcp
docker compose up -d
# Server listens on http://localhost:8010/mcp
```

With auth token:
```bash
MCP_AUTH_TOKEN=your-secret docker compose up -d
```

### Option C — Python venv + HTTP

```bash
python server.py --transport streamable_http --port 8010
```

---

## Example Workflows

### Deploy Docker to a fleet
```python
ssh_playbook_on_group(
  group_tag="production",
  playbook_json='''{
    "name": "deploy_docker",
    "on_error": "stop",
    "steps": [
      "apt-get update -qq",
      "apt-get install -y docker.io",
      "systemctl enable --now docker",
      "docker pull myapp:latest",
      "docker compose -f /opt/app/docker-compose.yml up -d"
    ]
  }'''
)
```

### Forward a private database
```python
ssh_port_forward("bastion", local_port=5432, remote_host="db.internal", remote_port=5432)
# Now connect: psql -h 127.0.0.1 -p 5432
```

### Persistent deployment session
```python
sid = ssh_create_session("web01")
ssh_session_exec(sid, "cd /opt/app")
ssh_session_exec(sid, "git pull origin main")
ssh_session_exec(sid, "docker compose up -d --build")
ssh_session_exec(sid, "docker compose logs --tail=20")
```

### Rolling restart with health checks
```python
ssh_rolling(
  hosts_json='["web01","web02","web03"]',
  command="systemctl restart nginx && sleep 3 && systemctl is-active nginx",
  delay_s=5.0,
  stop_on_error=True
)
```

### Monitor a background job
```python
result = ssh_background("worker01", "python3 /opt/jobs/import.py", name="data_import")
# → {"pid": "12345", "log_file": "/tmp/data_import.log"}
ssh_monitor("worker01", pid=12345)
ssh_run("worker01", "tail -f /tmp/data_import.log")
```

---

## Testing

```bash
# Requires a local SSH server (sshd must be running on 127.0.0.1:22)
cd /path/to/ssh-shell-mcp
pip install pytest pytest-asyncio
pytest tests/ -v
```

Environment variables for remote testing:
```bash
export TEST_HOST=10.0.0.10
export TEST_USER=root
export TEST_KEY_PATH=~/.ssh/id_ed25519
pytest tests/ -v
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SSH_HOSTS_YAML` | `config/hosts.yaml` | Path to host registry |
| `SSH_POLICIES_YAML` | `config/policies.yaml` | Path to policy config |
| `SSH_MCP_LOG_DIR` | `logs/` | Directory for logs |
| `MCP_AUTH_TOKEN` | *(empty)* | Bearer token for HTTP transport |
