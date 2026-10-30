# 模块化自媒体运营平台：代码实施总计划

> 日期：2026-07-15
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
→ M6 发布通用底座与 B站辅助发布
→ M7 百家号辅助发布
→ M8 互动管理闭环
→ M9 效果采集与数据统计
→ M10 打包、升级、诊断与稳定性验收
```

每个阶段都必须产生可以运行、可以测试、可以演示的闭环。M1 Cloud-Agent-Desktop 最小任务闭环完成前，不进入大规模业务模块开发。

## 2. 文档和事实源

```text
wt-media-workspace/
├── .ai/
│   └── CURRENT_CONTEXT.md          # 唯一执行状态快照，脚本生成，禁止手工编辑
├── docs/
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
| `NOT_STARTED` | 未进入该里程碑 | M6～M10 |
| `IN_PROGRESS` | 开发中 | 无 |
| `VERIFYING` | 自动综合验收完成，等待人工整体验收 | 无 |
| `DONE` | 人工整体验收通过 | M2、M3、M4、M5、M-launch-engineering |

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
| M2 | `DONE` | 2026-09-14 用户完成本轮综合人工验收并确认完整通过。M2-A/B/C/E 的真实依赖、构建、Desktop 与人工走查证据均已归档；原 M2-D 未纳入当时完成门槛。 | M2 原验收保持 DONE；2026-10-30 恢复 M2-D 社媒账号重构，108→109→110 独立交付，范围见 M2-D1～D3。 |
| M3 | `DONE` | A～E1 已实施并有真实证据；C2、E2 已于 2026-09-23 暂停；E3 综合验收 2026-09-23 在 Cloud `aaf66c5` 执行，验收矩阵第 1～7 项全部通过（首轮硬阻断 D-scheduler 同日修复并复验通过，另补证 Desktop 走查与 `material_failed` 注入），**用户同日签收** | M3 冻结为内容挖掘自动化入口基线；验收期只登记未修的 D1～D10、D-scheduler-2、S-1 仍由 `CHG-20260923-054`（planned）处置，**用户裁定 D3 不阻塞 M3**；C2/E2 留待后续版本 |
| M4 | `DONE` | M4 各实施 CHG、M4-H1 视觉整改与 M4-H2 统一走查均已完成；机器闭环与真实页面签收均有证据。 | 2026-10-28 用户签收 M4-H2；M4 冻结为 Cloud 内容生产闭环基线。 |
| M5 | `DONE` | M5-C1～C7（含 C2a）与 M5-F 均已归档；真实 Scheduler/Worker/FFmpeg/对象存储全链与页面走查有证据。 | 2026-10-28 用户签收 M5-AC-13 与 M4-H2；M5 冻结为策略自动生产基线。 |
| M6-M10 | `NOT_STARTED` | 无达到当前里程碑退出条件的正式完成项 | 按本计划顺序执行 |

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
| Active CHG | None；108/109/110 均为 PLANNED，当前仅核实数据库表、接口和文档，前置合并后逐项激活 |

当前交付顺序：

1. CHG-108：矩阵维护与人工登录后手动检查；无 Cookie 入库、未分类亦可识别，失败与历史结论分离。
2. CHG-109：单账号 Cookie 接入/更新；新建窗口优先、占用核实、内部写前保护、目标平台隔离与结果确认。
3. CHG-110：批量 Cookie 接入；预览零副作用、逐项执行、七计数、跳过恢复、成功不重放、未知先核实。

这是同一目标方案的实施顺序，不建设旧模块兼容层，也不恢复旧三种上号、接码和通用任务范围。数据库表、接口和废弃实现清理见[社媒账号设计](../docs/engineering/specs/social-accounts.md)。原已验收窗口、代理与运行环境不重做；每项新闭环必须验证真实效果、Cloud 事实和最终页面，不能以代码存在或请求成功宣称完成。

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

### M6：发布通用底座与 B站辅助发布

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 先建立发布通用模型，再完成第一个真实平台发布闭环。 |
| 依赖 | M5 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

目标闭环：

