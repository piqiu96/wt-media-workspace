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
→ M3 抖音内容发现到素材入库
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
├── docs/
│   ├── product/                    # 当前有效产品事实
│   ├── engineering/                # 当前有效工程架构
│   ├── contracts/                  # 人类可读的跨仓库协议治理
│   └── decisions/                  # 少量重大决策及原因
├── delivery/
│   ├── MASTER_IMPLEMENTATION_PLAN.md
│   ├── LEDGER.md                   # 当前 Active CHG 索引，不是历史归档
│   └── active/
│       └── CHG-YYYYMMDD-NNN/
│           ├── change.md           # 当前变更唯一执行依据
│           └── evidence/           # 测试、Spike、Diff、人工验证事实
├── config/
│   ├── contract-map.yaml           # 机器可读协议归属和消费关系
│   └── release-matrix.yaml         # 已验证版本组合
├── skills/
├── scripts/
└── templates/
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
BLOCKED
VERIFYING
DONE
```

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
| M0 | `IN_PROGRESS` | 治理、仓库骨架、基础健康检查和历史 CI/Contract Map | 需完成 M0-R1～R6 的真实构建和启动门禁 |
| M1 | `NOT_STARTED` | Contract 兼容、注册心跳、noop task、Local API/SSE 的历史基础实现 | 需完成持久化、正式 task schema、真实 Desktop 和恢复闭环 |
| M2 | `NOT_STARTED` | 认证、媒体账号基础、Profile 扫描、运行环境和并发保护的历史实现 | 按新 M2-C1～C11 审计复用并补齐完整产品域 |
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
| 状态 | `IN_PROGRESS` |
| 目标 | 在治理体系可用的基础上，使 Cloud、Web、Agent、Desktop 成为可安装依赖、可真实构建、可启动停止、可测试的独立工程组件。 |
| 依赖 | None |
| Active CHG | `CHG-20260715-002` |
| Evidence | 继承证据：CHG-002 执行控制；CHG-003 Master Plan；CHG-004 工程骨架；CHG-005 脚手架健康检查；CHG-006 测试、CI、Contract Map 和版本矩阵；CHG-007 历史综合验收。以上证据不包含真实 Desktop/Tauri 构建，不能满足修订后的 M0 退出条件。 |
| 完成日期 | None |
| Commit/Tag | CHG-002 commits: `63092e8`, `1504355`, `e20f672`, `681d9c9`, `6e800a0`, `b439038`; CHG-003 commits: `a7d49fe`, `784b3b8`; CHG-004 runtime commits: Cloud `c28bd3d`, Agent `4ef0dfe`, Desktop `0774635`; Workspace evidence commit `67245d2`; CHG-005 runtime commits: Cloud `3bb6028`, Agent `2c2562f`, Desktop `54e6e70`; Workspace evidence commit `2442ba0`; CHG-006 runtime commits: Cloud `f00ae41`, Agent `1351f5f`, Desktop `54d7b6f`; Workspace evidence commit `a4d141e`; CHG-007 Workspace evidence commit `716c143`。 |

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
| 状态 | `NOT_STARTED` |
| 目标 | 在 M0 的真实组件上建立持久化、无 Mock、可重启恢复的 Cloud-Agent-Desktop-Web 最小任务环境，供后续所有业务里程碑复用。 |
| 依赖 | M0 `DONE` |
| Active CHG | None |
| Evidence | 继承证据：CHG-008 至 CHG-014 已验证 Contract 兼容、Agent 注册心跳、noop task、Local API/SSE 和脚手架集成。Cloud task/Agent Registry 仍为内存实现，Desktop 仍使用 Mock 入口，`task_schemas` 仍为占位，因此不能满足修订后的 M1 退出条件。 |
| 完成日期 | None |
| Commit/Tag | CHG-008 commits: Cloud `d2acf2a`; Agent `9a97b2d`; Workspace `fab15d3`, `1cac21f`, `559f907`; CHG-009 commits: Cloud `047d006`, `8cb351a`; Agent `eb5183d`, `482d1f8`; Workspace `e607c98`, `98220b3`; CHG-010 commits: Cloud `89d776b`; Agent `356aa3f`; Workspace `9a4ccf3`, `6e3d216`; CHG-011 commits: Cloud `90daf2e`; Agent `598e0eb`; Workspace `cdeb63c`, `100c09c`; CHG-012 commits: Agent `aaeabdb`; Workspace `edc5e14`, `c2aa5f8`; CHG-013 commits: Desktop `a8f8eef`; Workspace `cf0a49c`, `cd626c2`; CHG-014 commits: Workspace `8859162`, `b86e34c`。 |

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
| 状态 | `NOT_STARTED` |
| 目标 | 在 M1 真实端到端环境上，完整交付用户、媒体账号、BitBrowser 窗口、代理、Cookie、开户、运行环境、敏感任务权限以及对应 Web/Desktop 产品体验。 |
| 依赖 | M1 `DONE` |
| Active CHG | None |
| Evidence | 继承证据：CHG-015 至 CHG-020 已验证认证、媒体账号基础模型、BitBrowser 主账号树/Profile 扫描、运行环境上报、敏感任务并发和真实 MySQL/BitBrowser 基础链路。窗口管理、代理、Cookie、开户、完整用户管理 UI、真实 Desktop 产品体验尚未交付，历史 PASS 不自动关闭新的 M2-C1 至 C11。 |
| 完成日期 | None |
| Commit/Tag | CHG-015 commits: Cloud `50b5c8d`, `03b0dcc`; Workspace `f3e7d1a`, `51ab7de`, `e79db94`, `6576c44`, `a1f12d7`。CHG-016 commits: Cloud `18f687a`, `8eb70ba`; Workspace `266595f`, `3c65f6e`, `92c4565`。CHG-017 commits: Agent `14e51be`, `f0257b5`; Cloud `bba30ef`, `727ad9e`; Workspace `0bb7ba8`, `b67d493`, `5123ab8`。CHG-018 commits: Agent `8652a90`, `d5a9e4d`; Cloud `6ef0308`, `866364e`, `9770e1b`; Workspace `f54c08c`, `955f8ab`, `1bc1de9`。CHG-019 commits: Agent `5cd9212`, `3d4081a`; Cloud `d1d0ddc`, `2753715`; Workspace `5c59c5a`, `019d4a6`。 |

候选 CHG：

```text
M2-C1 用户认证、单活会话、三角色、游戏范围与用户管理台
M2-C2 媒体账号生命周期、标签、分配与账号工作台
M2-C3 BitBrowser 主账号树、Profile 扫描 Diff 与 Cloud 分配
M2-C4 窗口/Profile 创建、修改、打开、检测、归档与恢复
M2-C5 代理导入、解析、检测、配额、分配与回读
M2-C6 Cookie 导入导出读写、active Cookie 与账号检测
M2-C7 批量 Cookie、短信链接、人工验证码开户与部分成功重试
M2-C8 Agent 节点绑定、运行环境上报与健康页面
M2-C9 Profile 并发、敏感任务预检、结果不确定审核与审计
M2-C10 Web/Desktop 账号环境综合工作台与三角色 UX
M2-C11 真实 MySQL、BitBrowser、代理、Cookie、Desktop 综合验收
```

重新执行规则：

- 每个新 CHG 先审计历史实现和 Contract，再决定复用、修正或补齐；
- 历史 C1-C6 的自动测试和真实证据可以复用，但必须满足新 CHG 的完整范围和 UI/人工验收后才能标记 PASS；
- 不为重新编号而盲目重写已经正确的代码；
- 任何代理、Cookie、Profile 修改都必须写入 BitBrowser 后读回验证；
- 批量操作必须支持部分成功、失败项重试和明确错误反馈。

退出条件：

- 技术角色可以创建、启停、修改用户、分配角色和游戏范围、重置密码并查看审计；普通/高级运营只能访问授权范围；
- 可以完成媒体账号创建、识别、标签、分配、状态维护和批量账号检查；
- 一个 Cloud 用户最多绑定一棵 `main_user_id` 主账号树；同一主账号树可服务多个运营，但 Profile 访问严格按 Cloud 分配隔离；
- 窗口/Profile 的同步、Diff、创建、修改、打开、检测、归档和恢复均有 UI 与读回验证；
- 代理支持批量导入、智能解析、检测、平台配额、分配、停用和 BitBrowser 回读；
- Cookie 支持导入、导出、读取、写入、original/active 分离以及实际登录状态检查；
- 批量 Cookie、短信链接和人工验证码三种开户路径均可完成，支持部分成功和失败重试；
- Agent 能确认 Profile 的 `main_user_id`、`profile_user_id` 审计信息和 Cloud 授权范围；
- 未授权用户不能执行敏感任务；同一 Profile 的敏感任务被拒绝或串行；结果不确定时进入人工审核；
- Cloud 是正式账号事实来源；
- Desktop 不复制账号业务规则，但能承载 Cloud Web 并提供真实本地环境、Agent、文件和任务状态页面；
- M2-C11 通过自动 Contract/测试、真实 MySQL/BitBrowser/代理/Cookie、三角色 UI、Desktop 人工、恢复、安全和独立提交验收。

### M3：抖音内容发现到素材入库

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 打通链接导入、关键词搜索、作者监控到素材入库的首条业务数据闭环。 |
| 依赖 | M2 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

目标闭环：

```text
即时多链接 / 手动关键词查询
→ 临时结果
→ 运营选择
→ source_content
→ material

