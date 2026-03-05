---
name: nova_studio_market
description: "用于访问 Nova Studio 集成市场 API 的 skill，可以查询、安装和更新 skills、MCPs 和 providers。注意：这是 Nova Studio 集成市场（NovaPaw 的功能市场），不是 Nova Studio（5050 端口的应用平台）。"
metadata:
  {
    "copaw":
      {
        "emoji": "🛒",
        "requires": {}
      }
  }
---

# Nova Studio 集成市场

本 skill 用于访问 **Nova Studio 集成市场** 的 API，可以查询、安装和更新 skills、MCPs 和 providers。

**注意**：这是 **Nova Studio 集成市场**（NovaPaw 的功能市场），不是 **Nova Studio**（5050 端口的应用平台）。

## 什么是 Nova Studio 集成市场

Nova Studio 集成市场是 **NovaPaw** 的功能市场，提供：
- **Skills**: 供 NovaPaw AI 使用的技能包
- **MCPs**: 供 NovaPaw AI 使用的 MCP 客户端
- **Providers**: 供 NovaPaw AI 使用的 LLM 配置

## API 信息

- **API 基础 URL**: `http://127.0.0.1:8088/api/nova-studio`
- **注意**: 使用前请确保 API 服务正在运行
- **重要**: API 调用需要通过 Python 代码或 HTTP 客户端，不要使用 curl 命令（在 Windows PowerShell 环境中 curl 会出错）

## API 端点

### 查询可用内容

**注意**: 请使用 Python 代码或 HTTP 客户端调用 API，不要使用 curl 命令。

```python
import requests

# 获取 Skills 列表
response = requests.get("http://127.0.0.1:8088/api/nova-studio/skills")
data = response.json()

# 检查哪些有更新
for item in data.get("items", []):
    if item.get("has_update"):
        print(f"{item['name']} 有可用更新: {item['installed_version']} -> {item['version']}")
```

| 操作 | API |
|------|-----|
| 获取 Skills 列表 | GET /api/nova-studio/skills |
| 获取 MCPs 列表 | GET /api/nova-studio/mcp |
| 获取 Providers 列表 | GET /api/nova-studio/providers |

### 安装内容 API

| 操作 | API |
|------|-----|
| 安装 Skill | POST /api/nova-studio/skills/install, Body: {"skill_id": "xxx"} |
| 安装 MCP | POST /api/nova-studio/mcp/install, Body: {"mcp_id": "xxx"} |
| 安装 Provider | POST /api/nova-studio/providers/install, Body: {"provider_id": "xxx"} |

### 获取配置

| 操作 | API |
|------|-----|
| 获取 Configs 列表 | GET /api/nova-studio/configs |
| 获取 Marketplace URLs | GET /api/nova-studio/marketplace/urls |
| 获取 Providers 列表 | GET /api/nova-studio/providers |
| 获取单个 Provider | GET /api/nova-studio/providers/{provider_id} |

## 版本更新功能

API 返回的数据中包含以下字段，用于检测版本更新：

### Skills 返回字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | Skill 标识符 |
| `name` | string | Skill 名称 |
| `version` | string | 远程最新版本号 |
| `installed` | boolean | 是否已安装 |
| `installed_version` | string | 已安装的版本号（如果有） |
| `has_update` | boolean | 是否有可用更新 |

### MCPs 返回字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | MCP 标识符 |
| `name` | string | MCP 名称 |
| `version` | string | 远程最新版本号 |
| `configured` | boolean | 是否已配置 |
| `installed_version` | string | 已配置的版本号（如果有） |
| `has_update` | boolean | 是否有可用更新 |

## 如何查询可用更新

**调用 GET /api/nova-studio/skills**，检查返回数据中的 `has_update` 字段：

```json
{
  "items": [
    {
      "id": "example-skill",
      "name": "Example Skill",
      "version": "2.0.0",
      "installed": true,
      "installed_version": "1.0.0",
      "has_update": true
    }
  ]
}
```

当 `has_update` 为 `true` 时，表示远程有新版本可用。

## 如何执行更新

更新操作与安装操作相同，调用相同的 API 端点即可覆盖安装旧版本：

- 更新 Skill: `POST /api/nova-studio/skills/install`, Body: `{"skill_id": "xxx"}`
- 更新 MCP: `POST /api/nova-studio/mcp/install`, Body: `{"mcp_id": "xxx"}`

## 常见用途

1. **查看可用的 skills**：用户想知道集成市场有哪些 skills 可以安装
2. **查看可用的 MCPs**：用户想知道集成市场有哪些 MCPs 可以安装
3. **查看可用的更新**：用户想知道哪些已安装的内容有新版本
4. **安装 skill**：用户想要安装某个特定的 skill
5. **安装 MCP**：用户想要安装某个特定的 MCP
6. **更新内容**：用户想要更新已安装的内容到最新版本

## 重要提醒

- 本 skill 用于访问 **Nova Studio 集成市场**，不是 Nova Studio（5050 端口的应用平台）
- Nova Studio（5050 端口）是一个 AI 应用平台，里面没有 skills 和 MCPs
- **Nova Studio 使用教程**: https://docs.qq.com/aio/DSU5pZWRzdGFGQ1JH?p=QrF9XzUyZLRFhxUztlsUVg&nlc=1
- 集成市场的 skills/MCPs 是**给 NovaPaw 的 AI 使用的**
- 使用 `has_update` 字段可以检测是否有可用更新
- 更新操作直接调用安装 API 即可
