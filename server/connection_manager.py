"""
Connection Manager — SSH connection pool, host registry, key-auth.
Manages persistent AsyncSSH connections to multiple remote hosts.
"""
import asyncio
import os
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

import asyncssh
import yaml

logger = logging.getLogger("ssh_mcp.connections")


@dataclass
class HostConfig:
    name: str
    host: str
    port: int = 22
    user: str = "root"
    key: Optional[str] = None
    password: Optional[str] = None
    connect_timeout: int = 30
    known_hosts: Optional[str] = None
    tags: list = field(default_factory=list)


@dataclass
class PooledConnection:
    host_name: str
    conn: asyncssh.SSHClientConnection
    created_at: float
    last_used: float
    in_use: int = 0

    @property
    def is_alive(self) -> bool:
        try:
            return not self.conn.is_closed()
        except Exception:
            return False


class ConnectionManager:
    """
    Manages a pool of AsyncSSH connections keyed by host name.
    Supports host registry from YAML, dynamic registration, and connection reuse.
    """

    def __init__(self, hosts_yaml: str = "config/hosts.yaml", pool_size: int = 5):
        self._registry: dict[str, HostConfig] = {}
        self._pool: dict[str, list[PooledConnection]] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._pool_size = pool_size
        self._hosts_yaml = hosts_yaml
        self._load_registry()

    def _load_registry(self):
        """Load host definitions from YAML file."""
        p = Path(self._hosts_yaml)
        if not p.exists():
            logger.warning(f"hosts.yaml not found at {p}, starting empty registry")
            return
        with open(p) as f:
            data = yaml.safe_load(f) or {}
        hosts = data.get("hosts", {})
        for name, cfg in hosts.items():
            self._registry[name] = HostConfig(
                name=name,
                host=cfg["host"],
                port=int(cfg.get("port", 22)),
                user=cfg.get("user", "root"),
                key=self._resolve_path(cfg.get("key")),
                password=cfg.get("password"),
                connect_timeout=int(cfg.get("connect_timeout", 30)),
                tags=cfg.get("tags", []),
            )
        logger.info(f"Loaded {len(self._registry)} hosts from registry")

    def _resolve_path(self, path: Optional[str]) -> Optional[str]:
        if not path:
            return None
        return str(Path(path).expanduser())

    def register_host(self, name: str, host: str, user: str = "root",
                      port: int = 22, key: Optional[str] = None,
                      password: Optional[str] = None, tags: list = None) -> str:
        """Dynamically register a new host into the registry."""
        self._registry[name] = HostConfig(
            name=name, host=host, port=port, user=user,
            key=self._resolve_path(key), password=password,
            tags=tags or []
        )
        logger.info(f"Registered host: {name} ({user}@{host}:{port})")
        return f"Host '{name}' registered: {user}@{host}:{port}"

    def list_hosts(self) -> list[dict]:
        return [
            {"name": h.name, "host": h.host, "port": h.port,
             "user": h.user, "tags": h.tags}
            for h in self._registry.values()
        ]

    def remove_host(self, name: str) -> str:
        if name in self._registry:
            del self._registry[name]
            return f"Host '{name}' removed from registry"
        return f"Host '{name}' not found"

    async def _get_lock(self, name: str) -> asyncio.Lock:
        if name not in self._locks:
            self._locks[name] = asyncio.Lock()
        return self._locks[name]

    async def _build_connect_kwargs(self, cfg: HostConfig) -> dict:
        kwargs = dict(
            host=cfg.host, port=cfg.port, username=cfg.user,
            connect_timeout=cfg.connect_timeout,
            known_hosts=None,  # permissive by default; override via policies
        )
        if cfg.key:
            kwargs["client_keys"] = [cfg.key]
            kwargs["passphrase"] = None
        elif cfg.password:
            kwargs["password"] = cfg.password
        else:
            # Try default SSH agent / key locations
            default_keys = []
            for k in ["~/.ssh/id_ed25519", "~/.ssh/id_rsa", "~/.ssh/id_ecdsa"]:
                kp = Path(k).expanduser()
                if kp.exists():
                    default_keys.append(str(kp))
            if default_keys:
                kwargs["client_keys"] = default_keys
        return kwargs

    async def get_connection(self, host_name: str) -> asyncssh.SSHClientConnection:
        """Get or create a pooled connection to a host."""
        if host_name not in self._registry:
            raise ValueError(f"Unknown host: '{host_name}'. Register it first.")
        cfg = self._registry[host_name]
        lock = await self._get_lock(host_name)

        async with lock:
            pool = self._pool.get(host_name, [])
            # Reuse alive, available connection
            for pc in pool:
                if pc.is_alive and pc.in_use < self._pool_size:
                    import time
                    pc.last_used = time.time()
                    pc.in_use += 1
                    return pc.conn
            # Prune dead connections
            self._pool[host_name] = [p for p in pool if p.is_alive]
            # Create new connection
            import time
            kwargs = await self._build_connect_kwargs(cfg)
            logger.info(f"Opening SSH connection to {host_name} ({cfg.user}@{cfg.host}:{cfg.port})")
            conn = await asyncssh.connect(**kwargs)
            pc = PooledConnection(
                host_name=host_name, conn=conn,
                created_at=time.time(), last_used=time.time(), in_use=1
            )
            self._pool.setdefault(host_name, []).append(pc)
            return conn

    def release_connection(self, host_name: str, conn: asyncssh.SSHClientConnection):
        """Decrement in-use counter for a connection."""
        for pc in self._pool.get(host_name, []):
            if pc.conn is conn:
                pc.in_use = max(0, pc.in_use - 1)
                return

    async def close_all(self):
        """Close all pooled connections gracefully."""
        for name, pool in self._pool.items():
            for pc in pool:
                try:
                    pc.conn.close()
                    await pc.conn.wait_closed()
                except Exception:
                    pass
        self._pool.clear()
        logger.info("All SSH connections closed")

    def pool_status(self) -> list[dict]:
        import time
        result = []
        for name, pool in self._pool.items():
            for pc in pool:
                result.append({
                    "host": name,
                    "alive": pc.is_alive,
                    "in_use": pc.in_use,
                    "age_s": round(time.time() - pc.created_at, 1),
                    "idle_s": round(time.time() - pc.last_used, 1),
                })
        return result


# Module-level singleton
_manager: Optional[ConnectionManager] = None

def get_manager() -> ConnectionManager:
    global _manager
    if _manager is None:
        hosts_yaml = os.environ.get("SSH_HOSTS_YAML", "config/hosts.yaml")
        _manager = ConnectionManager(hosts_yaml=hosts_yaml)
    return _manager
