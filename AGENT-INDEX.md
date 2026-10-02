# WT Media Workspace Agent Index

本文件定义 `wt-media-workspace` 的长期 Agent 工作规则，以及 WT Media 多仓之间的任务路由、上下文协作和 Delivery 规则。

系统级 Product、Architecture、Contract、Decision 和 Delivery 由 Workspace 维护；Cloud、Agent、Desktop 的本仓工程规则由各自 `AGENT-INDEX.md` 维护。

本文件不复制产品、架构、协议或运行仓规则，也不记录当前 Milestone、CHG、临时任务状态和本机路径。


## 1. Workspace 与关联工程

`wt-media-workspace` 是 WT Media 的研发控制中心（Engineering Control Plane），负责系统级知识、决策、交付和跨仓协作，不承载运行时代码。

| 仓库 | 主要职责 |
| --- | --- |
| `wt-media-workspace` | Product、Architecture、Contract、Decision、Delivery、AI 协作规则 |
| `wt-media-cloud` | 业务事实、Backend、HTTP API、数据、Cloud Runtime，以及 Cloud Web / Desktop 共用的 Vue 业务源码 |
| `wt-media-agent` | 运营电脑上的本地执行、浏览器自动化、Profile、Cookie、本地文件及其他受控执行 |
| `wt-media-desktop` | Tauri Runtime、系统桥、Local Agent Sidecar 生命周期和安装包 |

任务按实际能力和代码 Ownership 路由，不根据页面名称、产品名称或需求表述机械分仓。

关联工程物理路径统一从：

`config/repository-map.yaml`

读取。

文档和脚本不得维护第二份固定工程路径。


## 2. 核心边界

- Workspace 不存放运行时代码，也不能成为 Cloud、Agent 或 Desktop Runtime 的运行时依赖。
- 运行时代码只修改在其所属工程，不复制到 Workspace。
- 用户讨论、分析、建议和假设不自动进入实施范围；实施以当前明确指令和已确认的 Delivery / Decision 为准。
- 不实现 Delivery 中明确排除的范围。
- `.ai/CURRENT_CONTEXT.md` 是生成内容，禁止手工维护第二份执行快照。
- `skills/` 是 Skill 源目录；分发到各 Harness 的 Skill 副本不手工修改。
- 不建立第二套 Delivery、任务状态或临时上下文系统。


## 3. 系统事实来源

不同类型的信息由不同位置负责，不设置一套覆盖所有内容的全局优先级。

| 位置 | 负责内容 |
| --- | --- |
| `docs/product/` | 产品需求、用户场景、功能目标和产品验收 |
| `docs/engineering/architecture/` | 系统架构、模块边界、分层和通信设计 |
| `docs/engineering/specs/` | 工程规范、技术标准和开发约束 |
| `docs/contracts/` | 跨仓 API、协议、Event Schema 和数据契约 |
| `docs/decisions/` | 已确认的架构选择、技术取舍和 ADR |
| `reference/state-models/` | 可引用的业务状态说明与一致性索引；不独立裁定产品状态或接口枚举 |
| `delivery/` | Milestone、CHG、执行状态、验证和完成交付 |
| `config/` | 仓库映射、Skill 分发、Contract 映射和发布配置等治理配置 |
| `skills/` | Claude Code / Codex Skill 源文件 |
| `scripts/` | 上下文生成、Skill 分发和治理校验工具 |
| `bin/` | 本地开发环境统一启停入口 |

历史分析、旧 Evidence 和已完成 Delivery 不作为当前任务的默认依据。

分析结果只有在进入 Product、Architecture、Contract、Decision 或 Delivery 后，才成为正式项目事实。


## 4. 上下文加载

采用渐进式加载，不要求所有任务读取固定材料。

### 普通分析和小修改

从当前问题开始，只读取解决问题需要的文档、代码和测试。

不因为存在 Workspace 或 `.ai/CURRENT_CONTEXT.md` 就自动创建 CHG。

### CHG 任务

先读取当前 CHG，再根据：

- CHG 的目标与范围；
- References；
- 实施过程中实际发现的依赖；

读取相关 Product、Architecture、Contract、Decision 和代码。

References 是优先入口，不限制任务确实需要的进一步查证。

### 涉及运行仓

进入目标工程时：

1. 使用当前 Harness 对应的入口文件；
2. 读取该仓 `AGENT-INDEX.md`；
3. 目标位置不明确时读取 `DIRECTORY_MAP.md`；
4. 再进入目标代码、直接依赖、调用方和相关测试。

Workspace 不复制运行仓局部规则。

### 默认不加载

默认不做：

- 全量代码扫描；
- `delivery/completed/` 扫描；
- 历史分析和旧 Evidence 扫描；
- 全量 Skills 源码扫描；
- 与任务无关的工程扫描；
- 构建、缓存、临时和生成目录扫描。

任务确实需要扩大范围时可以扩大，并说明要解决的问题。


