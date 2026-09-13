# 2026-09-12 M2 人工验收环境

- 命令：`scripts/m2b-local-acceptance.sh all --force-restart`，随后独立执行 `scripts/m2b-local-acceptance.sh verify`。
- 数据库：固定使用 `wt_media_cloud`；迁移结果为 `0 applied, 28 total`，PASS。
- Cloud：当前提交 `171184a241e275a5e583632f556dfacac5cc67d7`；进程 PID 23483 于 2026-09-12 16:54:35 +0800 启动；`GET http://127.0.0.1:18080/api/v1/health` 返回 `errcode: 0`，PASS。
- Agent：当前提交 `f716b66604033d8f764bcb5679d6d6d91c0b0398`；进程 PID 23484 于 2026-09-12 16:54:37 +0800 启动；`GET http://127.0.0.1:8765/healthz` 正常，`/api/v1/status` 的 `bitbrowser_status` 为 `normal`，并读到 40 个 BitBrowser Profile，PASS。
- BitBrowser：首次全流程因客户端未启动而在强制门禁处停止；启动 `/Applications/比特浏览器.app` 后，Agent 到 BitBrowser 的状态恢复为 `normal`，再从全流程顶部重跑并通过。
- Desktop 前端：当前 Cloud Web 源码构建；生成资源包含绝对 API 基址 `127.0.0.1:18080/api/v1`，资源新鲜度检查 PASS。
- DMG：`WT Media_0.1.0_aarch64.dmg` 大小 4,942,150 bytes，构建时间 2026-09-12 16:55:46 +0800；相对 Cloud Web 与 Desktop 源码提交为新构建，PASS。
- 挂载与启动：DMG 挂载到 `/Volumes/WT Media`，并从 `/Volumes/WT Media/WT Media.app` 启动，PASS。
- CORS：从 `Origin: http://tauri.localhost` 对登录接口预检返回 HTTP 204、`Access-Control-Allow-Origin: http://tauri.localhost` 和 `Access-Control-Allow-Credentials: true`，PASS。
- 登录冒烟：`admin` 使用 `replace_existing: true` 登录返回 `errcode: 0`，PASS。
- 最终独立复验：Cloud、Agent、BitBrowser、Desktop assets、DMG、登录全部 PASS；环境已留存用于 M2 人工验收。

