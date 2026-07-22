# M2-A3 Evidence: 用户管理、运营分组、游戏字典与Desktop角色入口

## 1. Scope

本 Evidence 验证 `CHG-20260723-024`：

- Cloud 系统管理拆为用户管理、运营分组、游戏管理；
- 管理类列表默认具备搜索、列表和分页；
- 创建/编辑用户的游戏范围来自游戏字典；
- 停用游戏不能继续分配给新用户；
- Desktop 业务入口只允许普通运营；
- 创建用户失败展示可理解错误；
- Desktop 菜单不显示空的“系统”分组；
- 普通运营不能在 Cloud 看到或访问用户管理、运营分组、游戏管理；
- 用户管理里的游戏范围显示游戏中文名称；
- 游戏 ID 仅允许 32 位以内字母或数字，且唯一；
- 用户密码最少 6 位。

## 2. Automated verification

Command:

```text
GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/... ./internal/app
```

Actual result:

```text
ok github.com/wt-media/wt-media-cloud/internal/modules/cloudagent
ok github.com/wt-media/wt-media-cloud/internal/modules/identity
ok github.com/wt-media/wt-media-cloud/internal/modules/mediaaccount
ok github.com/wt-media/wt-media-cloud/internal/modules/migration
ok github.com/wt-media/wt-media-cloud/internal/modules/profilebinding
ok github.com/wt-media/wt-media-cloud/internal/modules/profileguard
ok github.com/wt-media/wt-media-cloud/internal/modules/runtimebinding
ok github.com/wt-media/wt-media-cloud/internal/app
```

Command:

```text
npm run test
```

Actual result:

```text
Test Files  7 passed
Tests       20 passed
```

Command:

```text
npm run build
```

Actual result:

```text
Cloud build PASS
```

Command:

```text
npm run build:cloud
```

Actual result:

```text
Cloud config build PASS
```

Command:

```text
npm run build:desktop
```

Actual result:

```text
Desktop build PASS
```

Latest feedback regression verification:

```text
go test ./internal/modules/... ./internal/app
npm run test
npm run build
npm run build:cloud
npm run build:desktop
```

Actual result:

```text
All PASS.
```

## 3. Real MySQL + Cloud API verification

Environment:

- MySQL database: `wt_media_m2_a2_task5_acceptance`
- Cloud API for Cloud Web: `127.0.0.1:18080`
- Cloud API for Desktop Web proxy: `127.0.0.1:8080`
- Admin user: `m2a2_task5_admin`

Applied migration to current local acceptance DB:

```text
20260723_013_operation_games.sql
```

### Case A: game dictionary can be managed

Operation:

```text
POST /api/v1/games
payload = {"id":"naruto","name":"火影忍者","remark":"M2-A3验收"}
```

Actual result:

```text
errcode = 0
game.id = naruto
game.status = enabled
```

Result: PASS.

## 8. 2026-07-23 Manual acceptance

Manual action:

```text
User performed acceptance on the running local environment.
```

User confirmation:

```text
确定已验收
```

Accepted scope:

- Cloud user management page;
- Cloud operation team management page;
- Cloud game management page;
- Desktop role-entry behavior;
- latest reference protection behavior for teams and games.

Result: PASS.

### Case B: operator user can be created only with configured enabled game

Operation:

```text
POST /api/v1/users
payload = {
  "username":"m2a3_operator",
  "password":"operatorSecret123",
  "role":"operator",
  "team_id":3,
  "game_ids":["naruto"]
}
```

Actual result:

```text
errcode = 0
user.username = m2a3_operator
user.role = operator
user.team_name = M2-A3运营组
user.game_ids = ["naruto"]
```

Result: PASS.

### Case C: disabled game cannot be assigned to a new user

Operations:

1. `PATCH /api/v1/games/naruto` with `status=disabled`;
2. `POST /api/v1/users` with `game_ids=["naruto"]`;
3. restore `naruto` to `enabled`.

Actual result:

```text
disabled_game_user_create = [10002, 请选择已启用的游戏]
```

Result: PASS.

### Case D: invalid game ID is rejected with operator-readable message

Operation:

```text
POST /api/v1/games
payload = {"id":"bad-01","name":"非法游戏ID验收744244","remark":""}
```

Actual result:

```text
http_status = 400
errcode = 10004
message = 游戏ID仅支持32位以内字母或数字
```

Result: PASS.

### Case E: 6-character password can create an operator

Operation:

```text
POST /api/v1/users
payload = {
  "username":"m2a3_shortpwd_744244",
  "password":"abc123",
  "role":"operator",
  "team_id":8,
  "game_ids":["a3g744244"]
}
```

Actual result:

```text
http_status = 201
errcode = 0
user.username = m2a3_shortpwd_744244
one_time_password = abc123
```

Result: PASS.

### Case F: ordinary operator cannot access user management API

Operation:

```text
POST /api/v1/auth/login
payload = {"username":"m2a3_shortpwd_744244","password":"abc123","replace_existing":true}

GET /api/v1/users
```

Actual result:

