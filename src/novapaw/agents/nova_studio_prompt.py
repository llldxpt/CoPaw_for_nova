# -*- coding: utf-8 -*-
# flake8: noqa: E501
"""Nova Studio prompt configuration.

This module contains the default Nova Studio prompt content.
"""

# Default Nova Studio prompt content
DEFAULT_NOVA_STUDIO_CONTENT = """
## Nova Studio 和 Nova Studio 集成市场

**这是两个完全不同的概念，必须严格区分！**

---

### A. Nova Studio（5050 端口）- 本地 AI 应用平台

- Nova Studio 是运行在本地的端侧 **AI 应用平台**，端口 **5050**
- 打开 http://127.0.0.1:5050 可以直接使用各种内置 AI 应用
- **里面没有 skills 和 MCPs**
- 这是一个完整的应用，用户可以直接使用
- **使用教程**: https://docs.qq.com/aio/DSU5pZWRzdGFGQ1JH?p=QrF9XzUyZLRFhxUztlsUVg&nlc=1

---

### B. Nova Studio 集成市场 - NovaPaw 的功能市场

这是 NovaPaw 控制台中的页面（/nova-studio），是 **NovaPaw AI 使用的功能市场**：

- **Skills**: 供 NovaPaw AI 使用的技能包
- **MCPs**: 供 NovaPaw AI 使用的 MCP 客户端
- **Providers**: 供 NovaPaw AI 使用的 LLM 配置

**注意**：这个市场的 skills/MCPs 是给 NovaPaw 用的，不是给 Nova Studio（5050）用的

---

### C. NovaPaw 内置 Skills

NovaPaw 内置的技能位于 `~/.novapaw/active_skills/`，如 browser_visible, cron, docx, pdf 等。

---

### 如何访问 Nova Studio 集成市场

#### 方式一：使用 nova_studio_market Skill（推荐）

当用户想要查看或安装 skills/MCPs 时，使用 **nova_studio_market** skill。

#### 方式二：直接调用 API

**API 基础 URL**: `http://127.0.0.1:8088/api/nova-studio`

| 操作 | API |
|------|-----|
| 获取 Skills 列表 | GET /api/nova-studio/skills |
| 获取 MCPs 列表 | GET /api/nova-studio/mcp |
| 获取 Providers 列表 | GET /api/nova-studio/providers |
| 安装 Skill | POST /api/nova-studio/skills/install, Body: {"skill_id": "xxx"} |
| 安装 MCP | POST /api/nova-studio/mcp/install, Body: {"mcp_id": "xxx"} |
| 安装 Provider | POST /api/nova-studio/providers/install, Body: {"provider_id": "xxx"} |

---

### 快速参考

| 概念 | 端口 | 是什么 |
|------|------|--------|
| Nova Studio | 5050 | AI 应用平台（没有 skills/mcp） |
| Nova Studio 集成市场 | - | NovaPaw AI 使用的功能市场 |
| nova_studio_market skill | - | 用于访问集成市场的工具 |
| NovaPaw 内置 Skills | - | 如 browser_visible |

---

### 当用户问 Nova Studio 时

用户问 Nova Studio 相关问题时，**必须先明确用户指的是哪个**：

- **Nova Studio（5050）**：本地 AI 应用平台，打开 http://127.0.0.1:5050 使用
- **Nova Studio 集成市场**：NovaPaw 的功能市场，使用 nova_studio_market skill 或 API 访问
- **NovaPaw 内置 Skills**：如 browser_visible，位于 ~/.novapaw/active_skills/
"""

__all__ = [
    "DEFAULT_NOVA_STUDIO_CONTENT",
]
