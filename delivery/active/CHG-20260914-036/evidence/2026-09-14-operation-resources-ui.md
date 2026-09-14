# M2 运营资源统一 UI 验收（2026-09-14）

## 范围事实

- 新增全局 `design-token.css`，Cloud 与 Desktop 入口均加载 Token 和资源模块样式。
- 浏览器窗口、代理管理、社媒账号均使用共享页面 Header、资源统计、内容卡与浅色状态 Badge。
- 既有 API 客户端、路由、权限过滤、表格字段和 Tauri/Local Agent 调用未改。
- 浏览器窗口操作列保留详情与打开；分配、关闭、绑定代理、编辑、启用/停用均在更多菜单中复用既有处理函数。

## 自动验证

```text
cd wt-media-cloud/web && npm test -- --run
18 test files passed, 60 tests passed

cd wt-media-cloud/web && npm run build:desktop
vite production build passed

cd wt-media-workspace && ./scripts/local-control.sh start
Cloud health PASS
Agent health PASS
BitBrowser via Agent PASS
Desktop assets fresh / PASS
DMG fresh / PASS
Login smoke PASS user=admin
```

## 走查状态

最新 DMG 已挂载并启动。待用户在 Desktop 的“运营资源”下依次查看浏览器窗口、代理管理和社媒账号的视觉一致性。
