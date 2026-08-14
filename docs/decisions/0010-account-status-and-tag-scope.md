# Decision 0010: 社媒账号业务状态两态模型与标签范围

## Status

Accepted

## Context

社媒账号页 v3 冻结功能范围（不新增、不删除、不改状态口径），只做信息架构与视觉布局重排（CHG-20260805-032 Task 7）。收口过程中暴露两处文档口径冲突：

1. **标签批量操作**：PRD 第三章 3.3.6 写「支持批量添加、批量移除」，但 v3 页面已移除批量工具栏，账号页只保留「批量检查」一个批量入口，标签只在编辑弹窗按单账号增删。
2. **business_status 枚举**：milestone `M2-account-runtime.md` 写 `draft`/`enabled`/`disabled`/`abnormal`/`retired` 五态，但迁移 `021` 已收敛为 `enabled`/`disabled` 两态（历史 draft/abnormal → enabled），PRD 第三章 3.3.9 亦为两态。

## Decision

1. **业务状态（business_status）为两态 `enabled` / `disabled`**：业务状态只表达「启用 / 停用」这一业务选择，不承载账号真实健康度。`draft`（待识别）、`abnormal`（异常）、`retired`（退役）从媒体账号业务状态中移除（迁移 021 已执行，历史数据回填为 `enabled`）。账号健康度由独立的「账号状态」派生（login_status + identification_status），与业务状态解耦。
2. **社媒账号页 v3 不设批量工具栏**：唯一批量操作是「批量检查」（勾选多行后执行）。批量启用/停用、批量添加/移除标签从本期页面移除。标签按单账号在编辑弹窗中多选 allow-create 增删；批量标签操作延后，不作为本期页面能力。

## Consequences

- Positive：业务状态与健康状态职责分离，页面口径与代码（迁移 021）、PRD 第三章 3.3.9 一致。
- Negative：milestone 与 PRD 中残留的五态/批量标签描述需回改（本决策落地时同步修正）。
- Follow-up：批量标签操作如需恢复，作为独立需求立项；`login_status` 枚举在 milestone（`unchecked`/`logged_in`/`not_logged_in`/`expired`/`mismatch`/`check_failed`）与 PRD 第三章（`unknown`/`normal`/`not_logged_in`/`verification_needed`/`expired`/`restricted`/`account_mismatch`/`environment_error`）之间亦存在口径差异，建议后续单独对齐。