```text
composite_output
→ publication
→ task
→ Agent 打开指定 Profile
→ 上传和填写
→ pending_manual_submit
→ 运营人工提交
→ 链接校验/补录
→ published
→ tracked_object
```

候选 CHG：

```text
M6-C1 publication 模型、正式状态、创建规则与权限
M6-C2 发布管理工作台、状态页签、预检、重复和链接校验
M6-C3 发布 task Contract、Profile 串行队列与重启恢复
M6-C4 平台 Adapter、platform_publish_config 和版本
M6-C5 B站字段、固定流程、元素 JSON 与 Executor
M6-C6 B站单条辅助发布和 pending_manual_submit
M6-C7 批量配置、账号筛选快照和连续严格串行发布
M6-C8 人工提交、链接补录/纠正、手工补录和 tracked_object
M6-C9 failed、cancelled、result_uncertain、精确重试与审计
M6-C10 B站真实辅助发布综合验收
```

关键约束：

- Agent 不点击最终发布按钮；
- 同一 Profile 一次只执行一个敏感任务；
- 结果不明确时不得盲目重试；
- 不建设运营可视化流程编排器。

退出条件：

- 发布管理提供待发布、执行中、待人工提交、待补链接、失败、已发布和全部页签；
- 正式状态统一使用 `pending_manual_submit` 和 `cancelled`，`result_uncertain` 是任务/错误结果，不是新的 publication 主状态；
- 完成一条真实 B站辅助发布；
- 批量任务严格串行；
- 人工提交后可以补录或纠正链接，链接有效且 publication=`published` 时创建或复用 `tracked_object`；
- 重试创建新的实际 task，不覆盖历史尝试；
- 异常、取消、结果不确定和精确重试行为明确；
- Agent 重启后可以识别未完成任务；
- M6-C10 通过真实 B站、三角色 UI、Profile 串行、人工提交/补录、重启恢复和独立提交验收。

### M7：百家号辅助发布

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 通过第二个平台验证 Adapter 边界，而不是复制一套发布系统。 |
| 依赖 | M6 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

候选 CHG：

```text
M7-C1 百家号字段、元素配置和版本
M7-C2 百家号 Adapter 与 Executor
M7-C3 百家号单条、批量和连续辅助发布
M7-C4 人工提交、手工补录、链接校验和异常恢复
M7-C5 百家号真实发布与 B站完整回归验收
```

退出条件：

- 没有复制 B站通用发布逻辑；
- Cloud 不包含页面元素操作细节；
- Adapter 不直接修改 Cloud 正式状态；
- 百家号单条、批量、连续发布和手工补录均可完成；
- 链接校验、`tracked_object` 创建和异常恢复复用通用发布底座；
- M7-C5 完成百家号真实辅助发布、B站完整回归、UI/恢复/安全和独立提交验收。

### M8：互动管理闭环

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 完成点赞、收藏和评论任务闭环。 |
| 依赖 | M7 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

核心对象：

```text
tracked_object
→ interaction_task
→ 每个账号一个实际 task
```

候选 CHG：

```text
M8-C1 外部 tracked_object 录入、去重、状态和目标列表
M8-C2 interaction_task、账号级 task 和动作快照
M8-C3 公共评论模板和个人评论模板
M8-C4 DeepSeek 候选评论生成与人工确认
M8-C5 全局基础风控、执行预检和账号/Profile 校验
M8-C6 点赞和收藏 Executor、状态预判与幂等
M8-C7 评论 Executor、提交确认和结果不确定处理
M8-C8 任务台、队列、暂停/继续/取消、验证码接管、精确重试、审计与导出
M8-C9 互动真实业务综合验收
```

明确不建设：

- 关注；
- 转发；
- 私信；
- 主动搜索互动作品。
- 独立 `interaction_batch`；
- `interaction_item`。

这些不是暂缓功能，不允许创建占位接口或未来状态。

退出条件：

