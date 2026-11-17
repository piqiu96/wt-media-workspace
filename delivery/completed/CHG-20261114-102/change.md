---
id: CHG-20261114-102
parent: delivery/milestones/M-publishing-prototype.md#封面模板v1原型闭环
status: DONE
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
merge_commits: {"wt-media-workspace": "92e8606e5c56fab160aa2e408f21efb06f8e7d6d", "wt-media-cloud": "d3f666f9f90f50a3c052c6ad38453a57a97a842c"}
---

# CHG-20261114-102：封面模板 V1 原型闭环

## Change

Cloud 原型中的图片库、封面模板位于运营工具。模板按新建基础信息、独立编辑、保存草稿、列表发布、列表 Switch 启停形成闭环；已发布配置与编辑草稿可共存。实际内容按所选模板及必需规格生成，现成图片直接使用；不以样例代替任务最终封面。

产品依据为 [PRD 6.6—6.7](../../../docs/product/prd/详细文档/第六章_发布管理.md#66-图片库)，画布专项交互见 [设计说明](../../../docs/design/cover-templates.md)，验收闭环见 [Milestone](../../milestones/M-publishing-prototype.md#封面模板v1原型闭环)。不接入正式图片、模板或生成服务。

## Done When

- 保存不等于发布或启用；首次发布保持停用，发布更新保持原启停值。
- 草稿不影响已发布内容；模板只在列表启停，停用阻止新引用，历史成品保留。
- 选用的每种规格均校验实际文字和输出，未知或失败结果不冒充成品。
- 图片库筛选、只读详情及编辑器布局符合 common，定向测试和浏览器验证通过。
- 用户最终评审和合并前保持 VERIFYING。

## 验收与合并

2026-11-17 已按用户授权完成本地原型验收、独立审查和两仓合并，并回读本地及远端 `main`：

- [Cloud PR #40](https://github.com/piqiu96/wt-media-cloud/pull/40)：实现提交 `bbf95a8`，主干合并 `d3f666f`。
- [Workspace PR #44](https://github.com/piqiu96/wt-media-workspace/pull/44)：产品与规范提交 `9130148`，主干合并 `92e8606`。
- 自动验证：发布原型 349 项、计划 34 项、example 21 项、Web 1001 项；完整浏览器回归 20 文件、96 项。example、Cloud、Desktop 构建，CI 数据库迁移及发布打包检查均通过。Workspace 单仓校验和测试通过。

验收、修复边界与过程清理汇总见 [发布原型闭环](../CHG-20261111-101/change.md#验收与合并)。

本记录只证明本地交互原型及共享呈现交付，不代表真实资源、AI、平台发布或正式执行器验收。
