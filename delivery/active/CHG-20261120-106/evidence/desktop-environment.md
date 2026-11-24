# Desktop 环境身份与数据隔离验证

日期：2026-11-24。范围：用户确认的 Desktop dev/test/prod 身份、标记、本地隔离与正式发布门禁。沿用 CHG106，不关闭 CHG 或 M6，不合并发布。

## 修改范围

- Desktop：编译期固定 environment，独立于 Cloud 目标与资源文件声明；release 支持 test/prod，正式 stable 门禁只接受 release+prod。release 包仍禁止系统 Python 回退。
- Desktop：DEV/TEST 原生图标、应用名称、窗口标题、bundle identifier、主程序名称、单实例身份、默认本地端口；统一设置、升级记录、缓存、日志、导出和清理的系统命名空间。正式目录兼容原位置。
- Desktop 显式向 Agent 传入当前环境的数据根和日志文件。自定义 Agent 数据根对 dev/test 追加环境层。Windows 卸载只清理当前身份的管理目录；选择延后到宏展开，适应 Tauri 在 PRODUCTNAME 定义前加载 hooks 的顺序。
- Cloud 仓仅修改共用 Vue 品牌组件和 Desktop 入口：读取原生 environment 后挂载，登录页和收起侧栏保留 DEV/TEST；Web 与正式端原样。配置读取失败显示重新启动／安装提示。
- Workspace：正式流水线固定 prod/stable，新增持续集成回归，回写架构、端口与本记录。Agent 源码和 Cloud 后端未修改。

## 实际验证

| 检查 | 本次结果 |
| --- | --- |
| Desktop `bash scripts/test.sh` | Rust 558 通过、0 失败、6 项既有忽略；控制脚本 12 项、release-versions 20 项及其他既有 shell 套件通过 |
| `python3 scripts/test-desktop-environment.py -v` | 4 项通过；覆盖三身份资源覆盖层／Cloud prod 保留、release dev 拒绝、正式入口门禁与真实 NSIS 编译 |
| Cloud 受影响前端 6 文件 | 65 项通过，含品牌、桌面角色入口、本地 Agent 边界、设置与草稿 |
| Workspace unittest discovery | 212 项通过，包含 build-desktop 作业 prod/stable 和无 debug 构建断言 |
| Desktop 前端生产构建 | 通过，已同步生成资源 |
| macOS 开发／测试／正式 .app | 三种均成功本地构建，分别核对 Info.plist、打包 TOML、icns 摘要；测试包还使用最终前端重新构建 |
| stable+test 反向编译 | 实际 `cargo build --release` 被拒绝：stable channel requires release + prod |
| Agent 真实组件与 SQLite | 仅临时根、无网络／后台执行循环；dev/test/prod 均配置 cloud_env=prod、同一用户9，构造三个组件图、三个 SQLite、分别写入／读回草稿标记，互不串用 |
| 文档、Delivery、产品计划对齐 | 通过 |
| 独立只读代码复核 | 无确认的阻断问题，收尾复核包括正式门禁、NSIS 展开时机与前端失败提示 |

新增回归先暴露旧身份／目录问题再修复；NSIS 夹具也先在旧顶层 PRODUCTNAME 判断处编译失败，修复后真实编译通过。NSIS 测试只在临时目录生成夹具安装器，不执行。其编译器缺失时明确 skip，不冒充通过。

macOS 包核对：dev 为“起飞 Dev”／com.wtmedia.desktop.dev，test 为“起飞 Test”／com.wtmedia.desktop.test，prod 保持“起飞”／com.wtmedia.desktop。dev/test 包内 cloud_env=prod 时 environment 仍分别为 dev/test，图标与对应源文件摘要一致。测试安装包是 release 编译。

## 验证边界

- 本轮未执行 Windows 真实安装、升级和卸载；真实 NSIS 编译及路径解析测试不能代替安装器实机验收。
- 本轮未启动三个应用并行登录，未实际验证 macOS 开发窗口 WebView 存储行为、Dock/Finder 图标刷新或同机长期并行运行；应用标识和各管理目录已在代码、包与解析测试中核对。
- 包采用本地临时签名，未公证，不等于正式签名发布；未执行 GitHub 线上发布流水线。
- 没有迁移或清理旧开发数据、正式设置／SQLite、用户下载目录，没有触发真实发布。Cloud 环境仅在配置和组件组装中验证，未声称完成线上登录或连接验收。
- 相同线上 Cloud 的远程业务数据仍按线上用户与权限访问，本次隔离的是本机进程状态和管理数据。

原始构建日志、临时数据库、测试夹具和图片过程产物不提交；仓库保留代码、测试、正式图标和本摘要。


## 开发包实机故障补充（2026-11-24）

前述三种包的名称／图标／外层签名验证没有覆盖 Agent 实际启动，不能据此证明包内 Agent 可用。用户实际使用暴露出两处问题，本节补充并更正验证范围：

1. 新环境打包入口未执行既有 `repair-macos-signing.sh` 收尾。Tauri 签名改写 Agent 后，包内仍为构建前 SHA，原生完整性检查按设计拒绝启动。修复为 app 构建→既有签名修复→写最终运行记录→外层封签→检查 Agent SHA→生成全新临时 DMG→校验后替换最终输出。实际镜像占用问题也改为新路径校验后原子替换，不覆盖挂载中的镜像文件。
2. 冻结 Agent 即使完整性通过，启动仍约35秒。只读进程采样确认阻塞于 HTTPServer 构造期间的 `socket_gethostbyaddr→mdns_hostbyaddr`。Agent 本机 HTTP server 直接使用绑定的数字地址作为 server_name，取消反向 DNS，保持线程、退出、API 和运行令牌校验。

新增两个签名收尾回归、一个 Cargo 输出布局回归，以及 Agent 服务启动不依赖 DNS 的回归。先确认失败原因再修复：Agent 相关77项、Desktop打包7项和既有release-versions 20项通过。显式目标／自定义 Cargo 输出目录的审查问题已修复；构建输出目录来自 cargo metadata，目标架构跟随 --target/CARGO_BUILD_TARGET。

最新源码已重新冻结 Agent、构建前端和开发 app／DMG，安装盘校验、签名、Agent最终 SHA 与运行记录一致。包内 Agent 以临时数据根、独立端口和内存运行令牌实测：4.69秒内启动（小于15秒时限），healthz和api/v1/status均HTTP200，测试后正常关闭，不执行任务循环。

用户在最终开发版实际登录后：127.0.0.1:18765监听，Desktop记录“Agent校验通过”“Local Agent已就绪”“健康检查成功”；原生窗口工作环境状态实际显示“这台电脑可以工作”“本机服务已连接，当前无任务”，执行凭证已配置。本轮只核对状态，不启动业务任务。开发版已恢复并保持运行，正式版进程保留。

本次补充开始涉及 Agent 的本机服务启动代码；此前“Agent源码未修改”只描述上一轮隔离实现，不能作为当前累计修改结论。Cloud后端仍未修改。已交付镜像替换为修正包，先前直接由新入口生成的未收尾预览包需重新构建。正式macOS发布入口原已包含签名收尾，门禁不变。
