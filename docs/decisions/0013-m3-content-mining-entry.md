# ADR-0013：M3 内容挖掘统一入口与业务边界

- Status: Accepted（实现边界由 ADR-0015 进一步收敛）
- Date: 2026-09-15
- 来源：用户本轮提供的 M3 内容挖掘 Milestone 与页面参考图。
- Supersedes：原第四章和 M3 草案中“即时选择直接建素材、策略自动转素材、四个独立页面、crawl_strategy 命名、五态业务任务”的 M3 规则；不改变 M2 权限或运行职责。M3 的 Cloud-owned 执行边界见 ADR-0015。

## Context

M3 从“内容发现功能开发”调整为“内容挖掘自动化入口建设”。用户明确产品只包含内容池、挖掘策略、挖掘任务；内容统一入池后人工转素材，策略定义规则，调度触发执行。旧七段计划包含自动转素材且没有主动博主搜索，不能继续作为实施依据。

## Decision

1. 三个页面：内容池、挖掘策略、挖掘任务。链接导入、关键词搜索和博主搜索均由内容池进入。
2. 链接点击“解析并入池”即为入池意图；解析成功的有效内容进入 source_content。关键词/博主搜索须选择结果才入池。上述行为均不自动创建 material。
3. 自动挖掘只创建或更新 source_content；人工转素材保留 material.source_content_id 唯一关联。M3 不提供自动转素材配置。
4. 统一 discovery_strategy，通过 strategy_type 区分 keyword / author；保留 crawl_task 表达一次自动挖掘执行。不得按策略类型拆成两套业务模型。
5. 统一 content_channel 抽象并由 channel_type 引用；当前仅实现抖音。预留快手/B站/小红书/热榜等能力接入点，不实现这些渠道，不建设通用插件或工作流引擎。
6. 策略只存业务规则及关联的触发配置，不自行运行定时器。Cloud Scheduler 负责何时触发，Cloud Crawler 查询外部平台并由 DiscoveryService 写入正式业务事实；M3 不创建 Agent 任务，页面可配置执行周期但不提供可视化调度器。
7. 业务状态采用 source_content 的 pending / material_created / ignored；crawl_task 的 pending / running / success / failed。不因此修改 M1 通用技术 task 的状态机。
8. 工作流仅是基于实际策略、触发、任务、内容池与素材事实的只读业务流转视图，不允许编排、拖拽、条件分支或任意脚本。
9. 不含视频下载、文件存储/校验、剪辑、AI 评分、自动生产、发布、互动与数据分析。

## 未被本 Decision 解决的事项

内容域共享范围、游戏归属、全局忽略影响范围仍需独立确认，ADR-0009 不被静默覆盖。任务部分失败的四态映射、首次作者扫描范围、启用后首次触发时点、具体频率菜单和渠道接口能力待澄清。执行计划中的验收细化属于草案，不能因为本 ADR Accepted 就视为全部批准。

## Consequences

- Positive：所有入口先入池；人工与自动发现共用身份/去重规则，生产边界清楚。
- Negative：原七个 CHG 草案需撤销执行资格；新增主动博主搜索、渠道抽象及每日时间触发配置的设计核对。
- Follow-up：以 Product 的 M3-content-mining-v2.md 为有效基线；同步 Engineering、Master Plan 与 M3-content-discovery-v2.md；旧草案保留并标记 SUPERSEDED。全部仍未实施。
