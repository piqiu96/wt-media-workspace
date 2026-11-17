---
id: CHG-20261114-102
parent: delivery/milestones/M-publishing-prototype.md#封面模板v1原型闭环
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
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

## 当前验证与交接

2026-11-17：本轮验证覆盖图片库、模板编辑与发布、启停、封面使用和失败恢复，结果通过。自动测试、完整浏览器回归、构建及独立审查汇总见 [验收与清理](../CHG-20261111-101/change.md#当前验证与交接)。待两仓 PR 检查、合并及主干回读，保持 VERIFYING；不代表正式平台或执行器验收。
