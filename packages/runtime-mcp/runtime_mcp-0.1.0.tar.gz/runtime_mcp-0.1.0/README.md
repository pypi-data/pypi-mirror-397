# MCP STDIO Proxy Client

## Project Role
- Transparent MCP client that reads JSON-RPC requests from STDIN, sends them to a remote MCP Engine via HTTP, and writes responses back to STDOUT without modification.
- No embeddings, databases, caching, or local model logic; every capability lives entirely in the remote MCP Engine.

## Relationship With the MCP Engine
- Acts purely as a byte-level transport bridge for JSON-RPC messages.
- Any MCP-conformant engine reachable over HTTP can be used; the proxy never inspects business semantics.

## Quick Start
1. Install (optional):
   ```bash
   pip install -e .
   ```
2. Configure environment variables:
   ```bash
   export SERVER_URL=http://127.0.0.1:14501
   export RPC_PATH=/mcp/rpc
   export AUTHORIZATION=0123456789ABCDEF
   export HTTP_TIMEOUT=30
   ```
   When `SERVER_URL` is omitted the proxy defaults to `https://runtime.lincloud.cn`, and `AUTHORIZATION` can be unset if the remote engine does not require it.
3. Launch via `runtime` or `python -m runtime.main`.
4. Send JSON-RPC over STDIN, e.g.:
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | runtime
   ```

## Authorization Forwarding
Priority order for the HTTP `Authorization` header:
1. `params.authorization` when present and exactly 16 characters.
2. Environment variable `AUTHORIZATION` if set.
3. No header when neither source exists.

## Error Handling
- Invalid JSON input -> `code: -32700`.
- HTTP/network failures or remote non-JSON responses -> `code: -32000` with the specific proxy error message.
- The proxy always echoes the original `id` whenever possible and preserves `jsonrpc: "2.0"`.

## Process Lifecycle
- Produces no extra STDOUT noise; only raw JSON-RPC responses are emitted.
- Terminates gracefully on EOF, `Ctrl+C`, or startup configuration errors.

## Development
- Requires Python 3.9 or later and no additional dependencies.
- Layout:
  ```
  runtime/
    config.py
    http_client.py
    main.py
  ```
