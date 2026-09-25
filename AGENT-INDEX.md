# WT Media Agent Index

> 本文件是 WT Media 全部仓库的 **Agent 统一索引与治理规范正文**（中文）。表述冲突时以本文件为准；与 `delivery/`、`docs/decisions` 中的确认记录冲突时，以确认记录为准。
>
> `AGENTS.md`（Codex 入口）与 `CLAUDE.md`（Claude Code 入口）是**薄入口**：只声明本文件的权威性与读取入口。**它们不复制本文件内容——包括 §2 的红线**：红线的唯一落点是 §2，入口文件一旦复述，§2 改动时就会静默过期。

**读取顺序**：见 §4——该节是全项目唯一落点，`.ai/CURRENT_CONTEXT.md` 的 Required Reading Order 是它的生成物镜像。

**导航**

| 我要… | 去 |
| --- | --- |
| 确认不可协商的红线 | §2 |
| 找某个事实的权威来源 | §3 |
| 知道先读什么、不读什么 | §4 |
| 判断改动属于哪个仓库 | §5、§6 |
| 知道一个需求的完整执行流程 | §7 |
| 判断要不要建 CHG、如何收尾 | §8、§9 |
| 维护入口文件与执行快照 | §10 |
| 多工程并行执行 | §11 |
| 在本地跑校验 | §12 |

## 1. 本仓库定位

`wt-media-workspace` 是 WT Media 多项目系统的研发控制中心（Engineering Control Plane）。

- **拥有**：产品需求、工程架构、跨仓库协议、技术决策、交付生命周期、AI 开发协作规范。
- **不拥有**：运行时代码、服务运行代码、构建产物、临时文件。
- **只保存**：知识、规范、决策、交付状态。

运行时代码位于 `../wt-media-cloud`、`../wt-media-agent`、`../wt-media-desktop`。

## 2. 红线（不可协商）

- 运行时改动只在对应工程仓库执行；本仓库不得成为任何运行时的依赖。
- 本仓库不得存放运行时代码、业务实现、编译文件、临时输出或自动生成产物。
- 讨论、建议与假设不是需求；只有 Delivery 或 Decision 中确认的内容可以驱动修改。
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
| `scripts/` | 快照生成、skill 分发、入口与治理校验 | 治理工具 |

其他历史文档（含 `docs/superpowers/` 下的分析材料）不作为新开发依据；分析材料必须经 Delivery 或 Decision 确认后才可驱动修改。执行根 `wt-media/` 不承载 `docs/`，不存在第二份文档树。

## 4. 读取顺序与上下文加载

**读取顺序**（本节是**全项目**读取顺序的唯一落点；`.ai/CURRENT_CONTEXT.md` 的 Required Reading Order 是它的**生成物镜像**，由 `scripts/prepare_ai_workspace.py` 的 `reading_order` 渲染。各仓 `AGENT-INDEX.md` 另载**本仓内**的入口顺序——那属本仓局部事实，不在本清单内。两者是**两个层级**的顺序，不是同一事实的两个落点：改本清单不必改它们，反之亦然）：

1. `AGENTS.md` —— Codex / OpenAI Harness 的薄入口；
2. `CLAUDE.md` —— Claude Code 的薄入口；
3. `AGENT-INDEX.md` —— 治理规范正文与路由（本节所在文件）；
4. `.ai/CURRENT_CONTEXT.md` —— 全项目唯一执行快照，指明当前 CHG、受影响仓库与稳定基线路径；
5. `delivery/LEDGER.md` —— 交付台账（哪些 CHG 在做、哪些已归档）；
6. 快照指明的当前 Milestone（仅 M/L 级 CHG 有）；
7. 当前 CHG 的 `change.md`，及其 plan / spec / checkpoint；
8. 目标仓库的 `AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`、`DIRECTORY_MAP.md`，再进入相关代码与测试。

第 1、2 项由各自 Harness 在会话启动时载入，列出它们是为了说明入口集合完整。无活动 CHG（`--no-active`）时第 6–8 项不存在。开工会话另需、但不属本顺序：受影响仓库的 `git status`、当前分支与相关测试。

**理解优先级**（理解完成后再改代码）：

1. `delivery/active` —— 当前目标、范围、验收标准
2. `docs/product` —— 为什么做
3. `docs/engineering/architecture` —— 系统设计、模块边界
4. `docs/contracts` —— 跨项目通信
5. `docs/engineering/specs` —— 实现规范

**默认不加载**，除非当前任务明确需要：`delivery/completed`、旧 evidence、历史 decisions、历史 specs、临时实验目录。

