---
id: CHG-20261111-101
parent: delivery/milestones/M-publishing-prototype.md#单任务创建与状态化处理
status: DONE
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
merge_commits: {"wt-media-workspace": "92e8606e5c56fab160aa2e408f21efb06f8e7d6d", "wt-media-cloud": "d3f666f9f90f50a3c052c6ad38453a57a97a842c"}
---

# CHG-20261111-101：发布原型创建与状态处理体验整改

## Change

在 Cloud `web/example/proto/publishing-design/` 保留最终发布任务、批次配置和运营工具原型，及其 common 组件接入。快速发布创建独立待执行任务；列表按状态处理，详情独立只读；批量配置按本次所选字段与条目预览后应用，现成封面无需生成。新建续编不进入正式列表，未知结果禁止重发，历史结果和占用按 PRD 保留。

正式产品规则见 [PRD 第六章](../../../docs/product/prd/详细文档/第六章_发布管理.md)，通用规则见 [AdminUI](../../../docs/standards/frontend/AdminUI页面规范.md)及[交互规范](../../../docs/standards/frontend/前端交互规范.md)。本轮用户授权清理全部原型过程截图、日志、图册、压缩包和重复计划；最终源码、必需资源与可复用测试保留。

## Done When

- 新建、编辑、列表、详情、批量配置及异常处理符合 PRD；common 呈现一致。
- 定向测试、构建及必要浏览器场景通过，失败和未验收项如实说明。
- 未接入真实 AI、资源及平台执行服务，不将演示结果写成正式能力完成。
- 验收及独立提交、合并完成前不记 DONE。

## 验收与合并

2026-11-17 已按用户授权完成本地原型验收、独立审查和两仓合并，并回读本地及远端 `main`：

- [Cloud PR #40](https://github.com/piqiu96/wt-media-cloud/pull/40)：实现提交 `bbf95a8`，主干合并 `d3f666f`。
- [Workspace PR #44](https://github.com/piqiu96/wt-media-workspace/pull/44)：产品与规范提交 `9130148`，主干合并 `92e8606`。
- 自动验证：发布原型 349 项、计划 34 项、example 21 项、Web 1001 项；完整浏览器回归 20 文件、96 项。example、Cloud、Desktop 构建，CI 数据库迁移及发布打包检查均通过。Workspace 单仓校验和测试通过。

新增修复仅包含两项明确确认内容：历史批次续编提示单次弹出；首次启动前略过无未决任务的已终止前序批次，确认后执行后续可执行批次。其余页面以已确认原型为准，批次详情只展示单项“发布成功率”。执行中的原有阈值、未决结果和人工衔接保护保留。

两仓六处过程目录共清理 1,236 个文件（约 156 MB）及四份重复计划；最终源码、必需图片字体与可复用测试保留。后续截图和日志进入临时目录，不重新纳入源码。无关既有改动保留在工作区，未纳入本轮合并。

本记录只证明本地交互原型及共享呈现交付，不代表真实资源、AI、平台发布或正式执行器验收。
