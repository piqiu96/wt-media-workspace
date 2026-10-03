# WT Media 首次全端上线部署计划（待评审）

- 日期：2026-10-02
- 状态：`DRAFT_FOR_REVIEW`；本文件是评审稿，不授权实施、发布或连接生产环境。
- 目标：拆成两个连续交付阶段。**阶段一**通过 GitHub Actions 从产品 Tag 构建 Cloud、Agent、Desktop 并完成首次上线；**阶段二**在这条已运行的 GitHub 发布链上建设可持续交付体系。两阶段都按 Tag 锁定源码；Windows x64、macOS Intel、macOS Apple Silicon 的原生构建、打包及制品 smoke 全部由 GitHub 对应平台 Runner 完成，不依赖用户持有任何目标平台电脑。
- 当前优先顺序：先评审并在用户另行触发后执行[首次 GitHub 打包试跑计划](2026-10-03-github-packaging-trial-plan.md)，由人推送产品 RC Tag，验证四仓 Tag 到完整 GitHub 制品/Pre-release 的链路；取得试跑报告后再继续本文件的预发布部署与首次上线。
- 已定部署路线：Cloud 使用 Linux amd64 发布包，由人工上传宝塔；宝塔提供反向代理、HTTPS 和部署期间的维护提示，服务进程由受控进程管理器托管。本轮不设计自动 SSH 部署、Docker Compose 或 Kubernetes。
- 输入：用户提供的《WT Media 构建、打包与发布工程重构执行任务》作为目标约束；后续补充裁定为 Tag 驱动发布、FFmpeg/FFprobe 仅放 Cloud `bin/`、本轮不设 `.build/`、本轮无 macOS 签名证书。补充裁定优先于附件中的示例目录和组件分工；实际入口和阻塞项以本次仓库检查为准。

## 1. 上线边界与成功定义

首次上线要求 **Cloud、Agent、Desktop 三者在同一发布窗口都可用**：Cloud 能提供 Web/API 和后台进程，Agent 能由 Desktop 启动并响应本地健康检查，Desktop 能打开、连接 Cloud 并调用匹配版本的 Agent。三者任一不可用，首次上线不算完成。这不等于把尚未完成的 M4～M10 规划功能宣布完成；发布清单必须列出本次实际交付且验收通过的功能。当前交付快照仍记录 `CHG-20261001-072` 为 `IMPLEMENTING`，发布冻结前必须与 `delivery/LEDGER.md`、代码和验收记录重新对账。

同一产品发布至少包含：

1. 可在目标 Linux amd64 主机安装的 Cloud 包，含当前确实独立运行的 API Server、Discovery Scheduler、Discovery Worker、Migration、Cloud Web、版本和校验信息；未来 Compose Worker 只在其功能进入本次发布范围且真实存在时加入。
2. 对应平台原生构建的 Local Agent 和 Desktop 安装包。Agent 作为 Desktop Sidecar 交付；若另发 Agent 制品，必须与安装包内版本和摘要一致。
3. 阶段一先在 `releases/manifests/<产品Tag>.yaml` 保存**简版 Release Manifest（版本锁定记录）**，列出产品 Tag、Cloud/Agent/Desktop 各仓 Tag、Desktop Web 来源、目标环境和非敏感服务地址；构建完成后将解析出的 Commit、制品摘要与目标平台附在 GitHub Release 发布记录中。阶段二在同一位置扩展为逐次不可变、可自动校验的正式 Release Manifest；Tag 后生成的摘要继续放在发布结果中，不回写已打的 Tag。
4. 阶段一已有 Workspace 产品 Tag 触发的 GitHub 发布工作流：自动完成 Cloud Linux 和三平台 Agent/Desktop 构建、Agent 启动 smoke、Desktop 与 Agent 的版本/启动链验证、制品汇总；RC 生成 Pre-release，正式 Tag 生成 Draft Release。Cloud 在预发布环境完成配置、迁移、备份恢复与回滚演练，正式环境完成关服切换、三者可用性检查、观察和签收。阶段二再统一各仓构建接口、扩展 Manifest 校验与发布门禁。

**发布结论只依据实际验证证据。** 三平台客户端以 GitHub Actions 对应平台 Runner 的真实构建、Agent 启动/健康 smoke、安装包结构及 Desktop 启动 Agent 的验证为门禁；Cloud 以预发布环境的进程、配置、迁移及恢复演练为门禁。正式恢复服务前还要核对 Cloud 与本次 Desktop/Agent 的接口兼容和登录等核心链路。不要求额外准备本地真机。

## 2. 2026-10-02 现状盘点

| 范围 | 已有事实 | 首次上线缺口 |
| --- | --- | --- |
| Cloud | `cmd/server`、`cmd/discovery-scheduler`、`cmd/discovery-worker`、`cmd/migrate` 已存在；`web/package.json` 有 `build:cloud` 和 `build:desktop`；CI 使用 MySQL 8.4 跑测试与迁移。 | `scripts/build.sh` 只构建 Server 和默认 Web；`bin/control.sh` 启动时现场编译且只管理 Server；无 Linux 发布包、独立进程验证、Cloud `bin/ffmpeg`/`bin/ffprobe` 和生产运行清单。仓库还有旧 `Dockerfile`，不能当作本次宝塔部署证据。 |
| Agent | 有 Python 依赖锁与原生 PyInstaller Sidecar 构建脚本；已能为当前平台生成带摘要的 Sidecar。 | 普通 `scripts/build.sh` 只执行 `uv build`；Sidecar 构建为 `--onefile`，与附件期望的 `onedir` 不一致；尚无 Windows x64、macOS Intel、macOS ARM 三平台正式制品矩阵和统一 smoke/package 入口。切换打包形态须先验证 Tauri `externalBin` 和配置路径。 |
| Desktop | macOS 发布脚本可构建、校验 DMG 和内嵌 Sidecar；Tauri 指向 `.generated/frontend`。 | `beforeBuildCommand` 直接读取相邻 Cloud/Agent 工作树；没有消费明确制品的 `prepare` 入口；生产配置中的 Cloud 地址及 CSP 仍指向本地地址；Windows 和 macOS Intel 尚无正式 GitHub Release Matrix 制品。本轮没有 macOS 签名证书。 |
| Workspace | 有跨仓映射、历史 `config/release-matrix.yaml` 和前端联合构建脚本。 | 没有产品级 Release Manifest、联合构建工作流与发布校验；现有矩阵含历史 Cloud Agent 字段，不能充当新版本组合的批准记录。 |
| 配置与数据 | Cloud 运行时从 `./config` 读取，`config_online` 用作发布替换；Migration 按版本记录，重复执行会跳过已应用文件。 | 生产配置、域名、MySQL、对象存储、凭据、备份位置尚未形成已核验清单。Cloud 配置说明明确记录过已入库的外部平台凭据需要在发布前轮换；部分迁移包含不能靠应用回退逆转的 DDL。 |
| CI | Cloud、Agent、Desktop 各有基础 GitHub Actions。 | 现有 CI 不是可发布制品流水线；缺少产品 Tag 驱动的跨仓版本组合、目标平台构建、制品摘要、Runner 上的制品验证和统一发布门禁。 |

