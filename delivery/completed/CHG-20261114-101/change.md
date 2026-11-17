---
id: CHG-20261114-101
parent: delivery/milestones/M-publishing-prototype.md#发布详情统一体验
status: DONE
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
merge_commits: {"wt-media-workspace": "92e8606e5c56fab160aa2e408f21efb06f8e7d6d", "wt-media-cloud": "d3f666f9f90f50a3c052c6ad38453a57a97a842c"}
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

## 验收与合并

2026-11-17 已按用户授权完成本地原型验收、独立审查和两仓合并，并回读本地及远端 `main`：

- [Cloud PR #40](https://github.com/piqiu96/wt-media-cloud/pull/40)：实现提交 `bbf95a8`，主干合并 `d3f666f`。
- [Workspace PR #44](https://github.com/piqiu96/wt-media-workspace/pull/44)：产品与规范提交 `9130148`，主干合并 `92e8606`。
- 自动验证：发布原型 349 项、计划 34 项、example 21 项、Web 1001 项；完整浏览器回归 20 文件、96 项。example、Cloud、Desktop 构建，CI 数据库迁移及发布打包检查均通过。Workspace 单仓校验和测试通过。

验收、修复边界与过程清理汇总见 [发布原型闭环](../CHG-20261111-101/change.md#验收与合并)。

本记录只证明本地交互原型及共享呈现交付，不代表真实资源、AI、平台发布或正式执行器验收。
