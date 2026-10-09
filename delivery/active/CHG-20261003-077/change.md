# CHG-20261003-077：Cloud 预发布部署与 Windows Desktop 部署问题修复

- Status: IMPLEMENTING
- Level: L
- Milestone: `delivery/milestones/M-first-production-release.md#cloud-预发布部署与数据库初始化`
- References: `docs/superpowers/specs/2026-10-02-first-production-deployment-plan.md` §5.1、§7；`docs/superpowers/specs/2026-10-04-baota-cloud-deployment-layout-design.md`；`docs/superpowers/specs/2026-10-08-windows-desktop-console-logging-design.md`；`docs/superpowers/plans/2026-10-08-windows-desktop-console-logging-plan.md`；`docs/decisions/0020-tagged-release-and-environment-config.md`；已完成 [CHG-20261003-076](../../completed/CHG-20261003-076/change.md)。
- Affected repositories: `wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`、`wt-media-workspace`。
- Current repository: `wt-media-workspace`
- 用户目标：基于 RC6 后的固定源码产出可由宝塔服务器直接拉取的 Cloud 独立部署包、可执行数据库初始化/迁移步骤，并初始化管理员。

## 目标与范围

1. Cloud Linux 部署包包含现有可执行程序、Cloud Web、FFmpeg/FFprobe、`migrations/`、从 `config_online/` 生成的包内 `config/` 模板、版本/摘要记录和服务器安装/验收脚本；本地 `config/` 不得进入制品。
2. 提供数据库准备模板：用户可先创建专用数据库和账号；部署脚本只对显式目标库执行迁移，不隐式创建生产库。
3. 提供宝塔/服务器可执行步骤：每个版本自包含私有 `config/`、`logs/`、`data/tmp/`，由单一 `current` 软链切换；执行迁移后，以宝塔 Go 项目启动 Server、宝塔进程管理器启动 Scheduler/Worker，并验证 Web、健康与登录。
4. 用新的 Cloud 组件 Tag 和产品 Tag 重新生成可部署 Cloud Artifact；客户端无变更时沿用已验证组件 Tag。
5. 记录预发布部署边界：不宣称对象存储、BitBrowser、业务发布或正式稳定版上线通过。
6. Cloud Server 提供包内 Cloud Web 静态文件与 Vue history 路由回退，使宝塔 Go 项目能统一管理域名、反向代理与 HTTPS。
7. 处置部署回归发现的 Windows Desktop 问题：发布构建不弹控制台；Windows Desktop 与 Agent 使用一致的每用户数据、日志和缓存路径；下载目录设置可跨启动保留。
8. 处置 Windows 真机下载卡在 99% 的提交错误：Agent 保留 .part 与摘要校验语义，使用 Windows 可用的文件同步方式完成重命名和 Cloud 成功回报。
9. 修复 Windows 安装与卸载生命周期：在覆盖 Sidecar 或卸载前停止并核实该安装目录下的 Agent；显式卸载选择清理应用数据时删除应用私有配置、数据、日志与缓存，用户自选下载目录及视频始终保留。

## Explicitly Not Doing

- 不把数据库密码、对象存储密钥或平台凭据写入仓库、Manifest或制品。
- 不自动 SSH 到生产服务器。
- 不使用或移动 RC6 之前的旧 Tag。
- 不把 RC 部署成功宣称为正式生产验收完成。
- 不使用 `shared/` 保存跨版本配置或日志。
- 不使用 systemd 管理 Cloud 三个常驻进程。
- 不为 Scheduler/Worker 配置虚假监听端口。
- 不修改 Agent 的 PyInstaller console 模式或下载目录拒绝规则。
- 不在 Local AppData 不可用时伪装成功或回退到安装目录/cwd。

## 有序任务

