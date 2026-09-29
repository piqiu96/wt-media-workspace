# WT Media Workspace（Codex 入口）

## 项目定位

WT Media Workspace 是多工程系统的研发控制中心（Engineering Control Plane），管理产品需求、工程架构、跨仓协议、技术决策、Delivery 和 AI 协作规范。

本仓保存知识、规范、决策和交付状态；不存放业务运行时代码、服务实现、构建产物或临时实验代码。

## 关联工程

| 工程 | 主要职责 |
| --- | --- |
| `wt-media-cloud` | 后端服务、API、业务状态和数据 |
| `wt-media-agent` | 本地执行、浏览器自动化和外部副作用 |
| `wt-media-desktop` | Tauri 桌面应用、用户交互和本地桥接 |

工程路径由 `config/repository-map.yaml` 维护。找不到工程时先核对配置和工作区，不猜测路径。

## 任务执行

1. 开始任务时，先读 [`AGENT-INDEX.md`](AGENT-INDEX.md) 了解正式规则，再看 `.ai/CURRENT_CONTEXT.md` 的当前状态。
2. 按任务类型进入对应的 Delivery、稳定文档或工程仓库。

| 类型 | 使用场景 |
| --- | --- |
| Milestone | 阶段目标、闭环和 CHG 规划 |
| CHG | 中大型功能、跨仓改动、架构或 Contract 调整 |
| 单仓任务 | 不触及上述 CHG 条件的单仓工作 |
| 小修改或分析 | 文档修正、小 Bug、分析与建议；可直接处理，不因分析而创建 CHG |

## 相关文档

| 要找什么 | 位置 |
| --- | --- |
| 产品目标 | `docs/product/` |
| 架构和工程规范 | `docs/engineering/` |
| 跨工程协议 | `docs/contracts/` |
| 技术决策 | `docs/decisions/` |
| 当前交付与计划 | `delivery/` |
| 当前执行状态 | `.ai/CURRENT_CONTEXT.md`（生成物） |

## 相关约束

- 本仓不承载运行时代码，也不复制目标工程的本仓规则。
- 按任务加载上下文；不默认扫描全量代码、`delivery/completed/`、历史文档或全量 skills。
- `skills/` 是唯一源；`.claude/skills/`、`.codex/skills/` 等为同步副本，不直接修改。
- 涉及具体工程时，先读目标仓的 `AGENTS.md`，再读该仓的 `AGENT-INDEX.md` 和 `DIRECTORY_MAP.md`，然后看相关代码与测试。
- 不建立第二套任务状态系统。
