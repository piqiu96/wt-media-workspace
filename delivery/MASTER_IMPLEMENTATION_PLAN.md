# 模块化自媒体运营平台：代码实施总计划

> 路线更新：2026-11-20（快速发布工具前移M6、合并交付切片；M0—M5历史验收保持原样）
> 适用项目：WT Media 模块化自媒体运营平台  
> 执行方式：一个总路线、当前工作树选一个 CHG、每个 CHG 一次只完成一个可验证闭环
> 运行仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`  
> 治理仓库：`wt-media-workspace`

## 1. 总原则

本项目不按产品章节逐章编码，也不按“先写完 Cloud、再写 Agent、最后写 Desktop”的横向方式实施。

采用纵向闭环路线：

```text
M0 项目治理与工程基线
→ M1 Cloud-Agent-Desktop 最小任务闭环
→ M2 用户、角色、媒体账号与运行环境
→ M3 内容挖掘自动化入口建设
→ M4 Cloud 内容生产闭环
→ M5 策略自动生产与 Worker 资源控制
→ M6 百度快速发布与运营工具完整闭环
→ M7 多任务批次真实发布
→ M-publishing-plan 发布计划推进与结束
→ M-publishing-operations 后续平台与三平台整体回归
→ M10 打包、升级、诊断与稳定性验收
```

发布分四个可独立验收的业务阶段，不把数据库、API 或基础设施单列为业务完成。M6/M7 复用原编号并替换未实施内容；新增阶段使用名称标识，不占用历史 M8/M9 编号。M8 互动管理、M9 效果采集退出当前未来实施路线，不保留未来实施章节或候选，原编号不复用；发布任务结果、目标进度和成功率继续随发布业务交付。

每个阶段都必须产生可以运行、可以测试、可以演示的闭环。M1 Cloud-Agent-Desktop 最小任务闭环完成前，不进入大规模业务模块开发。

## 2. 文档和事实源

```text
wt-media-workspace/
├── .ai/
│   └── CURRENT_CONTEXT.md          # 唯一执行状态快照，脚本生成，禁止手工编辑
├── docs/
│   ├── design/                     # 当前设计工作稿，正式承接后退出
│   ├── product/                    # 当前有效产品事实
│   ├── engineering/                # 当前有效工程架构
│   ├── contracts/                  # 人类可读的跨仓库协议治理
│   └── decisions/                  # 少量重大决策及原因
├── delivery/
│   ├── MASTER_IMPLEMENTATION_PLAN.md
│   ├── LEDGER.md                   # 当前 Active CHG 索引，不是历史归档
│   ├── active/
│   │   └── CHG-YYYYMMDD-NNN/
│   │       ├── change.md           # 当前变更唯一执行依据
│   │       ├── checkpoint.md       # 可选：跨执行器接力的进度记录
│   │       └── evidence/           # 最终交付、审批与验收结论（保留边界见文档治理规范）
│   ├── milestones/                 # 人工确认的业务闭环基线
│   ├── planned/                    # 待规划与待决记录
│   ├── completed/                  # 已收口记录，默认不加载
│   └── reports/                    # 阶段性审计与分析报告
├── config/
│   ├── contract-map.yaml           # 机器可读协议归属和消费关系
│   ├── release-matrix.yaml         # 已验证版本组合
│   ├── skills-distribution.yaml    # skill 分发目标唯一声明
│   └── repository-map.yaml         # 关联工程路径唯一来源
├── skills/
├── scripts/
├── tests/
├── .claude/skills/                 # 自动生成并提交 Git
├── .codex/skills/                  # 自动生成并提交 Git
├── templates/
│   └── delivery/                   # CHG 与 evidence 记录模板
├── AGENT-INDEX.md                  # 跨仓库路由与治理规范正文（唯一权威源）
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

| 位置 | 保存内容 | 不保存内容 |
|---|---|---|
| `docs/design` | 当前设计探索、评审及待回写结论，完成承接后移除 | 第二套正式 PRD、开发状态、永久草稿 |
| `docs/product` | 当前系统应该做什么 | 每日开发进度 |
| `docs/engineering` | 当前系统应该如何设计 | 临时实施清单 |
| `docs/contracts` | 协议所有权、兼容性、变更流程和跨项目协作规范 | 完整 OpenAPI、Schema、DTO、事件定义 |
| `docs/decisions` | 重大且长期有效的取舍原因 | 普通功能讨论 |
| `delivery/MASTER_IMPLEMENTATION_PLAN.md` | 全系统实施顺序和执行纪律 | 代码级详细方案 |
| `delivery/active/<CHG>/change.md` | 当前变更范围、任务、验收和检查点 | 完整产品文档副本 |
| `delivery/active/<CHG>/evidence/` | 本次验证事实 | 第二份需求文档 |
| `delivery/LEDGER.md` | 当前 Active CHG 索引 | 已完成 CHG 历史归档 |

实际接口定义由接口提供方仓库持有：

- Cloud 相关 Contract 归 `wt-media-cloud`；
- Local Agent API 和 SSE 归 `wt-media-agent`；
- Workspace 不保存重复正式定义。

完成 CHG 后：

1. 必要产品结论回写 `docs/product`；
2. 必要架构结论回写 `docs/engineering`；
3. 必要协议治理结论回写 `docs/contracts`；
4. 重大取舍写入 `docs/decisions`；
5. 更新 `config/release-matrix.yaml` 中已验证组合；
6. 确认各仓库独立提交；
7. 从 `delivery/active` 和 `delivery/LEDGER.md` 移除已完成 CHG；
8. 由 Git 和 PR 保留执行历史。

## 3. 里程碑路线

### 状态词汇

状态词只有下表这些；写记录时从表里取，不造新词。读数取记录自己的状态字段：新格式读 frontmatter，旧格式读 `- Status:` 或 `> 状态：`。

**CHG**，变迁为 `DISCUSSION → PLANNED → IMPLEMENTING → VERIFYING → DONE`（`SUPERSEDED` 可从除 `DONE` 外的任何状态进入）：

| 状态 | 含义 | 活记录 | 归档记录 |
|---|---|---|---|
| `DISCUSSION` | 草案，方向待裁定；不激活 | 2 | 0 |
| `PLANNED` | 方向已定、已拆分，可激活 | 2 | 0 |
| `IMPLEMENTING` | 实施中 | 0 | 2 |
| `VERIFYING` | 实施完成，待验收 | 0 | 1 |
| `DONE` | 已收口归档；**活记录不得取此词** | 0 | 68 |
| `SUPERSEDED` | 已被后续工作取代，不再独立激活 | 0 | 0 |

