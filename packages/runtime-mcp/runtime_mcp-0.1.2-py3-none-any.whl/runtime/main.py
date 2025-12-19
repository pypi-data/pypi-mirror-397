from __future__ import annotations

import json
import sys
from typing import Any, Optional

from .config import ProxyConfig, load_config
from .http_client import HttpClient, ProxyHTTPError

PARSE_ERROR_CODE = -32700
PROXY_ERROR_CODE = -32000
INVALID_REQUEST_CODE = -32600
REMOTE_JSON_ERROR_MESSAGE = "Proxy HTTP error: Remote response is not valid JSON"


def _emit_error(request_id: Any, code: int, message: str) -> None:
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }
    sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def _emit_raw_line(text: str) -> None:
    cleaned = text.rstrip("\r\n")
    sys.stdout.write(cleaned + "\n")
    sys.stdout.flush()


def _select_authorization(request_obj: dict[str, Any], fallback: Optional[str]) -> Optional[str]:
    params = request_obj.get("params")
    if isinstance(params, dict):
        token = params.get("authorization")
        if isinstance(token, str) and len(token) == 16:
            return token
    return fallback


def _is_valid_json(text: str) -> bool:
    try:
        json.loads(text)
    except json.JSONDecodeError:
        return False
    return True


def _handle_line(raw_line: str, client: HttpClient, default_auth: Optional[str]) -> None:
    request_payload = raw_line.rstrip("\r\n")
    request_id: Any = None
    try:
        request_obj = json.loads(request_payload)

        if not isinstance(request_obj, dict):
            _emit_error(None, INVALID_REQUEST_CODE, "Invalid request")
            return

        request_id = request_obj.get("id")
        authorization = _select_authorization(request_obj, default_auth)

        try:
            response_text = client.post(request_payload, authorization)
        except ProxyHTTPError as exc:
            _emit_error(request_id, PROXY_ERROR_CODE, f"Proxy HTTP error: {exc}")
            return

        if not _is_valid_json(response_text):
            _emit_error(request_id, PROXY_ERROR_CODE, REMOTE_JSON_ERROR_MESSAGE)
            return

        _emit_raw_line(response_text)
    except json.JSONDecodeError:
        _emit_error(None, PARSE_ERROR_CODE, "Parse error")
    except Exception as exc:
        print(f"Unexpected proxy error: {exc}", file=sys.stderr)
        detail = f"{exc.__class__.__name__}: {exc}"
        _emit_error(request_id, PROXY_ERROR_CODE, f"Proxy HTTP error: {detail}")


def run_loop(config: ProxyConfig) -> None:
    client = HttpClient(config)
    for raw_line in sys.stdin:
        if not raw_line.strip():
            continue
        _handle_line(raw_line, client, config.default_authorization)


def main() -> int:
    try:
        config = load_config()
    except RuntimeError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    try:
        run_loop(config)
    except KeyboardInterrupt:
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
