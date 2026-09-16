# CHG-20260916-052：M3-B～E 内容挖掘自动化入口

- Status: ACTIVE
- Level: M
- Milestone: `delivery/milestones/M3-content-discovery-v2.md`
- 日期：2026-09-16
- 基线：`docs/product/M3-content-mining-v2.md`；ADR-0013、ADR-0015；团队隔离决策见 ADR-0014。
- 当前仓库：wt-media-cloud、wt-media-agent、wt-media-workspace。Agent 仅做 M3 遗留 discovery task/adapter 清理，M2 本地执行能力保持不变。

## 独立目标与范围

在 M3-A 内容池基础上交付人工入口与自动挖掘入口：分享链接导入、关键词搜索、博主搜索、关键词/博主策略、挖掘任务记录及 Cloud-owned Douyin Crawler。搜索结果先保存在任务结果中，由运营选择后入池；链接导入与策略任务成功结果自动入池。策略不承担调度；Cloud Scheduler 只创建 `pending crawl_task`，Cloud Discovery Worker 原子领取并执行，不创建 Agent task。

不建设通用工作流引擎、视频下载/存储、AI 评分、剪辑、发布互动和数据分析；B站/快手等仅保留渠道字段，不宣称已接入。

## 权限与数据边界

普通运营按业务团队隔离；同团队可见全部内容，管理员跨团队可见。Cloud 持有 `discovery_strategies`、`crawl_tasks` 与搜索结果投影；Cloud Crawler 只通过服务端环境变量读取凭据；Agent/BitBrowser/Desktop 不参与 M3 执行。

## 实施任务

- B：分享链接单条导入并在任务成功后幂等进入内容池。
- C：关键词/博主搜索，任务详情展示结果，确认选中结果后入池。
- D：统一 `discovery_strategy`，支持 keyword/author、启停和手动执行。
- E：统一 `crawl_task` 状态、统计、错误和每分钟到期策略触发；Scheduler 只入队，Worker 统一领取后由 Cloud Crawler 执行并直接入池。Cloud Server 默认启动两者，并提供仓库内 Go CMD/脚本用于本地独立运行。

## 验收口径

自动化单元/集成测试必须通过：团队权限、重复去重、搜索结果选择入池、任务状态、Crawler 映射和调度。真实 Douyin 端到端仅在 Cloud 配置 `WT_MEDIA_DOUYIN_API_BASE`、`WT_MEDIA_DOUYIN_API_KEY`（可选 Cookie）后执行，不以 mock 或 HTTP 200 替代真实业务读回。

## 提交边界

Cloud、Agent、Workspace 分仓提交；Desktop 不因本次 M3 纠偏修改，只复用 Cloud Web 构建，不复制业务逻辑。完成前必须更新 checkpoint 与 evidence。

## Checkpoint

- Completed：用户已确认 Scheduler/Worker 职责边界；ADR-0015 已更新为“Scheduler 只入队、Worker 统一执行”，手动立即执行同样入队。
- Current：Scheduler/Worker 架构纠偏已实现并已在本机 Cloud 验证；CHG 继续保留，用于 M3 其余真实外部验收与完整闭环。
- Next：按 M3-E 真实授权样本继续验证关键词/博主策略的定时入队、Worker 执行、内容池读回；不将空队列验证替代真实外部验收。
- Blockers：无；真实 Douyin 外部读回仍依赖本地受控凭据，但不阻塞调度/Worker 架构测试。
- Recent verification：`scripts/test.sh` 的 Go 全包与 Web 20/76 Vitest 通过；迁移 `20260916_031` 已应用；独立 Scheduler/Worker 脚本均在空队列返回成功；本机 `/api/v1/health` 通过。详见 `evidence/20260916-scheduler-worker-boundary.md`。
