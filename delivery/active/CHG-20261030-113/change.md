---
id: CHG-20261030-113
parent: delivery/milestones/M2-account-runtime.md#m2-d-社媒账号重构
status: IMPLEMENTING
depends_on: []
affected_repos: ["wt-media-cloud", "wt-media-workspace"]
risk: M
---

# CHG-20261030-113：社媒账号浮层与操作结果视觉收口

## Change

按已确认原型与现行标准逐项核对社媒账号全部弹窗、抽屉、操作结果及确认入口。补齐旧容器、成功引导、只读详情、身份对照、凭证更新、窗口候选、批量输入/预览/历史/处理中/结果/空闲窗口选择的视觉与响应式遗漏；复用现有公共容器与结果模式，清理被替代样式。Cloud 维护唯一 Vue 实现；Desktop 仅重建验证。不改数据库、接口、Cookie 执行规则、权限或业务范围，不修改其他会话原型。

先登记入口和偏差，再按普通浮层、批量结果两步实施，检查空态/失败/部分/待确认/运行中、长文本、窄屏、关闭和动作可达。必要行为回归、关联构建和最新包检查后提交逐项走查记录与人工清单。受外部副作用限制的结果状态用真实生产组件的隔离场景核验并明确标注，不冒充真实 Cookie 验收。

References:
- example/proto/social-accounts/index.html
- example/common/index.html
- docs/standards/frontend/AdminUI页面规范.md §6、§7
- docs/standards/frontend/前端交互规范.md §8、§9、§11、§14
- docs/standards/frontend/前端架构与视觉规范.md §4.4、§4.5
- docs/product/prd/详细文档/第三章_用户与账号管理.md §3.3

## Done When

- 全部入口有逐项核对记录，无遗漏的旧窄表格弹窗、正文业务动作或重复摘要；新增、编辑与已修正窗口详情保持规范。
- 批量结果复用公共视觉模式：状态图标/标题、七项计数、进度与逐项表、固定操作；成功/全失败/部分/暂停/待确认呈现准确。
- 长名称、UID、Cookie、原因及窄屏不撑破浮层；表格仅在内部滚动，关闭/提交/恢复动作可达。
- 相关回归、Web/Desktop 构建和实际页面检查通过；证据区分真实操作与隔离展示，人工清单可逐项签收。M2-D 仍待人工整体验收。