本盘点仅依据当前文件与脚本的静态检查；没有运行构建、连接线上环境或验证目标服务器。三个运行仓和 Workspace 均有其他未提交改动，发布候选必须等相关工作合并后给各仓创建发布 Tag，不取当前工作区快照。

## 3. 目标构建与运行边界

```text
阶段一：三仓组件 Tag + Workspace 产品 Tag/锁定记录
      → GitHub Actions 联合构建 Cloud 与三平台客户端、smoke、汇总制品
      → GitHub RC Pre-release / 正式 Draft Release
      → 宝塔关服部署 Cloud → 放出同产品 Tag 的客户端 Release

阶段二：产品 Tag + 正式 Manifest → 加固已有 build/verify/package
      → 扩展已有 Workspace Release DAG/自动门禁 → 可重复的后续发布
```

Cloud 当前独立进程是 Server、Discovery Scheduler、Discovery Worker；Migration 是一次性命令，不是常驻服务。未实现的 Compose 进程不为满足目录示例而虚构，不设 Cloud Agent 发布链。FFmpeg/FFprobe 只由 Cloud 安装和使用，两个可执行文件放进 Cloud `bin/` 并随 Linux 包交付；Agent 制品与 Desktop 安装包不携带、不校验 FFmpeg/FFprobe。静态检查已发现 Agent `runtime/environment.py` 检查本机 `ffmpeg`，`runtime-environment.yaml` 将其列为必填，Desktop `preflight.rs` 和 Agent DTO 也消费此状态。实施时必须同步调整状态协议、Desktop 展示和对应测试，避免客户端继续因本机未装 FFmpeg 报错；如有实际媒体调用仍落在客户端，先把调用迁到 Cloud。

构建产物与正式制品分离，两阶段都不设 `.build/`。阶段一 Cloud 编译出的 Go 可执行文件与 FFmpeg/FFprobe 放在 Cloud `bin/`；Agent 可复用已验证的 `onefile` 输出。阶段二将 Agent 的 PyInstaller `onedir` 结果放在 Agent `bin/local-agent/`；Web 使用自身构建输出，Desktop 保留 `.generated/` 联合输入和 Tauri `target/` 编译输出。各仓 `output/` 只放正式交付包。`bin/` 同时有受 Git 管理的构建脚本和不提交 Git 的生成文件，须按具体生成路径配置忽略与 `clean`，打包时只复制明确列出的可执行文件，不能把整个 `bin/` 连同脚本打进运行包。阶段二的 Makefile 或等效命令只做薄入口，实际步骤由一个确定的脚本实现，不保留两套会漂移的发布路径。

### 3.1 阶段二完成后的命令契约

| 仓库 | 正式入口 | 产物边界 |
| --- | --- | --- |
| Cloud | 按实际能力提供 `make bootstrap`、`make dev`、`make test`、`make lint`、`make generate`、`make build`、`make verify`、`make package`、`make clean`；生命周期命令由 `bin/control.sh` 承接；`bin/migrate.sh` 与包内 Migration 使用同一配置约定。 | `build` 将实际 Go 可执行文件放入 `bin/`，两种 Web 留在各自构建输出；FFmpeg/FFprobe 放入 `bin/`；`verify` 运行二进制和 Web 制品 smoke；`package` **只消费**已验证结果，写入 `output/cloud/`。开发模式直接运行源码。 |
| Agent | Windows CI 也可直接调用 `python bin/build.py`、`python bin/verify.py`、`python bin/package.py`；Makefile 仅作本地快捷入口。 | 原生平台 PyInstaller `onedir` 结果放 `bin/local-agent/`，正式 Agent 包放 `output/`；PyInstaller Spec/Hook 等静态配置可在 `packaging/`，编译缓存使用临时目录并可清理。Agent 包不含 FFmpeg/FFprobe；正式 Sidecar 生命周期只由 Desktop 管理。 |
| Desktop | `python bin/prepare.py --frontend <artifact> --agent <artifact> --target <target>`，再分别执行 build、verify、package；准确参数以实施后的 CLI 帮助为准。 | `prepare` 只消费明确制品并填充 `.generated/`；Tauri 编译仍在 `target/`；最终安装包写入 `output/`。正式构建不触发跨仓 checkout 或临时 Agent 构建。 |
| Workspace | Manifest 校验、当前平台 dry-run 和联合 Release 命令由 `bin/` 提供；GitHub Actions 使用同一入口。 | `releases/manifests/` 保存逐次不可变的版本组合；`output/` 只放本地联合构建结果，不成为运行时依赖。 |

阶段一只补齐首次交付必需的构建、smoke、打包入口，允许复用现有 `scripts/`，但不容许在服务器现场编译或靠开发机生成跨平台安装包。阶段二才按上表统一命令和目录：先建立新入口和等价验证，再逐个将调用者切到新入口，真实构建通过后清理重复路径。目录整理不顺带修改业务 API、任务状态或执行器行为。

## 4. 两阶段任务与验收

### 4.1 阶段一：完成最基础的首次交付

阶段一的目标是让 **Cloud、Agent、Desktop 在首次生产环境真实可用**，并能从固定 Tag 通过 GitHub 重新生成整组制品。保留已有可用构建脚本，做首次上线必需的修复和最小 Workspace 联合发布工作流；全仓脚本重构与完整 Manifest schema 留给阶段二。

