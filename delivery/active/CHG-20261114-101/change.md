---
id: CHG-20261114-101
parent: delivery/milestones/M-publishing-prototype.md#发布详情统一体验
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
---

# CHG-20261114-101：发布任务、批次与计划详情统一

## Change

三类详情共用 Cloud `ResourceDetailPage`、卡片、字段、分区、状态、指标与提示组件。按当前原型，返回与必要详情决策统一放在 Footer，返回保留来源上下文；任务名称位于任务信息；批次信息、执行情况、任务与记录分区；计划保留完成矩阵与批次推进。终态只读，不重复整组列表动作。

业务见 [PRD 第六章](../../../docs/product/prd/详细文档/第六章_发布管理.md)，公共呈现见 [AdminUI](../../../docs/standards/frontend/AdminUI页面规范.md)，闭环见 [Milestone](../../milestones/M-publishing-prototype.md#发布详情统一体验)。仅呈现和导航，不改变平台执行、历史结果或指标计算。

## Done When

- 三页引用同一容器及公共组件，任务步骤条与内容版本角标不恢复。
- 批次详情进度条仅保留“发布成功率”（已确认发布成功数／发布目标数），不恢复处置进度条；处理情况通过现有统计和任务状态表达。详情和编辑表格样式一致。
- 详情操作与列表采用同一状态条件；长文本及窄屏可读，返回保留上下文。
- 定向测试、构建及必要浏览器验证通过；用户最终评审和合并前保持 VERIFYING。

## 当前验证与交接

2026-11-17：本轮验证覆盖三类详情的公共样式、单项发布成功率、状态动作及来源返回；桌面与窄屏布局，结果通过。自动测试、完整浏览器回归、构建及独立审查汇总见 [验收与清理](../CHG-20261111-101/change.md#当前验证与交接)。待两仓 PR 检查、合并及主干回读，保持 VERIFYING；不代表正式平台或执行器验收。
