# CHG-20261008-078：Windows Desktop 控制台与日志修复

- Status: IMPLEMENTING
- Level: L
- Milestone: `delivery/milestones/M-first-production-release.md#windows-desktop-控制台与日志修复`
- References: `docs/superpowers/specs/2026-10-08-windows-desktop-console-logging-design.md`；`docs/superpowers/plans/2026-10-08-windows-desktop-console-logging-plan.md`。
- Affected repositories: `wt-media-desktop`、`wt-media-cloud`（Cloud Web 文案）、`wt-media-workspace`。
- Current repository: `wt-media-workspace`
- 用户目标：Windows 发布版无黑色控制台，Desktop/Agent 使用一致的每用户 Windows 数据与日志目录，本机设置可跨启动保留，未配置下载目录时提示明确且不启动下载。

## 目标与范围

1. 仅在 Windows release 构建主进程声明 GUI subsystem；debug 构建保留终端。
2. Windows 生产路径统一为 `%LOCALAPPDATA%\WTMedia\Desktop\{data,logs,cache}`，Agent 默认数据目录为 `%LOCALAPPDATA%\WTMedia\Agent`；macOS 路径保持不变。
3. Desktop 日志写入、路径诊断、打开/清理和 Agent 诊断读取使用同一路径解析结果；Local AppData 缺失或不可写时只使用明确临时日志目录并在 UI 报告，不回退 cwd/安装目录。
4. Desktop 启动侧车时在 Windows 始终传 `WT_MEDIA_AGENT_DATA_DIR`；用户显式 Agent 配置优先。macOS 只在显式配置时传递。
5. 旧数据只在旧目录存在且新目录为空时复制可确认用户数据；不删除旧目录、不覆盖新目录、不迁移显式 Agent 配置。
6. Cloud Web 本机设置保存位置提示改为“请先选择下载目录”，并保留未配置时不启动本机下载的产品规则。

## Explicitly Not Doing

- 不改 Cloud Backend API、Agent 执行规则或 PyInstaller console 模式。
- 不新增用户自定义日志/数据目录入口或文件夹选择器。
- 不把 Local AppData 不可用伪装成成功。
- 不合并或处理已暂停的 CHG-20261003-077。

## 有序任务

1. 生成并评审 Desktop/Cloud Web 实施计划。
2. Desktop 建立可注入的平台路径解析，先补 Windows/macOS 和故障回退测试。
3. 接入 app_paths、logging、settings、storage、diagnostic、reveal、cleanup、upgrade 和启动初始化。
4. Windows 侧车环境变量与迁移测试，接入启动参数。
5. 验证本地设置持久化、下载未配置提示与 Cloud Web 文案。
6. 运行 Desktop Rust 测试、Cloud Web 相关测试和 Workspace 治理校验。
7. 记录各仓证据与状态；保留 Windows 实机/CI 验证缺口，不宣称人工回归通过。

## 验收

- Desktop 路径单元测试覆盖 Windows 默认目录、macOS 保留、显式 Agent 目录优先、旧数据不覆盖、Local AppData 缺失回退。
- Windows release `windows_subsystem = "windows"` 生效，debug 不受影响；CI/后续实机核对 PE subsystem。
- 侧车在 Windows 收到计算的 Agent 数据目录；诊断读写路径一致。
- Cloud Web 相关测试证明文案为“请先选择下载目录”。
- 治理校验通过；Desktop 与 Cloud Web 各自独立提交；状态文件如实记录 Windows 实机验证未完成前不得关闭。

## 7. Pending Questions

None.