| 顺序 | 必做工作 | 阶段一结束证据 |
| --- | --- | --- |
| 1. 冻结首版范围和环境 | 核实宝塔/Linux、域名/TLS、MySQL、对象存储与生产凭据；列出本次实际交付的业务链路。解决 §5.5 的上线阻断项，明确代理功能是否在首版范围。 | 首版功能与配置清单、可用生产地址/存储命名空间、外部链接可达证据；未完成的功能不出现可误操作入口。 |
| 2. 打通 Cloud 包生成 | 复用现有入口并做必要修正：在 GitHub Linux amd64 Runner 构建实际存在的 Server、Scheduler、Worker、Migration 与 Cloud Web，Cloud `bin/` 携带 FFmpeg/FFprobe；加入版本/来源信息、摘要和最小 smoke。先用未发布的 GitHub 试构建验证打包能力，正式发布包在第 4、5 步从 Tag 重建。宝塔只解压运行，不现场编译。 | GitHub 试构建包可在目标 Linux 解压，Migration 对准预发布库执行，三常驻进程由进程管理器启动并通过健康/业务检查；媒体功能能访问目标环境对象存储。 |
| 3. 打通三平台客户端构建 | 在 GitHub Windows x64、macOS Intel、macOS ARM Runner 上，沿用已验证的 Agent Sidecar/Tauri 构建方式并做必要适配；处理远程 Cloud URL、CSP、Windows 数据目录、本机 FFmpeg 误报、Sidecar 与 BitBrowser 本机连接。阶段一可保留现有 PyInstaller `onefile`，只要安装包内启动和健康 smoke 通过。正式安装包在第 4、5 步从 Tag 重建。 | 三平台试构建均含匹配 Agent，能启动/连接 Cloud 并验证目标架构和包内配置；不要求本地真机或 macOS 签名。 |
| 4. 固定版本并演练 | 三仓分别打不可移动的组件 Tag；Workspace 在 `releases/manifests/<产品Tag>.yaml` 保存简版版本锁定记录并打产品 RC Tag。建立最小 `release.yml`：产品 Tag 触发，按锁定文件检出三个组件 Tag；GitHub Linux 构建 Cloud 包与 Desktop Web，三平台 Runner 构建匹配 Agent 与 Desktop，执行 smoke、校验摘要、汇总同产品 Tag 的 RC Pre-release。再完成预发布迁移、登录、Agent 启动、存储外部下载和备份恢复演练。 | RC 对应的 Cloud/Agent/Desktop Tag、Commit、摘要、配置、smoke 与演练记录齐全；任何平台失败，工作流不发布整组制品。 |
| 5. 首次生产上线 | 为确认后的三仓版本与 Workspace 版本打正式 Tag；同一 GitHub 工作流从正式 Tag 重建 Cloud 包及三平台安装包，自动汇总为 Draft GitHub Release。人工复核结果并按 §7 关服、备份、宝塔部署、迁移、启动与三者验收；恢复服务后公开同产品 Tag 的客户端下载。 | GitHub Release 草稿中的三平台包和摘要齐全；Cloud/Web/API、Agent、Desktop 及首版承诺功能全部可用，发布记录、维护时长、异常与回退结果可追溯。 |

阶段一**不能推迟**真实生产地址、凭据与对象隔离、GitHub 产品 Tag 触发的联合构建和 RC Pre-release/正式 Draft Release、三平台原生 smoke、可运行的 Cloud 包、Migration/备份恢复、制品摘要、用户可见的维护/失败状态。只允许把工程结构统一、完整 Manifest schema 和发布体系加固放到阶段二。阶段一如需增加构建胶水，应就地扩展现有入口；阶段二演进同一条 `release.yml`，不并行维护两套发布路径。

### 4.2 阶段二：建设可持续交付体系

阶段二在阶段一上线并留存证据后，按原附件的 **Inventory → 接口 → Cloud → Agent → Desktop → Workspace → 各仓 CI 后联合发布 → 旧路径清理** 顺序实施。它改善后续版本的可重复性，不把首版仅有的人工步骤描述为长期方案。

| 顺序 | 工作 | 阶段二结束证据 |
| --- | --- | --- |
| 1. Inventory | 逐仓核查 Makefile、`scripts/`、`bin/`、`packaging/`、GitHub workflows、Web/Go/Python/Tauri 入口；从阶段一实际发布记录列出重复、临时和待迁移项。 | 四仓真实调用图与清理清单，不凭附件示例猜入口。 |
| 2. 统一接口 | 确定 `bootstrap/dev/test/lint/generate/build/verify/package/clean` 各自适用范围和职责；明确 `bin/` 生成可执行文件、Web/Tauri 输出和 `output/` 的边界，不设 `.build/`。 | 命令契约、目录/版本/配置契约和正式 Manifest schema 经评审。 |
| 3. Cloud 重构 | 收敛 `bin/` 脚本和 Makefile；build、verify、package 分离；已编译程序与 FFmpeg/FFprobe 在 `bin/`，`control.sh` 只管理生命周期。 | 从全新 Tag 连续完成 build → verify → package；Linux 包与阶段一业务能力等价。 |
| 4. Agent 重构 | 将原生构建收敛到跨平台 `bin/*.py`；在不破坏 Sidecar 启动的条件下由阶段一已验证的形态迁到 PyInstaller `onedir`；整理 `packaging/`、`output/`，不携带 FFmpeg。 | 三平台原生 Runner 对新版形态完成真实启动、Local API、配置与升级数据保留验证。 |
| 5. Desktop 重构 | 建立 `prepare → build → verify → package`，只消费明确的 Desktop Web 与对应架构 Agent Artifact，取消相邻仓实时构建依赖。 | 三平台安装包仍与阶段一功能等价，内部版本、Sidecar 和前端来源可追溯。 |
| 6. Workspace 重构 | 以阶段一简版记录为输入，给**后续新 Tag** 扩展正式 Release Manifest、版本兼容校验和当前平台 dry-run；已打 Tag 下的首版文件保持原样，Workspace 不运行 Cloud/Agent。 | 新产品 Tag 与 Manifest 可解析三仓 Tag、契约、组件及目标平台；首版仍可按原记录追溯。 |
| 7. GitHub Actions | **先**完善三仓独立 CI，**再**扩展阶段一已有的 Workspace `release.yml`：统一跨仓 Artifact 契约、Manifest schema/兼容性校验和更完整的 Release 门禁；保持产品 Tag 触发与 Cloud Linux/三平台 Runner。 | 新 RC Tag 的升级后流水线通过，包与首发功能等价；任一平台失败不发布整组制品。 |
| 8. 清理旧路径 | 新链路通过后才删除被替代的 `scripts/`、旧 CI、重复入口与已确认废弃的 Cloud Agent 专属代码；保留仍有职责的脚本。 | 清理后四仓 CI 全绿，并用**新候选 Tag**复跑联合发布；下一正式版本无需人工拼接跨仓制品。 |

两阶段分别按 Workspace Delivery 规则拆分实施；本评审文件不建立第二套执行状态，也不让一个 CHG 同时承载首次上线和完整工程重构。

## 5. 包、版本与配置规则

### 5.1 Cloud 包与宝塔目录

Cloud Linux 包至少包含 `bin/server`、`bin/discovery-scheduler`、`bin/discovery-worker`、`bin/migrate`、`bin/ffmpeg`、`bin/ffprobe`、Cloud Web、迁移文件、版本记录与 SHA-256；若本次范围已有其他独立 Cloud Worker，则按同样标准纳入。`bin/` 路径为发布包内的运行目录，打包时只复制列出的可执行文件，不包含构建脚本。Cloud `verify` 检查 FFmpeg/FFprobe 的版本、可执行权限、目标架构和实际调用结果。打包只消费已验证的构建结果，不能在宝塔现场编译或安装 npm 依赖。

