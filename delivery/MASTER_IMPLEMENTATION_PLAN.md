# 模块化自媒体运营平台：代码实施总计划

> 日期：2026-07-15
> 适用项目：WT Media 模块化自媒体运营平台  
> 执行方式：一个总路线、一个当前变更、一次只完成一个可验证闭环  
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
→ M4 素材使用与本地合成闭环
→ M5 云端自动生产与云端成片池
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
│   │       ├── checkpoint.md       # 已完成 / 未完成 / 阻塞 / 下一步
│   │       └── evidence/           # 测试、Spike、Diff、人工验证事实
│   ├── milestones/                 # 人工确认的业务闭环基线
│   ├── planned/                    # 待规划与待决记录
│   ├── completed/                  # 已收口记录，默认不加载
│   ├── reports/                    # 阶段性审计与分析报告
│   └── verifying/
├── config/
│   ├── contract-map.yaml           # 机器可读协议归属和消费关系
│   ├── release-matrix.yaml         # 已验证版本组合
│   ├── skills-distribution.yaml    # skill 分发目标唯一声明
│   └── repository-map.yaml         # 关联工程路径唯一来源
├── skills/
├── scripts/
├── .claude/skills/                 # 自动生成并提交 Git
├── .codex/skills/                  # 自动生成并提交 Git
├── templates/
│   └── delivery/                   # CHG 与 evidence 记录模板
├── AGENT-INDEX.md                  # 跨仓库路由与渐进式加载规则
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

每个里程碑只允许以下状态：

```text
NOT_STARTED
IN_PROGRESS
VERIFYING
DONE
```

CHG 只允许以下状态：

```text
TODO → IMPLEMENTED → VERIFIED → CLOSED
```

状态定义：

| 级别 | 状态 | 含义 |
|---|---|---|
| CHG | TODO | 已规划，未开始 |
| CHG | IMPLEMENTED | 代码完成，待自测 |
| CHG | VERIFIED | 自测/集成/回归通过 |
| CHG | CLOSED | 验证通过，evidence 就绪 |
| 里程碑 | NOT_STARTED | 未进入该里程碑 |
| 里程碑 | IN_PROGRESS | 开发中 |
| 里程碑 | VERIFYING | Codex 完成自动综合验收，等待你人工整体验收 |
| 里程碑 | DONE | 人工整体验收通过 |

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
| M2 | `DONE` | 2026-09-14 用户完成本轮综合人工验收并确认完整通过。M2-A/B/C/E 的真实依赖、构建、Desktop 与人工走查证据均已归档；M2-D 保持 `DEFERRED`。 | M2 冻结为当前运行环境与账号管理基线；后续内容发现从 M3 开始，M2-D 或真实受限样本校准须以独立 CHG 恢复。 |
| M3-M10 | `NOT_STARTED` | 无达到当前里程碑退出条件的正式完成项 | 按本计划顺序执行 |

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

### M2：用户、角色、媒体账号与运行环境

| 字段 | 内容 |
|---|---|
| 状态 | `DONE` |
| 目标 | 在 M1 真实端到端环境上，完整交付用户、媒体账号、BitBrowser 窗口、代理、运行环境、敏感任务权限以及对应 Web/Desktop 产品体验；Cookie 与开户整体由暂缓的 M2-D 后续单独交付。 |
| 依赖 | M1 `DONE`（M1 复验通过后自动解除） |
| Active CHG | None。M2-A/B/C/E 的本轮收口变更均已归档。 |
| Evidence | 最终人工验收见 `delivery/reports/2026-09-14-m2-final-acceptance.md`；各闭环证据位于已归档 CHG。历史 PRD 差距记录和 47% 旧口径不作为当前完成率。 |
| 业务闭环基线 | `delivery/milestones/M2-account-runtime.md`。本轮以 M2-A、M2-B、M2-C、M2-E 的用户操作、真实副作用、假成功禁止项和业务验收为准；M2-D 为 `DEFERRED`。 |
| 完成日期 | 2026-09-14 |
| Commit/Tag | 继承历史提交；M2-C `CHG-20260805-033`、M2-E `CHG-20260913-035` 与资源页统一改造 `CHG-20260914-036` 已归档。 |