## 5. Delivery 与跨仓执行

### 任务类型

以下情况通常建立 CHG：

- 中大型功能；
- 跨仓修改；
- Architecture 调整；
- Contract 调整；
- 需要明确范围、计划和验收的工程变更。

以下任务可以直接进行：

- 分析和调研；
- 问题定位；
- 文档修正；
- 小 Bug；
- 明确的小范围单仓修改；
- 不影响行为的简单重构。

如果直接任务在执行过程中扩大为跨仓、架构或 Contract 变化，再进入 CHG 管理。

### CHG 文件

活动 CHG 位于：

`delivery/active/<change-id>/`

文件职责：

- `change.md`
  - 为什么做；
  - 做什么；
  - 范围；
  - References；
  - Acceptance Criteria。

- `plan.md`
  - 如何实现；
  - 复杂或中大型 CHG 使用；
  - 记录技术方案、实施顺序和验证计划。

- `checkpoint.md`
  - 当前完成情况；
  - 未完成内容；
  - 阻塞；
  - 下一步。

- `status/<repo>.md`
  - 仅同一 CHG 需要多个工程并行实施时使用；
  - 记录对应工程的当前进度、修改和验证结果。

单仓 CHG 不创建 `status/`。

不创建独立 `context.md`。

任务上下文由当前 CHG、相关事实源和 `.ai/CURRENT_CONTEXT.md` 共同提供。

### 跨仓执行

Workspace 维护：

- 共同目标；
- CHG 范围；
- 系统级 Contract / Architecture；
- 整体交付状态。

各运行仓维护：

- 自己的代码；
- 本仓工程规则；
- 本仓测试和验证。

Workspace 发起跨仓任务时，直接通过当前 Workspace 上下文访问关联工程，不向运行仓复制临时任务上下文。

运行仓完成自己的 CHG 工作后：

- 多仓 CHG 更新对应 `status/<repo>.md`；
- 整体状态由 Workspace 汇总到 `checkpoint.md`。

如果实施过程中发现需要改变：

- 跨仓 Contract；
- 系统 Architecture；
- 仓库 Ownership；
- 已确认 CHG 范围；

先更新 Workspace 中的共同定义，再继续扩大实现。

### 完成与归档

CHG 完成前确认：

- Acceptance Criteria 满足；
- 必要验证通过；
- 相关 Contract / Architecture 已同步；
- checkpoint 和多仓状态已收口；
- 稳定事实已经进入对应正式文档。

完成记录移入：

`delivery/completed/`
`delivery/completed/` 是历史归档，不作为当前状态依据，也不默认加载。

## 6. Agent 入口与执行快照

### Harness 入口

Workspace 和各运行仓分别维护：

- `AGENTS.md`
  - Codex / OpenAI Harness 入口；

- `CLAUDE.md`
  - Claude Code 入口；

- `AGENT-INDEX.md`
  - 本仓长期 Agent 工作规则。

`AGENTS.md` 与 `CLAUDE.md` 是平级入口。

入口文件负责快速说明：

- 项目定位；
- 关联工程；
- 任务执行；
- 相关文档；
- 关键约束。

详细规则不在入口文件重复。

运行仓额外维护：

- `DIRECTORY_MAP.md`
  - 代码导航；
  - 验证入口；
  - 默认扫描边界。

### CURRENT_CONTEXT

`.ai/CURRENT_CONTEXT.md` 是当前 AI 执行快照，由：

`scripts/prepare_ai_workspace.py`

生成。

它用于提供：

- 当前 Milestone；
- 当前 CHG；
- 当前状态；
- 受影响仓库；
- 当前任务入口；
- 稳定事实源位置。

它不是新的事实源，不复制：

- 产品正文；
- 架构正文；
- Contract 正文；
- 完整 Decision；
- 技术实施方案；
- 历史执行记录。

禁止手工编辑，也不在 Workspace 外建立第二份副本。


## 7. Skills 与验证

### Skills

`skills/` 是 Skill 唯一源目录，按现有 scope 管理，例如：

- `common/`
- `workspace/`
- `agent/`
- `desktop/`

由现有脚本分发到对应 Harness 目录。

正常任务使用已经分发的 Skills，不默认扫描源 `skills/`。

只有以下任务才读取 Skill 源目录：

- Skill 开发；
- Skill 修改；
- Skill 分发；
- Skill 治理。

### 验证

验证范围与修改范围匹配。

优先使用：

- 目标仓已有测试；
- 仓库现有脚本；
- Contract / Schema 校验；
- 已有构建和验收入口。

不默认执行全部仓库、全部构建和全部测试。

涉及跨仓 Contract、Schema 或运行边界时，必须同时核对提供方和消费方。

具体命令和脚本行为以：

- Workspace `README.md`
- `scripts/README.md`
- 目标运行仓 `DIRECTORY_MAP.md`
- 当前代码和测试配置

为准。

验证结果以本次实际执行输出为准。
