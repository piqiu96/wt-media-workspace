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

Cloud `web/example/proto/publishing-design/plan/` 为唯一计划原型，通过统一工作台使用同一计划、批次及任务记录。创建目标矩阵和单平台批次骨架，按原顺序准备与推进；首次启动后禁止编辑计划或中途补发，全部批次执行完并处理未决结果后才能补量或确认结束。终止计划停止所有所属未结束批次；单独终止批次仅影响本批，后续按原有推进条件继续。

业务依据为 [PRD 6.2](../../../docs/product/prd/详细文档/第六章_发布管理.md#62-发布计划)，体验闭环见 [Milestone](../../milestones/M-publishing-prototype.md#发布计划v1原型)。仅本地原型，不修改正式 API、Agent 或 Desktop；真实平台派发和停止能力不在本轮验证范围。

## Done When

- 目标、原始拆批守恒，已锁定行不能拖拽或跨越，运行中入口与保存同时锁定。
- 本轮执行结束与最终计划结束区分；补量只覆盖实际缺口、不修改原目标，不允许执行中并行追加。
- 终止计划取消未开始任务、保留在途及未知结果核实入口，终止单批不误停其他批。
- 列表、详情、配置和返回符合 common；定向测试与浏览器验证通过。
- 未经用户最终评审和独立合并不记 DONE。

## 当前验证与交接

2026-11-17：本轮验证覆盖首次启动前终止首批后，从列表与详情确认执行后续批次；运行中锁定、终止范围、补量与确认结束；拖拽持久化及已锁定边界，结果通过。自动测试、完整浏览器回归、构建及独立审查汇总见 [验收与清理](../CHG-20261111-101/change.md#当前验证与交接)。待两仓 PR 检查、合并及主干回读，保持 VERIFYING；不代表正式平台或执行器验收。