已完成 CHG 降级为继承证据：

```text
CHG-20260715-010 M2-R0 UI 重构：TDesign 迁移 + 统一页面模板（继承证据）
CHG-20260715-011 M2-C1 用户管理追认（继承证据）
CHG-20260716-012 架构迁移阶段四（继承证据）
CHG-20260716-013 架构迁移阶段五+六（继承证据）
```

实施方式：按 M2-A→M2-B→M2-C→M2-E 四条业务闭环顺序补齐。M2-D 账号上号与Cookie闭环暂缓，后续恢复时必须重新创建独立 CHG。每条闭环必须满足"用户可完成完整业务操作"方可标记 CLOSED。

### M2-A：用户、权限、会话与运行环境可信闭环

兼容能力索引：M2-A：用户与权限闭环。

```text
管理员创建分组和用户 → 分配角色、分组与游戏 → 用户确认登录会话 → Desktop验证Agent与BitBrowser身份 → 权限和环境可信
```

目标：建立三角色、单层运营分组、游戏范围、会话替换和BitBrowser主账号身份可信链路。M2-A 已通过 CHG-20260723-024 人工验收：Cloud 用户管理、运营分组、游戏管理、Desktop 角色入口限制、主账号确认 API、引用保护和本地敏感入口阻断已形成当前可用基线。

### M2-B：媒体账号与 Profile 闭环

```text
绑定 BitBrowser 主账号 → 扫描 Profile → 展示差异 → 人工确认同步 → 创建媒体账号 → 绑定 Profile → 打开并检查真实账号
```

目标：打通 BitBrowser 主账号绑定、Profile Diff、窗口生命周期、账号绑定与真实检查。当前Cloud镜像、Diff、任务接口和Agent适配器可复用，但必须改为Desktop安全桥下的单项同步调用，补齐双向Diff、授权、批量结果和页面闭环。

### M2-C：代理与 Profile 闭环

```text
导入代理 → 解析预览 → 检测可用性 → 分配给 Profile → 写入 BitBrowser → 回读确认 → Profile 可以正常打开
```

目标：代理从无副作用预览、真实检测、统一窗口配额，到写入Profile并读回的全链路。当前台账、文本解析、检测和Agent适配器可复用；平台配额、预览即入库、异步写入和缺少读回闭环必须修正。

### M2-D：Cookie 与开户闭环（DEFERRED）

```text
导入 Cookie → 写入 Profile → 打开平台 → 判断真实登录身份 → 回填媒体账号 → 批量部分成功 → 失败项单独重试
```

目标：CK、接码链接、人工验证码和自动失败后的人工接管均可完成真实上号。当前账号台账、Cookie字段和Agent执行器可复用；登录凭据字段、专用batch/item、三种独立流程、人工登录后“同步账号信息”、冲突处理和恢复均需补齐。本轮 M2 暂缓该闭环，不将其计入 M2 退出条件。

### M2-E：Desktop 与安全闭环

```text
Desktop 启动 → Local Agent 启动 → 登录 Cloud → 查看本地环境状态 → 执行账号和 Profile 操作 → 查看进度与错误 → 未授权操作被阻止 → 同一 Profile 敏感任务不能并发
```

目标：Desktop 端可完成本地管理操作。已实现 7/10 功能点，需修复 E2/E6。

重新执行规则：

- 每个新 CHG 先审计历史实现和 Contract，再决定复用、修正或补齐；
- 历史 C1-C6 的自动测试和真实证据可以复用，但必须满足新 CHG 的完整范围和 UI/人工验收后才能标记 CLOSED；
- 不为重新编号而盲目重写已经正确的代码；
- 任何代理、Cookie、Profile 修改都必须写入 BitBrowser 后读回验证；
- 批量操作必须支持部分成功、失败项重试和明确错误反馈。

