# CHG-20261003-076 实施进度

- Status: DONE
- 当前：`v0.1.0-rc.6` 已完成最终打包闭环。用户修复 GitHub 计费后 rerun `package`/`publish-pre` 成功；Pre-release 附件下载与 SHA-256 复核通过，用户反馈客户端可正常打开。
- 已验证：Workspace Release Manifest、环境注入、附件汇总单元测试及治理检查通过；`release.yml` 经 actionlint 校验；Cloud 打包/前端标记单元测试、Agent 冻结进程 smoke 单元测试通过；Cloud Web 487 项测试与 Desktop 507 项测试通过（Desktop 另有 6 项既有忽略）。
- GitHub 主干 CI：Cloud `37081704343` 成功、Agent `37081932453` 成功、Desktop `37082128429` 成功。Agent 首轮 CI 暴露既有 Linux 配置复制入口提前解析本机 Sidecar 架构，修复后成功。
- 前两轮 GitHub 试跑详情见 [github-rc-trial.md](evidence/github-rc-trial.md)。Cloud 根因是发布工作流选用 `go.mod` 声明的 Go 1.24 最低版本，与已通过主干 CI 的 Go 1.26.5 不一致；Windows Agent 清理故障在 `rc.2` 已修复。旧 Tag 保留，不移动。
- 未完成：无。云端部署、生产数据库与默认管理员属于后续 CHG，不在本 CHG 范围。
- 特别发现：原 Desktop Web 某些页面及通用 HTTP 客户端将 Cloud 写死为本机地址，现按 Cloud 网页、Desktop 开发、打包 Desktop 三种运行形态读取各自地址；打包路径拒绝硬编码本机 Cloud 地址。
- 最近验证：Desktop 修复后本机 `cargo check --workspace` 通过；`scripts/test.sh` 通过（507 项 Rust 测试，6 项既有忽略；control 12 项、release-versions 20 项）。Workspace Release 单元测试 7 项通过（含非 ASCII 附件名规范化）、治理检查通过。RC4 Windows Runner 已通过 Rust Release 编译与 NSIS 打包；`release-versions.sh` 修复后本机 release-versions 20 项测试与 `--check` 通过，仍需 Runner 复验。
- 约束：各仓分别提交；所有 Tag 在代码、配置和校验固定后创建；生产部署不在本 CHG。

- 最终验证：Run `37091241538` 成功；RC6 Pre-release 附件 5 项下载校验通过；Cloud/Agent/Desktop 来源与摘要记录见 [rc6-release-verification.md](evidence/rc6-release-verification.md)。
