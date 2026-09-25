# CLAUDE.md

Claude Code 在本仓库工作时的指引。本文件保持简短：只写项目概览、权威源、常用命令与工作流；治理规范正文一律不在本文件重复。

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

## 常用命令

在仓库根目录执行：

```text
python3 scripts/verify_delivery_governance.py
python3 scripts/verify_agent_entry.py
python3 scripts/verify_skills.py
python3 -m unittest discover -s tests -q
```

切换活动 CHG 后重新生成执行快照：

```text
python3 scripts/prepare_ai_workspace.py --change <CHG>
```

已知红项、成因与不在范围内的说明见 `README.md` 的 Verification 一节。不要假设本仓库门禁整体是绿的。

## 目录结构

| 路径 | 用途 |
| --- | --- |
| `AGENT-INDEX.md` | 治理规范与路由正文（权威源） |
| `AGENTS.md` / `CLAUDE.md` | Codex / Claude Code 薄入口，指向 `AGENT-INDEX.md` |
| `.ai/CURRENT_CONTEXT.md` | 唯一执行快照（生成物） |
| `docs/product` | 产品基线：需求、场景、目标、验收标准 |
| `docs/engineering` | 工程基线：`architecture` 架构与模块边界，`specs` 技术规范 |
| `docs/contracts` | 跨仓协议治理：API、Cloud–Agent、Cloud–Desktop、Event Schema |
| `docs/decisions` | 耐久决策记录（ADR） |
| `delivery` | 交付治理：`LEDGER.md`、`milestones`、`active`、`planned`、`completed` |
| `config` | repository-map、skills-distribution、contract-map、release-matrix |
| `skills` | Codex / Claude skill 唯一源文件 |
| `scripts` | 快照生成、skill 分发、入口与治理校验 |
| `templates/delivery` | CHG 与 evidence 模板 |

## 工作流

1. 读 `AGENT-INDEX.md` 与 `.ai/CURRENT_CONTEXT.md`，确认当前 CHG、范围与验收标准。
2. 按快照给出的顺序读取稳定基线与当前 CHG 记录；历史记录默认不加载。
3. 判断真正发生修改的能力属于哪个工程，路由到该仓库并读其 `AGENT-INDEX.md` 与 `DIRECTORY_MAP.md`。
4. 在对应工程仓库修改代码；本仓库只写知识、规范、决策与交付状态。
5. 结束前更新当前 CHG 的 checkpoint：已完成、未完成、阻塞、下一步。

## 提交约定

提交信息采用 Conventional Commits：`<type>(<scope>): <subject>`，scope 用 CHG 号、Milestone 或仓库名。一仓一 commit；纯移动与改逻辑不放进同一个 commit。

## 高频红线

以下四条最容易出错，完整规则与例外见 `AGENT-INDEX.md`：

- 运行时改动不落在本仓库，本仓库也不得被运行时依赖。
- `.ai/CURRENT_CONTEXT.md` 不手工编辑，执行根父层不留副本。
- 讨论、建议与假设不是需求；只有 Delivery 或 Decision 中确认的内容可以驱动修改。
- `skills/` 是唯一源，`.claude/skills` 与 `.codex/skills` 是生成副本，不手改。

## 延伸阅读

- [`AGENT-INDEX.md`](AGENT-INDEX.md) —— 治理规范与需求路由（权威源）
- [`README.md`](README.md) —— 目录说明、校验命令与已知红项
- [`docs/engineering/specs/agent-workspace-conventions.md`](docs/engineering/specs/agent-workspace-conventions.md) —— 入口文件、上下文加载与校验约定