关键词 / 作者监控策略
→ crawl_strategy
→ crawl_task
→ source_content
→ 自动或人工转 material
```

候选 CHG：

```text
M3-C1 抖音外部接口 Spike、Cloud-Agent Contract 和正式任务 Schema
M3-C2 crawl_strategy、crawl_task、Scheduler、快照与幂等
M3-C3 抖音多链接即时查询与选择导入
M3-C4 抖音手动关键词即时查询与选择导入
M3-C5 关键词/作者监控、立即执行、初始化与重试
M3-C6 source_content 全局去重、状态和最新原始 JSON
M3-C7 待选内容列表、筛选、忽略、恢复、权限与日志
M3-C8 source_content 到 material 的事务转换和幂等
M3-C9 真实抖音接口、Scheduler 和素材入库综合验收
```

明确不做：

- B站搜索；
- 小红书搜索；
- 百度搜索；
- Excel 导入；
- 竞品账号监控；
- 动态抓取工作流平台。
- 独立 `crawl_result`；
- `content_lead`；
- 候选内容领取锁。

退出条件：

- 即时多链接和手动关键词查询不创建 `crawl_task`，未选择结果不写正式数据；
- 定时、立即执行、初始化和重试必须创建 `crawl_task` 并保存策略快照；
- Scheduler 具备防重、同策略串行和重启恢复；
- 重复作品不会重复创建 `source_content`；
- 抓取失败不会产生正式素材；
- 精准策略可自动转素材，泛化策略进入人工筛选，不新增精准词对象类型；
- `source_content` 保存最新来源字段和最新原始 JSON，可忽略和恢复；
- `source_content -> material` 事务幂等，同一内容不重复创建素材；
- M3-C9 通过真实抖音接口、自动测试、Web UI、失败重试、调度恢复和独立提交验收。

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

## 6. DONE 门禁

一个 CHG 只有满足以下条件才能标记为 `DONE`：

- 范围内实现完成；
- 自动测试通过；
- 必要人工验证完成；
- 验收矩阵全部关闭；
- Contract 归属和兼容关系一致；
- Git Diff 无越界修改；
- 旧路径、旧状态和旧方案残留扫描完成；
- 必要产品、工程、协议和决策基线已回写；
- 受影响仓库独立 Commit；
- `delivery/active` 和 `delivery/LEDGER.md` 不保留已完成 CHG 作为长期归档。

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
