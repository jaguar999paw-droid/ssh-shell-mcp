# Contributing to ssh-shell-mcp

Thanks for your interest! Here's how to contribute effectively.

## Development Setup

```bash
git clone https://github.com/jaguar999paw-droid/ssh-shell-mcp.git
cd ssh-shell-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config.example.json config.json   # fill in your test hosts
```

## Adding a New Tool

1. Identify which module it belongs to (`tools/shell.py`, `tools/files.py`, etc.)
2. Add the function with a `@mcp.tool()` decorator
3. Include a clear docstring — the docstring becomes the tool's MCP description
4. Add the tool to `docs/tools.md`
5. Write a test in `tests/`

**Docstring format:**

```python
@mcp.tool()
async def my_new_tool(host: str, param: str) -> str:
    """
    One-line summary of what this tool does.

    Args:
        host: Name of the configured SSH host to connect to.
        param: Description of what this parameter controls.

    Returns:
        Human-readable result string.
    """
```

## Coding Standards

- Python 3.10+, typed where possible
- `async/await` throughout — no blocking I/O
- No hardcoded hostnames, usernames, IPs, or paths — always read from config
- Keep each tool focused on one operation
- Handle SSH exceptions gracefully and return descriptive error strings

## Pull Request Checklist

- [ ] No secrets, real hostnames, or personal details in any file
- [ ] `config.example.json` updated if new config keys added
- [ ] Docstrings written for all new tools
- [ ] `docs/tools.md` updated
- [ ] `requirements.txt` updated if new deps added

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add docker container exec tool
fix: handle broken pipe on long-running commands
docs: update Claude Desktop integration example
chore: bump asyncssh to 2.15.0
```
