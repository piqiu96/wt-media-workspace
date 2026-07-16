# CHG-20260716-017: M2-C3 BitBrowser Profile 扫描前端

## 1. Basic Information

- Level: M
- Status: DONE
- Created: 2026-07-16
- Affected repositories: `wt-media-cloud`

## 2. 已完成的前置基础设施

### 数据库
- `browser_profiles` 表 ✅
- `profile_sync_scans` + `profile_sync_candidates` 表 ✅
- `users.bit_main_user_id` 字段 ✅

### 后端 API
- `POST /api/v1/bit-browser/profile-scans` — 提交扫描快照 ✅
- `GET /api/v1/bit-browser/profile-scans/:scan_id` — 获取扫描详情 ✅
- `POST /api/v1/bit-browser/profile-scans/:scan_id/confirm` — 确认扫描 ✅
- `GET /api/v1/browser-profiles` — 列表 ✅

### Agent
- `bitbrowser.py` — BitBrowser Local API 扫描 ✅

### 前端
- `shared/api/profileBindings.js` — API 客户端 ✅

## 3. 待完成

- `modules/profiles/pages/ProfilesPage.vue` — Profile 管理页面
- Cloud/Desktop 路由注册
- 侧边栏菜单项

