# CHG-20260716-016: M2-C5 代理管理

## 1. Basic Information

- Level: M
- Status: DONE
- Created: 2026-07-16
- Affected repositories: `wt-media-cloud`

## 2. Scope

### Add

- Migration: `proxy_configs` 表（协议/host/port/用户名/密码/地区/到期/供应商/状态/检测结果）
- 后端模块：`internal/modules/proxy/`（CRUD + 导入解析 + 检测触发）
- 后端路由：`POST/GET/PATCH /api/v1/proxies`、`POST /api/v1/proxies/import`、`POST /api/v1/proxies/:id/check`
- 前端页面：`modules/proxy/pages/ProxyPage.vue`
- API 客户端：`shared/api/proxy.js`

### Explicitly Not Doing

- 与 Profile 关联的分配/回读（属 C3/C4 范围）
- BitBrowser API 集成（属 C3/C4）
- 真正的代理连通性检测（由 Agent 执行，本 CHG 做触发接口）
