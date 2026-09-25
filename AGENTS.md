# WT Media Workspace Agent Rules（Codex 入口）

本文件是 Codex / OpenAI Harness 的入口，只声明权威源与最小硬约束，不承载治理规范正文。

## 权威源

治理规范、仓库职责边界、需求路由与上下文加载规则的唯一文本是 [`AGENT-INDEX.md`](AGENT-INDEX.md)。本文件不重复其内容；表述冲突时以该文件为准。

| 文件 | 角色 |
| --- | --- |
| `AGENT-INDEX.md` | 统一索引与治理规范正文（唯一权威源） |
| `AGENTS.md` | 本文件：Codex / OpenAI Harness 入口，只做指针 |
| `CLAUDE.md` | Claude Code 入口，只做指针 |
| `.ai/CURRENT_CONTEXT.md` | 全项目唯一执行快照（生成物） |

读取顺序：

1. `AGENT-INDEX.md`
2. `.ai/CURRENT_CONTEXT.md`
3. `.ai/CURRENT_CONTEXT.md` 指明的当前 CHG

`AGENTS.md` 与 `CLAUDE.md` 平级：互不软链、互不替代，二者都指向 `AGENT-INDEX.md`。

## 最小硬约束

- 本仓库是治理中心，不是运行时代码仓库；运行时改动只在对应工程仓库执行。
- 关联工程路径以 `config/repository-map.yaml` 为准，脚本与文档不得另行硬编码，也不得与之漂移。
- `.ai/CURRENT_CONTEXT.md` 是全项目唯一的执行快照，由脚本生成；手工编辑无效，执行根父层不得出现副本。
- 讨论、建议与假设不是需求。只有 Delivery 或 Decision 中确认的内容可以驱动修改。
- 结束任何开发任务前更新 checkpoint：已完成、未完成、阻塞、下一步。
