# ADR-0015：M3 内容挖掘由 Cloud 内部执行

- Status: Accepted
- Date: 2026-09-16
- Scope: M3 内容池、挖掘策略、挖掘任务及 Douyin 内容发现适配
- Supersedes: ADR-0013 第 6 条中“Cloud Agent 查询外部平台”的 M3 具体实现约束；不改变 M2 浏览器、文件、FFmpeg、发布和互动自动化的 Agent 边界。

## Context

M3 的内容挖掘只需要访问公开/已授权的内容数据接口，不涉及用户本机、BitBrowser、Cookie 注入、文件、FFmpeg 或浏览器自动化。现有实现把 discovery 任务接入通用 Cloud-Agent task store，扩大了运行链路，也让 `crawl_task` 混淆为 Agent 执行任务。

## Decision

1. M3 不创建、分配或执行 Cloud Agent / Local Agent task；Desktop 不参与内容挖掘执行。
2. Cloud 内部提供受控 `Crawler` 接口和渠道适配器。当前实现 `DouyinCrawler` 通过 **`config/` 下的 TOML 配置**读取 API 地址和凭据（`config/clients/http/douyin.toml`、`config/credentials/douyin.toml`），不能从客户端传入或在代码中硬编码。（2026-09-23 更正：原文写「通过服务端环境变量读取」。Cloud 运行时只读 `config/`，全仓零 `os.Getenv`（架构边界测试禁止）；`WT_MEDIA_DOUYIN_*` 环境变量与 `.env.local` 对运行时**无效**。凭据值不得提交进版本库。）
3. Cloud Scheduler 只扫描到期启用策略并创建 `pending` 的 `crawl_task`，不得在调度调用栈中执行 Crawler。
4. Cloud Discovery Worker 统一领取 `pending crawl_task`，原子推进为 `running`，调用 Crawler，按统一入池服务写入 `source_content`，最后更新为 `success` 或 `failed`。手动“立即执行”同样只创建任务，不旁路 Worker。
5. `crawl_task` 是一次策略运行记录，也是 M3 Cloud 内部 Worker 的执行事实；它不是通用 Agent 任务。状态、策略快照、结果和错误均由 Cloud 业务表保存。
6. 关键词/博主人工搜索复用同一 Cloud Worker/Crawler，结果先保存在 `crawl_task.result_json`，只有用户确认选择后才入池；链接导入和自动策略任务成功结果直接入池。（2026-09-23 增补：博主搜索已暂停，本期只有关键词搜索在使用；机制本身不变，恢复时直接复用。）
7. 渠道通过 `channel_type` 选择适配器；本期仅实现 `douyin`，其他渠道只保留不可执行的扩展位。
8. M3 默认仍由一个 Cloud 进程承载 API Server、Scheduler 和 Discovery Worker 三个模块；模块以独立 goroutine 和接口隔离，不拆微服务、不引入 MQ。Cloud 仓库同时提供独立 Go CMD（`cmd/discovery-scheduler`、`cmd/discovery-worker`），便于本地单独运行调度或 Worker。调度与 Worker 的间隔取 `config/scheduler/scheduler.toml`；一次性触发走管理员受控端点 `POST /api/v1/discovery-scheduler/run-due`。（2026-09-23 更正：原 `scripts/run-discovery-*.sh` 已在 Cloud `36a7cfe` 删除，入口以 CMD 为准。**同日第二次更正**：原文「一个 Cloud 进程承载三个模块」与实现不符——`cmd/server` 只启动 HTTP 引擎，Scheduler 与 Worker 是各自独立的 CMD 进程，没有 flag，循环间隔取自 `config/scheduler/scheduler.toml`。实测只起 `cmd/server` 观察 120 秒，`pending/running` 任务数不变。本 ADR 的**职责分离主张不变**（Scheduler 只入队、Worker 统一领取执行、不得在调度调用栈中执行 Crawler），只是承载形态不是单进程。）

## Consequences

- M3 的最小闭环不依赖 Agent/桌面进程，任务事实集中在 Cloud；Scheduler 重启不会丢失已经创建的 `crawl_task`，Worker 可从数据库继续领取待执行任务。
- Scheduler 与执行器可以在同一 Cloud 进程部署，但不能共享同一职责或同步调用链；独立 CMD 运行时必须通过数据库的原子领取和调度幂等避免重复执行。
- Agent 仍是 M2 本地浏览器、文件、FFmpeg、发布和互动等外部执行能力的唯一入口；本 ADR 不是全局撤销 Agent 架构。
- 真实 Douyin 验收需要在 `config/clients/http/douyin.toml`（API 地址）与 `config/credentials/douyin.toml`（凭据）中提供有效值，并准备合法授权样本；缺少凭据只能验证接口契约和受控失败，不得宣称真实发现通过。（2026-09-23 更正：原文列的 `WT_MEDIA_DOUYIN_API_BASE` / `WT_MEDIA_DOUYIN_API_KEY` 环境变量对 Cloud 运行时无效。）

## 增补记录

2026-09-23：按用户指令「以 wt-media-cloud 执行的事实为准更新基线」，对本 ADR 做了三处更正：
第 2 条与 Consequences 的凭据读取方式由「服务端环境变量」更正为 `config/` 下的 TOML；
第 8 条的进程承载形态更正为「`cmd/server` 只启动 HTTP 引擎，Scheduler/Worker 为独立 CMD」。
第 3、4、6 条的职责分离主张（Scheduler 只入队、Worker 统一领取执行、人工搜索经确认后入池）
经实测仍然成立，未作改动。

同日亦记录一项实现偏离（缺陷 D-scheduler，不改变本 ADR 的主张）：独立
`cmd/discovery-scheduler` 进程首次 tick 即 `panic: douyin: Get called before Initialize` 退出，
导致本期**无人值守的真实周期触发未交付**。

**同日第二次更正（根因归因）**：原文把根因写作「`schedulerResourcePlan()` 缺少 `clientsResource()`」，
**该归因有误**。真正原因是**未收尾的迁移遗留**：`0699e8a` 把单进程拆成三个 CMD 时，crawler 由
「自读配置的 `NewDouyinCrawlerFromEnv()`」换成「生命周期管理的单例 `douyinclient`」，server 与
worker 的资源计划都补了 `clientsResource()`，**唯独调度路径漏补**；同一提交又用
`TestInitializeSchedulerDoesNotInitializeDouyinClient` 把「调度计划不含 clients」锁定为预期，
两边从未对齐。

**修法（2026-09-23，用户裁定）**：「scheduler 只是扫库做任务调度，不需要依赖这些额外的 client」。
故**不给 `schedulerResourcePlan()` 补 `clientsResource()`** —— 那会与本 ADR 第 3 条
「不得在调度调用栈中执行 Crawler」的分离主张相悖 —— 而是让调度路径不再持有 crawler
（Cloud 新增 `defaultSchedulerDiscoveryService()`，`RunDue` 改走它；`runDue` 只读库入队，
从不解引用 `s.crawler`）。`schedulerResourcePlan()` 与其测试原样保留。
进程级复验通过（无人值守触发端到端成立），详见治理仓库
`delivery/active/CHG-20260916-052/evidence/m3-e3-acceptance-20260923/15-dscheduler-fix-reverification.md`。