推荐目录为 `releases/<release>/`（只读程序）、`shared/conf`、`shared/logs`、`shared/data`、`current`（指向当前版本）。运行时现要求 `./config`，需用经验证的相对路径或链接将每个版本接到 `shared/conf`，并固定工作目录；不能依赖开发机路径。宝塔负责 HTTPS 入口和包上传；各常驻进程由受控进程管理器分别守护、重启和采集日志。现有会现场编译的 `bin/control.sh` 必须改成仅管理已打包程序或由正式进程管理器替代，不能直接用于生产。

Migration 使用与 Cloud 发布 Tag 同源的可执行程序和 SQL。生产部署时禁止自动创建误指向的数据库；先核对目标数据库名、当前迁移版本与备份，再在维护窗口应用。MySQL DDL 可能隐式提交，应用回退不等于数据库回退，必须先在数据副本上演练。[MySQL 官方 DDL 说明](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html)

### 5.2 Desktop 与 Agent

阶段一允许沿用现有 Desktop 联合构建入口和 Agent `onefile`，但 GitHub 构建必须先按简版记录检出三仓 Tag，检查输入版本/平台、最终安装包内 Sidecar、Cloud 地址与摘要；不能从相邻仓 `main`、`latest` 或用户机器 Python 隐式取源码。阶段二的 Desktop `prepare` 改为只接收指定的 Desktop Web、对应平台 Agent 制品与非敏感生产配置，拒绝不匹配的 OS/CPU、版本、契约或摘要；Agent 按附件目标迁到 PyInstaller `onedir` 并在 Runner 上验证 `externalBin`、启动及升级数据保留。两阶段 Desktop/Agent 安装包都不放 FFmpeg/FFprobe。

Desktop/Agent 安装包中的 Cloud 域名、CSP、版本兼容范围属于**非敏感发布配置**，在打包前注入并在 GitHub Actions 中验证；不得继续指向 `127.0.0.1`。之后变更这些值应生成新安装包及摘要。个人保存目录和偏好设置留在用户数据目录，升级不清除。Cloud 数据库密码、对象存储密钥和平台凭据仅在服务器受控配置中提供，不进入前端、安装包、Manifest 或 GitHub Artifact。发布前扫描仓库及历史已知凭据，并完成轮换。

本轮没有 Apple 开发者签名证书；macOS 安装包不签名、不公证，也不配置相关 GitHub Secret 或发布门禁。只验证原生构建、Sidecar、制品结构、版本和摘要。这里的 macOS 证书与 Cloud HTTPS 所需 TLS 证书是两件事，Cloud HTTPS 配置仍按服务端部署要求执行。

### 5.3 产品发布清单

两阶段都先给有变更的 Cloud、Agent、Desktop 版本打组件 Tag；未变更的仓库可沿用已发布 Tag。再将三个组件 Tag、目标环境、Desktop Web 来源写入 Workspace `releases/manifests/<产品Tag>.yaml`，最后给包含该文件的 Workspace 版本打同名产品 Tag（例如 `v0.5.0`）。**Tag 是发布入口；Commit 只用于校验和追溯。** 发布后的 Tag 不移动、不复用；修订创建新 Tag，正式构建不接受 `main`、`latest` 或未提交工作区。

阶段一的 GitHub 工作流读取简版 Manifest 并检查产品 Tag、三仓 Tag、目标平台、服务地址和构建结果，将包内配置、摘要与解析出的完整 Commit 写入 RC/正式 Release；发布负责人在公开前复核。阶段二给**后续新 Tag** 的同类文件加入发布类型、契约修订、构建工具链、目标平台、Cloud FFmpeg/FFprobe 版本与摘要等字段，扩展已有工作流的 schema 和兼容性校验；Agent/Desktop 不记录客户端 FFmpeg 组件。现有 `config/release-matrix.yaml` 保留历史验证记录，阶段二清理其当前推荐组合的 Cloud Agent 旧口径，避免与新 Manifest 冲突。

### 5.4 开发构建、预发布候选与正式发布

不建立两套 `dev/`、`release/` 打包脚本或目录；阶段一就让开发 CI、RC 和正式版复用 `build → verify → package` 的必要入口，阶段二加固这些入口的契约与校验深度。两阶段 `output/` 正式文件名都包含版本、平台和架构。区分的是**触发方式、版本身份、配置与可见范围**：

| 类型 | 触发与命名 | 制品和用途 |
| --- | --- | --- |
| 开发构建 | PR/分支 CI，无发布 Tag；构建信息标记为开发快照。 | 测试结果和短期 Actions Artifact，供研发检查；不创建 GitHub Release，不给用户下载。 |
| 预发布候选（RC） | Workspace 产品 Tag 形如 `v0.5.0-rc.1`；修复后递增为 `v0.5.0-rc.2`，不移动旧 Tag。同名版本锁定文件指向对应组件 Tag。 | 产品 Tag 触发 GitHub Actions 完成 Cloud 和三平台原生构建/验证，并自动创建 **Pre-release**，用于预发布演练，不作为正式下载入口。 |
| 正式发布 | Workspace 产品 Tag 形如 `v0.5.0`；同名版本锁定文件指向最终组件 Tag。 | 同一 GitHub 工作流生成 Cloud 包和三平台安装包，自动创建 **Draft Release**；关服部署、Cloud/Agent/Desktop 验证通过后再由发布负责人公开。 |

`-rc.N` 是命名约定；两阶段的 GitHub 工作流都要显式把 RC 标为 Pre-release、正式版先建为 Draft，并检查版本锁定文件、组件 Tag、目标环境和包内配置，不能只看 Tag 字符串。Cloud 的预发布/生产差异来自服务器受控配置；若 Desktop 安装包内固化 Cloud 地址，RC 使用预发布地址，正式包使用生产地址，正式包必须重新完成三平台构建、配置和启动链验证。不要把 RC 安装包改名后直接当正式包，也不要让开发构建复用正式 Tag。

GitHub Release 支持 Pre-release 与 Draft 两种状态；本计划分别用来标记 RC 和等待 Cloud 上线的正式制品。[GitHub 官方 Release 文档](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)

### 5.5 线上/线下配置审计与修改清单（静态检查）

