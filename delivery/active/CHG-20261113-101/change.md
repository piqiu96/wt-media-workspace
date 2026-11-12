---
id: CHG-20261113-101
parent: delivery/milestones/M-publishing-prototype.md#发布计划v1原型
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
---

# CHG-20261113-101：发布计划 V1 原型及 common 对齐

## Change

以用户 2026-11-13 提供的 ZIP 为已选定的交互设计，完成 Cloud `web/example/proto/publishing-design/plan/` 的完整离线计划原型，并接入现有计划导航。范围仅计划原型，使用 common 样式与控件；不改 API、Agent、Desktop 或正式运行时。与 CHG-20261111-101 的任务整改独立，不修改其任务表单与状态规则。

Workspace 保留既有 `docs/design/publishing.md` 与旧 CHG review.md 修改；Cloud 保留既有走查截图。继续当前非 main 分支，避免切换或覆盖既有工作。新 CHG start 预检与例外原因记入 evidence。

## Done When

- 列表、资源盘点、平台/类目多选、目标矩阵、批次推荐及人工编辑、详情、待办、执行与结束路径均可操作。
- 已锁定批次只读；拆分合并守恒；补量不超过单元格缺口；复制清空执行事实。
- 按 common 统一筛选查询/重置、8 条分页、按钮、表格、字体、颜色与可键盘操作的弹层。
- 本地刷新恢复与保存异常有明确反馈；未知/重试结果未收敛时不能结束。
- 定向行为测试、示例构建通过，真实浏览器逐项操作并保留关键截图；真实服务缺口和停止中条件状态如实记录。
- 本地成果进入 VERIFYING；未经合并不记 DONE。

## Acceptance

本地 V1 原型、common 对齐与原入口接入已实现；18 项计划行为测试、239 项既有发布原型测试及 22 项示例测试通过，示例构建与构建产物浏览器检查通过。保存 40 张真实浏览器截图，18 项浏览器核验通过，无页面异常。详见 [验收记录](evidence/review.md)。真实服务、执行器与停止能力不在本轮已验证能力内，待用户视觉 Review，未推送或合并。
