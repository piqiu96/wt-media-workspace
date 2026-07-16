# CHG-20260716-019: M2-C7 开户

## 1. Basic Information

- Level: M
- Status: DONE
- Created: 2026-07-16
- Affected repositories: `wt-media-cloud`

## 2. Change Goal

实现批量 Cookie 开户流程：Cookie 导入 → 解析预览 → 创建媒体账号 → 分配代理 → 执行开户。

## 3. Deliverables

- `modules/accounts/pages/AccountOpeningPage.vue` — 批量 Cookie 开户向导（三步：导入→预览→执行）
- 路由 `/account-opening` 注册到 Cloud + Desktop 路由
- 侧边栏「账号开户」菜单项
