# M2-B 多游戏关系表持久化（Task 8 / 计划 Task 3）

- Command: `go test ./internal/modules/mediaaccount/... ./internal/modules/migration/... -count=1`
- Expected: MySQL Store 对基础账号与关系替换使用事务；按任一游戏筛选无重复账号；关系行批量读回；迁移 025 包含关系表、旧值迁移与旧列删除。
- Actual: `mediaaccount` 和 `migration` 测试包均 PASS（2026-09-04）。新增 sqlmock 覆盖 `BEGIN → UPDATE → DELETE relations → INSERT relations → COMMIT`，并覆盖 `EXISTS` 筛选和有序关系读回。
- Status: PASS
- Migration direction: `media_accounts.game_id` → `media_account_games(media_account_id, game_id)`；只触及游戏关联。真实 MySQL 的预检、执行与计数校验仍在计划 Task 6。
