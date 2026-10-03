# CHG-20261003-076 实施进度

- Status: IMPLEMENTING
- 当前：产品 `v0.1.0-rc.1` 已触发 GitHub 试跑但未发布；修复 Cloud Linux 构建和 Windows Agent smoke 后准备 `v0.1.0-rc.2`。Cloud 修复提交 `de9da96`、Agent 修复提交 `ac7f0b6` 已推送；Desktop 组件沿用无改动的 `v0.1.0-rc.1`。RC 目标地址为 `https://wt.longyanyue.cn`。Workspace GitHub Actions 已配置三个组件仓的只读 Deploy Key 和对应 Secret。
- 已验证：Workspace Release Manifest、环境注入、附件汇总单元测试及治理检查通过；`release.yml` 经 actionlint 校验；Cloud 打包/前端标记单元测试、Agent 冻结进程 smoke 单元测试通过；Cloud Web 487 项测试与 Desktop 507 项测试通过（Desktop 另有 6 项既有忽略）。
- GitHub 主干 CI：Cloud `37081704343` 成功、Agent `37081932453` 成功、Desktop `37082128429` 成功。Agent 首轮 CI 暴露既有 Linux 配置复制入口提前解析本机 Sidecar 架构，修复后成功。
- 首轮 GitHub 试跑：`v0.1.0-rc.1` Run `37082431936` 的 Manifest/跨仓读取与 macOS Intel、ARM Agent 成功；Cloud Linux 构建与 Windows Agent smoke 失败，Desktop/汇总/发布按门禁跳过。Cloud 失败是 `CGO_ENABLED=0` 下 sonic/loader 与 Go 1.26 Linux 链接不兼容；Windows Agent 已健康但 PyInstaller 子进程占用临时日志导致清理失败。原 Tag 保留，不移动。
- 未完成：`rc.2` 组件/Product Tag、GitHub 原生 Runner 构建、Pre-release 附件核验和完整试跑报告。
- 特别发现：原 Desktop Web 某些页面及通用 HTTP 客户端将 Cloud 写死为本机地址，现按 Cloud 网页、Desktop 开发、打包 Desktop 三种运行形态读取各自地址；打包路径拒绝硬编码本机 Cloud 地址。
- 约束：各仓分别提交；所有 Tag 在代码、配置和校验固定后创建；生产部署不在本 CHG。
