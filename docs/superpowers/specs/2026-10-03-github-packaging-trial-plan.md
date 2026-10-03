# WT Media 首次 GitHub 打包试跑计划

- 日期：2026-10-03
- 状态：`IN_EXECUTION`。用户已在 2026-10-03 授权执行，并要求直接在当前四仓修改提交；执行记录由 `delivery/active/CHG-20261003-076/` 维护。本试跑仍不连接宝塔或生产环境。
- 与主计划关系：本试跑是《2026-10-02 首次全端上线部署计划》阶段一的**预发布验证**。使用与正式版相同的构建、验证、制品命名和校验流程，真正生成一次 RC GitHub Pre-release；试跑通过只证明 GitHub 打包/预发布链路，不代表线上部署或业务验收通过。
- 触发方式：实施准备完成后创建并推送 **Workspace 产品 RC Tag**，Tag 推送自动触发发布工作流。源码只从四仓 Tag 检出，Commit 仅记录和核对，不作为发布选择器。

## 1. 本次只回答一个问题

能否在**没有 Windows、macOS Intel、macOS Apple Silicon 本地电脑**的前提下，仅使用 GitHub Actions 的原生 Runner，从固定的四仓 Tag 连续产出：

1. Cloud Linux amd64 发布包，包含实际存在的 Server、Discovery Scheduler、Discovery Worker、Migration、Cloud Web，以及仅放在 Cloud `bin/` 的 FFmpeg/FFprobe。
2. 同一 Cloud Tag 的 Desktop Web 构建结果。
3. Windows x64、macOS Intel、macOS Apple Silicon 的 Agent Sidecar 和包含对应 Sidecar 的 Desktop 安装包。
4. 构建来源、目标架构、文件摘要和基本 smoke 结果；RC GitHub **Pre-release** 中有三平台安装包、版本锁定文件、构建信息与 `SHA256SUMS`，Cloud 包作为受控 GitHub Actions Artifact 可下载。这些文件的结构和命名须与未来正式 Release 一致。

本次**不做**宝塔上传、线上数据库迁移、生产对象存储写入、账号/比特浏览器真实登录与发布、软件签名公证、正式稳定版公开发布。RC Pre-release 会按仓库的可见范围对外可见，故所有附件必须是可分发的非敏感制品。macOS 构建可使用打包所需的临时/ad-hoc 签名，但不依赖 Apple 开发者证书。试跑制品内不得包含真实生产密钥。Cloud 包的 FFmpeg/FFprobe 来源和 SHA-256 必须预先锁定；Agent/Desktop 均不得携带它们。不新增 `.build/`，也不另建 `dev/`、`release/` 两套打包目录或脚本。

## 2. 当前入口与试跑前缺口

| 仓库 | 2026-10-03 已见入口 | 为这次试跑必须补的最小能力 |
| --- | --- | --- |
| Cloud | `.github/workflows/m0-cloud.yml` 只对 `main`/PR 运行；`scripts/build.sh` 只构建 Server 和默认 Web。 | GitHub Linux Job 从 Cloud Tag 构建四个实际程序和两种 Web，打 Linux 包；Cloud `bin/` 放锁定的 FFmpeg/FFprobe，写入来源/版本/摘要，验证包内程序与文件结构。 |
| Agent | `.github/workflows/m0-agent.yml` 目前只在 Ubuntu 验证普通 Python 包；`scripts/build_desktop_sidecar.py` 有按原生平台构建 Sidecar 的入口。 | GitHub Windows、macOS Intel、macOS ARM Runner 分别构建当前可工作的 Sidecar 形态并做启动/Local API smoke；按平台归档、标注版本与 SHA-256。试跑不以改成 PyInstaller `onedir` 为前置。 |
| Desktop | `.github/workflows/m0-desktop.yml` 只跑 macOS 测试；`scripts/build-release-macos.sh` 只覆盖 Mac DMG，正式构建会消费相邻仓工作树。 | GitHub 三平台 Job 显式检出锁定的 Cloud/Agent/Desktop Tag，消费同一 Desktop Web 和匹配架构 Sidecar；补 Windows 构建/校验入口，检查安装包内前端、Sidecar、目标架构、非敏感 Cloud 地址和 SHA-256。 |
| Workspace | 有 `scripts/build-desktop-frontend.sh`，依赖本地相邻仓；当前没有 `.github/workflows/release.yml`。 | 新增简版 Release Manifest 与产品 Tag 推送触发的 `release.yml`：共用一套 `build → verify → package`，RC 走 `publish-pre` 产出 Pre-release，稳定 Tag 走 `publish-release` 产出 Draft Release。不建立两份会漂移的打包工作流；不要求先完成完整 Manifest/Makefile/目录重构。 |

