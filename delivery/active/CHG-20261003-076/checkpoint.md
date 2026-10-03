# CHG-20261003-076 实施进度

- Status: IMPLEMENTING
- 当前：产品 `v0.1.0-rc.1` 到 `v0.1.0-rc.5` 均不能作为最终通过：`rc.1`-`rc.4` 门禁失败；`rc.5` Job 全绿但发布后附件名被 GitHub 改写，手工校验失败并已删除无效 Release。`rc.3` 中 Cloud Linux、三平台 Agent、macOS ARM 与 macOS Intel Desktop 均通过；Windows Desktop 失败于 Rust 源码无条件使用 Unix-only `rustix::process/Errno` 常量，`package` 与 `publish-pre` 正确跳过。`rc.5` 已证明 Desktop Windows Rust/NSIS、SHA-256 版本门禁、整组 package 与发布 Job 可运行；发布后验收发现 GitHub 会改写中文附件名。正在用 ASCII 公共附件名和发布后下载复核准备 `rc.6`。RC 目标地址为 `https://wt.longyanyue.cn`。Workspace GitHub Actions 已配置三个组件仓的只读 Deploy Key 和对应 Secret。
- 已验证：Workspace Release Manifest、环境注入、附件汇总单元测试及治理检查通过；`release.yml` 经 actionlint 校验；Cloud 打包/前端标记单元测试、Agent 冻结进程 smoke 单元测试通过；Cloud Web 487 项测试与 Desktop 507 项测试通过（Desktop 另有 6 项既有忽略）。
- GitHub 主干 CI：Cloud `37081704343` 成功、Agent `37081932453` 成功、Desktop `37082128429` 成功。Agent 首轮 CI 暴露既有 Linux 配置复制入口提前解析本机 Sidecar 架构，修复后成功。
- 前两轮 GitHub 试跑详情见 [github-rc-trial.md](evidence/github-rc-trial.md)。Cloud 根因是发布工作流选用 `go.mod` 声明的 Go 1.24 最低版本，与已通过主干 CI 的 Go 1.26.5 不一致；Windows Agent 清理故障在 `rc.2` 已修复。旧 Tag 保留，不移动。
- 未完成：产品 `rc.6` Manifest/发布后复核修复提交与 Tag 推送、GitHub 原生 Runner 重跑、Pre-release 附件核验和完整试跑报告。
- 特别发现：原 Desktop Web 某些页面及通用 HTTP 客户端将 Cloud 写死为本机地址，现按 Cloud 网页、Desktop 开发、打包 Desktop 三种运行形态读取各自地址；打包路径拒绝硬编码本机 Cloud 地址。
- 最近验证：Desktop 修复后本机 `cargo check --workspace` 通过；`scripts/test.sh` 通过（507 项 Rust 测试，6 项既有忽略；control 12 项、release-versions 20 项）。Workspace Release 单元测试 7 项通过（含非 ASCII 附件名规范化）、治理检查通过。RC4 Windows Runner 已通过 Rust Release 编译与 NSIS 打包；`release-versions.sh` 修复后本机 release-versions 20 项测试与 `--check` 通过，仍需 Runner 复验。
- 约束：各仓分别提交；所有 Tag 在代码、配置和校验固定后创建；生产部署不在本 CHG。
