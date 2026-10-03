# CHG-20261003-076 实施进度

- Status: IMPLEMENTING
- 当前：Cloud `61bd43f`、Agent `b0ab365`、Desktop `50f707a`、Workspace `7ca1cd5` 已在各仓 `main` 提交并推送。RC 目标地址为 `https://wt.longyanyue.cn`。Workspace GitHub Actions 已配置三个组件仓的只读 Deploy Key 和对应 Secret。
- 已验证：Workspace Release Manifest、环境注入、附件汇总单元测试及治理检查通过；`release.yml` 经 actionlint 校验；Cloud 打包/前端标记单元测试、Agent 冻结进程 smoke 单元测试通过；Cloud Web 487 项测试与 Desktop 507 项测试通过（Desktop 另有 6 项既有忽略）。
- GitHub 主干 CI：Cloud `37081704343` 成功、Agent `37081932453` 成功、Desktop `37081724377` 成功。Agent 首轮 CI 暴露既有 Linux 配置复制入口提前解析本机 Sidecar 架构，修复后成功。Desktop Windows 发布包的 Sidecar 记录要求补强后，新的主干 CI 尚待完成。
- 未完成：四仓组件/Product RC Tag、GitHub 原生 Runner 构建、Pre-release 附件核验和试跑报告。
- 特别发现：原 Desktop Web 某些页面及通用 HTTP 客户端将 Cloud 写死为本机地址，现按 Cloud 网页、Desktop 开发、打包 Desktop 三种运行形态读取各自地址；打包路径拒绝硬编码本机 Cloud 地址。
- 约束：各仓分别提交；所有 Tag 在代码、配置和校验固定后创建；生产部署不在本 CHG。
