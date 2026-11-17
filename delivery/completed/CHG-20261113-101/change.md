---
id: CHG-20261113-101
parent: delivery/milestones/M-publishing-prototype.md#发布计划v1原型
status: DONE
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
merge_commits: {"wt-media-workspace": "92e8606e5c56fab160aa2e408f21efb06f8e7d6d", "wt-media-cloud": "d3f666f9f90f50a3c052c6ad38453a57a97a842c"}
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

## 验收与合并

2026-11-17 已按用户授权完成本地原型验收、独立审查和两仓合并，并回读本地及远端 `main`：

- [Cloud PR #40](https://github.com/piqiu96/wt-media-cloud/pull/40)：实现提交 `bbf95a8`，主干合并 `d3f666f`。
- [Workspace PR #44](https://github.com/piqiu96/wt-media-workspace/pull/44)：产品与规范提交 `9130148`，主干合并 `92e8606`。
- 自动验证：发布原型 349 项、计划 34 项、example 21 项、Web 1001 项；完整浏览器回归 20 文件、96 项。example、Cloud、Desktop 构建，CI 数据库迁移及发布打包检查均通过。Workspace 单仓校验和测试通过。

验收、修复边界与过程清理汇总见 [发布原型闭环](../CHG-20261111-101/change.md#验收与合并)。

本记录只证明本地交互原型及共享呈现交付，不代表真实资源、AI、平台发布或正式执行器验收。