分母：活记录＝`delivery/planned/*/change.md` **4** 篇 ＋ `delivery/active/*/change.md` **0** 篇；归档记录＝`delivery/completed/*/change.md` **82** 篇。归档列 71（`DONE` 68＋`IMPLEMENTING` 2＋`VERIFYING` 1）与退役词 `CLOSED` 4、`HANDOFF` 2、`IN_PROGRESS` 5 合计 82。planned 4 篇中 1 篇（CHG-20260903-034）使用块引用旧格式，状态同为 `PLANNED`。读数随归档动作变化；登记时按当时的实测值填写，不沿用旧数。

**里程碑**（现状见 `delivery/milestones/README.md`）：

| 状态 | 含义 | 当前处于该态的里程碑 |
|---|---|---|
| `NOT_STARTED` | 未进入该里程碑 | M-publishing-operations、M10 |
| `IN_PROGRESS` | 开发中 | M-publishing-plan |
| `VERIFYING` | 自动综合验收完成，等待人工整体验收 | M7 |
| `DONE` | 人工整体验收通过 | M2、M3、M4、M5、M6、M-launch-engineering |

里程碑文件内部的子项状态（如 M2-D 的 `DEFERRED`）不是里程碑状态词，不占上表，只在其所属里程碑文件内自述。

**历史词汇**（不再取用；**归档记录**保持原样、不回改，**活记录一律改用上表的词**）：`CLOSED`、`HANDOFF`（工作并入后续门槛、其门槛本身尚未验收）、`IN_PROGRESS`（**里程碑层仍用此词，CHG 层不再用**）、`TODO`、`IMPLEMENTED`、`VERIFIED`、`ACTIVE` 为已退役写法；`TODO` 在 §8 的任务表状态列仍是合法值，那是另一个轴。落到 `delivery/active/` 的记录只有一个合法状态：`IMPLEMENTING`（实施中）或 `VERIFYING`（待验收）——由 `scripts/verify/verify_product_master_alignment.py::validate_active_change` 强制。更早的记录可能用块引用 `> 状态：` 代替 `- Status:`，取值仍是上表中的词。

**「归档记录保持原样」与「移除已完成 CHG」不矛盾，因为两者说的不是同一件事**：§2 完成清单第 7 项的「移除」指的是把记录**移出** `delivery/active/` 与 `delivery/LEDGER.md`；记录**本身**移入 `delivery/completed/` 并保持原样，**不删除、不重写、不合并**。`delivery/completed/` 的完整只读边界（含新增原始捕获的入库阈值与已知例外）唯一落点是 `delivery/completed/README.md`，本节不复述其正文。

里程碑不能因为代码目录已经存在而标记为 `DONE`。必须逐项核验代码、自动测试、Contract、Evidence、人工验证、跨仓库集成、Git 提交和退出条件。

历史 `DONE` 可以在退出条件被证明过宽或证据只覆盖脚手架时重新打开。重新打开不会删除历史提交和局部验证结果；这些结果标记为“继承证据”，只有重新满足当前退出条件后才能再次标记为 `DONE`。

每个里程碑必须记录：

| 字段 | 内容 |
|---|---|
| 状态 | 当前里程碑状态 |
| 目标 | 完成后新增的可验证能力 |
| 依赖 | 必须完成的前置里程碑 |
| 候选 CHG | 规划中的变更单元，只记录，不自动激活 |
| Active CHG | 当前激活变更，没有则为 `None` |
| 退出条件 | 进入下一里程碑前必须满足的条件 |
| Evidence | 里程碑综合验证索引 |
| 完成日期 | `DONE` 后记录 |
| Commit/Tag | 相关提交和版本标签 |

当前进度总览：

| 里程碑 | 当前状态 | 已完成或可复用事实 | 当前结论 |
|---|---|---|---|
| M0 | `DONE` | M0 工程基线复验通过。Cloud/Web/Agent/Desktop 真实构建、测试、启动验证完成。MySQL 真实连接。修复 2 个测试问题。 | M0 冻结。不继续扩建。 |
| M1 | `DONE` | M1 任务链路闭环复验通过。创建→领取→执行→上报→查询完整链路跑通，MySQL 持久化确认。统一 API 响应规约已迁移。修复：router 连接、mysql_registry 时间格式。 | M1 冻结。不扩建通用任务系统。 |
| M2 | `DONE` | 2026-09-14 用户完成本轮综合人工验收并确认完整通过。M2-A/B/C/E 的真实依赖、构建、Desktop 与人工走查证据均已归档；原 M2-D 未纳入当时完成门槛。 | M2 原验收保持 DONE；2026-10-30 恢复 M2-D 社媒账号重构，108→109→110 已依次交付并完成自检，本次整体人工走查待签收，范围见 M2-D1～D3。 |
| M3 | `DONE` | A～E1 已实施并有真实证据；C2、E2 已于 2026-09-23 暂停；E3 综合验收 2026-09-23 在 Cloud `aaf66c5` 执行，验收矩阵第 1～7 项全部通过（首轮硬阻断 D-scheduler 同日修复并复验通过，另补证 Desktop 走查与 `material_failed` 注入），**用户同日签收** | M3 冻结为内容挖掘自动化入口基线；验收期只登记未修的 D1～D10、D-scheduler-2、S-1 仍由 `CHG-20260923-054`（planned）处置，**用户裁定 D3 不阻塞 M3**；C2/E2 留待后续版本 |
| M4 | `DONE` | M4 各实施 CHG、M4-H1 视觉整改与 M4-H2 统一走查均已完成；机器闭环与真实页面签收均有证据。 | 2026-10-28 用户签收 M4-H2；M4 冻结为 Cloud 内容生产闭环基线。 |
| M5 | `DONE` | M5-C1～C7（含 C2a）与 M5-F 均已归档；真实 Scheduler/Worker/FFmpeg/对象存储全链与页面走查有证据。 | 2026-10-28 用户签收 M5-AC-13 与 M4-H2；M5 冻结为策略自动生产基线。 |
| M6 | `DONE` | CHG106工具、内容准备/续编、结果处置与统计已交付；任务11/attempt34自动核实公开作品4，四仓改动已合入main | 已有真实业务、安装版关键流程与异常回归证据；2026-11-25用户签收，已归档 |
| M7 | `VERIFYING` | 107/108技术交付与真实单Profile双端闭环通过，多Profile受控验证 | 用户指定107–109后统一整体验收；109可按已完成技术依赖启动 |
| M-publishing-plan | `IN_PROGRESS` | 109契约、数据与服务已实现并独审；共用页面按原型源码对齐，正在收口编码自测 | 自测闭环后真实多批E2E，最后双端UI走查和PR/main交付 |
| M-publishing-operations | `NOT_STARTED` | 后续平台未验收；工具已归M6 | 完成后续平台和三平台回归 |
| M10 | `NOT_STARTED` | 首次上线已有部分打包部署证据 | 依赖发布四阶段，补验升级、恢复及发布业务 |

