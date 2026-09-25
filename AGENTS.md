# WT Media Workspace Agent Rules（Codex 入口）

- 正文：`AGENT-INDEX.md`

本文件是 Codex / OpenAI Harness 的入口，只声明权威源与读取入口，不承载治理规范正文。

## 权威源

治理规范、仓库职责边界、需求路由、上下文加载规则与**全部红线的唯一文本**是 [`AGENT-INDEX.md`](AGENT-INDEX.md)。本文件不重复其内容——包括 §2 的红线：入口文件一旦复述，`AGENT-INDEX.md` 改动时就会静默过期。

| 文件 | 角色 |
| --- | --- |
| `AGENT-INDEX.md` | 统一索引与治理规范正文（唯一权威源） |
| `AGENTS.md` | 本文件：Codex / OpenAI Harness 入口，只做指针 |
| `CLAUDE.md` | Claude Code 入口，只做指针 |
| `.ai/CURRENT_CONTEXT.md` | 全项目唯一执行快照（生成物） |

读取顺序见 [`AGENT-INDEX.md`](AGENT-INDEX.md) §4——该节是全项目唯一落点，本文件不重复其清单。

## 红线

本仓全部不可协商的红线，唯一落点是 [`AGENT-INDEX.md`](AGENT-INDEX.md) §2。本文件**不复述其正文**：复述就是 §2 的第二个落点，§2 一改它就静默过期，而没有任何机制会提醒。开工前先读 §2。

`AGENTS.md` 与 `CLAUDE.md` 平级：互不软链、互不替代，二者都指向 `AGENT-INDEX.md`。