目标仓库尚无 `AGENT-INDEX.md` 时不得凭空创建：回退为「本文件 + 该仓 `AGENTS.md`」，并在当前 CHG 中登记该缺口；`scripts/verify_agent_entry.py` 会报告仍缺失该文件的仓库。

## 5. 关联仓库与职责边界

| 仓库 | 路径 | 拥有 | 不拥有 |
| --- | --- | --- | --- |
| `wt-media-cloud` | `../wt-media-cloud` | 后端服务、HTTP API、业务编排、数据存储（MySQL / Redis）、Scheduler、Cloud Runtime | 浏览器自动化、本地机器操作、Desktop UI |
| `wt-media-agent` | `../wt-media-agent` | 本地执行能力、浏览器自动化、Agent Runtime、系统级操作 | Cloud 业务逻辑、数据业务管理 |
| `wt-media-desktop` | `../wt-media-desktop` | Desktop 应用、Tauri 运行环境、用户交互、本地桥接能力 | Cloud 业务逻辑、Agent 内部执行能力 |
| `wt-media-workspace` | `../wt-media-workspace` | 知识、规范、决策、交付状态 | 上述全部运行时职责 |

工程可以并行执行，但不得同时修改其他工程拥有的代码与正式治理状态。

## 6. 需求路由

按**真正发生修改的能力**定位工程，不按需求关键词：

| 用户需求 | 主要责任工程 |
| --- | --- |
| 修改用户权限和数据库规则 | Cloud |
| 修改正式业务状态和 API | Cloud |
| 修改内容发现策略与当前 M3 抓取执行 | Cloud |
| 修改 Cloud Web 页面 | Cloud Web |
| 修改 Desktop 使用的 Vue 业务页面 | Cloud Web |
| 修改 Desktop Vue Runtime 适配 | Cloud Web，必要时联动 Desktop |
| 修改 BitBrowser 实际执行逻辑 | Agent |
| 修改 Playwright 平台适配 | Agent |
| 修改 M4-M5 Cloud FFmpeg / 视频合成执行 | Cloud |
| 修改文件下载到运营电脑 | Agent |
| 修改 Agent Sidecar 启停 | Desktop |
| 修改 Tauri 安全桥 | Desktop |
| 修改 Windows/macOS 安装包 | Desktop |
| 修改 Milestone、Plan、Spec 和 CHG | Workspace |
| 修改跨工程 API 或通信契约 | Workspace 协调，责任工程分别实施 |

定位后，进入对应仓库的 `AGENT-INDEX.md` 与 `DIRECTORY_MAP.md` 定位目录。

## 7. 端到端工作流

收到端到端需求（例如 Cloud + Agent、Cloud + Desktop、Agent + Desktop）：

1. **理解产品目标**，读取 Delivery 与稳定基线（见 §4）。
2. **分析影响范围**：列出 Cloud、Agent、Desktop 的修改点与 Contract 变化。
3. **确认职责边界**：不得把 Agent 能力实现到 Cloud、把业务逻辑实现到 Desktop、把 UI 逻辑实现到 Backend。
4. **在对应工程仓库改代码**，遵守该仓库的 `AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`。
5. **更新 Delivery**，并把架构、协议变化同步回 workspace。

## 8. 交付治理

必须创建 `delivery/active/<change-id>/` 的情形：中大型功能、跨项目修改、架构调整、Contract 调整。该目录至少包含 `change.md` 与 `checkpoint.md`。

小修改可直接执行：文档修正、小 Bug、不影响行为的重构。

## 9. 变更规则与完成检查

- 只有记录在 Delivery 或 Decision 中的确认内容可以驱动代码修改。
- 结束开发任务前必须更新 `checkpoint.md`（不是 `change.md`），记录：已完成、未完成、阻塞、下一步。
- **提交纪律**（治理仓与三个工程仓一律适用）：
  - 提交信息用 Conventional Commits：`<type>(<scope>): <subject>`，例如 `docs(chg-064): T-03 …`。
  - **纯移动／重命名与改逻辑不放进同一个 commit**——混在一起 diff 不可审，review 只能看出「文件全变了」。
  - 一仓一 commit：跨仓改动在各仓分别提交（commit boundaries 见 `skills/workspace/executing-wt-media-change/SKILL.md`）。
- 完成检查项：
  - 修改项目归属正确
  - 跨项目协议正确
  - 未破坏模块边界
  - Delivery 已更新
  - Release Matrix 已同步（如适用）
  - Skill 源文件与生成副本关系正确

## 10. Agent 入口与执行快照

### 入口文件

四类入口文件的**角色、禁止项、指针预算与机读键语法**由 `docs/engineering/specs/agent-workspace-conventions.md` §3 规定（唯一落点）；本节只列**强制项**：

