# CHG-20260716-018: M2-C4 窗口管理 + C6 Cookie + C8 Agent绑定 + C9 并发预检 + C10 综合

## 1. Basic Information

- Level: L
- Status: DONE
- Created: 2026-07-16
- Affected repositories: `wt-media-cloud`、`wt-media-agent`

## 2. Scope

### C4 窗口管理
- Agent: BitBrowser create/open/close/update/delete profile CRUD
- Agent: Local API endpoints for profile operations
- Cloud: Profile CRUD API (create/open/close/update/delete)
- Cloud: DeleteProfile service + store + route
- Frontend: ProfilesPage — 新建/打开/关闭/删除窗口 + 扫描 Diff

### C6 Cookie 导入导出
- AccountsPage 详情抽屉: Cookie 状态展示、导出原始CK/活跃CK、导入CK弹窗

### C8 Agent 节点绑定
- 后端已有：runtimebinding service + routes（签发绑定凭证/注册节点/上报运行环境）

### C9 并发预检 + 敏感任务
- 后端已有：profileguard service + routes（预检/续期/完成）

### C10 综合
- 侧边栏菜单更新，ComingSoon 替换为实际页面