- 一个 `tracked_object` 对应一个 `interaction_task`；
- 批量选择多个作品时分别创建 `interaction_task`，批量操作不形成独立核心对象；
- 每个账号直接生成一个实际 `task`，并保存动作快照；
- 每次真实执行和重试产生新的 `task`；
- 个人模板仅本人可见；
- 风控、账号、Profile、代理和登录状态预检通过后才执行；
- 支持暂停、继续、取消、验证码人工接管和动作级精确重试；
- 高风险结果不确定时停止自动重试；
- 不存在明确排除能力的残留实现；
- M8-C9 通过真实点赞/收藏/评论、UI、并发、人工接管、恢复、安全和独立提交验收。

### M9：效果采集与数据统计

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 让发布、互动、素材和策略形成可追踪的数据闭环。 |
| 依赖 | M8 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

候选 CHG：

```text
M9-C1 platform_metric_snapshot 模型、采集 Contract 与调度
M9-C2 B站效果采集
M9-C3 百家号效果采集
M9-C4 工作量和内容发现/素材/生产/发布/互动业务聚合
M9-C5 用户、账号、Profile、代理和运行环境统计与新鲜度
M9-C6 看板、趋势、排名、漏斗、积压、提醒和下钻
M9-C7 Excel 导出、权限、历史范围快照与明细对账
M9-C8 数据统计综合验收
```

关键约束：

- Analytics 只读取正式业务事实；
- 统计异常不能修改原始业务数据；
- 原始快照和聚合结果分离；
- 首版不建设复杂实时数仓；
- 不建设 `production_signal`，生产提示和重复风险从正式业务事实派生。

退出条件：

- `tracked_object` 已由 M6/M8 创建，M9 不重新定义或延迟创建；
- 定时采集生成不可变快照；
- 可以按用户、游戏、平台、账号、Profile、代理、素材、策略和时间查询工作与效果；
- 支持趋势、排名、漏斗、积压、提醒、下钻、Excel 导出和明细对账；
- 历史范围使用业务发生时快照，不随后续主数据变化改写；
- 采集失败不影响发布业务；
- M9-C8 通过真实 B站/百家号采集、调度恢复、权限、UI、导出、对账和独立提交验收。

### M10：打包、升级、诊断与稳定性验收

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 将开发环境可运行升级为运营人员可安装、可升级、可诊断、可恢复。 |
| 依赖 | M9 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

候选 CHG：

```text
M10-C1 Cloud Docker Compose、反向代理、HTTPS、配置和 Migration 部署
M10-C2 MySQL/Object Storage 备份、恢复和回滚
M10-C3 Agent 正式打包、受控依赖和可复现构建
M10-C4 Cloud Compose Worker 的 FFmpeg/FFprobe 镜像、Manifest、Hash、许可证和回滚
M10-C5 Desktop 生产级 WebView、Sidecar 生命周期和本地数据目录
M10-C6 Windows x64、macOS Intel/Apple Silicon 安装包、签名和公证
M10-C7 组件更新、版本兼容、升级、回滚和用户数据保留
M10-C8 Cloud/本地状态页、告警、日志脱敏和诊断包
M10-C9 中断恢复、安全、备份恢复和升级故障演练
M10-C10 全系统生产发布综合验收
```

退出条件：

- 用户不需要安装系统 Python；
- Cloud Compose Worker 不依赖系统 PATH 中的 FFmpeg，Desktop / Agent 不打包或执行视频合成；
- Cloud 可通过 HTTPS 部署，Migration、备份、恢复和回滚可演练；
- MySQL 和 Object Storage 均有可验证备份/恢复；
- 三种桌面目标可以构建、安装、启动、卸载，macOS 完成签名和公证；
- Desktop 使用 M0/M1 的真实集成并完成生产级 Sidecar、目录、权限和更新加固；
- 不兼容版本禁止执行敏感任务；
- 升级失败可回滚且不删除用户数据；
- 普通日志不存在敏感信息；
- Cloud 和本地状态页、告警、诊断包可以定位关键故障；
- 关键中断恢复场景通过；
- `release-matrix.yaml` 存在正式可用版本组合；
- M10-C10 通过安装、升级、回滚、备份恢复、安全、诊断、三平台和全业务回归验收。

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
- `delivery/active/<CHG>/evidence/` 目录存在非空证据文件；
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