1. 裁定 Q-01 初始管理员口令策略。
2. Cloud Server 增加 Cloud Web 静态文件服务和 Vue history 路由回退，保持 API 与健康路由优先。
3. Cloud 部署脚本改为版本自包含目录，通过 `.toml.tpl` 和指定 `pre|online` 环境的远程变量表生成并校验实际配置，通过 `current` 原子切换；预发与生产复用同一制品和渲染能力。
4. 宝塔手册改为 Go 项目管理 Server、进程管理器管理 Scheduler/Worker，移除 systemd 与手工 Nginx 静态站点方案。
5. 增加 Web 路由、包结构与部署脚本测试；验证空库迁移、重复迁移和管理员初始化。
6. Workspace 固定新 Cloud 组件 Tag 与产品 Tag，重新运行 GitHub 打包工作流。
7. 输出服务器部署手册和人工验收记录模板；用户按手册在宝塔执行并回填实际结果。
8. 将 Cloud 运行路径在启动初始化阶段解析并保存一次，提供全局 getter；初始化失败直接 panic，未初始化读取不得回退到工作目录。Server、Scheduler、Worker、Migration 和配置检查入口使用同一已初始化路径。用单元测试和任意工作目录启动检查验证。
9. 服务器直接以只读 GitHub 权限拉取固定产品 Tag 的 Cloud Actions Artifact，核对包摘要后运行已有 `wtmctl`；不再要求本地下载、上传或服务器现场编译源码。
10. Windows Desktop release 主进程声明 GUI subsystem；Desktop 统一解析 `%LOCALAPPDATA%\WTMedia\Desktop\{data,logs,cache}`，Windows 侧车显式接收 Agent 默认数据目录，Windows 磁盘可用空间使用 `GetDiskFreeSpaceExW` 读取；旧数据只在旧目录存在且新目录为空时复制，不删除、不覆盖。
11. Cloud Web 本机设置下载目录提示改为“请先选择下载目录”，并配合 Desktop 验证 Windows 设置文件跨启动保留。
12. Agent 修复 Windows 下载提交时对只读文件句柄及目录执行 fsync 的不兼容路径；覆盖单流与分片提交、失败保留 .part，并在 Windows 真机复测最终文件与 Cloud 状态。
13. Desktop Windows NSIS 安装和卸载钩子停止本安装实例的 Agent，失败则中止文件覆盖/卸载；覆盖安装、显式卸载分别验证进程与文件结果。
14. Desktop 卸载器的应用数据选项清理当前及旧版应用私有配置、数据、日志和缓存；覆盖安装保留现有设置与数据；验证用户自选目录的视频及其他文件不受影响。

## 验收

- 编译和打包会双向校验 `config/` 与 `config_online/` 的归一化运行路径一一对应；缺失、多出或重复映射时失败。
- 新 Cloud Artifact 包含全部运行程序、Web、FFmpeg/FFprobe、全部 SQL Migration、部署脚本，以及仅由 `config_online/` 生成的非敏感 `config/` 模板；不包含本地 `config/` 或 `config_test/`。
- 在用户预先创建的 MySQL 空库上，包内 `bin/migrate --dir migrations --create-database=false` 能完整应用并重复执行通过。
- 初始管理员能按 Q-01 裁定结果登录；密码不明文进入制品或交付记录。
- Server、Discovery Scheduler、Discovery Worker 可按提供的进程管理模板启动，`/healthz` 与 `/api/v1/health` 通过。
- `/`、真实静态资源和 `/login` 等深层路由由 Cloud Server 正确返回 Cloud Web，未知 `/api/` 路径仍返回 API 404 而不是前端页面。
- 新版本安装后拥有独立配置、日志和临时目录；部署脚本能按显式环境拉取变量表、渲染 `.toml.tpl`、拒绝缺失/未知/残留变量，并通过 Cloud 配置校验；`current` 切换前不改变正在使用的版本。
- 宝塔 Go 项目与两个进程管理器条目使用固定 `current` 路径、`www` 用户和正确工作目录，不依赖 systemd 或虚假端口。
- 部署手册明确备份、校验、失败停止、回退和未验证业务边界。
- 服务器拉取流程固定 Run/Artifact 与 SHA-256；缺少权限、下载失败或摘要不符时停止，不进入迁移和 `current` 切换。

## Open Questions

- **Q-01（RESOLVED）**：用户于 2026-10-03 裁定保留 6 位密码下限，RC 初始管理员固定为 `admin / admin123`。该值由部署脚本写入服务器私有配置，不进入 Git。
- **Q-02（RESOLVED）**：覆盖安装沿用既有升级保留设置与数据规则；显式卸载选择“删除应用数据”时清理应用私有配置、数据、日志和缓存。
- **Q-03（RESOLVED）**：用户于 2026-10-09 明确自选目录的视频不删除；本 CHG 不清理用户下载目录。

## 部署发现的 Windows Desktop 验收补充

- Windows release 主 EXE 的 PE subsystem 为 `WINDOWS_GUI`；debug 构建保留终端输出。
- Desktop 路径测试覆盖 Windows `LOCALAPPDATA` 目标目录、macOS 原路径保留、显式 Agent 数据目录优先、旧数据不覆盖、缺失 `LOCALAPPDATA` 时日志使用明确临时目录并可见报告故障。
- Windows Desktop/Agent 文件日志与诊断读取路径一致；应用内“打开日志文件夹”定位同一目录。
- Windows 本机设置页能读取数据所在磁盘的可用空间，不再触发非 Unix 平台拒绝。
- Windows 设置文件可落盘，下载保存目录重启后保留；未配置时页面提示“请先选择下载目录”且不启动本机下载。
- Windows Agent 对已下载并通过大小、摘要校验的单流及分片文件成功提交为最终文件，并向 Cloud 报成功；提交失败时保留可恢复的 .part，不误报成功。
- Windows 实机/CI 回归证据未回填前，不得宣称本 CHG 的 Windows 部署问题闭环。
- Windows 安装与卸载需验证 Agent 已退出且 Sidecar 文件实际被覆盖/移除；卸载数据清理和视频选择需 Windows 实机验收。

## 7. Pending Questions

None.
