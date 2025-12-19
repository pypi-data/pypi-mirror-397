from __future__ import annotations

from typing import Optional
from urllib.error import HTTPError, URLError
import urllib.request

from .config import ProxyConfig

MAX_BODY_PREVIEW = 1000


class ProxyHTTPError(Exception):
    pass


class HttpClient:
    def __init__(self, config: ProxyConfig) -> None:
        self._config = config

    def _format_body_preview(self, data: bytes) -> str:
        if not data:
            return "<empty>"
        text = data.decode("utf-8", errors="replace")
        if len(text) > MAX_BODY_PREVIEW:
            return text[:MAX_BODY_PREVIEW] + "...(truncated)"
        return text

    def _encode_payload(self, payload: str) -> bytes:
        try:
            return payload.encode("utf-8")
        except UnicodeEncodeError:
            return payload.encode("utf-8", errors="surrogatepass")

    def post(self, payload: str, authorization: Optional[str]) -> str:
        data = self._encode_payload(payload)
        headers = {"Content-Type": "application/json"}
        if authorization:
            headers["Authorization"] = authorization

        request = urllib.request.Request(
            self._config.endpoint,
            data=data,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self._config.http_timeout) as response:
                response_data = response.read()
        except HTTPError as exc:
            body = exc.read()
            preview = self._format_body_preview(body)
            raise ProxyHTTPError(f"HTTP {exc.code}: {preview}") from exc
        except URLError as exc:
            reason = getattr(exc, "reason", exc)
            raise ProxyHTTPError(f"{exc.__class__.__name__}: {reason}") from exc
        except Exception as exc:
            raise ProxyHTTPError(f"{exc.__class__.__name__}: {exc}") from exc

        if not response_data.strip():
            raise ProxyHTTPError("Remote MCP server returned empty response")
        try:
            return response_data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ProxyHTTPError(f"Remote MCP server returned non-text response: {exc}") from exc
