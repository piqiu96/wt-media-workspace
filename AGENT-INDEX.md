# WT Media Agent Index

> 本文件是 WT Media 全部仓库的 **Agent 统一索引与治理规范正文**（中文）。表述冲突时以本文件为准；与 `delivery/`、`docs/decisions` 中的确认记录冲突时，以确认记录为准。
>
> Workspace 的 `AGENTS.md`（Codex 入口）与 `CLAUDE.md`（Claude Code 入口）提供五分钟内可读完的项目定位、关联工程、任务执行、相关文档和关键约束。它们只概述行动路线；正式规则、流程和例外以本文件为准。运行仓入口同样提供可直接使用的定位和任务起点，长期规则由各仓自己的 `AGENT-INDEX.md` 承载。

按“读取顺序与上下文加载”渐进读取；`.ai/CURRENT_CONTEXT.md` 的 Required Reading Order 是它的生成物镜像。入口只负责把读者带到这里，本文件不要求读者返回入口。

## 1. 本仓库定位

`wt-media-workspace` 是 WT Media 多项目系统的研发控制中心（Engineering Control Plane）。

- **拥有**：产品需求、工程架构、跨仓库协议、技术决策、交付生命周期、AI 开发协作规范。
- **不拥有**：运行时代码、服务运行代码、构建产物、临时文件。
- **只保存**：知识、规范、决策、交付状态。

运行时代码分别由 `wt-media-cloud`、`wt-media-agent`、`wt-media-desktop` 维护。实际路径从 `config/repository-map.yaml` 读取。

## 2. 红线（不可协商）

- 运行时改动只在对应工程仓库执行；本仓库不得成为任何运行时的依赖。
- 本仓库不得存放运行时代码、业务实现、编译文件、临时输出或自动生成产物。
- 讨论、建议与假设不自动进入实施范围；以用户当前明确指令和已确认的 Delivery、Decision 为准。
- 不得实现 Delivery 中标记为 Explicitly Not Doing 的内容。
- 关联工程路径以 `config/repository-map.yaml` 为准，脚本与文档不得另行硬编码，也不得与之漂移。
- `.ai/CURRENT_CONTEXT.md` 由脚本生成；禁止手工编辑，执行根父层不得出现副本。
- `skills/` 是唯一源；`.claude/skills`、`.codex/skills` 等生成副本不得手工编辑。
- 不引入第二套任务管理系统。

## 3. 知识地图与唯一可信来源

| 位置 | 内容 | 权威性 |
| --- | --- | --- |
| `delivery/` | Milestone、实施状态、验证结果、完成交付 | 交付唯一可信来源 |
| `docs/product` | 产品需求、用户场景、功能目标、验收标准 | 产品唯一可信来源 |
| `docs/engineering/architecture` | 系统架构、模块边界、分层与通信规约 | 工程唯一可信来源 |
| `docs/engineering/specs` | 技术规范、工程标准、开发约束 | 工程唯一可信来源 |
| `docs/contracts` | API Contract、Cloud–Agent 协议、Cloud–Desktop 协议、Event Schema | 协议唯一可信来源 |
| `docs/decisions` | 架构选择、技术取舍、ADR 记录 | 决策唯一可信来源 |
| `config/` | repository-map、skills-distribution、contract-map、release-matrix | 配置事实 |
| `skills/` | Codex / Claude skill 唯一源文件 | skill 唯一源 |
| `bin/` | 本地开发环境的统一启停入口（`bin/control.sh`） | 运营入口 |
| `scripts/` | 快照生成、skill 分发、入口与治理校验；分类与落位规则见 `scripts/README.md` | 治理工具 |

其他历史文档（含 `docs/superpowers/` 下的分析材料）不作为新开发依据；分析材料必须经 Delivery 或 Decision 确认后才可驱动修改。执行根 `wt-media/` 不承载 `docs/`，不存在第二份文档树。

## 4. 读取顺序与上下文加载

当前工具的入口已自动载入时不必重读；随后读本文件和 `.ai/CURRENT_CONTEXT.md`，了解项目边界与当前状态。快照的 Required Reading Order 是这条基础路径的生成物镜像，不要求每个任务加载同一套后续资料。

- **分析或小修改**：根据问题选择产品、工程、协议或决策资料；不因快照显示 `none` 就建立 CHG。
- **交付规划、状态查询或 CHG 执行**：用 `delivery/LEDGER.md` 定位活动记录，再读相关 Milestone、CHG 和必要的稳定基线。
- **涉及运行仓**：使用目标仓当前工具对应的入口、`AGENT-INDEX.md` 和 `DIRECTORY_MAP.md`，按实际改动进入代码与测试。

不默认加载全量代码、`delivery/completed/`、旧证据、历史文档或全量 skills。开工时检查受影响仓库的工作区状态，避免覆盖已有修改。

## 5. 关联仓库与职责边界

| 仓库 | 拥有 | 不拥有 |
| --- | --- | --- |
| `wt-media-cloud` | 后端服务、HTTP API、业务编排、数据存储（MySQL / Redis）、Scheduler、Cloud Runtime | 浏览器自动化、本地机器操作、Desktop UI |
| `wt-media-agent` | 本地执行能力、浏览器自动化、Agent Runtime、系统级操作 | Cloud 业务逻辑、数据业务管理 |
| `wt-media-desktop` | Desktop 应用、Tauri 运行环境、用户交互、本地桥接能力 | Cloud 业务逻辑、Agent 内部执行能力 |
| `wt-media-workspace` | 知识、规范、决策、交付状态 | 上述全部运行时职责 |

