# ADR-0029：代理使用自增整数主键

- Status: Accepted
- Date: 2026-10-30
- Scope: `proxies`、窗口代理关系、Cloud API、共用 Vue 页面
- Related: ADR-0027、CHG-20261028-099

## Context

代理当前使用不适合运营辨认的字符串主键。用户明确要求数据库主键及接口 ID 一并改为自增整数，不能仅增加展示编号。窗口正式关系、进行中预留和代理操作回执引用该主键，迁移须保留存量关系。

## Decision

1. `proxies.id` 改为 MySQL `BIGINT UNSIGNED AUTO_INCREMENT` 主键；列表、详情、搜索、导入结果、代理操作请求/响应中的代理 ID 使用整数。
2. `browser_profiles.proxy_id` 和 `reserved_proxy_id` 同步改为 `BIGINT UNSIGNED` 外键。迁移通过旧到新 ID 映射转写存量正式关系、预留和当前操作回执；旧字符串仅保存在不参与运行时查询的迁移追溯列 `legacy_id`。
3. 这是破坏性接口变化。Cloud、Vue/Desktop 发布组合必须同步升级；旧客户端不得对新 Cloud 发起代理写入。
4. 不为兼容旧主键建立运行时双写，不清理存量代理或窗口关联。

## Consequences

- 隔离 MySQL 必须覆盖有代理、窗口正式/预留关系及操作回执的迁移场景，并验证外键、ID 类型和自增创建。
- Cloud 提供的 OpenAPI 与业务 schema 先更新，消费方随后同步。