四仓当前都有其他未提交变更；Tag 必须在目标改动完成、检查通过且提交后创建，不能把现有脏工作树直接当成候选来源。Workspace 当前执行快照与 Git 工作区状态也需在启动试跑前对账，避免选到仍在变动的功能版本。

## 3. 试跑准备顺序（收到执行指令后）

1. **权限与 Runner 预检**：确认四个 GitHub 仓库可由工作流读取，Workspace 工作流可读取组件 Tag、上传 Artifact 和创建/发布 Pre-release；核对 Actions 配额、Runner 标签及存储空间，并确认仓库可见性。使用固定架构的 GitHub 托管 Runner：Linux x64、Windows x64、macOS Intel、macOS arm64，实施时选定具体受支持的标签并记录。无需提供本地目标平台电脑。[GitHub 官方 Runner 列表](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
2. **确定本次候选输入**：读取各仓真实版本与兼容要求后，选一个未使用的产品候选 Tag（格式 `vX.Y.Z-rc.N`），为三个组件分别选/创建不可移动的 Tag。Workspace 简版 Release Manifest `releases/manifests/<产品Tag>.yaml` 至少锁定产品 Tag、三个组件 Tag、Desktop Web 的 Cloud Tag、构建目标和非敏感预发布 Cloud origin。不要在此文件写密码、token 或构建后才会出现的安装包摘要。Tag 只标识版本和触发流程；工作流还必须核对 Manifest 中的目标环境与包内服务地址。
3. **打通最小构建入口**：只补齐本次必需的 Cloud Linux 包、三平台 Sidecar 和三平台 Desktop 构建/验证；复用现有脚本能力，避免在此步开展全仓工程目录重构。Desktop/Agent 的测试 Cloud origin 必须在打包前注入，并检查 Vue、Rust、Agent 以及 CSP 对同一目标一致；没有预发布 Cloud 时可使用明确标注为不可连接的测试地址，但这时不把网络连接列为通过项。
4. **建立正式形态的试跑工作流**：Workspace 只用一份 `release.yml`，由产品 Tag 推送触发；先在 Tag 对应的 Workspace 提交中读取同名 Manifest，再校验三个组件 Tag 的存在与目标。开发构建由 PR/分支 CI 调用相同的构建、验证、打包入口，但没有发布 Tag、不创建 Release。RC 与正式版共用 `validate → build-cloud + build-agent[3] → build-desktop[3] → verify → package`；最后只按经严格校验的 Tag 类型分支：`vX.Y.Z-rc.N` 运行 `publish-pre`，稳定版 `vX.Y.Z` 运行 `publish-release`。Desktop Job 只下载对应架构 Agent Artifact 与 Cloud Desktop Web Artifact；跨 Job 核对 SHA-256，不从 `main`、`latest` 或工作区猜输入。两个发布分支消费同一组已验证制品和相同的资产命名规则。
5. **先验证工作流，再封存 Tag**：用不创建 Release 的 PR/分支检查验证 workflow、权限和脚本；修正后合并并冻结三个组件仓及 Workspace 的候选源码，再创建和推送 Tag。推送 Workspace 产品 RC Tag 即触发正式形态的预发布工作流；真正发布制品必须从 Manifest 锁定的组件 Tag 重建。工作流定义由产品 Tag 对应的 Workspace 提交固定，运行记录也要保存该提交，避免只记录组件源码却忽略编排版本。
6. **观察一轮 GitHub 运行**：逐 Job 查看输入 Tag、解析出的完整 Commit、Runner 架构、Cloud/Agent/Desktop 构建日志、smoke、配置检查、Artifact 与摘要。只有全部成功、敏感信息扫描通过、客户端附件完整后，才将同 Tag Release 从暂存 Draft 发布为 **Pre-release**；本次不执行稳定版 `publish-release`。如果外部依赖或 Runner 偶发故障、源码未变，可对同一 Tag 重新运行；若改了脚本、配置或代码，创建新的 `-rc.N` Tag，不移动旧 Tag，也不覆盖已公开的旧预发布制品。[GitHub Release 状态说明](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
7. **收尾与评审**：从 GitHub 下载并核对 Cloud 包、Desktop Web、三平台 Agent 和 Pre-release 中三个安装包的目录结构、版本、目标架构、摘要与附件命名；将工作流链接、运行编号、Tag→Commit、Artifact 名称/大小/摘要、失败与修复记录写入试跑报告。Pre-release 保留为真实 RC 发布记录；是否将它继续用于预发布部署，另按主计划决定。

## 4. GitHub 工作流的最低门禁

| Job | 最低通过条件 | 失败时停止点 |
| --- | --- | --- |
| `validate` | 产品 Tag 与锁定文件同名；三个组件 Tag 存在，均可解析为确定 Commit；四仓读取权限、目标平台和测试地址明确。 | 缺 Tag/权限/目标立即停止，不回退到 `main`。 |
| `build-cloud` | Linux amd64 包含实际 Cloud 程序、Migration、Cloud Web、FFmpeg/FFprobe；另产 Desktop Web；可执行权限、版本与 SHA-256 有记录。 | 不输出可部署 Cloud 包，不启动客户端汇总。 |
| `build-agent` ×3 | 每个平台的 Sidecar 原生构建成功，可启动、加载发布配置、响应健康/必要 Local API；版本、架构和 SHA-256 可读。 | 对应平台 Desktop Job 不运行。 |
| `build-desktop` ×3 | 只消费匹配架构 Sidecar 和同一 Cloud Desktop Web；Tauri 构建成功；安装包内版本/配置/Sidecar/前端完整；各平台 smoke 和摘要通过。 | 任一平台失败，不执行 `publish-pre`。 |
| `verify` | 校验 Cloud 与三平台构建结果、来源 Tag/Commit、包内地址、架构、smoke 和敏感信息；正式与 RC 使用同一判断规则。 | 失败则只保留 Actions 日志/受控 Artifact，不公开 Release。 |
| `package` | 汇总通过验证的制品、`SHA256SUMS`、Manifest 和构建信息；检查 Release 附件清单完整，RC 与正式版使用相同结构和命名规则。 | 缺附件或摘要不一致则不进入发布 Job。 |
| `publish-pre` / `publish-release` | `-rc.N` 先装齐附件再发布为 Pre-release；稳定 Tag 只创建 Draft Release，待未来部署验收后才公开。两个 Job 共用 build/verify/package 输出，Cloud 包留在受控 Artifact。 | Tag 类型不匹配或附件不完整时均不发布；本次只执行 `publish-pre`。 |

GitHub Runner 的 smoke 能验证**构建、包结构、Sidecar 和可模拟的本地 API**。它不能证明比特浏览器中已有真实登录账号、客户端能连接尚未部署的生产 Cloud，也不能证明宝塔迁移、对象存储和业务发布链路成功；这些属于后续预发布/上线验收。若 Runner 无法运行完整 GUI，可用可执行入口和包内结构 smoke，但必须在报告中写明覆盖边界，不把编译成功写成“安装运行通过”。

## 5. 结果判定与下一步

- **打包链路通过**：GitHub 一次 RC 候选运行的 Linux Cloud 包、Desktop Web、三平台 Agent 与三个 Desktop 安装包全部生成；来源 Tag、Commit、架构、配置、SHA-256 和必要 smoke 对齐；同产品 Tag 的 GitHub **Pre-release 已发布**且客户端附件齐全。此时才进入《首次全端上线部署计划》的生产配置/预发布部署环节。
- **部分通过**：某平台失败或缺少 smoke/摘要。报告按 Cloud、Agent、Desktop、Workspace 归属记录根因；修复后用新候选 Tag 重跑整组，不把不同候选运行的包混为一个版本。
- **试跑阻断**：GitHub 权限、配额、平台 Runner 或外部依赖使工作流无法运行。报告具体阻断项及可行替代；在获得同等原生平台验证前，不改用用户本地电脑拼装正式包，也不声称试跑通过。

本次只需交付**计划、必要的最小 GitHub 打包改动、一次候选试跑及试跑报告**；其中后三项必须等用户手动触发执行后才开始。预计执行与排障约 **5～9 个工程工作日**，实际取决于 Windows 打包入口、macOS Runner 资源和跨仓 Artifact 接线；此估计不包含生产部署。试跑结论将用于修订原部署计划的阶段一工期，而不是把这份文件作为第二套 Delivery 状态。
