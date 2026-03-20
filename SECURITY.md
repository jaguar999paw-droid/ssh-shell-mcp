# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| `main` branch | ✅ Active |
| Older tags | ❌ No backports |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report security issues privately via one of the following channels:

- **GitHub Security Advisories:** Use the [Report a Vulnerability](https://github.com/jaguar999paw-droid/ssh-shell-mcp/security/advisories/new) button on this repo.
- **Email:** Contact the maintainer directly through their GitHub profile.

### What to include

- A clear description of the vulnerability
- Steps to reproduce (proof-of-concept if available)
- Potential impact assessment
- Any suggested mitigations

### Response timeline

- **Acknowledgement:** Within 48 hours
- **Initial assessment:** Within 7 days
- **Resolution target:** Within 30 days for critical issues

## Security Considerations for Users

### Credential handling
- Store SSH private keys with `chmod 600` permissions
- Never commit `config.json` or any file containing hostnames, usernames, or key paths
- Use dedicated deploy keys with minimal privilege where possible

### Network exposure
- This MCP server binds to `stdio` by default and does not open any network ports on the MCP host
- All outbound connections are explicitly to your configured SSH targets
- Running behind a VPN (e.g. Tailscale) for remote targets is strongly recommended

### Principle of least privilege
- Create dedicated SSH users for automated access rather than using `root` or personal accounts
- Restrict SSH user permissions using `AllowUsers`, `Match` blocks, or `ForceCommand` in `sshd_config`

## Known Limitations

- Password-based SSH authentication is not supported by design
- Host key verification uses the system `known_hosts` by default; disabling it weakens MITM protection