配置分为三类：**构建前确定的公开地址**（Desktop/Agent 安装包和 CSP）、**服务器私有配置**（Cloud 数据库与对象存储凭据）、**用户机器上的本地地址与目录**（Agent、比特浏览器、个人下载目录）。三类不能用一个 `node_id`、同一套 IP/端口或同一个“上传路径”代替。实际域名、数据库位置、对象存储权限和宝塔目录须在阶段一第 1 步核实；下表给出已能从代码确认的差异和必改项。

| 配置项 | 开发 | 预发布候选（RC） | 正式生产 |
| --- | --- | --- | --- |
| 客户端访问 Cloud | 当前本机 `http://127.0.0.1:18080` | 预发布 HTTPS 域名/443，待核实 | 生产 HTTPS 域名/443，待核实 |
| Cloud 进程入口 | 本机 `127.0.0.1:18080` | 宝塔内网/本机监听端口，拟 8080，待核实 | 宝塔内网/本机监听端口，拟 8080，待核实 |
| 用户电脑本地服务 | Agent `127.0.0.1:8765`；比特 `127.0.0.1:54345` | 保持用户电脑本机地址 | 保持用户电脑本机地址 |
| MySQL | 开发库 `wt_media_cloud` | 独立预发布库、专用账号/私有密码 | 生产库 `wt_media`（核实名称）、专用账号/私有密码 |
| 云端对象文件 | 当前同一 endpoint/bucket 下 `dev/` 前缀 | 独立 bucket 或必填 `staging/` 前缀 | 独立 bucket 或必填 `prod/` 前缀 |
| 媒体暂存/日志 | 开发机本地目录 | 预发布服务器独立可写目录 | 宝塔 `shared/` 下受控可写目录 |

客户端只配置 Cloud **公开 HTTPS 地址**；用户机器的 `8765/54345` 不经宝塔暴露；MySQL `3306` 和 Cloud 内部 `8080` 也不作为客户端下载地址。对象存储的 endpoint/bucket/prefix 和 Cloud Worker 暂存磁盘是两种不同路径，分别验证。

| 优先级 | 配置/代码位置与现状 | 目标规则和验收 |
| --- | --- | --- |
| 上线阻断 | Cloud `config_online/app.toml` 监听 `:8080`，开发配置监听 `127.0.0.1:18080`。 | 宝塔对外统一走有有效证书的 HTTPS 域名/443，反向代理 Cloud Web 与 `/api`；Cloud 进程只接受宝塔可达的内网/本机地址（同机优先 `127.0.0.1:8080`），不要把 8080 作为客户端入口。核对端口占用、代理路径、转发头、真实健康检查和维护页/API 维护状态。 |
| 上线阻断 | Agent `config_online/agent.toml` 的 `cloud.base_url`、Desktop `src-tauri/resources/desktop.production.toml` 的 `cloud.base_url` 与 `browser.csp_connect_src` 都仍指向 `http://127.0.0.1:18080`。Desktop 生产配置还编进 Rust 二进制，不能指望部署后用环境变量修正。 | 由一次发布的环境清单生成同一个公开 Cloud HTTPS origin；RC 指预发布，正式版指生产。打包前注入并校验 Desktop 原生配置、CSP、Agent 发布配置和包内最终值一致，且生产包没有作为 Cloud 地址的回环地址。变更域名必须重打新 Tag 与安装包。 |
| 上线阻断 | Cloud Web `web/src/shared/api/http.js`、`web/src/modules/accounts/pages/AccountsPage.vue`、`web/src/modules/profiles/pages/ProfilesPage.vue` 的 Desktop 分支仍硬编码本机 Cloud URL，尽管 `web/src/apps/desktop/features/local-agent/init.js` 已能向原生层读取公开配置。 | Desktop Web 的所有 Cloud API 和本机状态刷新统一使用一个受控的公开 Cloud 地址来源；生产打包扫描不能出现有效运行路径上的旧本机 Cloud URL。Vite 开发代理仍可保留本机地址，不应被误改成线上地址。验证登录、账号/窗口检查、文件授权与 API 请求实际落在目标域名。 |
| 上线阻断 | Cloud `config_online/database/primary.toml` 为 `127.0.0.1:3306`、库 `wt_media`、用户 `root`、空密码；开发库名不同。Cloud `config_online/app.toml` 的首次管理员用户名/密码也均为空；空值会跳过建管理员。 | 根据宝塔 MySQL 的实际部署决定主机/端口/库名，使用最小权限专用数据库账号及服务器私有密码；先验证连接和迁移目标。新库必须有安全的一次性管理员初始化或等效已验证建号流程，首次登录通过后清除一次性密码。任何口令都不写入仓库、Manifest、安装包或 Actions Artifact。 |
| 上线阻断 | Cloud `config/storage/object_storage.toml` 与 `config_online/storage/object_storage.toml` 当前使用相同 endpoint 和 bucket；开发前缀为 `dev/`，线上前缀为空。对象写入与预签名 URL 均由 `internal/infra/storage/minio.go` 对逻辑 key 加配置前缀；逻辑 key 如 `materials/<id>/...`。 | 在首发前锁定明确的 `dev/`、`staging/`、`prod/` 隔离方案；优先独立 bucket 与最小权限密钥，若共用 bucket 则三个环境必须有非空独立前缀和各自权限，生产不能落在根目录。业务代码继续使用逻辑 key，不把环境名写进数据库 key。核对 endpoint 的 HTTPS、地域、bucket、读写权限、过期时间；从 Cloud 写入后由外部 Agent 实际用预签名 URL 下载，证明生成的主机名对客户端可达。若已有对象，改前缀前先迁移或保留旧 key 的读取路径。 |
| 上线阻断 | Cloud `config/README.md` 说明对象存储密钥文件不入库；缺少时 Cloud 可启动但对象操作返回 `ErrNotConfigured`。文档仍称 bucket 是占位符，与现有配置不一致。 | 在宝塔服务器私有 `shared/conf/credentials/object_storage.toml` 放目标环境专用密钥并限制权限；以实际上传、预签名下载和删除验证，不以 `/healthz` 成功代替存储可用。更正文档过时的 bucket 说明；已入库的外部平台凭据在发布前轮换。 |
| 按功能范围阻断 | Cloud `config_online/credentials/douyin.toml` 的 API key 与 cookie 为空，开发配置已有值；`config_online/clients/http/douyin.toml` 的外部服务地址与开发相同。 | 若首版使用抖音发现/素材准备等链路，在服务器私有配置中提供有效的生产凭据，并确认外部 API 地址、回调/网络权限、限流和功能验证；预发布使用独立凭据或隔离账号。历史已入库的开发凭据先轮换，不把开发文件整体复制到生产。若本次不交付相应功能，关闭调度和入口，不以 Cloud 启动成功推断外部集成可用。 |
| 按功能范围阻断 | Cloud `config_online/clients/http/agent.toml` 将代理检查/提取/修改请求发往 `127.0.0.1:8765`；迁到宝塔后这是**服务器自身**，不是用户电脑的 Agent。 | 阶段一第 1 步确认首次上线是否交付这些代理操作。若交付，须决定“Desktop 调本机 Agent”或“Agent 主动领取 Cloud 任务”等可达链路并按跨仓契约实施、验证；不能仅把 Cloud 配置改成某台用户电脑的公网 IP。若不交付，要在首版功能清单和 UI 中明确禁用相应入口并验证不会产生假成功。 |
| 必查 | Agent `config_online/agent.toml` 的本地 API `127.0.0.1:8765` 和比特浏览器 `127.0.0.1:54345`；Desktop Agent 端口同为 8765。Agent 发布配置的 `agent.id` 当前仍为 `local-agent-dev`。 | 这两个服务应继续只监听**用户电脑本机**，不改为线上 IP；核对 Desktop/Agent 端口一致、冲突提示与实际 BitBrowser API 探测。确认生产 Agent 身份是否由设备注册时生成并覆盖默认值；若没有，改为每安装/设备稳定且唯一的 ID，再检验任务归属与重装迁移，避免多个客户端共享开发 ID。 |
| 必查 | Agent `runtime/paths.py` 在生产或冻结模式统一使用 macOS 的 `~/Library/.../WTMedia/Agent`；Desktop 发布配置未默认传入 `agent.data_dir`。用户选的保存目录另存于 Agent 本地数据。 | Windows x64 与两种 macOS 分别使用操作系统合适、可写、跨版本保留的 Agent 数据与日志目录；在 GitHub Windows Runner 验证安装包内启动后的目录、权限、升级不清空历史数据。个人下载目录由用户选择并留在本机，它不是 Cloud 对象存储前缀，也不随部署环境切换。 |
| 必查 | Cloud 六类日志配置当前均为相对 `logs/*.log`；媒体准备 Worker 的下载暂存默认落在 OS 临时目录。 | 宝塔部署固定 Cloud 工作目录，将日志和大文件临时空间放在 `shared/` 下明确可写的位置或用稳定目录映射/进程 `TMPDIR`；检查容量、清理、权限及回滚后仍可读取日志。对象存储存放最终媒体，Cloud 临时目录只放处理中的本地副本，二者单独配置和监控。 |
| 必查 | Cloud/Agent 的 `config_online/` 只在**打包时替换** `config/`；运行时不会自动根据 `development/production` 合并。Cloud Web 的 Vite 本地代理和 Desktop `devUrl` 是开发工具配置。 | 制品校验最终 `config/` 文件集合、环境标记、地址和摘要；禁止将 `config/` 的开发地址/口令误打进正式包。服务器私有文件由部署时注入，发布包只含非敏感默认结构。开发工具地址不作为生产配置清单。 |

