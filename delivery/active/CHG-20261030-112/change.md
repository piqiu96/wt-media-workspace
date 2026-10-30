---
id: CHG-20261030-112
parent: delivery/milestones/M2-account-runtime.md#m2-d-社媒账号重构
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-cloud", "wt-media-workspace"]
risk: M
---

# CHG-20261030-112：社媒账号表单与公共字段逐页走查

## Change

依据已审定原型和当前前端规范，继续检查社媒账号新增、编辑、批量输入/预览/结果，以及实际分类、运营团队、成员字段消费者。修正发现的视觉、表单生命周期、清空/联动、错误反馈和提交偏差；为人工提供按页可勾选、含预期结果的验收清单。Cloud 是共用 Vue 唯一实现处，Desktop 只重建验收；不改数据库、接口、业务能力或 Cookie 写入规则，不重设其他模块整体视觉。

依次核对当前规范与页面映射；补定向回归并修正发现；运行关联测试与两端构建，最新安装包及 Web 逐页核验；登记实际结果与人工清单。实现和验收记录分别提交。不修改其他会话正在维护的原型目录。

References:
- example/proto/social-accounts/index.html
- example/common/index.html
- docs/standards/frontend/AdminUI页面规范.md §6、§7
- docs/standards/frontend/前端交互规范.md §6、§8、§9、§11、§14
- docs/standards/frontend/前端架构与视觉规范.md §4.1、§4.4
- docs/product/prd/详细文档/第三章_用户与账号管理.md §3.3

## Done When

- 新增/编辑保存、取消/关闭、重复提交和失败保留输入符合原型及规范；不增加业务字段或新审批流程。
- 批量输入、预览、返回修改、关闭/重进与结果显示保持资料一致，未提交输入不串入新接入；运行中不误关或重复执行。
- 实际公共字段消费者逐页登记，搜索、清空、单/多选、联动及必要业务差异可验证；发现的偏差已修正并有针对性回归。
- 关联自动测试、Cloud/Desktop 构建与最新安装包/Web 走查通过；提供含操作、预期、人工结果栏的清单。M2-D 人工最终签收仍由用户完成。

实施与自检已完成：见 [逐页验证记录](evidence/verification.md)、[人工验收清单](evidence/人工验收清单.md)。Cloud PR #21，最终前端版本 `0.1.0+59f8f8d`。M2-D 人工签收仍未完成。
