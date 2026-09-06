# 2026-09-06 代理来源与窗口详情人工验收环境

- 命令：`scripts/m2b-local-acceptance.sh all`。
- 数据库：固定 `wt_media_cloud`；迁移结果 `20260906_027_proxy_source` 已应用，累计 28 个迁移。
- Cloud：`GET http://127.0.0.1:18080/api/v1/health` 返回 `errcode: 0`，PASS。
- Agent：`GET http://127.0.0.1:8765/healthz` 正常；`/api/v1/status` 为 `idle` 且 `bitbrowser_status: normal`，PASS。
- CORS：从 `http://tauri.localhost` 对登录接口的预检返回该 Origin 和 credentials，PASS。
- Desktop：本次最新前端重建并打包；`/Volumes/WT Media/WT Media.app` 已挂载，PASS。
- 人工范围：静态地址解析、动态 API 提取/刷新、列表多选批量检测、绑定窗口详情，以及后续浏览器窗口同步读回。