仓库路径只从 `config/repository-map.yaml` 获取；文档与脚本不另写固定相对路径。

工程可以并行执行，但不得同时修改其他工程拥有的代码与正式治理状态。

## 6. 需求路由

先确认**实际要修改的能力和文件归属**，再确定责任仓库，不根据需求中的产品名或界面名直接分派。Cloud 负责服务、业务状态、API 和 Cloud Web；Agent 负责本地执行与浏览器自动化；Desktop 负责 Tauri 运行环境、桌面交互和本地桥接。Desktop 使用的业务页面也可能属于 Cloud Web，应按代码归属核对。

跨仓变更由 Workspace 维护共同目标和协议，各责任仓分别实施。具体目录和本仓约束以目标仓的入口、`AGENT-INDEX.md` 与 `DIRECTORY_MAP.md` 为准；遇到边界不明时先核对架构和现有实现，再决定落点。

## 7. 端到端工作流

跨仓任务先明确目标、受影响仓库和协议变化，再由各责任仓实施并验证自己的部分。Workspace 汇总已确认的交付状态，以及需要进入稳定基线的产品、架构和协议结果。具体实施步骤由当前任务和目标仓实际情况决定。

## 8. 交付治理

必须创建 `delivery/active/<change-id>/` 的情形：中大型功能、跨项目修改、架构调整、Contract 调整。该目录至少包含 `change.md` 与 `checkpoint.md`。

小修改可直接执行：文档修正、小 Bug、不影响行为的重构。分析和建议不因阅读交付资料或快照显示无活动 CHG 而创建 CHG；只有确认进入交付实施且达到上述条件时才建立。

**归档边界**：`delivery/completed/` 是只读归档，不作为当前状态依据，也不默认加载。关闭 CHG 时将记录从 `active/` 与 `LEDGER.md` 移出并保留在 `completed/`；具体边界见 [`delivery/completed/README.md`](delivery/completed/README.md)。

## 9. 变更规则与完成检查

- 实施前确认本次指令与已有交付记录的关系；分析与建议可以先形成可评审结论，无需建立 CHG。
- 执行中的 CHG 在每轮结束时更新其 `checkpoint.md`，记录已完成、未完成、阻塞和下一步；小修改和分析任务不套用这项要求。
- 完成前按实际改动核对责任仓、跨仓协议、必要测试和交付记录。提交与收口的细节在相应任务的 skill 和 Delivery 记录中处理。

## 10. Agent 入口与执行快照

### 入口文件

下表说明入口与快照各自承载的内容。

| 文件 | 角色 | 强制 |
| --- | --- | --- |
| `AGENT-INDEX.md` | 本仓是治理规范正文；运行仓承载各自长期规则与架构边界 | 四仓都必须存在 |
| `AGENTS.md` | Codex / OpenAI Harness 入口；概述项目定位、任务起点和关键约束 | 四仓都必须存在 |
| `CLAUDE.md` | Claude Code 入口；概述项目定位、任务起点和关键约束 | 四仓都必须存在 |
| `DIRECTORY_MAP.md` | 该仓**目录事实与禁止扫描区**的唯一落点 | 运行仓必须存在；本仓不要求（本仓目录树在“知识地图与唯一可信来源”及 `README.md`） |
| `.ai/CURRENT_CONTEXT.md` | 执行状态快照（生成物） | 必须存在且唯一 |

`AGENTS.md` 与 `CLAUDE.md` 是**平级入口**，不允许互相软链或互相替代，也不与本文件矛盾。会话只使用当前工具对应的入口，随后沿本文件、快照、相关交付与文档、目标仓规则、代码的方向前进。

两份入口允许概述同一组定位、任务分类和关键约束，以便首次进入时直接理解项目；详细条件、例外与长期规则由对应仓库的 `AGENT-INDEX.md` 维护。运行仓的目录事实归 `DIRECTORY_MAP.md`。

### 执行状态快照

`.ai/CURRENT_CONTEXT.md` 只保存当前执行状态：当前 Milestone、当前 CHG、当前状态、必读文件顺序、受影响仓库、稳定基线路径与稳定职责边界。

- 由 `scripts/prepare_ai_workspace.py` 生成；无活动 CHG 也是合法状态
- 禁止手工编辑；禁止在执行根父层再放一份
- 禁止写入历史记录、完整决策库或临时验证内容
- Milestone 专属决策不复制进快照，由当前 CHG 指明其依赖的 Decision 记录

## 11. 多 Agent 并行

- 禁止多个 Agent 同时修改 `.ai/CURRENT_CONTEXT.md`。
- **仅当同一个 CHG 需要多个工程并行实施时**，才在该 CHG 下建立 `delivery/active/<change-id>/status/`，按 `<repo>.md` 逐仓记录当前状态、修改内容、验证结果；单仓实施的 CHG 不建该目录。
- 由 workspace 统一汇总，不引入第二套任务管理系统。

## 12. 校验

根据本次修改的范围选择校验，不默认运行所有脚本。常用命令在 `README.md` 的“Verification”；脚本用途在 `scripts/README.md`，具体行为以脚本和测试为准。跨仓校验应依据协议、schema 或行为，避免依赖易随重构变化的源码字面量。校验结果以本次实际运行输出为准。
