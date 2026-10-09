# desktop 状态

- Status: DONE
- Evidence: `../evidence/windows-desktop-console-logging.md`
- Notes: Commit `5deebf9` 已实现 Windows GUI subsystem、每用户 Desktop/Agent 路径、日志一致性、Sidecar 数据目录传递和旧数据保护；commit `2231944` 补齐 Windows `GetDiskFreeSpaceExW` 可用空间读取。`cargo check`、`cargo test`（527 通过 / 6 忽略）与 GUI subsystem 源码检查通过。RC16 Windows 安装包已构建、校验并解包确认主 EXE subsystem 为 `WINDOWS_GUI`；Windows 实机回归仍未完成，CHG 不闭环。

- Final: 正式版 `v0.1.0` 固定 Desktop `v0.1.0-rc.8`；Windows 安装器 CI 首装/覆盖安装/卸载通过，macOS Intel/ARM 打包通过。用户于 2026-10-09 确认 Windows GUI、路径、设置、覆盖安装保留设备身份、显式卸载清理应用数据并保留视频，以及 macOS 两架构走查。
