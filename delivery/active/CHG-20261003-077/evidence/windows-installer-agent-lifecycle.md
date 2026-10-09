# Windows NSIS Agent 生命周期：本地验证

- 目标：Windows 覆盖安装和卸载在处理 Sidecar 文件前停止当前安装目录的 Agent，并避免误停其他目录的同名进程。
- 实现位置：Desktop `src-tauri/windows/installer-hooks.nsh`、`stop-installed-agent.ps1`、`tauri.conf.json`；Workspace `release.yml` Windows 作业执行 `tests/windows_installer_agent_stop.ps1`。
- 静态来源：Tauri v2.11.4 NSIS 模板在文件复制前调用 `NSIS_HOOK_PREINSTALL`，删除前调用 `NSIS_HOOK_PREUNINSTALL`，在原生数据复选框处理后调用 `NSIS_HOOK_POSTUNINSTALL`。原生检查只检查主程序名，未检查 Agent。
- 本地命令：`makensis -V2 /tmp/wt-media-installer-hook-probe.nsi`（探针引用真实 hook，分别展开安装、卸载宏并生成 uninstaller）退出码 0；仅报告探针变量未赋值的两条警告。`cargo check --all-targets --message-format=short` 退出码 0，Desktop 既有 dead-code warning。`python3 scripts/verify_delivery_governance.py` 通过。
- Desktop commits：`9f11d27` 添加路径限定停止与 NSIS hook，`d705451` 补充进程消失竞争处理、Sidecar 删除后核验及 Windows 安装/重装/卸载回归脚本。组件 Tag `v0.1.0-rc.7` 已推送并回读指向 `d7054519a0b60a858165398bb2d65c29522ec919`。
- 用户范围裁定：2026-10-09 明确用户自选目录的视频一律不删除。卸载器仅在“删除应用数据”选项选中时清理确认归属的 WTMedia 目录；覆盖安装保留设置与数据。
- 尚未验证：Windows PowerShell 进程路径筛选、安装包真实执行、Sidecar 文件覆盖/删除、原生数据复选框与本项目目录清理，均需 Windows 发布作业及真机复测。此记录不声明运行时验收通过。