退出条件：

- 管理员可以创建、启停、修改用户和运营分组，分配角色、分组与游戏范围，重置密码并查看审计；普通/高级运营只能访问“本人或同组”与授权游戏的交集范围；
- 可以完成媒体账号创建、识别、标签、分配、状态维护和批量账号检查；
- 一个 Cloud 用户最多绑定一棵 `main_user_id` 主账号树；同一主账号树可服务多个运营，但 Profile 访问严格按 Cloud 分配隔离；
- 窗口/Profile 的同步、Diff、创建、修改、打开、检测、归档和恢复均有 UI 与读回验证；
- 代理支持批量导入、智能解析、检测、统一 `max_profile_count` 窗口配额、分配、停用和 BitBrowser 回读；
- M2-D 暂缓期间，不将 Cookie 导入/导出/读写、original/active 分离或实际登录状态写回作为本轮 M2 退出条件；
- M2-D 暂缓期间，不将批量 Cookie、短信链接和人工验证码开户路径作为本轮 M2 退出条件；
- Agent 能确认 Profile 的 `main_user_id`、`profile_user_id` 审计信息和 Cloud 授权范围；
- 未授权用户不能执行本地敏感操作；同一 Profile 的敏感操作被拒绝或串行；结果不确定时进入人工审核；单项短BitBrowser操作不得为追踪而强制创建异步任务；
- Cloud 是正式账号事实来源；
- Desktop 不复制账号业务规则，但能承载 Cloud Web 并提供真实本地环境、Agent、文件和任务状态页面；
- M2-C 与 M2-E 通过自动 Contract/测试、真实 MySQL/BitBrowser/代理、三角色 UI、Desktop 人工、恢复、安全和独立提交验收。

### M3：内容挖掘自动化入口建设

| 字段 | 内容 |
|---|---|
| 状态 | `IN_PROGRESS`（A～E1 有真实证据；C2/E2 未通过真实验收；E3 未开始） |
| 产品方向 | 用户已明确确认内容挖掘 V2（2026-09-15）；M2 保持 `DONE`。 |
| 目标 | 三个人工入口与两种自动策略统一入内容池，经人工筛选或策略规则转为可追踪素材；M3 自动发现由 Cloud Scheduler + Cloud Worker/Crawler 执行，不创建 Agent 任务。 |
| 依赖 | M2 `DONE`；按阶段解决接口、权限、周期与状态口径。 |
| 规划状态 | A～E 与八个 CHG 草案已拆分；当前由 CHG-20260916-052 承载实施，M3-B～E 由 Cloud Scheduler + Cloud Crawler 承担，不创建 Agent 任务。 |
| 闭环 | `delivery/milestones/M3-content-discovery-v2.md` |
| 产品/决策 | `docs/product/M3-content-mining-v2.md`；ADR-0013（第 3、7 条已于 2026-09-23 增补）、ADR-0014（团队级隔离已确认）、ADR-0015（Cloud-owned 执行） |
| Active CHG | CHG-20260916-052 |
| Evidence | Cloud `docs/superpowers/handoffs/`（2026-09-18、2026-09-21、2026-09-22）与 CHG-052 `checkpoint.md`/`evidence/`；关键词链路经真实凭据取得 `status=success`。C2/E2 无真实外部证据。 |
| 完成日期 | None |
| Commit/Tag | None |

三个页面：内容池、挖掘策略、挖掘任务。

目标闭环：

```text
分享链接解析并入池 / 关键词与博主搜索选择 / 自动挖掘策略
→ source_content 内容池
→ 人工转素材
→ material
```

