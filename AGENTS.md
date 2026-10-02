# WT Media Workspace（Codex 入口）

## 项目定位

WT Media Workspace 是多工程系统的研发控制中心（Engineering Control Plane），负责系统级产品、架构、跨仓协议、技术决策、Delivery 和 AI 协作。

本仓保存研发知识和交付状态，不承载业务运行时代码，也不成为运行时依赖。

## 关联工程

| 工程 | 主要职责 |
| --- | --- |
| `wt-media-cloud` | 业务事实、Backend、Cloud Runtime，以及 Cloud / Desktop 共用的 Vue 业务源码 |
| `wt-media-agent` | 运营电脑上的本地执行、浏览器自动化和本地资源操作 |
| `wt-media-desktop` | Tauri Runtime、系统桥、Local Agent Sidecar 和安装包 |

工程路径由 `config/repository-map.yaml` 统一维护。找不到工程时核对配置，不猜测路径。

详细 Ownership 以 `AGENT-INDEX.md` 和目标仓规则为准。

## 任务执行

开始任务时先读 `AGENT-INDEX.md`；需要当前交付状态时读取 `.ai/CURRENT_CONTEXT.md`。

根据任务选择执行方式：

| 类型 | 使用场景 |
| --- | --- |
| Milestone | 阶段目标和 CHG 规划，不直接作为代码实施单元 |
| CHG | 中大型功能、跨仓、Architecture 或 Contract 变化 |
| 单仓任务 | 范围明确且不涉及跨仓、Architecture 或 Contract 变化 |
| 分析 / 小修改 | 调研、定位、文档、小 Bug 等，可直接处理 |

涉及具体工程时，读取目标仓的 `CLAUDE.md` 和 `AGENT-INDEX.md`；目标位置不明确时再读取 `DIRECTORY_MAP.md`，然后进入相关代码和测试。

## 相关文档

| 内容 | 位置 |
| --- | --- |
| 产品 | `docs/product/` |
| 架构与工程规范 | `docs/engineering/` |
| 跨仓协议 | `docs/contracts/` |
| 技术决策 | `docs/decisions/` |
| 可引用的状态说明 | `reference/state-models/` |
| Milestone / CHG / 交付状态 | `delivery/` |
| 当前执行快照 | `.ai/CURRENT_CONTEXT.md` |

## 相关约束

- 运行时代码只修改在所属工程，不复制目标工程的本仓规则到 Workspace。
- 按任务渐进加载上下文，不默认扫描全量代码、`delivery/completed/`、历史材料或全量 Skills。
- CHG 只执行已确认范围；发现跨仓 Contract、Architecture 或 Ownership 变化时回到 Workspace 更新定义。
- 不建立第二套 Delivery、任务状态或临时 context。
