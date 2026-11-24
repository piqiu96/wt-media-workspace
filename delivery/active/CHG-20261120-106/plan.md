# Desktop 环境身份与数据隔离实施计划

目标：Desktop environment 独立于 cloud_env；dev/test/prod 使用独立目录与应用身份，DEV/TEST 图标；正式流水线保持 release+prod 门禁。

已由用户确认执行，沿用 CHG106 分支，不修改 Cloud 后端或 Agent 业务执行逻辑。

- [x] Desktop：先添加失败回归，分离编译模式和桌面身份；安装包限制仍依照 release 编译，禁止回退系统 Python。
- [x] Desktop：Dev/Test 系统目录、正式原目录；统一设置、日志、清理、诊断、WebView 身份；显式传入 Agent 目录和日志。
- [x] Desktop：DEV/TEST 图标、名称、窗口标题与应用标识；可复用的打包入口与正式 release+prod 校验。
- [x] Cloud web：从原生 environment 初始化桌面品牌，登录页和侧栏同步标记，Web 入口保持现状。
- [x] Workspace：固定正式构建身份并校验；同步工程定义与 CHG106 范围。
- [x] 验证：Rust、受影响前端、构建门禁；dev/test 连接 prod 身份不变、SQLite 隔离、正式目录兼容。记录真实通过/未验证项。

Review重点：测试包使用 release 仍为 test；Cloud URL 不决定桌面身份；环境配置失败不偷偷落入正式目录；清理和导出仅当前环境；正式流水线拒绝 dev/test/debug。

本轮实现与自动化验证完成，实际安装器和并行登录限制见 [验证记录](evidence/desktop-environment.md)。2026-11-24四仓合入后，当前状态见[CHG定义](change.md)；环境隔离完成不代替整项签收。
