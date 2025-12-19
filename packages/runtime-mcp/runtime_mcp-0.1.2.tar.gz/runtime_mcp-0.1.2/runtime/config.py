from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urljoin

DEFAULT_RPC_PATH = "/mcp/rpc"
DEFAULT_HTTP_TIMEOUT = 30.0
DEFAULT_SERVER_URL = "https://runtime.lincloud.cn"


@dataclass(frozen=True)
class ProxyConfig:

    server_url: str
    rpc_path: str
    default_authorization: str | None
    http_timeout: float

    @property
    def endpoint(self) -> str:
        base = self.server_url.rstrip("/") + "/"
        path = self.rpc_path.lstrip("/")
        return urljoin(base, path)


def load_config() -> ProxyConfig:
    server_url = os.environ.get("SERVER_URL") or DEFAULT_SERVER_URL
    rpc_path = os.environ.get("RPC_PATH", DEFAULT_RPC_PATH)
    default_authorization = os.environ.get("AUTHORIZATION") or None
    timeout_raw = os.environ.get("HTTP_TIMEOUT")

    http_timeout = DEFAULT_HTTP_TIMEOUT
    if timeout_raw:
        try:
            http_timeout = float(timeout_raw)
        except ValueError as exc:
            raise RuntimeError("HTTP_TIMEOUT must be numeric") from exc

    return ProxyConfig(
        server_url=server_url,
        rpc_path=rpc_path,
        default_authorization=default_authorization,
        http_timeout=http_timeout,
    )