配置检查顺序：先定三个环境各自的 Cloud 公网域名与对象存储命名空间 → 定宝塔内网端口、MySQL、日志/临时/备份目录 → 定首版代理功能的调用链和 Agent 身份 → 在 CI 校验包内公开配置 → 在预发布环境从**服务器和外部客户端两个位置**验证登录、Agent 连接、对象上传与预签名下载。公开域名、端口、bucket/prefix 属于非敏感发布记录；数据库密码、对象存储密钥和平台凭据只在受控服务器保存。当前审计未披露密钥值，也未连接真实宝塔/MySQL/对象存储。

## 6. CI/CD 与发布门禁

**阶段一最小 GitHub 发布链。** 三仓现有 PR CI 保留。Workspace 新增简版 `release.yml`，由**产品 Tag 推送触发**，从同名锁定文件读取 Cloud/Agent/Desktop 组件 Tag；Linux Runner 生成 Cloud 包和 Desktop Web，Windows x64/macOS Intel/macOS ARM Runner 各自构建 Agent 与 Desktop。工作流执行可执行文件/Sidecar 启动和配置 smoke，校验目标架构、包内版本与 SHA-256，汇总制品；任一平台失败即不创建整组 Release。RC 自动创建同产品 Tag 的 Pre-release，正式版自动创建 Draft Release。Cloud 包作为 GitHub 受控 Artifact 供人工上传宝塔；三平台客户端包直接附到 GitHub Release。发布负责人只复核结果、执行宝塔部署并在三者验收后公开正式 Release，不参与跨平台构建或本地拼装安装包。

GitHub 官方当前提供 Linux x64、Windows x64、macOS Intel 和 macOS arm64 的托管 Runner；可分别选用 `ubuntu-24.04`、`windows-2022`、`macos-15-intel`、`macos-15`，实施时核对仓库的 Actions 权限、配额及打包所需磁盘空间，不使用会改变架构的模糊 macOS 标签。[GitHub 官方 Runner 列表](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) Runner smoke 可验证安装包、Sidecar、本地 API 和与测试 Cloud 的连接；若首版业务包含比特浏览器已登录会话中的真实操作，还需在受控可用环境做该外部集成验收，不能把 Sidecar smoke 当作比特浏览器登录成功。

**阶段二可持续交付加固。** 各仓 CI 只验证自身：Cloud 执行 Go/Web 测试、迁移和两个 Web 构建；Agent 执行锁定依赖、测试、原生 Sidecar smoke；Desktop 执行 Rust、契约与本机桥验证。Workspace 沿用同一条产品 Tag 触发的 `release.yml` 和阶段一已有的 build/verify/package 入口，扩展正式 Manifest schema、版本/契约兼容校验、跨 Job Artifact 摘要、权限和失败门禁；不另建一条正式发布路径。阶段二步骤 7 使用新候选 Tag 演练升级后的工作流，步骤 8 清理后再用新候选 Tag 复验，才用于下一次正式发布。跨仓读取使用最小权限凭据和显式 Tag，构建时记录解析出的 Commit。

下面六类 Job 在**阶段一就必须运行**；阶段二扩展各 Job 的验证深度和复用性：

