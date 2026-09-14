# M2-E macOS ZIP 交付验证（2026-09-13）

## 交付物

- 构建命令：`cd wt-media-desktop && bash scripts/package-release-macos.sh --output-dir /Users/aqiuye/Develop/workspace/wt-media/output`。
- 输出目录：`/Users/aqiuye/Develop/workspace/wt-media/output/WT-Media_0.1.0_macos-aarch64/`。
- ZIP：`WT-Media_0.1.0_macos-aarch64.zip`，29 MB。
- ZIP SHA-256 文件：`WT-Media_0.1.0_macos-aarch64.zip.sha256`。
- 目录包含 ad-hoc 签名的 `WT Media.app`、DMG、最终 Sidecar 清单、冻结阶段清单、DMG/清单校验和及安装说明。

## 验证

- `unzip -t`：通过。
- 输出目录内 `WT Media.app` 的 `codesign --verify --deep --strict --verbose=2`：通过。
- ZIP SHA-256 与 DMG/最终 Sidecar 清单 SHA-256：通过。
- 最终 Sidecar：Agent `0.2.2`，目标 `aarch64-apple-darwin`，包内运行时文件 `Contents/MacOS/wt-media-agent` 的 SHA-256 与 `sidecar-manifest.json` 一致：通过。
- `bash tests/package-release-macos.test.sh`：通过。
- `cargo test`：11/11 通过。

## 发布边界

- 此包为 macOS Apple Silicon 原生包；Windows x64 仍只能在 Windows 原生机器生成。
- 未提供 Apple 公证凭据，产物使用 ad-hoc 签名；这不绕过 Gatekeeper，首次未知开发者放行仍依系统流程进行。
