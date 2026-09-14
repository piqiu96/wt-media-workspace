# 本地端到端走查环境（2026-09-14）

## 命令与结果

- `bash scripts/m2b-local-acceptance.sh all --force-restart`：通过。脚本停止旧 Agent、执行固定 `wt_media_cloud` 数据库迁移、启动 Cloud 与 Local Agent、验证 BitBrowser、重建并挂载 DMG、刷新 Desktop 资源并执行登录烟测。
- `./scripts/local-control.sh verify`：通过。Cloud、Agent、BitBrowser、Desktop 资源、DMG 新鲜度及 `admin` 登录烟测均为 PASS。
- 两个走查账号以 `replace_existing: true` 实际登录，且未回显会话令牌：`admin`、`operator01` 均通过。

## 手动入口

- `scripts/local-control.sh start`：重建并启动完整环境。
- `scripts/local-control.sh verify`：复核环境门禁。
- `scripts/local-control.sh stop`：停止 Cloud 与 Local Agent。