| 发布 Job | Runner | 输入 | 必须输出 |
| --- | --- | --- | --- |
| `validate-manifest` | Linux | Workspace 产品 Tag、同名简版锁定记录、三仓只读访问 | 阶段一检查产品 Tag 与文件同名、三仓 Tag 可解析、目标平台与配置可用，记录解析出的 Commit；阶段二增加正式 schema 与契约校验 |
| `build-cloud` | Linux amd64 | Cloud Tag | Cloud Linux 包、Desktop Web 制品、两者摘要 |
| `build-agent` | Windows x64、macOS Intel、macOS ARM 原生矩阵 | Agent Tag | 各平台 Agent 包、smoke 结果、摘要 |
| `build-desktop` | 对应三平台原生矩阵 | Desktop Tag、同一 Desktop Web、匹配架构 Agent | 安装包、包内版本/Sidecar/组件校验、Runner 可执行的 smoke 结果 |
| `verify` / `package` | Linux | Cloud 与三平台构建结果、Manifest、测试记录 | 核对来源、环境、包内地址、架构、摘要和敏感信息；汇总两种发布状态共用的制品结构、`SHA256SUMS` 和构建信息 |
| `publish-pre` / `publish-release` | Linux | 前面所有 Job 的已验证制品 | RC Tag 走 `publish-pre` 自动生成 Pre-release，正式 Tag 走 `publish-release` 自动生成 Draft Release；客户端附 `SHA256SUMS`、版本锁定记录与构建信息，Cloud 包保留为 GitHub 受控上传制品 |

任何 Matrix 平台失败，`publish-release` 不得给整组制品标记成功。阶段一就要校验跨 Job 下载制品的摘要，不只信任 Artifact 名称；阶段二进一步加入兼容性、来源和可重复构建检查。

发布的必要核对项：产品 Tag 与同名锁定文件、三仓 Tag/解析出的 Commit、目标架构、包内版本、SHA-256、Cloud `bin/ffmpeg`/`bin/ffprobe`、Agent 启动/健康 smoke、Desktop 启动 Agent 与安装包结构、目标环境域名与 CSP、敏感信息扫描、三平台 Runner 结果。`web-desktop` 只供 Desktop 构建；Cloud 包保留为供宝塔人工部署的受控 GitHub Artifact；正式版草稿 GitHub Release 自动收齐三平台客户端、版本记录、`SHA256SUMS` 和 build-info，正式环境恢复后才公开。阶段二再增加 Manifest schema/契约的自动校验，可增加 GitHub Artifact Attestation 作为制品来源证据。[GitHub 官方制品来源说明](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)

## 7. 预发布与首次生产执行顺序

### 7.1 预发布环境先完成

