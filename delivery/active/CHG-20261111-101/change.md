---
id: CHG-20261111-101
parent: delivery/milestones/M-publishing-prototype.md#单任务创建与状态化处理
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
---

# CHG-20261111-101：发布原型创建与状态处理体验整改

## Change

在现有 Cloud `web/example/proto/publishing-design/` 中完成快速发布、任务列表、任务详情一个可操作闭环。以用户本轮整改及本地 `docs/design/publishing.md` §8–9 为依据。仅修复批次/计划的必要联动，不变更业务模型、运行 API、Agent/Desktop 或生产发布能力。

执行顺序：审计与截图 → 快速发布单页与恢复 → 统一状态权限及详情 → 列表主动作与返回 → 定向测试、构建、真实浏览器操作 → 修复与证据。

保留 Workspace `docs/design/publishing.md` 的用户既有未提交修改。Cloud 初始干净，当前分支 `codex/publishing-interaction-closure`；Workspace 当前分支 `codex/publishing-design-boundaries`。不还原现有原型数据。

## Done When

- 三个核心页面的前后差异、实际操作、截图与遗留问题可检查。
- 快速发布一页完成，AI 保护人工字段，现成封面无需短标题，普通创建仅创建一条待执行任务。
- 详情覆盖待执行、执行中、等待人工、未知、审核、失败、公开、取消，列表与详情权限一致。
- 未知不可重发/取消/释放；原任务安全重试增加尝试不覆盖旧快照；取消保留占用且不可恢复。
- 预检阻断有修复入口；关闭详情保留来源筛选、分页和滚动；草稿及失败恢复经过验证。
- 原型定向测试及构建通过，浏览器核验事实记录在 evidence；提交与合并状态如实记录。

## Acceptance

三个核心页面和八种任务状态已通过本地真实浏览器走查，含草稿恢复、人工继续、核实未知、安全重试及取消释放。详见 [验收报告](evidence/review.md)。无账号/全空成片池的真实数据场景尚未用浏览器构造；真实平台窗口、查询和作品链接未联通，不作为已验证能力。

2026-11-11 补充发布任务专项产品与视觉复核，范围为任务列表、快速发布、任务详情及相关弹窗，不含批次和计划。保存 28 张本轮原图与 3 张整改前存档对照，详见 [专项走查报告](evidence/visual-review-20261111/00-走查结论.md) 和 [离线截图索引](evidence/visual-review-20261111/01-截图索引.html)。新增 3 项 P1、8 项 P2 尚待整改：P1 为失败预检提示易误解、缺作品链接时主操作不准确、执行中进度信息靠后。本次未提交任务状态变更，不能将专项体验复核记为全部通过，也不覆盖此前功能操作记录。

保留 VERIFYING：本地原型已可 Review，尚未创建或合并 PR，不代表运行时发布能力交付。`chg start --plan` 初始因 Workspace 既有设计文档未提交及当前分支不符而未通过；为保护用户修改，继续在现有两个 `codex/` 分支实施，通过 `chg resume` 选定上下文，未重置、切换或夹带用户文件。
