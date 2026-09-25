# CLAUDE.md

Claude Code 在本仓库工作时的指引。本文件保持简短：只写项目概览、权威源与最小硬约束；治理规范正文与红线正文一律不在本文件重复。

## 项目概览

WT Media 多项目系统的研发治理仓（Engineering Control Plane），承载产品需求、工程架构、跨仓库协议、技术决策、交付生命周期与 AI 协作规范。

本仓库**不是**运行时代码仓：不存放业务代码、服务运行代码、构建产物或临时文件，也不得成为任何运行时的依赖。运行时代码位于 `../wt-media-cloud`、`../wt-media-agent`、`../wt-media-desktop`。

## 权威源

[`AGENT-INDEX.md`](AGENT-INDEX.md) 是本仓库唯一的治理规范与路由文本——仓库职责边界、知识地图、需求路由、上下文加载、Delivery 与变更规则、**全部红线**都在其中。开始任何任务前先读它。

| 文件 | 角色 |
| --- | --- |
| `AGENT-INDEX.md` | 统一索引与治理规范正文（唯一权威源） |
| `AGENTS.md` | Codex / OpenAI Harness 入口，只做指针 |
| `CLAUDE.md` | 本文件：Claude Code 入口，只做指针 |
| `.ai/CURRENT_CONTEXT.md` | 全项目唯一执行快照（生成物） |

读取顺序见 [`AGENT-INDEX.md`](AGENT-INDEX.md) §4——该节是全项目唯一落点，本文件不重复其清单。

`AGENTS.md` 与本文件平级：互不软链、互不替代，二者都只声明权威源，都不重复 `AGENT-INDEX.md` 的内容。

## 红线

本仓全部不可协商的红线，唯一落点是 [`AGENT-INDEX.md`](AGENT-INDEX.md) §2。本文件**不复述其正文**：复述就是 §2 的第二个落点，§2 一改它就静默过期，而没有任何机制会提醒。开工前先读 §2。
