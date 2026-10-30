---
id: CHG-20261030-111
parent: delivery/milestones/M2-account-runtime.md#m2-d-社媒账号重构
status: IMPLEMENTING
depends_on: []
affected_repos: ["wt-media-cloud", "wt-media-workspace"]
risk: M
---

# CHG-20261030-111: 社媒账号视觉纠偏与公共字段交互统一

## Change

修正人工走查指出的原型/规范偏差，使社媒账号在真实桌面端具备与已审定原型一致的列表、筛选、选择后批量操作、启停开关与分类表单体验。分类、运营团队和成员选择收敛为共用组件，替换实际使用处的重复实现，保留各业务原有的单选/多选、权限范围、数据来源和提交语义。

依次完成：公共字段组件与消费者接入；账号列表/表单/批量抽屉视觉修正和废弃样式清理；定向交互回归、构建及新安装包视觉走查。代码只在 Cloud 共用 Vue 中维护，Desktop 仅重新构建验收。

不改数据库、接口、Cookie 执行/恢复规则或权限，不重新设计已确认业务，不修改其他会话正在维护的发布原型。

References:
- example/proto/social-accounts/index.html
- example/common/index.html
- docs/standards/frontend/AdminUI页面规范.md §2、§4.3–4.4、§7
- docs/standards/frontend/前端交互规范.md §4、§7.5、§11
- docs/standards/frontend/前端架构与视觉规范.md §4.1、§4.3–4.4
- docs/product/prd/详细文档/第三章_用户与账号管理.md §3.3

## Done When

- 无选择时不显示批量操作；选择、取消选择和列表上下文变化后的作用范围明确且真实可执行。
- 列表启停使用 TDesign Switch，确认取消/保存失败保留原值，提交时阻止重复，反馈与结果一致，移除重复启停动作。
- 账号筛选、行操作、详情、新增/编辑、分类及标签输入和批量接入容器对齐原型及公共规范；抽屉、滚动正文与固定底部不裁切。
- 公共分类/团队/成员选择在实际消费者中复用，搜索、清空、联动及单/多选保持业务语义，失效选择不会悄悄带入提交。
- 定向测试和 Web/Desktop 前端构建通过，重新构建安装包完成真实视觉与交互走查，保存截图及验证摘要；人工最终走查仍待用户。
