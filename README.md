# ssh-shell-mcp

> A Python [MCP](https://modelcontextprotocol.io/) server providing **57+ SSH tools** for remote shell operations, fleet orchestration, tunneling, and file management — built on [AsyncSSH](https://asyncssh.readthedocs.io/) and [FastMCP](https://github.com/jlowin/fastmcp).

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-compatible-brightgreen)](https://modelcontextprotocol.io/)

---

## Overview

`ssh-shell-mcp` turns any SSH-accessible host into a fully agentic target. It exposes a structured set of MCP tools that an AI agent (e.g. Claude Desktop) can call to execute commands, manage files, forward ports, orchestrate fleets, and more — all over SSH without exposing credentials in prompts.

---

## Features

| Category | Examples |
|---|---|
| **Shell execution** | Run commands, interactive shells, sudo operations |
| **File management** | Upload, download, read, write, stat, chmod, chown |
| **Fleet orchestration** | Run commands across multiple hosts in parallel |
| **Port forwarding & tunnels** | Local/remote/dynamic SOCKS tunnels |
| **Process management** | List, kill, monitor processes |
| **System info** | CPU, memory, disk, uptime, OS details |
| **User management** | Add/remove users, manage SSH authorized keys |
| **Service control** | systemctl start/stop/status/enable/disable |
| **Network diagnostics** | ping, netstat, route, DNS lookups |
| **Log inspection** | Tail logs, journalctl, syslog queries |
| **Package management** | apt/yum/dnf install, update, remove |
| **Cron management** | List, add, remove cron jobs |
| **Docker integration** | Container list, exec, logs, start/stop |
| **Extras (13 tools)** | Gap-audit additions: SCP batch, host health checks, etc. |

---

## Requirements

- Python 3.10+
- [`asyncssh`](https://pypi.org/project/asyncssh/) >= 2.14
- [`fastmcp`](https://pypi.org/project/fastmcp/) >= 0.1
- An MCP-compatible client (e.g. [Claude Desktop](https://claude.ai/download))
- SSH access to your target hosts (key-based auth recommended)

---

## Installation

```bash
git clone https://github.com/jaguar999paw-droid/ssh-shell-mcp.git
cd ssh-shell-mcp

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Configuration

Copy the example config and fill in your values:

```bash
cp config.example.json config.json
```

**`config.json` structure:**

```json
{
  "hosts": {
    "my-server": {
      "hostname": "192.168.1.100",
      "port": 22,
      "username": "your-user",
      "key_path": "~/.ssh/id_ed25519"
    },
    "prod-web": {
      "hostname": "10.0.0.5",
      "port": 22,
      "username": "deploy",
      "key_path": "~/.ssh/deploy_key"
    }
  },
  "default_timeout": 30,
  "max_parallel_hosts": 10
}
```

> **Never commit `config.json`** — it is already in `.gitignore`.

---

## Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ssh-shell": {
      "command": "/path/to/ssh-shell-mcp/.venv/bin/python",
      "args": ["-m", "ssh_shell_mcp.server"],
      "env": {
        "SSH_MCP_CONFIG": "/path/to/ssh-shell-mcp/config.json"
      }
    }
  }
}
```

Replace `/path/to/ssh-shell-mcp` with your actual clone path.

---

## Project Structure

```
ssh-shell-mcp/
├── ssh_shell_mcp/
│   ├── __init__.py
│   ├── server.py              # FastMCP server entrypoint
│   ├── core.py                # AsyncSSH connection pool
│   ├── tools/
│   │   ├── shell.py           # Command execution tools
│   │   ├── files.py           # File management tools
│   │   ├── fleet.py           # Multi-host orchestration
│   │   ├── tunnels.py         # Port forwarding / SOCKS
│   │   ├── system.py          # System info & process tools
│   │   ├── services.py        # systemctl tools
│   │   ├── network.py         # Network diagnostics
│   │   ├── docker_tools.py    # Docker integration
│   │   └── ...
│   └── ssh_shell_mcp_extras.py  # 13 gap-audit tools
├── config.example.json
├── requirements.txt
├── .gitignore
├── SECURITY.md
├── LICENSE
└── README.md
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SSH_MCP_CONFIG` | Path to `config.json` | `./config.json` |
| `SSH_MCP_LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`) | `INFO` |
| `SSH_MCP_TIMEOUT` | Global SSH operation timeout (seconds) | `30` |

---

## Security

- **Key-based auth only** — password auth is intentionally unsupported to discourage weak credential use.
- **Config file isolation** — host credentials live in `config.json`, never in code.
- **No telemetry** — this server makes no outbound connections except to your configured SSH hosts.
- See [SECURITY.md](SECURITY.md) for vulnerability reporting.

---

## ⚠️ Legal Notice

This tool provides programmatic SSH access to remote systems. **Use only on systems you own or have explicit written authorization to access.** Unauthorized access to computer systems is illegal in most jurisdictions.

---

## 🔐 Cryptography Notice

This software implements the SSH protocol, which uses cryptographic algorithms. Export, import, and use of cryptographic software may be restricted in some jurisdictions. Users are responsible for compliance with applicable laws. See the [Wassenaar Arrangement](https://www.wassenaar.org/) for reference.

---

## License

[Apache License 2.0](LICENSE) — see the LICENSE file for full terms.
