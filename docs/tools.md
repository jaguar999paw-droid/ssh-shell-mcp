# Tool Reference

Complete index of all MCP tools exposed by `ssh-shell-mcp`.

All tools accept a `host` parameter that maps to a key in your `config.json`.

---

## Shell Execution

| Tool | Description |
|---|---|
| `run_command` | Execute a shell command and return stdout/stderr |
| `run_command_sudo` | Execute a command with sudo privileges |
| `run_script` | Upload and execute a local shell script remotely |
| `run_interactive` | Open an interactive PTY session |
| `run_pipeline` | Execute a multi-command pipeline |
| `run_as_user` | Run a command as a specific user (su/sudo -u) |
| `get_exit_code` | Return the exit code of the last command |

---

## File Management

| Tool | Description |
|---|---|
| `read_file` | Read the contents of a remote file |
| `write_file` | Write content to a remote file |
| `append_file` | Append content to a remote file |
| `upload_file` | Upload a local file to a remote path |
| `download_file` | Download a remote file to a local path |
| `delete_file` | Delete a remote file or directory |
| `copy_file` | Copy a file within the remote host |
| `move_file` | Move/rename a file on the remote host |
| `stat_file` | Get metadata (size, mtime, permissions) of a file |
| `chmod` | Change file permissions |
| `chown` | Change file ownership |
| `mkdir` | Create a directory (with -p support) |
| `list_directory` | List directory contents |
| `find_files` | Find files matching a pattern |
| `disk_usage` | Show disk usage for a path |

---

## Fleet Orchestration

| Tool | Description |
|---|---|
| `fleet_run` | Run a command on multiple hosts in parallel |
| `fleet_upload` | Upload a file to multiple hosts |
| `fleet_status` | Check connectivity and uptime across all hosts |
| `fleet_diff` | Compare a file across multiple hosts |

---

## Port Forwarding & Tunnels

| Tool | Description |
|---|---|
| `forward_local_port` | Open a local port forwarding tunnel |
| `forward_remote_port` | Open a remote port forwarding tunnel |
| `socks_proxy` | Start a SOCKS5 dynamic tunnel |
| `list_tunnels` | List active tunnels |
| `close_tunnel` | Close a specific tunnel by ID |

---

## Process Management

| Tool | Description |
|---|---|
| `list_processes` | List running processes (ps aux) |
| `kill_process` | Kill a process by PID or name |
| `get_process_info` | Get detailed info about a specific PID |
| `wait_for_process` | Wait until a process exits |

---

## System Information

| Tool | Description |
|---|---|
| `get_uptime` | Get system uptime |
| `get_cpu_info` | CPU model, cores, usage |
| `get_memory_info` | RAM usage and availability |
| `get_disk_info` | Mounted filesystems and usage |
| `get_os_info` | OS name, kernel version, architecture |
| `get_hostname` | Retrieve the remote system's hostname |
| `get_env_vars` | List environment variables on the remote host |

---

## Service Control (systemctl)

| Tool | Description |
|---|---|
| `service_start` | Start a systemd service |
| `service_stop` | Stop a systemd service |
| `service_restart` | Restart a systemd service |
| `service_status` | Get the status of a systemd service |
| `service_enable` | Enable a service at boot |
| `service_disable` | Disable a service at boot |
| `list_services` | List all systemd units |

---

## Network Diagnostics

| Tool | Description |
|---|---|
| `ping_host` | Ping a host from the remote machine |
| `traceroute` | Traceroute to a target from the remote machine |
| `netstat` | List open ports and connections |
| `dns_lookup` | Perform a DNS lookup from the remote host |
| `get_interfaces` | List network interfaces and IPs |

---

## Log Inspection

| Tool | Description |
|---|---|
| `tail_log` | Tail the end of a log file |
| `journalctl` | Query systemd journal logs |
| `grep_log` | Search a log file for a pattern |

---

## Package Management

| Tool | Description |
|---|---|
| `apt_install` | Install a package via apt |
| `apt_remove` | Remove a package via apt |
| `apt_update` | Update package lists |
| `yum_install` | Install a package via yum/dnf |

---

## User Management

| Tool | Description |
|---|---|
| `list_users` | List system users |
| `add_user` | Create a new system user |
| `remove_user` | Remove a system user |
| `add_authorized_key` | Add an SSH public key to a user's authorized_keys |
| `remove_authorized_key` | Remove an SSH public key |

---

## Docker Integration

| Tool | Description |
|---|---|
| `docker_ps` | List running containers |
| `docker_exec` | Execute a command in a container |
| `docker_logs` | Fetch container logs |
| `docker_start` | Start a stopped container |
| `docker_stop` | Stop a running container |

---

## Extras (Gap Audit — ssh_shell_mcp_extras.py)

| Tool | Description |
|---|---|
| `scp_batch` | Transfer multiple files in a single SCP operation |
| `host_health_check` | Composite health check (CPU, memory, disk, services) |
| `diff_files` | Diff two remote files |
| `checksum_file` | Compute MD5/SHA256 of a remote file |
| `compress_directory` | tar.gz a remote directory |
| `extract_archive` | Extract a remote archive |
| `sync_directories` | rsync two remote directories |
| `watch_file` | Watch a file for changes |
| `run_tmux_session` | Run a command in a persistent tmux session |
| `list_tmux_sessions` | List active tmux sessions |
| `attach_tmux_session` | Send input to a tmux session |
| `set_cron_job` | Add or update a cron job |
| `remove_cron_job` | Remove a cron job by pattern |

---

*Total: 57+ tools across 14 categories.*
