# Task 2：运营分组生命周期证据

> 日期：2026-07-22

## 已验证事实

- 只有管理员可以创建、重命名和删除运营分组；
- 普通运营和高级运营必须属于一个有效分组；管理员必须无分组；
- 用户及历史 `media_accounts`、`browser_profiles`、`profile_sync_scans` 引用会阻止分组物理删除；
- 用户转组只改变用户当前分组，历史对象保留创建时 `team_id` 快照；
- 用户与分组的创建、修改、删除和审计在同一 Store 事务中完成；审计失败不会留下“接口失败但业务已成功”的部分结果。

## 验证

| 命令或用例 | 实际结果 | 状态 |
|---|---|---|
| `go test ./internal/modules/identity -count=1` | 分组生命周期、引用阻断、转组、审计和失败回滚用例通过 | PASS |
| `TestCreateTeamAuditFailureDoesNotPersistTeam` | 审计失败时不创建分组 | PASS |
| `TestCreateUserAuditFailureDoesNotPersistUser` | 审计失败时不创建用户 | PASS |
| `TestMySQLStoreRollsBackCreatedUserWhenAuditFails` | MySQL 事务回滚 | PASS |

## 结论

分组和用户写入不再依赖事后补审计，满足 A1 的可信持久化边界。