| 文件 | 角色 | 强制 |
| --- | --- | --- |
| `AGENT-INDEX.md` | 该仓**全部正式内容**的唯一落点——本仓（治理仓）是治理规范正文；运行仓是「本仓索引 ＋ `## 本仓规则`」 | 四仓都必须存在 |
| `AGENTS.md` | Codex / OpenAI Harness 的**薄指针**，指向 `AGENT-INDEX.md` | 四仓都必须存在 |
| `CLAUDE.md` | Claude Code 的**薄指针**，指向 `AGENT-INDEX.md` | 四仓都必须存在 |
| `DIRECTORY_MAP.md` | 该仓**目录事实与禁止扫描区**的唯一落点 | 运行仓必须存在；本仓不要求（本仓目录树在 §3 与 `README.md`） |
| `.ai/CURRENT_CONTEXT.md` | 执行状态快照（生成物） | 必须存在且唯一 |

`AGENTS.md` 与 `CLAUDE.md` 是**平级入口**，不允许互相软链或互相替代，也不与 `AGENT-INDEX.md` 矛盾。

**两者都不得承载规则正文。** 同一份规则写在两个入口上，就是同一事实的两个落点：改一处不会带动另一处，两个 Harness 各自加载到不同结论。运行仓的规则正文归 `AGENT-INDEX.md` 的 `## 本仓规则`；目录事实归 `DIRECTORY_MAP.md`。由 `scripts/verify_agent_entry.py` 强制。

### 执行状态快照

`.ai/CURRENT_CONTEXT.md` 只保存当前执行状态：当前 Milestone、当前 CHG、当前状态、必读文件顺序、受影响仓库、稳定基线路径与稳定职责边界。

- 生成：`python3 scripts/prepare_ai_workspace.py --change <CHG>`
- 无活动 CHG 时由 `--no-active` 渲染同一状态；`delivery/active/` 仍有 CHG 时拒绝执行
- 禁止手工编辑；禁止在执行根父层再放一份
- 禁止写入历史记录、完整决策库或临时验证内容
- Milestone 专属决策不复制进快照，由当前 CHG 指明其依赖的 Decision 记录

### 配置一致性

`config/skills-distribution.yaml` 的 targets 与 `config/repository-map.yaml` 重复声明同一批 path，两者必须一致，由 `scripts/verify_agent_entry.py` 强制。

## 11. 多 Agent 并行

- 禁止多个 Agent 同时修改 `.ai/CURRENT_CONTEXT.md`。
- **仅当同一个 CHG 需要多个工程并行实施时**，才在该 CHG 下建立 `delivery/active/<change-id>/status/`，按 `<repo>.md` 逐仓记录当前状态、修改内容、验证结果；单仓实施的 CHG 不建该目录。
- 由 workspace 统一汇总，不引入第二套任务管理系统。

## 12. 校验

本地手工执行，本仓库当前不设 CI。全部校验命令：

```text
python3 scripts/verify_delivery_governance.py      # delivery 指针与里程碑引用互相一致
python3 scripts/verify_agent_entry.py             # 入口文件、执行快照唯一性与体积预算、各仓入口漂移 WARN
python3 scripts/verify_skills.py                  # skill 单一源与分发目标
python3 scripts/verify_m0_config.py               # 工作区 contract-map / release-matrix 不变量、三仓 CI 工作流
python3 scripts/verify_product_master_alignment.py  # 产品基线与 MASTER 计划对齐、未关闭里程碑的候选块
python3 scripts/verify_m2_acceptance.py           # M2 的契约层与 schema 层跨仓验收矩阵（需兄弟仓在检出中）
python3 -m unittest discover -s tests -q          # 上述脚本自身的判别力
```

需要真实运行实例、不属上表：`scripts/verify_m1_integration.py`、`scripts/verify_m3_acceptance.py`、
`scripts/m2b_local_acceptance.py`；`scripts/verify_m0_local.sh` 在兄弟仓存在时跑上表加三仓构建与测试。

**判据按稳定性分层**（D-01）：跨仓**源码字面量**不作门禁，**契约层与 schema 层**判据保留并加固——
合法的跨仓重构不应能把门禁打红。**报「通过 / 0 命中」前必须先证明检查能失败**（附阳性对照、报出分母；
变异式的「先红」必须是关掉该判定后用例失败，不能是 `ImportError`）。

每个校验的分层判据、控制方法与已知限制（含一条结构性空转的如实登记）见
`docs/engineering/specs/agent-workspace-conventions.md` §10——**校验读数不作文档落点**：跑一下，读出什么就是什么，本节只列命令。