| 阶段 | 独立结果 | CHG |
| --- | --- | --- |
| M3-A | 内容池与人工转素材基础能力；必须由 B 复验真实来源 | CHG-20260915-044 |
| M3-B | 真实分享链接解析入池，首个外部闭环 | CHG-20260915-045 |
| M3-C1 | 关键词主动搜索选择入池 | CHG-20260915-046 |
| M3-C2 | 博主主动搜索选择入池 | CHG-20260915-047 |
| M3-D | keyword/author 统一策略配置、周期与启停 | CHG-20260915-048 |
| M3-E1 | 关键词周期任务、真实入池、日志统计与恢复 | CHG-20260915-049 |
| M3-E2 | 作者周期任务与真实增量入池 | CHG-20260915-050 |
| M3-E3 | 综合验收、只读运行视图核验及用户签收 | CHG-20260915-051 |

A、B、C1、D、E1 已实施并有真实证据；C2、E2 因作者侧接口未开放未通过真实验收；E3 仍为 DISCUSSION，其执行草案位于 `delivery/planned`。原 CHG-037～043 为 SUPERSEDED，不再执行，也不计为已完成。C1/C2 共同完成 C，E1/E2/E3 共同完成 E。逐阶段状态见 `delivery/milestones/M3-content-discovery-v2.md` 第 2.1 节。

明确不做：视频下载/存储/校验、剪辑、AI 评分、自动生产/发布/互动/数据分析、其他渠道真实采集、工作流引擎、可视化调度器、任意脚本执行、crawl_result、完整历史原始 JSON。

自动转素材为 M3 范围内正式能力（2026-09-23 用户确认，见 ADR-0013 第 3 条），按 `auto_material` / `material_rule` / 阈值规则生效，不再列入“明确不做”。

退出条件：

- 单/批量链接、关键词和博主搜索均有真实接口到入池证据；未选搜索结果不写正式来源。
- 两种策略均能真实定时触发，创建带快照的 crawl_task，自动入池；保存配置/任务列表不是完成证据。
- 策略只定义规则，Cloud Scheduler 负责触发，Cloud Crawler 负责外部执行；同周期防重、同策略串行及重启恢复通过。
- source_content 三态、crawl_task 五态（含 `partial_success`）与部分失败口径均明确，统计/错误和业务事实一致。
- 全局唯一、权限隔离、忽略保护、人工转换事务与素材来源可追踪同时成立。
- 仅预留渠道/策略扩展抽象；运行视图只读且基于真实记录。
- Cloud Web/Desktop、受控故障、M2 回归及用户最终验收通过后才标 M3 DONE。

### M4：素材使用与本地合成闭环

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 打通素材领取、合成任务、本地 Agent FFmpeg 执行和成片元数据闭环。 |
| 依赖 | M3 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

目标闭环：

```text
material
→ material_usage
→ compose_pool_item
→ task
→ Local Agent + FFmpeg
→ composite_output
```

候选 CHG：

```text
M4-C1 material 生命周期、公共/私有素材和私转公审核
M4-C2 material_usage 领取、下载、放弃与恢复
M4-C3 合成模板、版本与参数 Schema
M4-C4 合成策略、版本、快照与多版本选择
M4-C5 compose_pool_item、合成任务台、批量、取消与卡死处理
M4-C6 Local Agent SQLite、文件索引、Desktop 桥和 FFmpeg 环境
M4-C7 素材下载、Hash/文件校验、重试与重新定位
M4-C8 本地视频合成 Executor
M4-C9 composite_output、失败重试、强制中断和本地文件管理
M4-C10 本地合成真实视频综合验收
```

关键约束：

- 正式运行不依赖系统 Python；
- FFmpeg 不依赖系统 PATH；
- Agent 不自行创建正式业务任务；
- 失败任务不进入成片列表；
- 成片默认保存在本地；
- Cloud 保存正式元数据和必要引用。

退出条件：

