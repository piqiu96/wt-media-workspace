# ADR-0015：M3 内容挖掘由 Cloud 内部执行

- Status: Accepted
- Date: 2026-09-16
- Scope: M3 内容池、挖掘策略、挖掘任务及 Douyin 内容发现适配
- Supersedes: ADR-0013 第 6 条中“Cloud Agent 查询外部平台”的 M3 具体实现约束；不改变 M2 浏览器、文件、FFmpeg、发布和互动自动化的 Agent 边界。

## Context

M3 的内容挖掘只需要访问公开/已授权的内容数据接口，不涉及用户本机、BitBrowser、Cookie 注入、文件、FFmpeg 或浏览器自动化。现有实现把 discovery 任务接入通用 Cloud-Agent task store，扩大了运行链路，也让 `crawl_task` 混淆为 Agent 执行任务。

## Decision

1. M3 不创建、分配或执行 Cloud Agent / Local Agent task；Desktop 不参与内容挖掘执行。
2. Cloud 内部提供受控 `Crawler` 接口和渠道适配器。当前实现 `DouyinCrawler` 通过服务端环境变量读取 API 地址和凭据，不能从客户端传入或在代码中硬编码。
3. Cloud Scheduler 只扫描到期启用策略并调用 DiscoveryService；DiscoveryService 创建 `crawl_task`，调用 Crawler，按统一入池服务写入 `source_content`，并记录成功/失败统计。
4. `crawl_task` 是一次策略运行记录，不是通用任务系统的执行对象；状态、快照、结果和错误均由 Cloud 业务表保存。
5. 关键词/博主人工搜索复用同一 Cloud Crawler，但结果先保存在 `crawl_task.result_json`，只有用户确认选择后才入池；链接导入和自动策略任务成功结果直接入池。
6. 渠道通过 `channel_type` 选择适配器；本期仅实现 `douyin`，其他渠道只保留不可执行的扩展位。

## Consequences

- M3 的最小闭环不依赖 Agent/桌面进程，部署和恢复路径更短，任务事实集中在 Cloud。
- Agent 仍是 M2 本地浏览器、文件、FFmpeg、发布和互动等外部执行能力的唯一入口；本 ADR 不是全局撤销 Agent 架构。
- 真实 Douyin 验收需要服务端 `WT_MEDIA_DOUYIN_API_BASE`、`WT_MEDIA_DOUYIN_API_KEY`（可选 Cookie）和合法授权样本；缺少凭据只能验证接口契约和受控失败，不得宣称真实发现通过。
