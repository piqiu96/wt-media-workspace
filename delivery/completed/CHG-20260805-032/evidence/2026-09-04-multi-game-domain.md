# M2-B 多游戏领域模型（Task 8 / 计划 Task 2）

- Command: `go test ./internal/modules/mediaaccount ./internal/modules/identity -run 'Test(Service(AllowsEnabledPublicGamesAndNormalizesTheirSet|ReplacesAndClearsEntireGameSet|RejectsDisabledPublicGame)|PublicUserCanAccessOwnedResource|ServiceResolveGameReturnsStoredGameWithoutActorScope)' -count=1`
- Expected: 多游戏去重排序、完整替换与清空、已启用游戏公开关联、停用游戏拒绝，以及按账号归属授权均通过。
- Actual: `mediaaccount` 与 `identity` 两个目标包均 PASS（2026-09-04）。
- Status: PASS
- Notes: Cloud identity service 提供只读游戏事实解析；媒体账号授权只使用账号归属/团队边界，不使用 `users.game_ids`。关系表持久化、路由和页面验证仍在后续计划任务中。