1. 实施人先从现有宝塔服务器和 Cloud 配置核对上线所需的实际值：Linux 架构及磁盘、对外域名和 HTTPS、MySQL 连接、对象存储连接、Cloud 运行账号/进程管理、备份存放位置和维护提示入口。把结果写成发布记录；缺少的项逐项补齐，不要求业务方先提供一份完整技术规格。预发布环境至少复现生产的关键连接与配置。客户端三平台构建与验证由 GitHub Actions Matrix 完成，不要求本地真机或独立的三平台测试电脑。
2. 先用 RC 验证完整三平台打包与发布流程；正式 Tag 产出后，仍用**最终 Cloud 包**加预发布服务器配置部署一次，不只依赖 RC 的结果。验证配置路径、权限、Server/Scheduler/Worker 独立生命周期，以及端口只暴露必要入口。
3. 在空库和代表性数据副本上分别执行迁移；记录表行数、关键关系、耗时与异常处理。备份 MySQL 和对象存储，再实际恢复到隔离环境并核对数据。[MySQL 官方备份方法](https://dev.mysql.com/doc/refman/8.4/en/backup-methods.html)
4. 核对本次 Release 的三平台 Matrix 结果、实际安装包、Desktop 启动 Agent、Agent 健康 smoke、包内组件、目标架构、Cloud 域名/CSP 和制品摘要；Cloud 预发布环境走外部 HTTPS、登录与本次发布范围内可在服务端验证的业务 API，确认三者接口版本匹配。
5. 演练宝塔维护提示、API 维护状态及 Desktop 的升级提示，再演练 Cloud 进程失败、迁移失败、客户端与 Cloud 版本不兼容、网络中断和回滚；确认不会自动重放可能产生外部副作用的任务。

### 7.2 生产切换手册骨架

1. 部署前已有三仓 Tag、Workspace 同名简版版本锁定记录；产品 Tag 触发的 GitHub Actions 已生成 Cloud 包和含三平台客户端的 Draft Release，所有 Runner Job 与发布门禁通过。发布负责人复核制品、摘要和目标环境后，记录计划关服时间、维护提示文案、执行人与回退负责人，并提前告知用户；核对域名、HTTPS、Linux 架构、磁盘、MySQL、对象存储、凭据和备份位置。
2. 到点在宝塔启用维护模式：Web 展示“系统维护中”及预计恢复时间，API 返回可识别的维护状态；Desktop 将维护状态展示为升级提示，避免当成账号或本机 Agent 故障。停止新写入与调度，等待或记录尚未结束的任务，确保不会在切换中重复执行。
3. 做 MySQL 与对象存储的一致性备份并确认可读取；首次空环境也保存初始配置与 Schema 基线。维护期间继续保持对外关服。
4. 将 Cloud 包上传宝塔，在服务器校验 SHA-256，解压到新的 `releases/<release>/`，连接 `shared` 配置；保留旧版本和旧配置快照。使用该包的 Migration 对准指定生产库执行，核对 `schema_migrations` 和关键数据；失败即停止，不继续启动新版本。
5. 切换 `current`，按 Server → Worker → Scheduler 顺序启动当前确有的进程；在维护模式内通过内部地址或受控验证入口检查健康、登录、业务 API 和与本次 Desktop/Agent 的版本兼容。三者均通过后再解除维护模式、开放流量。
6. 公开同产品 Tag 的 GitHub Release，给用户一个客户端下载入口：Windows x64、macOS Intel、macOS ARM 安装包；Agent 已随 Desktop 安装，普通用户无需单独下载 Agent。独立 Agent 制品只用于追溯和工程集成。记录恢复时间、部署人、版本、摘要、验证结果和用户签收。
7. 观察错误率、进程重启、数据库连接、队列积压、对象存储失败、磁盘和日志；若发现任一组件不可用，重新启用维护提示并按回退规则处理。

### 7.3 回退规则

回退期间保持维护提示。若存在旧版本且未执行不兼容迁移，停止新 Scheduler/Worker/Server、恢复旧 `current` 与旧进程，校验健康和业务读写。若 Schema 或数据已发生不兼容变更，不允许只换回旧二进制：必须停止写入，按演练方案恢复 MySQL 与对象存储的一致快照，核对外部副作用与待确认任务后再开放。首次空环境若没有旧版本可回退，则保持关服，修复并复验后再开放。客户端回退使用上一版安装包并保留本机用户数据；数据库和平台上已产生的真实发布不能通过软件回退自动撤销。

### 7.4 上线后的重复发布规则

阶段一上线后、阶段二完成前若必须再发布，继续建立新的组件 Tag、同名版本锁定文件和产品 Tag，由阶段一 `release.yml` 在 GitHub 完成联合构建、验证和 Draft/Pre-release，再执行预发布演练、关服部署与公开 Release。阶段二完成后，沿用同一条产品 Tag 触发的 GitHub 工作流，增加正式 Manifest 和自动门禁；生产关服、备份、迁移、三者验收与观察仍保留人工执行。任何阶段都不移动或复用旧 Tag，也不在服务器编辑程序文件。Cloud 非敏感配置调整应在受控 `shared/conf` 中保留变更记录、前后校验和回退副本；密钥轮换走独立流程。Desktop 包内域名或 CSP 变更要重建安装包、摘要和 Tag。未来数据库改动优先采用可兼容前后版本的扩展、迁移、收缩顺序；不兼容删除单独安排恢复演练，不能依赖“切回旧二进制”作为回退承诺。

## 8. 已定方案与上线前检查

| 事项 | 已定方案 | 实施时检查什么 |
| --- | --- | --- |
| Cloud 部署 | 宝塔人工上传并部署 Linux 包；不使用 Docker/Compose 或 Cloud Agent 发布链。 | 同步修正 Master Plan、现行架构和相关 Decision 的旧部署口径；核验宝塔可上传、解压、切换版本和管理 Cloud 进程。 |
| 首次上线范围 | Cloud、Agent、Desktop 必须同时可用；按本次已完成的功能列验收清单，不把未来规划功能算入。 | Cloud Web/API 与后台进程、Agent 健康与本地 API、Desktop 启动 Agent 并连接 Cloud 的证据齐全。 |
| 服务器与连接 | 沿用实际可用的宝塔部署环境，由实施人盘点，不要求先拍板抽象的“基础设施方案”。 | 服务器 Linux/CPU/磁盘、对外域名和 HTTPS、MySQL 地址及库名、对象存储地址及桶、服务账号/进程管理、备份目录及恢复办法；缺项逐项补齐后才部署。 |
| 客户端分发 | 通过同产品 Tag 的 GitHub Release 提供 Windows x64、macOS Intel、macOS ARM 下载；Agent 随 Desktop 安装，普通用户只下载 Desktop。 | 三个安装包、对应架构、摘要和下载入口正确；Cloud 恢复后再公开 Release。本轮不要求 macOS 证书、签名或本地真机。 |
| 凭据与配置 | Cloud 敏感配置只放服务器；安装包只含非敏感服务地址等配置。 | 轮换历史已入库外部凭据，核对配置注入、访问范围及包内敏感信息扫描。 |
| FFmpeg/FFprobe | 仅 Cloud `bin/` 携带。 | 核对客户端环境状态字段及实际调用是否已迁移；验证 Cloud 包中的版本、权限和可执行性。 |
| 发布期间可停服 | 部署窗口开启维护提示并停止新任务；完成备份、迁移、切换和三者检查后恢复服务。当前不要求不停机切换或分钟级恢复承诺。 | 发布前通知维护时段与提示文案；若超时或失败，持续展示维护提示并更新进度，完成回退/修复验证后再开放。 |

## 9. 工期预估与依赖

基于本次静态检查，以 **1 名熟悉四仓的工程师、现有 CI 权限和宝塔账号可用** 为前提，从计划评审通过、范围冻结开始估算；以下为工作日，不把 GitHub Runner 排队、外部凭据申请或等待评审算作纯开发时间，也未执行实际构建测时。

| 阶段 | 工作 | 估算 | 主要不确定性 |
| --- | --- | --- | --- |
| 阶段一 | 首版功能/配置冻结、宝塔和对象存储核对 | 2～3 天 | 实际域名、MySQL、存储权限与代理操作首版范围。 |
| 阶段一 | Cloud Linux 包、FFmpeg、运行/迁移及存储验证 | 3～5 天 | 现有启动脚本现场编译，需改为直接运行包内程序。 |
| 阶段一 | Agent/Desktop 三平台原生制品、生产地址与 Sidecar smoke | 4～7 天 | Windows 数据目录、Web/Native 多处本机 Cloud URL、无签名 macOS 包。 |
| 阶段一 | 产品 Tag 触发的 GitHub 联合发布工作流、RC/预发布演练和首次宝塔上线 | 6～8 天 | 跨仓 Artifact、原生 Runner、备份恢复、首次迁移及关服窗口。 |
| **阶段一小计** | **GitHub 完成整组制品并首次上线** | **15～23 个工作日，约 3～5 周** | 以上四项全部通过后即可首次上线，不需要用户持有三平台电脑。 |
| 阶段二 | 全仓 Inventory、统一命令/Manifest 契约 | 2～3 天 | 阶段一真实入口和需保留的兼容路径。 |
| 阶段二 | Cloud/Agent/Desktop 构建、验证、打包入口收敛 | 3～5 天 | Agent `onefile` → `onedir` 与 Tauri Sidecar 适配。 |
| 阶段二 | 正式 Manifest、三仓 CI、已有 GitHub 联合 Release 加固 | 2～3 天 | schema/契约校验、跨仓权限及失败门禁。 |
| 阶段二 | 旧路径清理和新 RC Tag 复验 | 1～2 天 | 清理后回归与文档同步。 |
| **阶段二小计** | **形成可持续交付体系** | **8～13 个工作日，约 2～3 周** | 在首发 GitHub 工作流上演进，不重建第二条发布链。 |
| **合计** | **两阶段** | **23～36 个工程工作日，约 5～8 周** | 两人并行可缩短日历时间，不能省去串行的 Tag、演练和上线门禁。 |

若首版**必须包含现有 Cloud 直调本机 Agent 的代理操作**，设计、实现和验证需在阶段一基线外再预留约 **3～7 个工程工作日**，依跨仓契约影响重估。若环境账号、域名、TLS、密钥或三平台 Runner 权限未就绪，日历时间会延长。生产关服窗口不是上述总工期：演练通过后可先按 **半天操作与观察窗口**安排，实际停服时长须由真实备份、迁移、上传与验收测时确定，不提前承诺分钟级恢复。

## 10. 评审后的交付拆分

评审通过后，先把宝塔非 Docker 部署及发布 Ownership 裁定写入正式 Decision/Engineering 与 Master Plan，再将**阶段一 GitHub 首次上线**和**阶段二可持续交付**作为两个独立交付任务规划。阶段一按 §4.1 顺序完成 Cloud/Agent/Desktop 首版包、产品 Tag 触发的 GitHub 联合发布、RC 演练和生产切换；它通过后即完成首次交付。阶段二再按 §4.2 的八步顺序实施命令与目录重构、正式 Manifest、已有 GitHub 工作流加固和旧路径清理，并用新候选 Tag 复验。每个交付任务分别记录命令、制品、验证结果和未完成事项；本评审稿不预先标记完成，也不授权实施。
