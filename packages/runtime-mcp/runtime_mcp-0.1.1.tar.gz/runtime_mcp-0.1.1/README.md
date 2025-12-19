Runtime is an MCP client that connects directly to the cloud MCP Runtime. It runs over STDIO so MCP-compatible front-ends (Claude Desktop, Chatbox, etc.) can immediately access cloud task management and knowledge-base capabilities without deploying databases or large models locally.

---

## What You Can Do

Inside any client that speaks the MCP protocol you can invoke the following capabilities:

### 📋 Intelligent Task System
- Create tasks with steps and subtasks
- List tasks and inspect task status
- Delete tasks
- Keep task data decoupled from AI execution flows, ideal for automation and agent workflows

### 🧠 Cloud Knowledge Base
- Semantic vector search
- Power RAG, long-term memory, and document lookup workflows
- Structured entries with title / body / tags / categories

---

## Highlights

### ✨ Zero Local Model Footprint
- **Minimal onboarding:** launch instantly via `npx` or `uvx`.
- **Zero local resource usage:** compute and storage live in the cloud, perfect for lightweight or mobile hardware.
- **Client agnostic:** works with Claude Desktop, Chatbox, Cherry Studio, and any MCP-compliant client.
- **Mobile friendly:** on mobile AI clients you only supply an HTTP endpoint plus key to unlock cloud features.
- **Cross-platform consistency:** whether you connect over STDIO on desktop or HTTP on mobile, you access the same cloud state.

---

## 🚀 Quick Start

**Using uvx (Python environment)**
```json
{
  "mcpServers": {
    "runtime": {
      "command": "uvx",
      "args": ["runtime-mcp"],
      "env": {
        "AUTHORIZATION": "YOUR16CHARUPPERCASEKEY"
      }
    }
  }
}
```

**Mobile (HTTP access)**
```shell
# Stream-capable HTTP (streamableHttp)
https://runtime.lincloud.cn/mcp

# KEY
AUTHORIZATION:YOUR16CHARUPPERCASEKEY
```

## Environment Variables

| Variable        | Required | Description                               |
|-----------------|----------|-------------------------------------------|
| `AUTHORIZATION` | ✅ Yes   | 16-character user access key              |
| `SERVER_URL`    | Optional | Cloud MCP Runtime base URL                |
| `RPC_PATH`      | Optional | MCP RPC path, defaults to `/mcp/rpc`      |
| `HTTP_TIMEOUT`  | Optional | HTTP timeout in seconds, defaults to `30` |

### 🔑 User Access Key (mandatory)

You must supply a 16-character uppercase key that follows these rules:

- Allowed characters: `0–9`, `A–Z`
- Length must be exactly 16
- Example: `XAIMP0ETBUIXVP9X`

#### What the key does

- Identifies your user space
- Determines which data domain you can access
- All knowledge-base, task, and state data are namespaced by this key and isolated from others

#### How to obtain or use a key

- Generate any 16-character string that satisfies the rules
- Keep using the same key consistently
- The system only checks length and character set; it does not validate the key’s origin or meaning

> ⚠️ Keep your key safe. Anyone with the key can access the corresponding data space.

#### Example generation (for reference)

Use OpenSSL to produce a 16-character uppercase alphanumeric key:
```shell
openssl rand -base64 12 | tr -dc 'A-Z0-9' | head -c 16
```
