# CHG-20260715-011: M2-C1 用户管理（追认）

## 1. Basic Information

- Level: S
- Status: DONE
- Created: 2026-07-16（追认）
- Current repository: `wt-media-cloud`
- Affected repositories: `wt-media-cloud`

## 2. Change Goal

在后端增加用户列表查询、审计日志查询接口；在前端增加用户管理页面（仅技术角色可访问）。

## 3. Baseline References

- Master route: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`
- Architecture: `wt-media-workspace/docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md`
- Decision 0007: Visual and Frontend Engineering Baseline

## 4. Scope

### Add

- Service: `ListUsers()` / `GetUser()` 方法
- Store: memory 和 MySQL 实现
- Routes: `GET /api/v1/users`、`GET /api/v1/audit-logs`
- Frontend: `Users.vue` — TDesign 表格 + 新建用户弹窗
- 路由: `/users` 指向 Users 页面

### Modify

- `memoryStore.audits` → `auditLogs` 字段重命名

### Fix

- `updatePassword` 缺少 closing brace

### Explicitly Not Doing

- 用户编辑/删除（后续迭代）
- 角色管理独立页面（后续迭代）
- 密码重置 UI（后续迭代）

## 5. Implementation Completed

| Item | File | Commit |
|---|---|---|
| Service ListUsers | `internal/modules/identity/service.go` | `77f5241` |
| Service ListAuditLogs | `internal/modules/identity/service.go` | `77f5241` |
| Store MySQL ListUsers | `internal/modules/identity/store_mysql.go` | `77f5241` |
| Store MySQL ListAuditLogs | `internal/modules/identity/store_mysql.go` | `77f5241` |
| Store memory ListUsers | `internal/modules/identity/service.go` (memoryStore) | `77f5241` |
| Store memory ListAuditLogs | `internal/modules/identity/service.go` (memoryStore) | `77f5241` |
| Routes users + audit-logs | `internal/modules/identity/routes.go` | `77f5241` |
| Users.vue frontend | `web/src/views/Users.vue` | `77f5241` |
| Router update | `web/src/router/index.js` | `77f5241` |

## 6. Acceptance

| AC | Requirement | Verification |
|---|---|---|
| AC-01 | 技术角色可查看用户列表 | commit 代码 |
| AC-02 | 非技术角色返回 403 | route 有角色校验 |
| AC-03 | 可查看审计日志（最近 50 条） | route 测试通过 |
| AC-04 | 前端 TDesign 表格正常渲染 | commit 包含 Users.vue |
| AC-05 | 测试通过 | `service_test.go`、`routes_test.go`、`store_mysql_test.go` 存在 |

## 7. Evidence

- Commit `77f5241` — 包含所有后端和前端变更
- 继承测试：`internal/modules/identity/service_test.go`
- 继承测试：`internal/modules/identity/routes_test.go`
- 继承测试：`internal/modules/identity/store_mysql_test.go`

## 8. Status

`DONE` — 代码已提交，追认 CHG 记录。
