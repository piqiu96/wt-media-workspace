# ADR-0017：M4-M5 视频合成由 Cloud 内部执行

- Status: Accepted
- Date: 2026-09-24
- Scope: M4 内容生产闭环、M5 自动生产、原素材准备、成片存储与本地下载
- Supersedes:
  - `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` 中“Agent 统一承担 FFmpeg、文件下载和合成”、Local Agent 本地合成、Cloud Agent 云端合成的 M4-M5 约束；
  - `docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md` 中“合成属于 Desktop/Tauri/Agent 混合调用”和“Agent 负责合成执行”的约束；
  - `delivery/MASTER_IMPLEMENTATION_PLAN.md` 旧 M4“本地 Agent 合成”和旧 M5“Cloud Agent 自动生产”路线。
- Does not supersede: Agent 对 BitBrowser、Profile、Cookie、浏览器自动化、发布、互动以及运营电脑本地文件落地的边界。

## Context

旧 M4-M5 设计把视频生产拆为两套执行路径：运营电脑由 Local Agent + FFmpeg 合成，自动生产由 Cloud Agent + FFmpeg 合成。产品侧同时存在 `compose_pool_item`、通用 `task`、`production_rule`、`composite_output_pool` 和 `composite_output_claim` 等额外对象。

该设计造成以下问题：

1. 同一种视频生产在本机与云端维护两套环境、恢复和文件语义；
2. Desktop 是否在线会影响人工合成，而合成并不依赖运营电脑登录态、BitBrowser 或本机安全资源；
3. `production_rule` 与合成策略的自动规则重复，`compose_pool_item` 与合成任务重复；
4. 本地成片、云端成片、成片池和领取关系使“一个成片，一个资产”难以保持；
5. 长时间 HTTP 等待无法提供可靠的并发限制、heartbeat、超时、重试和崩溃恢复。

M3 已通过 ADR-0015 验证 Cloud Scheduler 只创建业务任务、Cloud Worker 从 MySQL 原子领取执行的轻量模型。视频合成同样不依赖运营电脑环境，适合复用这一职责分离原则，但必须使用独立的生产领域对象和 FFmpeg 运行隔离。

## Decision

1. **视频合成统一由 Cloud 内部执行。** M4 人工发起与 M5 自动发起最终都创建 `compose_task`，由 Cloud Compose Worker 领取并调用 Cloud 运行环境中的 FFmpeg。Desktop、Local Agent 和 Cloud Agent 均不执行视频合成。
2. **HTTP Server 不执行长任务。** `cmd/server` 只提供 API；Compose Scheduler 与 Compose Worker 以独立 CMD 入口运行，均由 Cloud bootstrap 装配。Scheduler 只创建 `pending` 任务，不能在同一调用栈下载文件或调用 FFmpeg。
3. **固定业务对象。** 使用 `material`、`material_usage`、`compose_strategy`、`compose_task`、`composite_output`；新增且只新增横向文件对象 `file_transfer_task`。不得新增 `production_rule`、`compose_pool_item` 或 `material_usage` 替代表。
4. **自动规则归 `compose_strategy`。** 策略保存模板、视频参数和可选 `schedule` 配置。M4 允许人工选择策略；M5 才启用 Scheduler 根据策略计划自动创建任务。
5. **`compose_task` 是生产执行事实。** 它同时承载生产意图、状态、策略快照、输入输出引用、租约、heartbeat、重试和错误。不再为同一次生产创建通用 Agent `task` 或另一张生产任务表。
6. **Worker 使用 MySQL 原子领取。** 首版不引入 MQ。Worker Pool 有界并发；同一任务只能被一个 Worker 执行；租约过期后可恢复；任务支持 timeout、heartbeat、技术失败重试、业务失败停止和取消。
7. **成片只在真实成功后创建。** FFmpeg 成功、输出媒体校验通过且对象存储落盘后，Cloud 才创建 `composite_output`。失败、取消、超时、损坏或上传失败不得产生假成片。
8. **文件传输统一建模。** `file_transfer_task` 通过 `asset_type`、`purpose` 和 `execution_scope` 区分：
   - Cloud Worker 准备原素材供合成；
   - Local Agent 把原素材或成片落到运营电脑。
   两者共享正式任务状态和进度口径，但执行器不同，不拆分新表。
9. **源视频懒加载。** 内容池转 `material` 时只保存源链接，不立即下载全部视频。用户主动下载，或创建合成任务发现 `material.video_status != ready` 时，才创建文件传输任务。
10. **FFmpeg 属于 Cloud 部署组件。** 使用绝对路径或受控容器入口，锁定版本、SHA256、CPU 架构、编码器、Filter 与许可证；不依赖宿主机 PATH。每个任务使用隔离临时目录。
11. **Agent 边界收窄而非取消。** Local Agent 继续负责运营电脑上的文件落地、打开目录、发布、互动、BitBrowser 和本地安全能力；Cloud Agent 如后续用于效果采集，不因此获得视频合成职责。
12. **不引入复杂编排。** 不建设微服务、MQ、动态插件、可视化工作流或任意脚本执行；模块化单体、独立进程和数据库任务领取足以覆盖 M4-M5。

## Consequences

- Positive:
  - 人工与自动生产复用同一执行环境、状态机和恢复模型；
  - Desktop 离线不阻塞视频合成；
  - `compose_strategy`、`compose_task` 和 `composite_output` 的职责更直接；
  - Worker 并发、超时、重试和资源成本可在 Cloud 统一控制；
  - 原素材与成片仍可按需下载到运营电脑。
- Negative:
  - Cloud 部署需要 FFmpeg、临时磁盘和对象存储容量治理；
  - 视频生产的 CPU、内存和带宽成本集中到 Cloud；
  - Local Agent 原有/规划中的合成 Executor 与 FFmpeg 打包工作不再复用；
  - `file_transfer_task` 必须清楚区分 Cloud 准备与本地落地，避免同一状态被误读。
- Follow-up:
  - Cloud 需新增生产领域 Migration、API、Scheduler/Worker CMD、对象存储与 FFmpeg 基础设施；
  - Cloud API、业务 Schema、枚举和错误码需发布兼容修订；
  - Local Agent API 需增加受控的本地下载执行契约，但不得增加合成契约；
  - M4 和 M5 必须分别以真实视频、真实对象存储、失败恢复和 UI 操作完成验收。