```text
login = [200, 0, operator]
GET /api/v1/users = [403, 11003, 没有权限执行此操作]
```

Result: PASS.

## 4. Page and role-scope verification

Source checks:

- `AppLayout.vue` Cloud menu now exposes:
  - 用户管理；
  - 运营分组；
  - 游戏管理；
- Desktop menu filters `/users`, `/operation-teams`, and `/games`;
- Desktop menu removes empty groups after filtering, so it no longer shows an empty “系统” group;
- Cloud route guard redirects non-admin users away from `/users`, `/operation-teams`, and `/games`;
- Cloud identity API forbids non-admin `GET /api/v1/users`;
- `UsersPage.vue` includes `t-pagination` and uses `enabledGames` rather than free-text game input;
- `UsersPage.vue` maps `game_ids` to game names for the table display;
- `UsersPage.vue` validates create/reset password with minimum 6 characters;
- `TeamsPage.vue` includes search, list, user count and pagination;
- `GamesPage.vue` includes search, status filter, list and pagination;
- `GamesPage.vue` validates game ID with `^[A-Za-z0-9]{1,32}$` before submit;
- Desktop route guard and login page reject non-operator roles with: `管理员和高级运营不能登录 Desktop，请使用 Cloud Web 管理。`

Result: PASS.

## 5. Manual acceptance entry points

- Cloud user management: `http://127.0.0.1:5173/users`
- Cloud operation teams: `http://127.0.0.1:5173/operation-teams`
- Cloud games: `http://127.0.0.1:5173/games`
- Desktop role guard: `http://127.0.0.1:5174/login`

Acceptance users:

```text
Admin:
  username = m2a2_task5_admin
  password = task5Secret123

Operator:
  username = m2a3_shortpwd_744244
  password = abc123
```

## 6. 2026-07-23 Frontend loading/blank-page follow-up

User report:

```text
刚登录进来，用户管理、游戏管理、运营分组都属于 loading 态不会消息。
```

Root cause:

- Admin user data can return `game_ids = null`;
- `UsersPage.vue` rendered game scope through `gameScopeText(gameIds)` and previously assumed `gameIds.length` was always valid;
- The user management page crashed during table cell rendering, which looked like a loading or blank-page state to the operator.

Fix:

```text
UsersPage.vue
gameScopeText(gameIds) now normalizes non-array values to [] before reading length.
```

Regression coverage:

```text
npm run test -- --run UsersPage.test.js TeamsAndGamesPage.test.js
```

Actual result:

```text
Test Files  2 passed (2)
Tests       8 passed (8)
```

Build verification:

```text
npm run build:cloud
```

Actual result:

```text
Cloud Web build PASS.
```

Browser verification on `http://127.0.0.1:5173`:

```text
/users
  用户管理 table rendered, includes UID、用户名、角色、运营分组、游戏范围、状态、操作.
  Admin row renders 游戏范围 = 全部游戏.

/operation-teams
  运营分组 table rendered, includes 分组ID、分组名称、用户数、操作.

/games
  游戏管理 table rendered, includes 游戏ID、游戏名称、状态、备注、操作.
```

Result: PASS.

Note:

- Browser console still contains old captured errors from before the fix at `2026-07-22T18:43:00Z`;
- The current DOM verifies the pages are no longer blank/loading;
- Existing historical game data such as `火影-01` may still appear because it was inserted before the new game ID validation. Current create/edit validation now blocks new invalid IDs.

## 7. 2026-07-23 Reference protection follow-up

User decision:

```text
游戏被用户引用时，不能停用、不能删除。
运营分组被用户引用时，不能删除。
```

Backend behavior:

- `Service.UpdateGame` now checks references before changing an enabled game to `disabled`;
- `Service.DeleteGame` already checks references before delete;
- `Service.DeleteTeam` already checks team references before delete;
- API error messages are operator-readable:
  - team in use: `该分组下还有用户或业务引用，不能删除，请先转移用户`;
  - game in use: `该游戏已分配给用户或已有业务引用，不能停用或删除，请先调整用户游戏范围`.

Frontend behavior:

- Operation teams page keeps `用户数` and disables delete when `user_count > 0`;
- Games page adds `用户数`;
- Games page disables delete when `user_count > 0`;
- Games page disables disable/toggle action when the game is enabled and `user_count > 0`;
- Disabled games with users may still be re-enabled, but cannot be deleted while referenced.

Browser verification on `http://127.0.0.1:5173`:

```text
/operation-teams
  user_count = 0 rows: delete enabled.
  user_count = 1 rows: delete disabled.

/games
  enabled + user_count = 0 rows: disable/delete enabled.
  enabled + user_count > 0 rows: disable/delete disabled.
  disabled + user_count > 0 rows: enable allowed, delete disabled.
```

Automated verification:

```text
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/... ./internal/app
npm run test
npm run build:cloud
```

Actual result:

```text
Cloud Go modules and app tests PASS.
Cloud Web tests PASS: 7 files, 20 tests.
Cloud Web build PASS.
```

Result: PASS.
