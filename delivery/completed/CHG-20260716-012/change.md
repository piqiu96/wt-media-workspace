# CHG-20260716-012: 架构迁移阶段四 — 共享模块化

## 1. Basic Information

- Level: M
- Status: DONE
- Created: 2026-07-16
- Current repository: `wt-media-cloud`
- Affected repositories: `wt-media-cloud`

## 2. Change Goal

将 Cloud Web 前端中 Cloud/Desktop 共享的业务页面从扁平的 `views/` 迁入 `modules/` 目录，使目录结构与架构规约文档一致。Login 归入 `modules/auth/`，Dashboard 归入 `modules/dashboard/`，Accounts 归入 `modules/accounts/`，Tasks 归入 `modules/tasks/`，ComingSoon 归入 `shared/ui/`。

联动更新 `apps/cloud/router.ts` 和 `apps/desktop/router.ts` 的 import 路径。

## 3. Baseline References

- Architecture: `docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md`
- Master route: `delivery/MASTER_IMPLEMENTATION_PLAN.md`

## 4. Scope

### Add

- `modules/auth/pages/LoginPage.vue` — 从 `views/Login.vue` 迁入
- `modules/dashboard/pages/DashboardPage.vue` — 从 `views/Dashboard.vue` 迁入
- `modules/accounts/pages/AccountsPage.vue` — 从 `views/Accounts.vue` 迁入
- `modules/tasks/pages/TasksPage.vue` — 从 `views/Tasks.vue` 迁入
- `shared/ui/ComingSoon.vue` — 从 `views/placeholders/ComingSoon.vue` 迁入

### Modify

- `apps/cloud/router.ts` — import 路径指向 `modules/*/pages/`
- `apps/desktop/router.ts` — import 路径指向 `modules/*/pages/`

### Delete

- `views/Login.vue`（内容已迁入 module）
- `views/Dashboard.vue`
- `views/Accounts.vue`
- `views/Tasks.vue`
- `views/placeholders/ComingSoon.vue`

### Explicitly Not Doing

- session.js/tasks.js/mediaAccounts.js 等 API 客户端暂不迁移（阶段五）
- 非活跃占位页面（ComingSoon 以外的 placeholder）暂不迁移
- Go 后端模块不涉及

## 5. Implementation Tasks

| Task | Goal | Status |
|---|---|---|
| T-01 | LoginPage.vue → modules/auth/pages/ | DONE |
| T-02 | DashboardPage.vue → modules/dashboard/pages/ | DONE |
| T-03 | AccountsPage.vue → modules/accounts/pages/ | DONE |
| T-04 | TasksPage.vue → modules/tasks/pages/ | DONE |
| T-05 | ComingSoon.vue → shared/ui/ | DONE |
| T-06 | 更新 cloud/desktop 路由器 import 路径 | DONE |
| T-07 | 删除旧 views/ 文件 | DONE |
| T-08 | 验证：Cloud 和 Desktop 构建均正常 | DONE |

## 6. Acceptance Matrix

| AC | Requirement | Status |
|---|---|---|
| AC-01 | Login 页面从 modules/auth/ 正确渲染 | DONE |
| AC-02 | Dashboard 页面从 modules/dashboard/ 正确渲染 | DONE |
| AC-03 | Accounts 页面从 modules/accounts/ 正确渲染 | DONE |
| AC-04 | Tasks 页面从 modules/tasks/ 正确渲染 | DONE |
| AC-05 | ComingSoon 从 shared/ui/ 正确引用 | DONE |
| AC-06 | Cloud 构建无报错 | DONE |
| AC-07 | Desktop 构建无报错 | DONE |
| AC-08 | 旧 views/ 文件已清理 | DONE |
