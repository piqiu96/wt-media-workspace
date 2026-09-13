# 2026-09-05 本地人工验收环境

## 启动与构建

- 命令：`wt-media-workspace/scripts/m2b-local-acceptance.sh all --force-restart`
- 结果：迁移 `0 applied, 27 total`；Cloud 与 Agent 被强制重启；Desktop 前端重建、DMG 重建并挂载。

## 自动回归

- Cloud：`go test ./internal/modules/proxy ./internal/modules/profilebinding -count=1`，通过。
- Agent：`python3 -m unittest discover -s tests -v`，76 项通过。

## 运行门禁

- Cloud `GET /api/v1/health`：`errcode=0`。
- Agent `GET /api/v1/status`：`bitbrowser_status=normal`，40 个可见 Profile。
- Desktop CORS 预检：`Origin: http://tauri.localhost` 返回 `204`、允许该 Origin 及 credentials。
- 登录烟测：本地 `admin` 使用 `replace_existing=true` 返回 `errcode=0`。
- DMG：`wt-media-desktop/target/release/bundle/dmg/WT Media_0.1.0_aarch64.dmg`，4.7 MB，2026-09-05 00:06；已挂载 `/Volumes/WT Media`。
- Desktop 前端：`http-*.js` 含 `127.0.0.1:18080/api/v1`。

## 边界

本环境证明当前已实现功能可人工验收；真实代理写入/读回、替换与解绑仍须使用操作者提供的可写真实代理，不能由本环境门禁替代。
