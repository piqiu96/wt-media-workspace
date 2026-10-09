# Windows Desktop 控制台与日志修复（待 review）

## 现象与证据

Windows 安装包启动时出现标题为 `wt-media-desktop-shell` 的黑色控制台，内容为 `desktop.startup`、`agent.supervisor` 日志，并提示 `HOME is not set ... this launch writes only stderr`。Desktop `src-tauri/src/main.rs` 没有声明 Windows GUI 子系统；发布流水线在 `windows-2022` 上构建 NSIS。Tauri Shell 2.3.5 启动子进程时已设置 `CREATE_NO_WINDOW`，因此截图指向 Desktop 主进程。Windows 生产日志、运行目录和诊断读取当前依赖 `HOME` 与 macOS `Library/...` 布局；Agent 冻结版默认会从 `Path.home()` 推导 macOS 风格目录，但只有实际运行并写入时才创建。

`Library/Application Support/WTMedia/{Desktop,Agent}` 是代码中的旧版路径拼接规则，**不是 Windows 系统自带目录，也不能据此断言用户机器上存在**。截图显示 Desktop 缺少 `HOME`，此时 Desktop 路径解析失败，通常不会创建旧版 Desktop 数据目录。Agent 可能通过 Windows 用户目录解析出旧版 Agent 目录；是否存在必须在目标机器检查。

## 用户可见目标

双击发布版 `起飞.exe` 或从安装程序启动时，只显示应用窗口，不弹黑色控制台；登录、绑定、下载功能照常工作。Desktop 与 Agent 的启动和错误日志写入每用户的 Windows 路径，应用内诊断能打开同一批日志。开发调试版保留终端输出。

## 方案比较

| 方案 | 效果 | 代价 |
| --- | --- | --- |
| 只给主程序加 Windows GUI 子系统 | 黑窗口消失 | 当前 Windows `HOME` 缺失时日志仅写 stderr，问题会变得不可见；不采用 |
| GUI 子系统 + `USERPROFILE` 代替 `HOME` | 快速恢复文件日志 | 数据与日志仍写入用户目录下的 macOS `Library` 布局，技术债继续扩大 |
| GUI 子系统 + Windows 原生目录 + 旧数据兼容迁移 | 无窗口、可诊断、路径明确 | 需要 Desktop 路径及 Agent 启动参数的配套修改；推荐 |

## 推荐设计

1. **主进程窗口**：在 Desktop `main.rs` 顶部为非 debug 的 Windows 构建设置 `windows_subsystem = "windows"`。保留 debug 构建控制台。不要给 PyInstaller 增加 `--noconsole`：Tauri Shell 已用 `CREATE_NO_WINDOW` 启动侧车，并读取其 stdout/stderr 作为启动故障诊断。
2. **统一 Windows 目录**：Desktop 启动时从系统每用户 Local AppData 路径解析一次根目录，不从 `HOME` 或当前工作目录猜测。拟使用 `%LOCALAPPDATA%\WTMedia\Desktop\{data,logs,cache}`；Agent 默认数据目录拟设为 `%LOCALAPPDATA%\WTMedia\Agent`，现有 Agent override 规则会把日志放在该目录的 `logs` 子目录、版本放在 `versions` 子目录。macOS 路径保持现状。这些是**修复后的目标位置**，不是当前安装包已创建的位置。
3. **日志写入和读取一致**：Desktop 的日志初始化、`app_paths`、存储/诊断命令共同使用上述路径解析结果。发布版优先写 `desktop.log`，开发版继续写控制台；日志目录不可写时保持进程可启动，在 UI 中显示故障和实际备用日志路径。Agent 启动时由 Desktop 传入 `WT_MEDIA_AGENT_DATA_DIR`；诊断页读取同一位置。用户显式配置的 Agent 数据目录优先。
4. **旧数据保护**：只在目标 Windows 机器上**实际发现**旧版数据目录、且新目录为空时，检查旧数据内容后复制可确认的用户数据；若旧目录不存在，直接使用新目录。不删除旧目录，不覆盖新目录。记录迁移结果和来源。旧日志保留在原位置供诊断查询，不作为新写入位置。显式配置的 Agent 数据目录不迁移、不改写。
5. **故障回退**：Local AppData 不可用时不回退到安装目录或 cwd；使用明确的临时日志目录并在应用内提示。若临时目录也不可写，仍保持现有“日志故障不阻止启动”原则，但诊断页必须明确报告日志不可用。

## 安装位置、运行数据与前置依赖

