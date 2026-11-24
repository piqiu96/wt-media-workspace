---
id: CHG-20261124-108
parent: delivery/milestones/M7-batch-publishing.md#批次执行与真实结果
status: PLANNED
depends_on: ["CHG-20261124-107"]
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: H
---

# CHG-20261124-108：批次启动、分组发布与结果

## Change

运营开始发布时，从107配置一次生成正式任务、取得占用并授权；本人不同账号按组并发、组间等待，支持组间处理【自动继续、异常暂停】、异常任务上限、人工继续/终止、全局Profile互斥和可信公开结果。

完整业务/API/数据库/步骤/证据见[执行落地清单](plan.md)。本次仅同步执行计划，2026-11-25用户授权依次完成107→108→109的编码、测试、PR修复、E2E和走查；当前PLANNED，按依赖预检后逐项激活；依赖归档及各仓main合并、相关事实/契约/原型review与CHG预检满足后再激活。状态只在本文件，清单不预填完成事实。

## Done When

- 首次start原子建单/占用/授权，同键重放不重复，配置冲突不遗留半批。
- 分组、可靠人工挂起/未知占位、跨批Profile、异常暂停/继续/终止真实收敛；不自动重发，不无限开窗。
- 原task/attempt/observation/作品与公开统计一致；真实多账号及双端验收完成、各仓main合并可查。
