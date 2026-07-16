# CHG-20260716-014: 清理 — 死文件 + 迁移 Users/LocalLogs + API 客户端

## 1. Basic Information

- Level: S
- Status: DONE
- Created: 2026-07-16
- Affected repositories: `wt-media-cloud`、`wt-media-desktop`

## 2. Change Goal

架构迁移结束后清理剩余死文件，将未完成的 3 个 view/ 页面和 4 个 API 客户端迁入正确目录。

## 3. Scope

### Add

- `apps/cloud/pages/users/UsersPage.vue` — 从 `views/Users.vue` 迁入
- `apps/desktop/features/local-logs/LocalLogsPage.vue` — 从 `views/LocalLogs.vue` 迁入
- `shared/api/session.js` — 从 `session.js` 迁入
- `shared/api/mediaAccounts.js` — 从 `mediaAccounts.js` 迁入
- `shared/api/tasks.js` — 从 `tasks.js` 迁入
- `shared/api/profileBindings.js` — 从 `profileBindings.js` 迁入

### Modify

- `apps/cloud/router.ts` — Users 路径 `../../views/Users.vue` → `../../apps/cloud/pages/users/UsersPage.vue`
- `apps/desktop/router.ts` — LocalLogs 路径 `../../views/LocalLogs.vue` → `../../features/local-logs/LocalLogsPage.vue`
- 所有模块页面的 `../../session.js` → `../../shared/api/session.js`
- `views/Users.vue` 和模块页面的 import 路径

### Delete

- `views/AgentStatus.vue`（死文件，无路由引用）
- `views/Users.vue`（迁出后删除）
- `views/LocalLogs.vue`（迁出后删除）
- `session.js`（迁出后删除）
- `mediaAccounts.js`（迁出后删除）
- `tasks.js`（迁出后删除）
- `profileBindings.js`（迁出后删除）
- `WT Media_0.1.0_aarch64.dmg`
- `desktop/.runtime/`（旧运行时状态）

