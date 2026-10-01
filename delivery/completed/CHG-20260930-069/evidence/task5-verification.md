# Task 5 证据：定向测试与双 Web 构建

- 日期：2026-09-30
- 范围：定向 Go/Web 测试复跑、`build:cloud` 与 `build:desktop`。

## 定向 Go 测试

- 命令：`go test ./internal/modules/production/... ./internal/infra/storage/... ./internal/bootstrap/...`
- 实际：production、production/repository、production/service、infra/storage、bootstrap 全部 `ok`。
- 全仓：`go test ./...` 0 失败（Task 2 时跑过，此后仅改 web）。
- 状态：PASS

## 定向 Web 测试

- 命令：`npx vitest run src/modules/materials src/modules/transfer src/shared/api/materials.test.js`
- 实际：91 条用例全部通过。
- 状态：PASS

## 双 Web 构建

- 命令：`npm run build:cloud` → `✓ built in 6.99s`
- 命令：`npm run build:desktop` → `✓ built in 6.60s`
- 两者仅有既有的 chunk 体积提示，无错误。
- 状态：PASS

## 本地环境启动（m2b-local-acceptance.sh all）

- 命令：`wt-media-workspace/scripts/m2b-local-acceptance.sh all`（exit 0）。
- 各门实际结果（2026-09-30）：
  - Cloud `GET /api/v1/health` → PASS（`http://127.0.0.1:18080/api/v1/health`）。
  - Agent `GET /healthz` → PASS；BitBrowser via Agent → PASS（`bitbrowser_status` normal）。
  - Cloud 迁移 `scripts/migrate.sh` 执行（本 CHG 无迁移，幂等通过）。
  - Desktop 前端与 DMG 全新构建并挂载：`WT Media_0.1.0_aarch64.dmg` fresh，挂载于 `/Volumes/WT Media`，`WT Media.app` 已启动（pid 73943）。
  - Desktop assets fresh：`dist-desktop/assets/index.desktop-9x8Rvakc.js` 含 `127.0.0.1:18080/api/v1`。
  - CORS 预检：`OPTIONS /api/v1/auth/login` + `Origin: http://tauri.localhost` → `Access-Control-Allow-Origin: http://tauri.localhost`、`Access-Control-Allow-Credentials: true`。
  - 登录冒烟：Login smoke PASS user=admin（`replace_existing: true`）。
- 状态：PASS

## 真实桌面包走查（待用户执行）

- 本 CHG 验收要求真实桌面页面走查与 M4-A 用户签收（change.md §4/§6），不能以测试或构建替代。
- 环境已就绪（上述各门），用户可在已启动的 WT Media.app 中逐条核对验收标准：封面/ID 列与占位图、详情四项（作者/平台原视频/体积/云端视频地址）、越权与不存在与未就绪素材不返回地址、下载中心两栏计数与终态行为、云端视频 URL 实际可访问性（取决于既有桶读权限，本 CHG 未改 ACL）。
- 状态：PENDING（用户签收前本 CHG 保持 ACTIVE）

## 相关提交（wt-media-cloud）

- `57654fe` Task 1、`cbfba93` Task 2、`0e78534` Task 3、`e40b5cf` Task 4
