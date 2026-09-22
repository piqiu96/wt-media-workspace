# ADR-0013：M3 内容挖掘统一入口与业务边界

- Status: Accepted（实现边界由 ADR-0015 进一步收敛；第 3、7 条于 2026-09-23 增补）
- Date: 2026-09-15（增补 2026-09-23）
- 来源：用户本轮提供的 M3 内容挖掘 Milestone 与页面参考图。
- Supersedes：原第四章和 M3 草案中“即时选择直接建素材、四个独立页面、crawl_strategy 命名”的 M3 规则；不改变 M2 权限或运行职责。M3 的 Cloud-owned 执行边界见 ADR-0015。
- 2026-09-23 增补：原文对“策略自动转素材”与“五态业务任务”的否定已被用户确认撤销，见下方第 3、7 条与「增补记录」。

## Context

M3 从“内容发现功能开发”调整为“内容挖掘自动化入口建设”。用户明确产品只包含内容池、挖掘策略、挖掘任务；内容统一入池后人工转素材，策略定义规则，调度触发执行。旧七段计划包含自动转素材且没有主动博主搜索，不能继续作为实施依据。

## Decision

1. 三个页面：内容池、挖掘策略、挖掘任务。链接导入、关键词搜索和博主搜索均由内容池进入。
2. 链接点击“解析并入池”即为入池意图；解析成功的有效内容进入 source_content。关键词/博主搜索须选择结果才入池。上述行为均不自动创建 material。
3. 自动挖掘创建或更新 source_content；人工转素材保留 material.source_content_id 唯一关联。策略可配置自动转素材：`auto_material` 开启时，按 `material_rule`（`AND` / `OR`）与各正阈值判定命中并在入池后自动生成 material，未命中项留在内容池等待人工处理。（2026-09-23 增补：本条原为“M3 不提供自动转素材配置”，经用户确认为 M3 范围内正式能力后改写。手工入口本身仍不自动创建 material。）
4. 统一 discovery_strategy，通过 strategy_type 区分 keyword / author；保留 crawl_task 表达一次自动挖掘执行。不得按策略类型拆成两套业务模型。
5. 统一 content_channel 抽象并由 channel_type 引用；当前仅实现抖音。预留快手/B站/小红书/热榜等能力接入点，不实现这些渠道，不建设通用插件或工作流引擎。
6. 策略只存业务规则及关联的触发配置，不自行运行定时器。Cloud Scheduler 负责何时触发，Cloud Crawler 查询外部平台并由 DiscoveryService 写入正式业务事实；M3 不创建 Agent 任务，页面可配置执行周期但不提供可视化调度器。
7. 业务状态采用 source_content 的 pending / material_created / ignored；crawl_task 的 pending / running / success / failed / partial_success（部分成功：至少一项失败且至少一项成功）。不因此修改 M1 通用技术 task 的状态机。（2026-09-23 增补：`partial_success` 由实施引入并已有真实证据（任务状态、失败项重试），按实施事实纳入；原表述为“不新增 partial 第五态”。）
8. 工作流仅是基于实际策略、触发、任务、内容池与素材事实的只读业务流转视图，不允许编排、拖拽、条件分支或任意脚本。
9. 不含视频下载、文件存储/校验、剪辑、AI 评分、自动生产、发布、互动与数据分析。

## 未被本 Decision 解决的事项

内容域共享范围与游戏归属仍需独立确认，ADR-0009 不被静默覆盖（内容域共享范围已由 ADR-0014 收敛为业务团队级隔离）。任务部分失败的状态映射已于 2026-09-23 关闭（见第 7 条）。首次作者扫描范围仍待澄清；作者侧接口当前未开放，博主搜索与作者策略未通过真实验收。启用后首次触发时点、具体频率菜单和渠道接口能力待澄清。执行计划中的验收细化属于草案，不能因为本 ADR Accepted 就视为全部批准。

## Consequences

- Positive：所有入口先入池；人工与自动发现共用身份/去重规则，生产边界清楚。
- Negative：原七个 CHG 草案需撤销执行资格；新增主动博主搜索、渠道抽象及每日时间触发配置的设计核对。
- Follow-up：以 Product 的 `docs/product/M3-content-mining-v2.md` 为有效基线；同步 Engineering、Master Plan 与 `delivery/milestones/M3-content-discovery-v2.md`；旧草案保留并标记 SUPERSEDED。实施进度见 M3 Milestone 记录，本 ADR 不跟踪。

## 增补记录

2026-09-23：用户确认自动转素材为 M3 范围内正式能力，第 3 条随之改写。同日按实施事实增补第 7 条的 `partial_success`，并关闭任务部分失败的状态映射待决项。第 6 条（Cloud-owned 执行）已由 ADR-0015 收敛为 Scheduler 只入队、Worker 统一领取执行。

增补依据在 Cloud 仓库：`wt-media-cloud/docs/superpowers/specs/2026-09-21-content-pool-discovery-closure-design.md`（`auto_material` / `material_rule` / 阈值语义）、`wt-media-cloud/docs/superpowers/handoffs/2026-09-21-content-pool-discovery-closure-handoff.md`（真实凭据下的自动转素材实测）、`wt-media-cloud/docs/superpowers/handoffs/2026-09-22-content-pool-discovery-hardening-handoff.md`（`partial_success` 端到端与失败项重试）。