- material 支持 active、paused、retired 生命周期，公共/私有范围和私转公审核；
- `material_usage` 支持领取、下载、放弃和恢复，且权限范围明确；
- 合成前素材必须下载并通过 Hash、文件存在性和可读性校验；
- compose_pool_item 支持批量、取消、卡死和异常池处理；
- 能从一个真实素材生成可播放视频；
- 来源素材、模板版本、策略版本和参数快照可追溯；
- FFmpeg 不兼容时禁止执行；
- Local Agent SQLite、文件索引和 Desktop 真实桥接可验证；
- 失败、重试、强制中断和本地文件状态明确；
- M4-C10 通过真实文件、FFmpeg、Desktop UI、Agent 重启恢复和独立提交验收。

### M5：云端自动生产与云端成片池

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 复用本地合成核心，打通 Cloud Agent 生产、云端成片池、领取、下载和清理。 |
| 依赖 | M4 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

目标闭环：

```text
production_rule
→ material
→ compose_pool_item
→ task
→ Cloud Agent
→ composite_output
→ composite_output_pool
→ composite_output_claim
→ Local Agent 下载到本地
```

候选 CHG：

```text
M5-C1 production_rule 范围、调度和单次/每日数量
M5-C2 素材风险校验、审核池和处置
M5-C3 Cloud Agent 共享合成核心、对象存储与完整性
M5-C4 compose_pool_item/task、重试、卡死和异常处理
M5-C5 composite_output_pool 和可见范围策略
M5-C6 composite_output_claim 独占领取和自动/人工释放
M5-C7 云端下载、Hash 校验和本地成片记录
M5-C8 7 天清理、重复风险和生产/发布摘要回写
M5-C9 云端生产与成片池综合验收
```

明确不做：

- 独立生产规则管理平台；
- 动态工作流引擎；
- 独立策略组表；
- `composite_output_download_task`；
- 独立 `pool_policy` 表。

退出条件：

- Local Agent 和 Cloud Agent 复用同一合成核心；
- 云端生产保留 `material -> compose_pool_item -> task` 正式链路；
- 对象存储上传、Hash、下载、生命周期和恢复可验证；
- 高风险素材进入审核池，处置行为有日志；
- 同一成片不会被多人重复领取；
- 领取失败、超时和高级运营释放不会永久锁死；
- 下载通过完整性校验并进入本地成片管理；
- 清理、重复风险和生产/发布摘要回写可验证；
- M5-C9 通过真实 Cloud Agent、对象存储、调度、领取并发、下载恢复和独立提交验收。

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
M10-C4 FFmpeg/FFprobe 分发、Manifest、Hash 和许可证
M10-C5 Desktop 生产级 WebView、Sidecar 生命周期和本地数据目录
M10-C6 Windows x64、macOS Intel/Apple Silicon 安装包、签名和公证
M10-C7 组件更新、版本兼容、升级、回滚和用户数据保留
M10-C8 Cloud/本地状态页、告警、日志脱敏和诊断包
M10-C9 中断恢复、安全、备份恢复和升级故障演练
M10-C10 全系统生产发布综合验收
```

退出条件：

- 用户不需要安装系统 Python；
- 不依赖系统 FFmpeg；
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

一次只允许一个 Active CHG。普通 S 级变更可以走 Issue/Commit/测试；M/L 级必须有 `delivery/active/<CHG>/change.md`。

## 5. Codex 执行协议

执行、恢复、审查或完成 CHG 时，必须使用 `executing-wt-media-change` Skill。

会话启动建议：

```bash
cd wt-media
python3 wt-media-workspace/scripts/prepare_ai_workspace.py --change CHG-YYYYMMDD-NNN
codex
```

Codex 每次必须按顺序读取：

1. 根 `AGENTS.md`；
2. 根 `.ai/CURRENT_CONTEXT.md`；
3. 当前 `delivery/active/<CHG>/change.md`；
4. CHG 引用的产品、工程、协议和决策基线；
5. 受影响仓库各自的 `AGENTS.md`；
6. 各仓库 `git status`、当前分支和相关测试。

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

### CHG 门禁 — CLOSED

一个 CHG 只有满足以下条件才能标记为 `CLOSED`：

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
