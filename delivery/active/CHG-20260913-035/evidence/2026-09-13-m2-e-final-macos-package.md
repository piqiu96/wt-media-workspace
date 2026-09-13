# M2-E 最终 macOS 包验证（2026-09-13）

## 清理与构建

- 清理范围：`wt-media-cloud/web/dist-cloud`、`wt-media-cloud/web/dist-desktop`、`wt-media-desktop/.generated`、Desktop `target` 与生成的 Sidecar；未触碰源码和 Agent 用户数据目录。
- 构建环境：macOS ARM64，Python 3.12.13 临时发布环境，PyInstaller 6.22.3，Desktop 版本 0.1.0，Local Agent 版本 0.2.2。
- 发布包：`wt-media-desktop/target/release/bundle/dmg/WT Media_0.1.0_aarch64.dmg`。
- DMG SHA-256：`f3f46632fee9cb65e9c17841cc307d906deff2aac220fbe1e85ecb928dc20d78`；大小 15119485 bytes。
- Sidecar SHA-256：`8e631fac6b6cae2142305fa9113fd4113e6d09c81ea0db1a961c125ec84ce7ab`；目标 `aarch64-apple-darwin`。

## 验证结果

- 发布脚本 `bash scripts/build-release-macos.sh`：通过。
- App `codesign --verify --deep --strict`：通过；外层 App 使用 ad-hoc hardened runtime，Sidecar 使用普通 ad-hoc 签名。
- 最终 DMG 只读挂载：通过。
- 直接运行 DMG 内 Sidecar：`GET http://127.0.0.1:8765/healthz` 返回 `{"status":"ok","service":"wt-media-agent","mode":"m1"}`：通过。
- 直接启动 DMG 内 `WT Media.app` 后，同一健康接口返回成功，且进程路径为 `/Volumes/WT Media 1/WT Media.app/Contents/MacOS/wt-media-agent`：通过。
- Cloud `GET /api/v1/health`：通过；BitBrowser `127.0.0.1:54345`：可达。

## 根因与修复

PyInstaller onefile 内嵌的 `libpython` 与 Tauri 默认给 Sidecar 的 hardened runtime 签名在 macOS 26 上发生 Team ID/库校验冲突。发布流程现改为先构建 App，再将 Sidecar 重签为普通 ad-hoc，最后只重签外层 App 并手工制作 DMG。

## 未完成目标

当前 macOS 没有 Windows x64 原生/交叉安装器工具链（Windows linker、NSIS、WiX、MinGW、zig、cargo-xwin），因此没有生成伪造的 Windows 包。Windows x64 需在 Windows 原生机器构建和安装验收。
