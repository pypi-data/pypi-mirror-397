# Runtime（云端 MCP 引擎接入器）

简体中文 | [English](./README.md)

---
Runtime 是一个 **可直接接入云端 MCP Runtime 的 MCP 客户端**。
通过 **STDIO 方式运行**，让你的 AI 客户端（如 Claude Desktop、Chatbox）立即获得云端任务管理与知识库能力，而 **无需在本地部署数据库或任何大模型**。

---

## 能实现什么

通过本 MCP，你可以在任何 **支持 MCP 协议** 的客户端中直接使用以下能力：

### 📋 智能任务系统（Task）
- 创建任务（支持步骤 / 子任务）
- 查询任务列表与任务状态
- 删除任务
- 任务数据与 AI 执行流程解耦，适合自动化与 Agent 工作流

### 🧠 云端知识库（Knowledge Base）
- 语义向量检索（Semantic Search）
- 支持 RAG、长期记忆、资料查询
- 结构化知识（标题 / 正文 / 标签 / 分类）

---

## 项目亮点

### ✨ 无需本地部署任何模型
- **极简接入：** 支持 npx 或 uvx 一键启动。
- **资源零消耗：** 复杂的计算与存储均在云端完成，特别适合移动端或轻量级电脑。
- **全客户端通用：** 完美适配 Claude Desktop, Chatbox, Cherry Studio 以及任何标准 MCP 客户端。
- **移动端友好：** 在移动端 AI 客户端中，只需填写 HTTP 地址和 KEY 即可唤醒云端能力。
- **跨平台一致性：** 无论在桌面端通过 STDIO 还是在手机端通过 HTTP，访问的都是同一套云端数据。

---

## 🚀 快速接入

**使用 uvx（Python 环境）**
```json
{
  "mcpServers": {
    "runtime": {
      "command": "uvx",
      "args": ["runtime-mcp"],
      "env": {
        "AUTHORIZATION": "您的16位大写KEY"
      }
    }
  }
}
```

**移动端（HTTP 接入）** 
```shell
# 可流式传输的 HTTP（streamableHttp）
https://runtime.lincloud.cn/mcp

# KEY
AUTHORIZATION:您的16位大写KEY
```


## 环境变量说明

| 变量名             | 是否必填 | 说明                         |
| ------------------ | -------- | ---------------------------- |
| `AUTHORIZATION`    | ✅ 必填  | 16 位用户访问 KEY            |
| `SERVER_URL`       | 可选     | 云端 MCP Runtime 服务地址    |
| `RPC_PATH`         | 可选     | MCP RPC 路径，默认 `/mcp/rpc` |
| `HTTP_TIMEOUT`     | 可选     | HTTP 超时（秒），默认 30     |

### 🔑 用户访问 KEY（必填）

你需要提供一个 **16 位的大写用户访问 KEY**，格式要求如下：

- 仅允许字符：`0–9`、`A–Z`
- 长度必须为 16 位
- 示例：`XAIMP0ETBUIXVP9X`

#### 这个 KEY 的作用

- 用于标识你的用户身份
    
- 决定你可访问的数据空间
    
- 所有 **知识库 / 任务 / 状态数据** 都会与该 KEY 绑定并相互隔离

#### 如何获取 / 使用 KEY

- 你可以 **自行生成任意符合规则的 16 位字符串** 作为 KEY
- 只要在使用时保持一致即可
- 系统不会校验 KEY 的来源或含义（仅校验长度与字符集）

> ⚠️ **请妥善保管你的 KEY。** 任何持有该 KEY 的人，都可以访问对应的数据空间。

#### 示例生成方式（仅示例）

使用 OpenSSL 生成 **16 位大写字母 + 数字** 的 KEY：
```shell
openssl rand -base64 12 | tr -dc 'A-Z0-9' | head -c 16
```
