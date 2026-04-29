# Tool Reference

Complete index of all 57 MCP tools exposed by `ssh-shell-mcp`, grouped by category.

All tools that target a remote host accept a `host_name` parameter matching a key in `config/hosts.yaml`.

---

## 1. Shell Execution

| Tool | Description |
|---|---|
| `ssh_run` | Execute a single command on a remote host; returns stdout/stderr/exit code |
| `ssh_run_batch` | Run a sequence of commands sequentially (stop-on-error supported) |
| `ssh_run_script` | Upload and execute a local script on a remote host |
| `ssh_run_with_env` | Execute a command with explicitly injected environment variables |
| `ssh_exec_retry` | Execute a command with automatic retry on failure |

---

## 2. Persistent Shell Sessions

| Tool | Description |
|---|---|
| `ssh_create_session` | Open a persistent interactive shell session on a remote host |
| `ssh_session_exec` | Execute a command inside an existing session (state/CWD preserved) |
| `ssh_session_read_buffer` | Read recent output from a session's output buffer |
| `ssh_session_set_env` | Inject an environment variable into a running session |
| `ssh_session_list` | List all currently active persistent sessions |
| `ssh_close_session` | Close and destroy a persistent session |

---

## 3. File Management

| Tool | Description |
|---|---|
| `ssh_upload` | Upload a local file to a remote host via SFTP |
| `ssh_download` | Download a file from a remote host to local disk |
| `ssh_ls` | List directory contents on a remote host |
| `ssh_cat` | Read a remote file's contents |
| `ssh_write` | Write content to a remote file (overwrites existing) |
| `ssh_rm` | Delete a file on a remote host |
| `ssh_sync` | Recursively sync a local directory to a remote host |

---

## 4. Process Management

| Tool | Description |
|---|---|
| `ssh_ps` | List running processes on a remote host |
| `ssh_kill` | Send a signal to a remote process by PID |
| `ssh_start` | Start a process on a remote host (foreground or background) |
| `ssh_background` | Start a named background process with PID tracking and log file |
| `ssh_monitor` | Monitor resource usage of a remote process by PID |

---

## 5. System Inspection

| Tool | Description |
|---|---|
| `ssh_info` | Get comprehensive system info: OS, CPU, memory, uptime, kernel |
| `ssh_df` | Show disk usage on a remote host |
| `ssh_free` | Show memory and swap usage |
| `ssh_netstat` | Show network interfaces, open ports, and routing table |
| `ssh_service` | Check systemd service status |
| `ssh_journalctl` | Retrieve systemd journal logs (filterable by unit, PID, time) |
| `ssh_docker` | List Docker containers and images on a remote host |

---

## 6. Fleet Orchestration

| Tool | Description |
|---|---|
| `ssh_parallel` | Execute a command simultaneously on multiple hosts |
| `ssh_rolling` | Execute a command sequentially across hosts with inter-host delay |
| `ssh_group_exec` | Execute a command on all hosts sharing a group tag |
| `ssh_broadcast_batch` | Broadcast a sequence of commands to multiple hosts in parallel |
| `ssh_playbook` | Execute an infrastructure playbook (YAML) on a single host |
| `ssh_playbook_on_group` | Execute a playbook across all hosts in a group |

---

## 7. Tunnels & Proxies

| Tool | Description |
|---|---|
| `ssh_port_forward` | Create a local port forward: `localhost:local_port → remote_host:remote_port` |
| `ssh_reverse_tunnel` | Create a reverse tunnel: `host_name:remote_port → local_host:local_port` |
| `ssh_socks_proxy` | Open a SOCKS5 dynamic proxy through a remote host |
| `ssh_close_tunnel` | Close an active SSH tunnel by ID |
| `ssh_active_tunnels` | List all currently active SSH tunnels |

---

## 8. Security Controls

| Tool | Description |
|---|---|
| `ssh_check_command` | Dry-run a command through the security policy without executing it |
| `ssh_check_host_access` | Check whether a host is accessible under the current policy |
| `ssh_security_status` | Show the current security policy (allowlists, blocklists, rate limits) |

---

## 9. Host Registry

| Tool | Description |
|---|---|
| `ssh_register_host` | Register a new SSH host in the runtime registry |
| `ssh_list_hosts` | List all registered hosts with their connection details |
| `ssh_remove_host` | Remove a host from the registry |
| `ssh_connection_status` | Show the current state of all pooled SSH connections |

---

## 10. Health & Observability

| Tool | Description |
|---|---|
| `ssh_ping_host` | Test SSH connectivity to a registered host |
| `ssh_health_check_fleet` | Ping all hosts (or a subset) in parallel and report status |
| `ssh_full_status` | Return a complete observability snapshot: connections, sessions, tunnels |
| `ssh_operation_history` | Show recent SSH operation history from the audit log |
| `ssh_audit_stats` | Return aggregate statistics from the audit log |

---

## 11. tmux

| Tool | Description |
|---|---|
| `ssh_tmux_new` | Create a new tmux session on a remote host |
| `ssh_tmux_send` | Send a command to a named tmux session |
| `ssh_tmux_list` | List all tmux sessions on a remote host |
| `ssh_tmux_kill` | Kill a tmux session on a remote host |

---

*Total: 57 tools across 11 categories.*