- **程序安装位置**：当前 Tauri 配置没有单独指定 Windows NSIS 安装模式。Tauri NSIS 默认按当前用户安装，默认位置为 `%LOCALAPPDATA%\起飞`；其默认模板包含“选择安装目录”页面，用户可在交互式安装时更改，例如选到 D 盘。无须先定制 NSIS 脚本，但必须用本项目实际安装包确认选择页、路径持久化、升级复用目录和卸载行为。程序位置与运行数据、日志和视频下载位置相互独立。
- **运行数据与日志**：上述 `%LOCALAPPDATA%\WTMedia\...` 是拟定的运行时路径，由程序首次需要时自动创建；安装时不要求用户填写 `HOME`、数据目录或日志目录。下载文件的保存位置由产品设置/用户选择，独立于这些内部目录。
- **最终用户依赖**：Windows Desktop 使用 WebView2 Runtime；当前安装配置未覆盖 Tauri NSIS 的默认 WebView2 下载引导方式，因此目标机器缺少 Runtime 时，安装过程需要联网取得它。Local Agent 已作为 PyInstaller sidecar 打进安装包，用户无需安装 Python。设备绑定和依赖本地浏览器的操作还需要单独安装并运行 BitBrowser；登录和 Cloud API 需要能连接线上 HTTPS 服务。
- **构建机依赖**：Rust、Node、Python、PyInstaller 及 Windows 构建工具属于 CI/开发机，不应转嫁为最终用户的手工安装步骤。

## 三种路径的指定方式

| 路径 | 当前 Windows 安装包 | 修复后的用户操作 |
| --- | --- | --- |
| 程序安装目录 | NSIS 安装器管理，应用内没有修改入口；默认模板已有安装目录选择页，实际包尚待 Windows 实机确认 | 显示默认安装位置并允许用户在交互式安装时更改；升级优先沿用已安装位置。程序运行后不提供“移动安装目录”按钮 |
| Desktop / Agent 日志 | 页面只能显示、打开、清理日志；没有自定义路径入口。Desktop 在缺少 `HOME` 时可能只向 stderr 写，关掉黑窗口后会更难诊断 | 沿用已讨论的自动路径规则：Windows 各写在每用户 Local AppData 下的 Desktop/Agent 日志目录；页面展示实际路径及“打开文件夹”。本次不增加用户自定义日志目录 |
| 视频/素材下载 | “本机设置 → 保存位置”可手动输入已存在的绝对路径；未设置时 Agent 会拒绝落盘，但当前页面的“留空由任务自行决定”提示与实际不符 | 继续由用户在本机设置中指定保存目录，不设默认下载目录；修复 Windows 设置文件落盘，并将提示改为“请先选择下载目录”。未配置时下载入口不启动本机下载，Agent 保留执行前拒绝作为兜底；更改目录只影响后续下载 |

上述下载目录设置也依赖 Desktop 的设置文件可落盘；修复 Windows `HOME` 路径故障后，才能保证用户的选择跨启动保留。视频下载没有默认目录：未配置时不启动本机下载，页面清楚提示用户先指定保存位置。本次不新增文件夹选择器，沿用现有路径输入方式。

## 验证与交付

- Desktop 单元测试覆盖 Windows 路径选择、显式 Agent 数据目录优先、旧数据迁移不覆盖、缺失 Local AppData 的故障路径；保留 macOS 路径测试。
- Agent 无需更改 PyInstaller 控制台模式；验证传入数据目录后文件日志与诊断读取路径一致。
- Windows CI 构建 NSIS 后检查主 EXE 的 PE subsystem 为 `WINDOWS_GUI`，并检查 Sidecar 构建/启动 smoke。
- 用临时 Windows 安装包做人工回归：先检查目标机器是否真的有旧版目录；分别覆盖干净用户配置与存在旧数据的情况；双击无控制台、Desktop/Agent 日志均落盘、应用内“打开日志文件夹”能定位、登录/绑定/下载正常、重复启动和卸载不损坏旧数据。另验证 WebView2 已安装与缺失两种机器状态。
- 在 Windows 上选择 `D:\WTMedia\Videos` 后重启应用，确认设置仍在、Agent 使用该目录落盘；清除选择后应显示明确的未配置提示且下载不执行。用本项目 NSIS 安装包验证默认安装位置、手动选 D 盘、升级保持所选目录、卸载和重装行为。
- 只交付测试包供回归；回归通过后按现有发布流水线创建正式版本。

## 边界

Desktop 负责主窗口、Windows 路径与侧车启动参数；Agent 保持现有 override 路径规则和未配置下载目录即拒绝的执行规则；Cloud Backend 不参与。本机设置页面的 Windows 文案由 Cloud Web 仓维护。无 Cloud API 变更；如 UI 命令载荷变化，须核对 Desktop 与 Cloud Web 的本机桥契约。实施前在 Workspace 记录跨仓范围，不并入当前 Cloud 部署 CHG。
