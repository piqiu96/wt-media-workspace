# Windows NSIS Agent 生命周期：本地验证

- 目标：Windows 覆盖安装和卸载在处理 Sidecar 文件前停止当前安装目录的 Agent，并避免误停其他目录的同名进程。
- 实现位置：Desktop `src-tauri/windows/installer-hooks.nsh`、`stop-installed-agent.ps1`、`tauri.conf.json`；Workspace `release.yml` Windows 作业执行 `tests/windows_installer_agent_stop.ps1`。
- 静态来源：Tauri v2.11.4 NSIS 模板在文件复制前调用 `NSIS_HOOK_PREINSTALL`，删除前调用 `NSIS_HOOK_PREUNINSTALL`，在原生数据复选框处理后调用 `NSIS_HOOK_POSTUNINSTALL`。原生检查只检查主程序名，未检查 Agent。
- 本地命令：`makensis -V2 /tmp/wt-media-installer-hook-probe.nsi`（探针引用真实 hook，分别展开安装、卸载宏并生成 uninstaller）退出码 0；仅报告探针变量未赋值的两条警告。`cargo check --all-targets --message-format=short` 退出码 0，Desktop 既有 dead-code warning。`python3 scripts/verify_delivery_governance.py` 通过。
- Desktop commits：`9f11d27` 添加路径限定停止与 NSIS hook，`d705451` 补充进程消失竞争处理、Sidecar 删除后核验及 Windows 安装/重装/卸载回归脚本。组件 Tag `v0.1.0-rc.7` 已推送并回读指向 `d7054519a0b60a858165398bb2d65c29522ec919`。
- 用户范围裁定：2026-10-09 明确用户自选目录的视频一律不删除。卸载器仅在“删除应用数据”选项选中时清理确认归属的 WTMedia 目录；覆盖安装保留设置与数据。
- 尚未验证：Windows PowerShell 进程路径筛选、安装包真实执行、Sidecar 文件覆盖/删除、原生数据复选框与本项目目录清理，均需 Windows 发布作业及真机复测。此记录不声明运行时验收通过。
- 真机卸载验收入口：先记下一个用户下载视频的绝对路径，卸载时勾选“删除应用数据”，然后在 Workspace 运行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/verify/windows_uninstall.ps1 -InstallDir '<安装目录>' -VideoPath '<视频绝对路径>'`。脚本只读，检查本安装路径的 Agent 进程与 EXE、当前/旧版应用目录均不存在，视频仍可读；不提供视频路径时跳过视频断言。

## RC18 构建失败与修正

- [`release.yml` Run 37880952823](https://github.com/piqiu96/wt-media-workspace/actions/runs/37880952823)：validate、Cloud、三平台 Agent、两平台 macOS Desktop 成功；Windows Desktop 作业失败，package 和 publish 未执行，RC18 没有可用 Release 资产。
- Windows 作业的 `windows_installer_agent_stop.ps1` 已通过，`cargo tauri build --bundles nsis` 已生成 14.31 MiB 的 NSIS 安装包。失败在随后执行的 `windows_installer_roundtrip.ps1`，首装检查报告 `First install did not place the Agent executable`。
- 烟测原脚本把产品名 `起飞` 写为无 BOM 的 UTF-8 PowerShell 5.1 源码字面量，再用它拼接默认安装目录。Windows PowerShell 5.1 的源码解码可能导致错误路径；本次日志未记录实际安装目录，不能据此认定安装器未复制 Sidecar。修正为从安装器文件名解析产品名，并在首装后读取 `HKCU` 卸载注册表的 `InstallLocation`，打印实际目录与缺失文件路径。脚本现为纯 ASCII，规避此类编码歧义。
- Desktop 修正 commit `dcf3144f39e78bde2a75fbfc2956ecf2e6573bc2` 已推送，组件 Tag `v0.1.0-rc.8` 已推送并回读。Workspace 下一个产品候选为 RC19；须由新的 Windows 作业确认实际首装、重装和卸载结果。
