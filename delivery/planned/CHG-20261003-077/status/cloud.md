# Cloud status

- Current component: `v0.1.0-rc.12` → `be1d1a1`; prior tags remain immutable.
- Path resolution: Server/Worker/Scheduler resolve the release root from `WT_MEDIA_CLOUD_HOME`, then the running binary's `<home>/bin/<binary>`, then the working directory, and every derived path is absolute. `config`/`logs`/`web` default to `<home>/...` and can be overridden with `WT_MEDIA_CLOUD_CONFIG_PATH`, `WT_MEDIA_CLOUD_LOG_PATH`, `WT_MEDIA_CLOUD_WEB_PATH`. BaoTa's generated `server.sh` (`cd <home>/bin`) therefore starts cleanly.
- Binary name: the HTTP entrypoint ships as `bin/wt-media-cloud` (source directory stays `cmd/server`); packaging, package checks, and `wtmctl` process checks were updated.
- Auth logging: every login attempt and authentication rejection logs a stable reason (`invalid_credentials`, `session_replace_needed`, `session_invalid`, `missing_credential`, `forbidden`, `internal_error`) with IP, Origin, and path; passwords and session tokens are never logged. Logs go through Hertz's global logger so they land in `app.log` and are safe before logger initialization.
- wtmctl: `release`/`package_root` are derived from the extracted package's `release-info.json` (installed-release commands fall back to `current`), so the profile no longer pins a version.
- Verification: full `go test ./...`, `go vet`, packaging tests, and `git diff --check` pass; Cloud CI `37198945138` succeeded; a local `wtmctl` fixture verified `artifact verify`/`doctor`/`deploy plan` with a profile that omits `release` and `package_root`.
- Remaining: real BaoTa installation and server acceptance. RC13 historical Cloud tar SHA-256 `25efe2ae2ee97256715690e44f186bccc7e90e3abbb5f400be3e3a357d80214b` and RC14 candidate SHA-256 `e7ea73b3984c4735d3e61db1a008ff1e8ea0c48966cf50cc39b0323485d9ac4e` have been read back.

## Task 10 commit `620cf89` (not tagged)

- `WT_MEDIA_CLOUD_HOME` must be absolute when set. Released binaries derive the root from their own `bin/` directory even when `config/app.toml` is missing; local development falls back to cwd.
- Config, logs, Web, and default Migration paths derive from one resolved root. Relative `WT_MEDIA_CLOUD_{CONFIG,LOG,WEB}_PATH` overrides are relative to that root, not cwd.
- Startup records the resolved paths before loading config. Resource initialization failure records the failing step and error; the app logger records its effective path once ready. Early failures go to the process manager's stderr log.
- Verification: path/bootstrap tests observed RED then GREEN; `go test ./... -count=1`, target `go vet`, package tests, and a released-binary missing-config smoke check passed. Evidence: `evidence/cloud-runtime-paths-and-startup-logs.md`.

## Task 11 commit `be1d1a1`（Cloud `v0.1.0-rc.12`）

- Cloud 路径在进程启动时解析并保存一次，`config.GetRuntimePaths()` 是运行时唯一读取入口；未初始化读取和根路径解析失败均 panic。初始化后环境变量变化不会改变路径。
- Server、Worker、Scheduler 的 Bootstrap、Migration 与配置检查入口使用已保存路径；直接调用 `config.Initialize()` 也先初始化路径。
- 完整 Go 测试、目标 `go vet`、任意 cwd 启动与非法根路径 panic 检查通过。证据：`evidence/cloud-runtime-path-initialization.md`。已 Tag，尚未执行宝塔服务器验收。

## 2026-10-07 本机打包启动演练

- 基于 commit `be1d1a1` 组装 macOS arm64 本机演练包，从 `/Users/aqiuye` 启动；根路径仍锚定包内，配置检查、健康接口、Web 深层路由、日志及退出清理通过。
- 本次不构成 Linux 发布制品或宝塔服务器验收。证据：`evidence/cloud-local-package-start-from-home.md`。

## Task 12 Cloud 组件 Tag

- `codex/cloud-runtime-paths-logs` 已推送 GitHub，远端 HEAD 为 `be1d1a11a603da475b4d6ce16244927adc8d8486`。
- `v0.1.0-rc.12` 已提交 GitHub，远端 peeled Tag 指向同一 Commit；本地完整 Go 测试、目标 `go vet` 与打包脚本测试通过。产品 RC14 工作流已构建 Linux Artifact 并完成摘要核对，详见 `evidence/rc14-manual-tag-and-build.md`。
