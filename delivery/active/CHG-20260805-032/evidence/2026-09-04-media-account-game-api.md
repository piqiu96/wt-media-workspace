# M2-B 多游戏 API 契约（Task 8 / 计划 Task 4）

- Command: `go test ./internal/modules/mediaaccount/... -count=1`
- Expected: `game_ids` 支持创建、完整更新/清空和任一游戏筛选；旧 `game_id` 兼容；双字段不一致被拒绝。
- Actual: 目标包 PASS（2026-09-04）。路由测试覆盖创建/清空回读、兼容字段冲突和按任一游戏筛选。
- Status: PASS
- Contract owner: Cloud。Cloud Web 为直接消费者；Agent 不保存媒体账号游戏关系；Desktop 仅加载 Cloud Web 构建资产。
