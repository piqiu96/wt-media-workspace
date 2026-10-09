# M-first-production-release：首次全端上线

- 状态：执行中；RC 打包、Cloud 首次预发布部署和 Windows 部署修复已通过验收，`v0.1.0` 正式版制品已发布。真实 Cloud 跨版本升级及回退待下次升级验证。
- 依据：[首次全端上线部署计划](../../docs/superpowers/specs/2026-10-02-first-production-deployment-plan.md)。

## RC 打包验证闭环

- 用户目标：仅用 GitHub 托管 Runner，从固定的四仓 Tag 生成 Cloud Linux 包和 Windows x64、macOS Intel、macOS ARM 客户端包，并发布可核对的 GitHub RC Pre-release。
- 前置：四仓源码与组件 Tag 固定；Workspace 产品 RC Tag 对应简版 Release Manifest；跨私有仓库只读访问可用；预发布 Cloud 地址或明确的不可连接测试地址已锁定。
- 用户操作：评审通过后要求执行；实施准备完成后推送产品 RC Tag。
- 系统动作：同一 `build → verify → package` 链路检查版本组合、平台、配置、Sidecar 和摘要，任何平台失败都不公开整组 Pre-release。
- 成功事实：Cloud、Agent、Desktop 目标制品及来源和摘要齐全，GitHub Pre-release 中三平台客户端附件完整，试跑报告说明烟测边界。
- 失败行为：不得从 `main` 或 `latest` 偷取源码；不得以编译成功宣称真实登录、BitBrowser、对象存储或宝塔部署通过；不得移动旧 Tag 或混用不同 RC 的包。
- 当前实施单元：[CHG-20261003-076](../completed/CHG-20261003-076/change.md)。

后续预发布环境与首次生产切换按部署计划另行实施，不由本闭环的打包通过自动宣布完成。

## Cloud 预发布部署与数据库初始化

- 验收：2026-10-09 用户确认服务器部署、数据库当前态、三进程、HTTPS/Web/登录正常；具体服务器输出未提供。2026-10-10 `v0.1.0` 正式版发布，GitHub 回读资产校验通过。真实旧版本到新版本数据库升级和回退明确延期至下次升级，不记作本次通过。

- 用户目标：把已通过 GitHub 打包闭环的 Cloud Linux 制品变成可由服务器直接拉取的独立部署包，并提供可重复执行的数据库准备、迁移、启动和验收步骤。
- 前置：RC 打包链路可用；用户能创建目标 MySQL 数据库/账号；服务器可托管 Cloud 进程并配置 HTTPS 反向代理；敏感生产配置只存在于服务器。
- 用户操作：创建数据库与专用账号，裁定初始管理员策略，在服务器以只读权限拉取固定产品 Tag 对应的 Cloud Artifact、校验摘要并执行部署包，按手册回填部署证据；无需本地下载和上传。
- 系统动作：校验固定版本与摘要，注入服务器私有配置，对显式目标库应用 Migration，启动 API Server、Discovery Scheduler、Discovery Worker，并验证健康、登录和关键表。
- 成功事实：Cloud 包、迁移、配置模板、进程模板和验收脚本齐全；空库迁移与重复迁移通过；初始管理员可登录；三个 Cloud 进程健康。
- 失败行为：不隐式创建或猜测生产库；迁移失败不得启动服务；不得把敏感凭据写入仓库或制品；不得把打包、部署或登录成功扩大为业务发布或正式稳定版上线。
- 已完成实施单元：[CHG-20261003-077](../completed/CHG-20261003-077/change.md)。

## Windows Desktop 控制台与日志修复

- 用户目标：Windows 发布版启动只显示应用窗口，不弹黑色控制台；Desktop 与 Agent 日志落在明确的每用户 Windows 目录，应用内诊断读取并打开同一批日志；下载目录选择跨启动保留。
- 前置：已批准的修复设计完成；Agent 保持现有 override 与下载目录拒绝规则；Cloud Backend API 不变更。
- 用户操作：安装测试版后双击启动，检查无控制台、登录/绑定/下载、日志路径与打开入口；在 Windows 上设置保存目录并重启验证保留。
- 系统动作：发布 Windows 主进程使用 GUI 子系统；Desktop 解析 `%LOCALAPPDATA%\WTMedia\Desktop\{data,logs,cache}`；侧车传入 `%LOCALAPPDATA%\WTMedia\Agent`；旧数据仅在旧目录存在且新目录为空时复制，不删除或覆盖。
- 成功事实：Windows CI 主 EXE subsystem 为 `WINDOWS_GUI`；Desktop/Agent 文件日志与诊断路径一致；干净与旧数据场景路径测试通过；Windows 设置文件跨启动保留。
- 失败行为：不从 `HOME`、cwd 或安装目录猜测 Windows 运行根；启动迁移时不删除旧数据；不用虚假默认下载目录；日志故障不静默吞掉。
- Windows 下载回归补充：Agent 在分片合并及大小、摘要校验后，必须在 Windows 上提交最终文件并向 Cloud 报成功；提交失败时保留可恢复的 `.part`，不误报成功。
- 已完成实施单元：[CHG-20261003-077](../completed/CHG-20261003-077/change.md)。

## Windows 卸载与覆盖安装生命周期

- 用户目标：卸载和覆盖安装时不留下仍在运行的已安装 Agent；卸载时能清理应用自有的历史数据与日志；用户自选目录的视频始终保留。
- 前置：明确安装目录、每用户数据目录和用户自选下载目录的归属；旧版启动迁移仍只复制数据，不在启动时删除。
- 用户操作：运行 Windows 安装器或卸载器；显式卸载时选择“删除应用数据”以清理配置、数据、日志和缓存。
- 系统动作：安装器覆盖文件前、卸载器删除文件前停止该安装目录下的 Agent 并确认退出；卸载器删除 Sidecar；选择清理应用数据时处理 `%LOCALAPPDATA%\WTMedia\Desktop` 与 `%LOCALAPPDATA%\WTMedia\Agent` 以及确认归属的旧版数据、日志和缓存目录；用户自选下载目录不参与清理。
- 成功事实：安装和卸载均无遗留的该安装实例 Agent 进程或锁定的 Sidecar 文件；显式卸载选中应用数据清理后约定的应用私有目录已清理；覆盖安装保留现有设置与数据；下载视频和目录中其他文件均保留。
- 失败行为：停止 Agent 失败时不得继续删除或覆盖 Sidecar 并宣称成功；不得对任意同名 Agent 进程或整个用户自选目录无差别删除；不得将正常覆盖安装当作无提示的清空数据。
- 已完成实施单元：[CHG-20261003-077](../completed/CHG-20261003-077/change.md)。
