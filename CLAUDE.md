# CLAUDE.md

Claude Code 在本仓库工作时的指引。本文件保持简短：只写项目概览、权威源与最小硬约束；治理规范正文一律不在本文件重复。

## 项目概览

WT Media 多项目系统的研发治理仓（Engineering Control Plane），承载产品需求、工程架构、跨仓库协议、技术决策、交付生命周期与 AI 协作规范。

本仓库**不是**运行时代码仓：不存放业务代码、服务运行代码、构建产物或临时文件，也不得成为任何运行时的依赖。运行时代码位于 `../wt-media-cloud`、`../wt-media-agent`、`../wt-media-desktop`。

## 权威源与读取顺序

[`AGENT-INDEX.md`](AGENT-INDEX.md) 是本仓库唯一的治理规范与路由文本——仓库职责边界、知识地图、需求路由、上下文加载、Delivery 与变更规则都在其中。开始任何任务前先读它。

| 文件 | 角色 |
| --- | --- |
| `AGENT-INDEX.md` | 统一索引与治理规范正文（唯一权威源） |
| `AGENTS.md` | Codex / OpenAI Harness 入口，只做指针 |
| `CLAUDE.md` | 本文件：Claude Code 入口，只做指针 |
| `.ai/CURRENT_CONTEXT.md` | 全项目唯一执行快照（生成物） |

读取顺序：

1. `AGENT-INDEX.md`
2. `.ai/CURRENT_CONTEXT.md`
3. 当前 CHG：`delivery/active/<change-id>/change.md` 及其 plan / spec / checkpoint

`AGENTS.md` 与本文件平级：互不软链、互不替代，二者都只声明权威源与最小硬约束，都不重复 `AGENT-INDEX.md` 的内容。

## 高频红线

以下四条最容易出错，完整规则与例外见 `AGENT-INDEX.md`：

- 运行时改动不落在本仓库，本仓库也不得被运行时依赖。
- `.ai/CURRENT_CONTEXT.md` 不手工编辑，执行根父层不留副本。
- 讨论、建议与假设不是需求；只有 Delivery 或 Decision 中确认的内容可以驱动修改。
- `skills/` 是唯一源，`.claude/skills` 与 `.codex/skills` 是生成副本，不手改。
