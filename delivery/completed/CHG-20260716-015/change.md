# CHG-20260716-015: M2-C2 媒体账号生命周期

## 1. Basic Information

- Level: M
- Status: IN_PROGRESS
- Created: 2026-07-16
- Affected repositories: `wt-media-cloud`

## 2. Change Goal

完成媒体账号生命周期管理。后端已于历史 CHG 中完成（Create/List/Update/Identify/BindProfile/AddTags/RemoveTags），本次主要完成前端页面和生命周期闭环。

## 3. 已完成的后端 API

| 方法 | 路径 | 用途 |
|------|------|------|
| POST | /api/v1/media-accounts | 创建账号 |
| GET | /api/v1/media-accounts | 列表（支持 user_id/game_id/platform/tag 过滤） |
| GET | /api/v1/media-accounts/:id | 单账号详情 |
| PATCH | /api/v1/media-accounts/:id | 更新业务/登录状态 |
| POST | /api/v1/media-accounts/:id/identify | 识别账号信息 |
| POST | /api/v1/media-accounts/:id/bind-profile | 绑定浏览器 Profile |
| POST | /api/v1/media-accounts/tags/add | 批量添加标签 |
| POST | /api/v1/media-accounts/tags/remove | 批量移除标签 |

## 4. 待完成的前端

### Add

- 账号详情页面（展示状态、标签、Profile、登录状态等完整信息）
- 账号状态操作（启用/停用/退役）
- 账号绑定 Profile 功能
- 搜索/过滤栏（平台、状态、标签筛选）
- 账号批量操作栏（选中 → 批量添加/移除标签）
- 账号工作台概览（总数、状态分布统计）

### Modify

- `modules/accounts/pages/AccountsPage.vue` — 升级为完整工作台
- `modules/accounts/api.ts` — 封装所有 API 调用

### Delete

- `modules/accounts/pages/AccountsPage.vue`（被新版替换）

## 5. Implementation Tasks

| Task | Goal | Status |
|---|---|---|
| T-01 | 创建 accounts API 封装（api.ts） | DONE | API 客户端已在 `shared/api/mediaAccounts.js`，无需再封装 |
| T-02 | 升级 AccountsPage：布局规范化 + 详情/状态/识别 | DONE | 改用标准 ResourceList 布局：统计卡片 → 搜索栏 → 操作栏 → 表格 → 详情抽屉 |
| T-03 | 添加搜索过滤栏（平台/状态/标签） | DONE | 搜索栏含平台/业务状态/标签三个过滤条件 |
| T-04 | 添加批量操作栏（标签管理） | DONE | 选择行后显示批量标签输入 + 添加/移除按钮 |
| T-05 | 验证：Cloud 和 Desktop 构建正常 | DONE | Cloud 3848 modules, Desktop 3854 modules |
