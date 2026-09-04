# 2026-09-04 游戏范围、引用管理与测试数据清理

## 已实现

- Decision 0012 确认非管理员媒体账号游戏范围以 `user_game_scopes` 为准；管理员代管时按目标归属用户范围校验。
- `GET /api/v1/games` 对管理员返回用户授权数和媒体账号引用数；新增管理员专用 `GET /api/v1/games/:game_id/references` 返回安全的处理明细。
- 游戏停用/删除引用检查改由 `user_game_scopes` 与 `media_account_games` 执行，不再访问已删除的 `media_accounts.game_id`；前端任一关联存在时禁用两个操作并提供只读详情抽屉。
- 用户缩小游戏范围若仍有其媒体账号引用被移除游戏则拒绝保存；非管理员创建、更新、筛选和账号检查均拒绝范围外游戏。历史越界关系不会静默删除。

## 测试与构建

- `go test ./internal/modules/identity ./internal/modules/mediaaccount -count=1` 通过。
- `npm test -- --run src/apps/cloud/pages/users/usersApi.test.js src/apps/cloud/pages/users/TeamsAndGamesPage.test.js src/mediaAccounts.test.js`：17 项通过。
- `npm run build:cloud` 与 `npm run build:desktop` 通过。
- `m2b-local-acceptance.sh all --force-restart` 退出码 0；Cloud 在 `18080`、Agent 在 `8765` 监听，Cloud Web 开发验收入口在 `5173`。

## 已批准测试数据清理

清理前确认 `account_groups.filters` 没有引用 `game1`。已在一个事务中删除：

- `media_account_games` 中 `game_id='game1'` 的 6 条关系；
- `operation_games` 中 `id='game1'` 的 1 条游戏记录。

保留全部 6 条 `media_accounts` 记录及其 Cookie、Profile、标签、检查记录等关联事实。清理后真实库游戏目录为 `hy`、`sjz`、`other`，且已确认 `game1` 游戏和关系均为 0。

## 人工验收

用户于 2026-09-04 确认 Cloud Web 人工验收完成：游戏管理关联摘要/详情和禁用态、媒体账号游戏范围限制、测试游戏清理后的页面状态均通过。