2026-10-26 M3–M5 易用性增量已确认：CHG-101 已合并；[M3-F／CHG-102](milestones/M3-content-discovery-v2.md#m3-f-public-content-scope)已完成并归档（Cloud PR #8，`cb26c66`），团队公共内容池与 Desktop 共用 Cloud 页面入口上线；CHG-106 前端状态色死表已删除并归档（Cloud PR #9，`d793d92`）；[M4-I／CHG-103](milestones/M4-content-production.md#m4-i-production-operator)已完成并归档（Cloud PR #10，`2cd341d`），策略→任务→成片负责人事实与代创建链路已上线；[M4-J／CHG-104](milestones/M4-content-production.md#m4-j-material-usage)已完成并归档（Cloud PR #11，`fc8504e`），以该事实投影素材使用并收敛个人下载；[M5-F／CHG-105](milestones/M5-automatic-production.md#m5-f-team-material-candidates)已完成并归档（Cloud PR #12，`c509ee8`），自动候选改为团队素材库且任务/成片归策略负责人；M5 总体当时仍为 `IN_PROGRESS`，待 CHG-098 统一走查 M5-AC-13 与 M4-H2；2026-10-28 用户签收 M4-H2 与 M5-AC-13，M4 与 M5 进入 `DONE`。CHG-104 与 CHG-105 均依赖 CHG-103，按单 CHG 执行纪律逐项激活。M3 原 `DONE` 签收不重开，M4/M5 旧机器 PASS 不冒充新增闭环通过；P1 跨团队昂贵资源复用待成本与现有缓存能力核实后另立交付项。

每个里程碑的最终综合验收至少包含：

1. 自动单元、Contract、集成和回归测试；
2. MySQL、BitBrowser、对象存储、平台接口等适用的真实依赖证据；
3. 浏览器或 Desktop 中的角色/UI/人工链路验收；
4. 中断、重启、幂等、恢复和敏感信息安全验收；
5. Diff 范围检查、Evidence、Checkpoint 和各仓库独立提交。

### M0：项目治理与工程基线

| 字段 | 内容 |
|---|---|
| 状态 | `DONE` |
| 目标 | 在治理体系可用的基础上，使 Cloud、Web、Agent、Desktop 成为可安装依赖、可真实构建、可启动停止、可测试的独立工程组件。 |
| 依赖 | None |
| Active CHG | None |
| Evidence | 继承证据 + M0-VERIFICATION-20260716 复验通过。Cloud/Web/Agent/Desktop 真实构建、测试、启动验证通过；MySQL 真实连接；2 个测试修复。 |
| 完成日期 | 2026-07-16 |
| Commit/Tag | 继承历史提交 + M0-VERIFICATION-20260716 修复提交 |

候选 CHG：

```text
M0-R1 真实工具链、依赖安装和当前脚手架差距核查
M0-R2 Cloud/Web 真实 bootstrap、build、test、MySQL Migration 和启动停止
M0-R3 Agent 正式包入口、依赖锁、SQLite Migration、build 和启动停止
M0-R4 Desktop Vue/Tauri Rust 正式依赖、build、dev、启动停止和本地页面
M0-R5 CI、Contract Map、Release Matrix 和跨平台工程门禁
M0-R6 三端独立构建、启动、健康检查和综合工程验收
```

退出条件：

- Skill、Active CHG、Checkpoint、Q-xx、Evidence 和 DONE 门禁能实际使用；
- 从最外层 `wt-media/` 启动 Codex 能识别四仓库；
- Cloud 和 Web 使用真实依赖完成 bootstrap、test、build、启动、健康检查和停止；
- Agent 使用正式包入口和独立环境完成 bootstrap、test、build、启动、健康检查和停止；
- Desktop 使用真实 Vue/Tauri Rust 完成 bootstrap、test、build、dev、启动和停止；echo 脚本、Mock-only 入口或未执行 Cargo 不通过；
- Cloud Migration 能在空 MySQL 数据库执行并重复验证；Agent SQLite Migration 能在独立用户目录执行；
- CI 覆盖 Go、Web、Python、Rust/Tauri、Migration 和 Contract 的真实构建/测试门禁；
- Workspace 不成为运行时依赖；
- Git 工作区、提交和交付历史可追踪；
- `contract-map.yaml` 和 `release-matrix.yaml` 符合当前已验证状态；
- M0-R6 在三个运行仓库分别形成自动 Evidence 和人工启动 Evidence。

本阶段不做：

- 正式业务模型；
- 正式用户认证；
- 任务执行协议；
- FFmpeg 合成；
- 平台自动化；
- 正式安装包。

### M1：Cloud-Agent-Desktop 最小任务闭环

| 字段 | 内容 |
|---|---|
| 状态 | `DONE` |
| 目标 | 在 M0 的真实组件上建立持久化、无 Mock、可重启恢复的 Cloud-Agent-Desktop-Web 最小任务环境，供后续所有业务里程碑复用。 |
| 依赖 | M0 `DONE` |
| Active CHG | None |
| Evidence | 继承证据 + M1 复验通过。创建→领取→执行→上报→查询闭环完整跑通，MySQL 持久化确认。统一 API 响应规约已迁移。修复：mysql_registry 时间格式。 |
| 完成日期 | 2026-07-16 |
| Commit/Tag | 继承历史提交 + M1 修复提交 |

目标闭环：

```text
用户在 Cloud Web 登录并创建 noop_task
→ MySQL 持久化 task、幂等键、租约和 Agent Registry
→ Desktop 通过真实 Tauri 启动 Local Agent
→ Agent 注册、领取并把检查点写入 SQLite
→ Agent 上报 started / progress / succeeded
→ Desktop 通过真实 HTTP/SSE 展示进度
→ Cloud、Agent 或 Desktop 重启后状态和待回传结果可恢复
```

候选 CHG：

```text
M1-R1 正式通用 task 模型、状态、错误和 task_schemas
M1-R2 MySQL task、幂等、租约和 Agent Registry 持久化
M1-R3 Agent Runner、SQLite 检查点、离线待回传和重启恢复
M1-R4 Local Agent HTTP/SSE、节点绑定、Token 和安全边界
M1-R5 Desktop Tauri 进程生命周期、HTTP/SSE 代理和安全存储
M1-R6 Cloud Web 登录、任务创建和 Desktop WebView 任务进度页
M1-R7 Cloud/Agent/Desktop 中断、租约、幂等和恢复矩阵
M1-R8 无 Mock 三端端到端人工验收
```

退出条件：

- 同一个任务不会被两个 Agent 同时执行；
- task、租约、幂等键和 Agent Registry 持久化到 MySQL，Cloud 重启后不丢失；
- `task_schemas` 已由 Cloud 正式发布，Agent 和 Desktop 锁定兼容版本；
- Agent 中断后从 SQLite 检查点恢复或安全释放租约；
- Cloud 暂时不可达时结果保存在 SQLite，恢复连接后幂等回传；
- Desktop 不直接读取 Agent SQLite；
- Desktop Vue 不持有 Local Token；
- Desktop 使用真实 Tauri/Rust 管理 Local Agent，不使用 Mock Service 作为验收入口；
- Cloud Web 能在浏览器和 Desktop WebView 中登录、创建任务并显示同一正式状态；
- 三端有自动单元、Contract、集成和重启恢复测试；
- M1-R8 完成从登录、创建、领取、进度、成功回写到重启恢复的真实人工演示和 Evidence。

### M2：用户、账号与运行环境

| 字段 | 内容 |
|---|---|
| 状态 | `DONE`（原 M2-A/B/C/E 于 2026-09-14 人工验收；本次扩展独立验收） |
| 已完成基线 | 用户/会话、Desktop 环境、浏览器窗口与代理；不以旧账号页面约束新设计 |
| 当前扩展 | 2026-10-30 用户批准 M2-D 社媒账号整体重构，按最终原型、PRD 和 ADR-0030 推进 |
| 闭环 | [M2-D1～D3](milestones/M2-account-runtime.md#m2-d-社媒账号重构) |
| Active CHG | None；M2-D 实现与浮层视觉自检已完成，仍为 VERIFYING，等待人工整体签收。 |

已交付能力（人工走查范围）：

1. CHG-108：矩阵维护与人工登录后手动检查；无 Cookie 入库、未分类亦可识别，失败与历史结论分离。
2. CHG-109：单账号 Cookie 接入/更新；账号表直接保存 CK 明细与必要写前值，不建版本表；新建窗口优先、占用核实、平台隔离与结果确认。
3. CHG-110：批量 Cookie 接入；单张批次表 content_json 包含批次信息和 items 数组，以固定原行号定位；预览零副作用、逐项执行、七计数、跳过恢复、成功不重放、未知先核实。

三项能力组成同一套最终方案，不建设旧模块兼容层，也不恢复旧三种上号、接码和通用任务范围。数据库表、接口和废弃实现清理见[社媒账号设计](../docs/engineering/specs/social-accounts.md)，交付职责、核心链路和发布验收见其[整体落地方案](../docs/engineering/specs/social-accounts.md#7-整体落地方案)。原已验收窗口、代理与运行环境不重做；每项新闭环必须验证真实效果、Cloud 事实和最终页面，不能以代码存在或请求成功宣称完成。

### M3：内容挖掘自动化入口建设

| 字段 | 内容 |
|---|---|
| 状态 | `DONE`（2026-09-23 用户签收；A～E1 有真实证据；C2/E2 已暂停；E3 验收矩阵第 1～7 项全 PASS） |
| 产品方向 | 用户已明确确认内容挖掘 V2（2026-09-15）；M2 保持 `DONE`。 |
| 目标 | 两个人工入口（内容池「ID/链接发现」与「关键词发现」）与关键词自动策略统一入内容池，经人工筛选或策略规则转为可追踪素材；M3 自动发现由 Cloud Scheduler + Cloud Worker/Crawler 执行，不创建 Agent 任务。博主搜索与作者策略已暂停。 |
| 依赖 | M2 `DONE`；按阶段解决接口、权限、周期与状态口径。 |
| 规划状态 | A～E 与八个 CHG 草案已拆分；M3-B～E 由 CHG-20260916-052 承载并已实施，由 Cloud Scheduler + Cloud Crawler 承担，不创建 Agent 任务。 |
| 闭环 | `delivery/milestones/M3-content-discovery-v2.md` |
| 产品/决策 | `docs/product/prd/详细文档/第四章_内容挖掘.md`；ADR-0013（第 3、7 条已于 2026-09-23 增补）、ADR-0014（团队级隔离已确认）、ADR-0015（Cloud-owned 执行） |
| Active CHG | None（M3 已关闭，active 名额为空） |
| Evidence | Cloud `docs/superpowers/handoffs/`（2026-09-18、2026-09-21、2026-09-22）与 CHG-052 `checkpoint.md`/`evidence/`；关键词链路经真实凭据取得 `status=success`；E3 验收矩阵见 CHG-052 `evidence/m3-e3-acceptance-20260923/`（含 `14-verdict.md` 与 `15-`～`17-` 补验）。C2/E2 无真实外部证据。 |
| 完成日期 | 2026-09-23（用户签收；记录见里程碑第 2.2 节） |
| Commit/Tag | None |

三个页面：内容池、挖掘策略、挖掘任务。

目标闭环：

```text
分享链接解析并入池 / 关键词搜索选择 / 关键词自动挖掘策略
→ source_content 内容池
→ 人工转素材或策略规则自动转素材
→ material
```

| 阶段 | 独立结果 | CHG |
| --- | --- | --- |
| M3-A | 内容池与人工转素材基础能力；必须由 B 复验真实来源 | CHG-20260915-044 |
| M3-B | 真实分享链接解析入池，首个外部闭环 | CHG-20260915-045 |
| M3-C1 | 关键词主动搜索选择入池 | CHG-20260915-046 |
| M3-C2 | 博主主动搜索选择入池（**已暂停**，后续版本再评估） | CHG-20260915-047 |
| M3-D | 统一策略配置（本期 keyword；`author` 取值保留）、周期与启停 | CHG-20260915-048 |
| M3-E1 | 关键词周期任务、真实入池、日志统计与恢复 | CHG-20260915-049 |
| M3-E2 | 作者周期任务与真实增量入池（**已暂停**，后续版本再评估） | CHG-20260915-050 |
| M3-E3 | 综合验收与用户签收；独立的只读运行视图本期不做（2026-09-23 裁定移出交付要求） | CHG-20260915-051 |

A、B、C1、D、E1 已实施并有真实证据；C2、E2 已于 2026-09-23 暂停（本期不做，后续版本再做），移出验收范围。E3 的独立验收草案 CHG-20260915-051 从未启动，其草案已于 2026-10-10 随 planned 清理删除，历史见 Git；E3 的**综合验收走查已于 2026-09-23 在 Cloud `aaf66c5` 上执行**（106 步中 87 PASS / 7 FAIL，唯一硬阻断为 D-scheduler：无人值守的真实周期触发未交付），D-scheduler 同日修复并复验通过，Desktop 走查与 `material_failed` 注入两项覆盖缺口同补，**验收矩阵第 1～7 项全部通过并经用户签收**，结论见 CHG-052 `checkpoint.md` 与 `delivery/completed/CHG-20260916-052/evidence/m3-e3-acceptance-20260923/`。原 CHG-037～043 为 SUPERSEDED，不再执行，也不计为已完成。C 阶段由 C1 完成，M3-E 由 E1 与 E3 完成。逐阶段状态见 `delivery/milestones/M3-content-discovery-v2.md` 第 2.1、2.2 节。

明确不做：视频下载/存储/校验、剪辑、AI 评分、自动生产/发布/互动/数据分析、其他渠道真实采集、工作流引擎、可视化调度器、任意脚本执行、crawl_result、完整历史原始 JSON。

自动转素材为 M3 范围内正式能力（2026-09-23 用户确认，见 ADR-0013 第 3 条），按 `auto_material` / `material_rule` / 阈值规则生效，不再列入“明确不做”。

退出条件：

- 单/批量链接、关键词搜索均有真实接口到入池证据；未选搜索结果不写正式来源。博主搜索已暂停，不在本期退出条件内。
- 关键词策略能真实定时触发，创建带快照的 crawl_task，自动入池；保存配置/任务列表不是完成证据。作者策略已暂停，不在本期退出条件内。
- 策略只定义规则，Cloud Scheduler 负责触发，Cloud Crawler 负责外部执行；同周期防重、同策略串行及重启恢复通过。
- source_content 三态、crawl_task 五态（含 `partial_success`）与部分失败口径均明确，统计/错误和业务事实一致。
- 全局唯一、权限隔离、忽略保护、人工转换事务与素材来源可追踪同时成立。
- 仅预留渠道/策略扩展抽象；独立的只读运行视图本期不做（2026-09-23 裁定移出交付要求，不因此改变 ADR-0013 第 8 条对编排/拖拽/条件分支/任意脚本的禁止性约束）。
- Cloud Web/Desktop、受控故障、M2 回归及用户最终验收通过后才标 M3 DONE。**（2026-09-23 已满足：四项均有证据，用户同日签收。）**

### M4：Cloud 内容生产闭环

| 字段 | 内容 |
|---|---|
| 状态 | `DONE` |
| 目标 | 打通素材库、我的素材、人工创建合成任务、Cloud Worker 生成成片和下载的完整闭环。 |
| 依赖 | M3 `DONE` |
| 闭环 | `delivery/milestones/M4-content-production.md` |
| 产品/决策 | 第五章素材生产；ADR-0017、ADR-0021；M4-M5 Cloud 内容生产工程设计 |
| Active CHG | None（M4 全部 CHG 已归档，含 CHG-20261015-098） |
| Evidence | M4-A 原功能证据见 `delivery/completed/CHG-20260924-061/evidence/`，用户签收见 `delivery/reports/2026-10-12-m4-a-signoff.md`；M4-C4 真实 FFmpeg 与 Garage 验证见 `delivery/completed/CHG-20261012-080/evidence/T-06.md`；M4-H2 统一走查与签收见 `delivery/completed/CHG-20261015-098/evidence/2026-10-27-m4-h2-m5-ac13-third-round-checklist.md` |
| 完成日期 | 2026-10-28 |
| Commit/Tag | `wt-media-cloud` `624e04e`、`7dd49e8`；`wt-media-agent` `1b6f196`；`wt-media-desktop` `8dff82c`（CHG-20261015-098 合并提交） |

目标闭环：

```text
material
→ material_usage
→ compose_task（保存模板版本和生效配置快照）
→ Cloud Compose Worker + FFmpeg
→ composite_output
→ file_transfer_task
→ 运营电脑本地文件 / 去发布

compose_template（技术模板，按版本发布）
→ compose_strategy
→ compose_task（执行时不读取最新策略）
```

C2 已激活；C3～C8 尚未建立正式 CHG。下表保留执行顺序。

候选 CHG：

```text
M4-C1 / CHG-20260924-061 素材库、material_usage 与原素材懒加载准备/下载（DONE，2026-09-27 归档）
M4-C2 基础：compose_template / compose_strategy 结构与合同，撤下未就绪的旧策略操作
M4-C4 对象存储、FFmpeg/FFprobe 与按模板版本执行的独立 Cloud Compose Worker 基础设施
M4-C2 策略交付：发布已验证的 basic_cut 模板版本与 schema，策略 API 和共用页面可用
M4-C3 compose_task 模型、API、模板版本与配置快照、批量创建与排队中取消
M4-C5 人工任务从源视频准备到 composite_output 的真实闭环，含运行中取消与单任务安全恢复
M4-C6 我的成片、来源追踪和去发布入口
M4-C7 复用 file_transfer_task 与下载中心 Drawer，扩展成片的 Local Agent 本地文件落地
M4-C8 真实视频、对象存储、故障恢复和 UI 综合验收
```

各候选的独立结果、依赖门槛、明确排除和关闭证据见 `delivery/milestones/M4-content-production.md` §3.1。M4-A 用户于 2026-10-12 确认走查通过；原记录中未覆盖的机器读数保留，不当作 M4 整体验收通过。

关键约束：

- 视频合成只在 Cloud Compose Worker 执行；Desktop / Local Agent 不执行 FFmpeg；
- HTTP Server 不同步等待视频生成，也不启动 Scheduler / Worker；
- 原素材采用懒加载，进入素材库只保存源链接；
- `material_usage` 是唯一“我的素材”关系；
- `compose_task` 是唯一生产任务，不创建 `compose_pool_item` 或 Agent task；
- `compose_template` 保留旧版本，`compose_strategy` 不建版本表；任务执行只读创建时的模板版本与配置快照；
- 失败、取消、超时、文件损坏或对象存储写入失败不创建成片；
- 原素材和成片下载统一使用 `file_transfer_task`。

退出条件：

- 素材库展示来源和 `not_downloaded / downloading / ready / failed` 视频状态；
- 同一用户、同一素材最多一个有效 `material_usage`，移出后历史任务和成片保留；
- 人工选择 `compose_strategy` 创建 `compose_task`，任务保存不可变策略快照；
- 源视频未就绪时先创建 Cloud 文件准备任务，成功后才执行 FFmpeg；
- Cloud Worker 从真实素材生成可播放视频，完成媒体校验和对象存储落盘后才创建 `composite_output`；
- 我的成片可预览、追溯来源、下载和进入发布管理；
- 原素材和成片能通过下载中心落到运营电脑并通过大小/Hash 校验；
- 取消、输入损坏、FFmpeg 失败、上传失败、Worker 崩溃和本地下载失败均无假成功；
- Desktop 退出不影响 Cloud 合成；Agent 侧不存在合成 Executor；
- M4-C8 通过真实 FFmpeg、对象存储、Cloud Web/Desktop WebView、Local Agent 下载和独立提交验收。

### M5：策略自动生产与 Worker 资源控制

| 字段 | 内容 |
|---|---|
| 状态 | `DONE` |
| 目标 | 在 M4 已验证的 Cloud 合成底座上，由 `compose_strategy` 定时自动创建任务，并完成批量、并发、超时、重试和恢复。 |
| 依赖 | M4 机器闭环已验证；M4-H2 人工走查暂缓，与 M5 最后统一签收（2026-10-14 用户确认） |
| 闭环 | `delivery/milestones/M5-automatic-production.md` |
| 产品/决策 | 第五章素材生产；ADR-0017；M4-M5 Cloud 内容生产工程设计 |
| Active CHG | None（CHG-20261015-098 已归档） |
| Evidence | M5-C1～C6（含 C2a）机器证据见已归档 CHG091～097；M5-F 见 `delivery/completed/CHG-20261026-105/`；C7 真实时间全链与 M5-AC-13 签收见 `delivery/completed/CHG-20261015-098/`。 |
| 完成日期 | 2026-10-28 |
| Commit/Tag | `wt-media-cloud` `624e04e`、`7dd49e8`；`wt-media-agent` `1b6f196`；`wt-media-desktop` `8dff82c`（CHG-20261015-098 合并提交） |

目标闭环：

```text
compose_strategy.schedule
→ Cloud Scheduler
→ 幂等创建 compose_task
→ Worker Pool
→ composite_output
```

候选 CHG：

```text
M5-C1 compose_strategy.schedule、启停、时区、单次/每日上限和素材范围
M5-C2 Compose Scheduler 到期扫描、调度幂等和重启恢复
M5-C3 Worker Pool 并发、租约、heartbeat、超时和资源保护
M5-C4 批量任务、部分失败、防重和数量控制
M5-C5 技术重试、卡死恢复、取消和对象存储异常处置
M5-C6 自动执行 UI、运行统计、日志摘要和人工处置
M5-C7 真实定时、批量、并发、恢复和回归综合验收
```

明确不做：

- 独立生产规则管理平台；
- `production_rule` 表；
- `compose_pool_item` 或重复生产任务表；
- 动态工作流引擎；
- 独立策略组表；
- `composite_output_download_task`；
- 成片池、成片领取或独立 `pool_policy` 表；
- MQ、微服务和动态 Worker 注册中心。

退出条件：

- `compose_strategy.schedule` 是自动规则唯一事实源，禁用策略不创建任务；
- Scheduler 只创建 `pending compose_task`，不下载文件、不执行 FFmpeg；
- 同策略、同时间槽、同素材不重复创建任务；
- 单次和每日上限真实生效，批量部分失败不回滚其他成功任务；
- Worker 实际并发不超过配置，配置非法时拒绝以无限并发启动；
- 同一任务只被一个 Worker 执行，heartbeat、租约过期、超时终止和重启恢复可验证；
- 技术错误在上限内退避重试，业务错误和结果不明确不盲目重试；
- HTTP Server 单独运行不会启动 Scheduler / Worker；
- M5-C7 通过真实计划时间、对象存储、并发压力、Worker 重启、故障注入、UI 和独立提交验收。

### M6：百度快速发布与运营工具完整闭环

| 字段 | 内容 |
| --- | --- |
| 状态 | `DONE` |
| 目标 | 图片库、模板及真实渲染、单条AI、续编与完整任务处置共同支撑百度真实公开发布和成功统计 |
| 依赖 | M2真实账号/环境、M4/M5真实成片及现有文件服务；工具不再依赖M7 |
| 业务验收 | [M6完整快速发布](milestones/M6-single-publishing.md) |
| Active CHG | None |
| Evidence | [CHG106验收及main合并核对](completed/CHG-20261120-106/evidence/main-merge-and-verification.md)；任务11/attempt34自动核实公开作品12052878563859428344并登记作品4；原生关键流程、权限/异常回归及四仓合入已记录，2026-11-25用户整体验收签收完成 |

2026-11-20用户确认将原运营工具阶段中的图片库、封面模板制作与真实渲染前移M6，单任务AI、Desktop/Web续编及真实成片缩略图同阶段补齐；B站、小红书仍后续交付。102～105的技术切片已合入main，退出独立Active管理。按用户最新要求，101已收齐四仓已有代码并关闭，[CHG-20261120-106](completed/CHG-20261120-106/change.md)统一承接图片库、模板和快速发布剩余实现与验收，不把合并等同于完成业务闭环。

内部顺序：收齐本地基线 → 图片与模板真实使用 → 完整内容准备/续编 → 结果与异常收尾 → 真实公开与整体验收。安全终止、原现场人工继续、四种核实结论、补录、关联作品、安全重试/放弃和条件复制均是M6范围。取消/终止保留占用，符合安全条件的明确放弃才释放；审核中不算公开成功。断网后必须核实且不重复投稿，浏览器自动提交是必须能力。

### M7：多任务批次真实发布

| 字段 | 内容 |
| --- | --- |
| 状态 | `VERIFYING` |
| 目标 | 本人批次候选保存、批量内容、启动原子建单、分组并发、异常保护与公开结果 |
| 依赖 | M6 `DONE` |
| 业务验收 | [M7批次](milestones/M7-batch-publishing.md) |
| Active CHG | None |
| Evidence | [107配置准备实际双端E2E](completed/CHG-20261124-107/evidence/installed-e2e.json)；[108实际双端验收](completed/CHG-20261124-108/evidence/installed-e2e.json)及合入核对完成；[110原型修复/本轮真实2批与main新包](completed/CHG-20261125-110/evidence/final-delivery.md)已验证，用户整体签收另行；[111状态与按钮修复验收](completed/CHG-20261125-111/evidence/final-delivery.md) |

候选 CHG：

```text
M7-准备：本人资源＋批量内容＋候选配置保存（无task/占用）
→ M7-执行：start原子建单＋分组/间隔＋跨批互斥＋异常暂停与公开结果
```

2026-11-25按用户最新裁定，[CHG107](completed/CHG-20261124-107/plan.md)只保存本人候选配置，不创建task/占用；[CHG108](completed/CHG-20261124-108/plan.md)首次start原子建单、占用并授权，按组运行、组间等待，组间处理和异常任务上限控制暂停/继续/终止。旧混合归属授权与滚动补位不进入本轮。两项已获用户执行授权，107技术交付DONE、108技术交付DONE，步骤/API/迁移/验收详见清单；依赖M6及相关review完成后预检启动。

### M-publishing-plan：发布计划推进与结束

| 字段 | 内容 |
| --- | --- |
| 状态 | `VERIFYING` |
| 目标 | 目标矩阵与拆批、全部批次准备后首次人工授权并冻结、10%自动推进、批次快捷处理、核实和最终结束 |
| 依赖 | M7 `DONE` |
| 业务验收 | [发布计划](milestones/M-publishing-plan.md) |
| Active CHG | None |
| Evidence | [109编码与自测矩阵](completed/CHG-20261124-109/evidence/implementation-selftest-checklist.md)；真实E2E两批公开2/2且达成结束已通过，最终d853e24双端UI及补验均通过；技术交付与归档随Workspace PR65合入main生效；[110修复与本轮真实验收](completed/CHG-20261125-110/evidence/final-delivery.md)通过，用户整体人工验收另行 |

门禁说明：上表依赖列记录标准门禁M7 `DONE`，不表示M7当前已签收。M7实际为技术交付完成、`VERIFYING`待用户整体人工验收。

本轮执行例外：用户明确指定107–109依次自主技术交付后统一整体验收。107/108已技术归档且四仓main核对，故109可启动；M7仍保留`VERIFYING`，不提前宣称用户最终签收。

候选 CHG：

```text
PLAN 计划闭环：全部批次准备与启动冻结 → 10%推进/批次快捷处理 → 核实与结束
```

[CHG-20261124-109](completed/CHG-20261124-109/change.md)已按授权完成技术实现、自测、真实E2E及最终双端走查并归档，[review清单](completed/CHG-20261124-109/plan.md)逐项对应产品、页面、API、数据与验收。本项作为一个计划闭环CHG，已依次完成目标与骨架/全部批次准备/启动冻结 → 10%推进与原批次快捷操作 → 核实/结束 → 技术验收。用户整体人工签收另行。10%边界、零分母、未知阻断、原资源等待与人工暂停、迟到结果不重复推进已按真实与受控边界验证；计划进度和发布成功率随本阶段交付，不依赖M9。2026-11-25裁定：启动后不修改计划及所属批次配置，不追加批次或补量；保留10%衔接和批次原有快捷操作，追加发布另建独立批次或新计划。

### M-publishing-operations：后续平台与三平台整体回归

| 字段 | 内容 |
| --- | --- |
| 状态 | `NOT_STARTED` |
| 目标 | 在完整百度能力上依次扩展B站、小红书，完成三平台任务/批次/计划回归 |
| 依赖 | 整体验收依赖 M-publishing-plan `DONE`；B站适配可在M7完成且百度已验收开放后先实施 |
| 业务验收 | [后续平台与三平台](milestones/M-publishing-operations.md) |
| Active CHG | None |
| Evidence | None，B站/小红书真实发布尚未验收 |

候选 CHG：

```text
PLATFORM 三平台闭环：B站验收开放 → 小红书验收开放 → 三平台整体回归
```

规划一个三平台扩展CHG，内部严格按B站真实验收开放 → 小红书真实验收开放 → 三平台整体回归推进。快速发布工具须先由M6完整交付，本阶段不再安排OPS-A/OPS-B。逐平台安全开放和提供方先于消费者的顺序不变；全部三平台通过才结束本阶段。

### M10：打包、升级、诊断与稳定性验收

| 字段 | 内容 |
| --- | --- |
| 状态 | `NOT_STARTED` |
| 目标 | 在真实发布能力上验证可安装、升级、诊断和恢复的交付组合 |
| 依赖 | M-publishing-operations `DONE`，继承 M6、M7、M-publishing-plan；不依赖 M8/M9 |
| 已有基线 | [首次全端上线](milestones/M-first-production-release.md)：已有 RC、部署和安装证据按原范围复用，不重复宣称发布业务通过 |
| Active CHG | None |
| Evidence | 生产发布综合验收尚未执行；升级/回退等未验项仍需补验 |

候选 CHG：

```text
M10 部署与恢复：HTTPS、MySQL/Object Storage 备份、恢复和回滚
M10 跨端交付：Agent 正式打包、FFmpeg/FFprobe 镜像、Sidecar 生命周期、签名和公证、升级、回滚和用户数据保留、日志脱敏和诊断包、故障演练及发布业务综合验收
```

规划两个可独立验收的交付单元：生产部署与数据恢复；跨端安装升级、诊断及发布业务综合验收。每个单元内部按依赖串行推进，不将打包脚本、单个组件锁或单项故障演练单列CHG。先核实首次上线已有证据，保留正确基线再补验实际缺口。

最终同时满足：

- 固定四仓版本组合可构建、安装、启动、卸载；Windows x64、macOS Intel/Apple Silicon 与适用签名/公证均有实际证据，用户不需要系统 Python。
- Cloud 合成继续只在 Cloud Worker 执行，FFmpeg 依赖受控；HTTPS、迁移、MySQL/对象存储恢复及真实跨版本升级/回退可验证，失败不丢用户数据。
- Desktop Sidecar 生命周期与认证正常；不兼容版本禁止敏感执行；日志和诊断不泄露凭据。
- 在安装版中回归单任务、批次、计划、图片和模板、三平台真实自动提交及公开核实；断网/重启/停止/升级均不重复投稿，不丢在途结果。
- 页面回归沿用[发布 Milestone 页面基线](milestones/README.md#页面实施与验收基线)与各阶段具体原型入口，实际页面须完成布局、交互、视觉一致性检查；接口/实现差异由研发在原型框架内解决，技术信息在原区域补充；改变业务规则时才由产品负责人确认。
- 发布必需统计可对账；互动、效果采集和综合数据看板不进入本轮验收分母；`release-matrix.yaml` 仅记录真实验证组合。

### 内容生产原型落地增量（2026-11-05）

原 M4／M5 签收保留；当前 PRD 与 ADR-0031 确认的新产品能力依次由 CHG-20261105-115 → 116 → 117 → 118 实施，闭环见 M4-K／L／M／N、M5-G。用户已授权连续推进并于次日人工走查；各项未通过实际验收前不升级整体完成状态，不用旧证据覆盖本次新增能力。

## 4. CHG 粒度

一个里程碑不是一个巨大 CHG。每个 CHG 应满足：

- 单一明确目标；
- 可单独审查；
- 有自动测试或人工验证；
- 能独立提交；
- 不包含未确认的产品或架构分叉；
- 发现范围扩大时立即拆分。

允许多个独立 Active CHG，但当前工作树一次只选一个执行，同一 CHG 同时只有一个执行器，CHG 内部默认串行；`depends_on` 未归档或合并证据不足时不得启动。共享 Contract / Infrastructure 的变更先交付共同 Foundation CHG，不能未协调并行修改。普通 S 级变更可以走 Issue/Commit/测试；M/L 级必须有 `delivery/active/<CHG>/change.md`。新 CHG 原则上使用短期分支、独立 Review、引用 CHG ID 的 PR 和合并 `main`；旧 CHG-20261015-098 的 `main` 历史不追溯迁移。

## 5. Codex 执行协议

执行、恢复、审查或完成 CHG 时，必须使用 `executing-wt-media-change` Skill。

会话启动建议：

```bash
cd wt-media
python3 wt-media-workspace/scripts/wt.py chg start CHG-YYYYMMDD-NNN   # 加 --plan 只预检，不切分支
codex
```

`chg start` 会完成依赖与 `main` 预检、切换/创建工作分支、生成 `.ai/CURRENT_CONTEXT.md` 并打印 handoff。恢复既有 CHG 用 `wt.py chg resume <CHG>`；直接运行 `prepare_ai_workspace.py` 只用于不切分支的纯快照重生成。

Codex 每次必须按 `AGENT-INDEX.md` §4 的**读取顺序**执行——该节是全项目唯一落点（入口、执行快照、交付台账、里程碑、当前 CHG、目标仓库逐项列明），本节不重复其清单。

编码前必须输出：

```text
当前事实
与本 CHG 的差距
真实文件映射
有序 Task 清单
每个 Task 的测试与验收方式
风险和阻塞
建议 Commit 边界
```

每个 Task 必须遵循：

```text
失败验证或测试
→ 最小实现
→ 测试
→ Diff 检查
→ Evidence
→ Checkpoint
→ 独立 Commit
```

必须暂停并写入 `Q-xx` 的情况：

- 需要改变“明确不做”；
- 需要新增核心对象、状态或 Contract；
- 需要改变事实来源；
- 需要跨越 Cloud、Agent、Desktop 既定职责；
- 需要引入新的基础设施；
- 需求和现有代码无法兼容；
- 测试只能通过修改验收标准通过。

## 6. 完成门禁

### CHG 门禁 — DONE

一个 CHG 只有满足以下条件才能标记为 `DONE`（状态词见第 3 节）：

- 范围内实现完成；
- 自动测试通过；
- 必要人工验证完成；
- 验收矩阵全部关闭；
- Contract 归属和兼容关系一致；
- Git Diff 无越界修改；
- 旧路径、旧状态和旧方案残留扫描完成；
- 必要产品、工程、协议和决策基线已回写；
- PRD 功能完整性：本 CHG 涉及的全部 PRD 功能点已逐条对照，且已实现或已记录暂缓（含原因和影响分析）；
- 受影响仓库独立 Commit；
- 验证结论及对应基线可从 `change.md`、PR／CI 或按风险保留的 `evidence/` 核对；不要求保存原始截图、日志或过程副本；
- `delivery/active` 和 `delivery/LEDGER.md` 不保留已完成 CHG 作为长期归档。

### 里程碑门禁 — DONE

一个里程碑进入 `DONE` 必须同时满足：

- 所有 P0 功能已经实现；
- 所有 CHG 自动验证通过；
- 完整跨端回归通过；
- 真实依赖验证通过；
- 没有关键 NOT_TESTED（来自功能事实矩阵）；
- 人工整体验收通过（你按真实用户流程操作确认）。

以下情况都不能单独作为完成依据：

- 页面存在、路由存在、按钮能够点击；
- 数据表存在、API 返回 200、单元测试通过；
- Mock 测试通过、构建成功；
- 历史代码存在、CHG 已提交；
- Codex 报告执行结束。

## 7. 下一步选择规则

执行控制体系完成后，不直接锁定 Cloud 用户与账号模块。下一项 CHG 必须根据 `MASTER_IMPLEMENTATION_PLAN.md` 和当前真实代码状态判断。

通常推荐顺序：

```text
三仓库最小工程骨架
→ Cloud-Agent Contract 与版本
→ Agent 注册、心跳、任务领取
→ Desktop 启停 Agent 和状态展示
→ 跨端闭环验收
→ 用户与账号/Profile
```

若工程骨架或最小跨端任务闭环未真实完成并通过验收，不得跳到用户与账号模块。

2026-11-06 用户确认的资源与合成闭环增量按 [M4-O](milestones/M4-content-production.md#m4-o-resource-composition-cutover) 及CHG121～125顺序独立交付；已授权清理现有改动后自动继续，在原仓库执行。
