# Cloud 运行根路径与启动日志验证

- 日期：2026-10-04
- 范围：CHG-20261003-077 Task 10；Cloud commit `620cf89` 与临时二进制，不代表宝塔服务器验收。

| 操作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 先运行新增 `internal/config`、`internal/bootstrap` 目标测试 | 旧代码暴露 cwd 依赖和诊断缺口 | 5 项目标测试按预期失败：缺配置时根路径退回 cwd；相对子路径覆盖值按 cwd 解析；相对根路径未拒绝；资源错误无步骤名；启动无路径日志 | PASS（RED） |
| 修改后运行 `go test ./internal/config ./internal/bootstrap ./cmd/config-check ./cmd/migrate -count=1` | 受影响包通过 | 两个测试包通过；两个命令包编译通过 | PASS |
| `go vet ./internal/config ./internal/bootstrap ./cmd/config-check ./cmd/migrate` | 无静态检查错误 | 退出码 0 | PASS |
| `python3 -m unittest scripts.verify.test_package_release_linux -v` | 部署包校验不受影响 | 3 项测试通过 | PASS |
| `go test ./... -count=1` | 全仓 Go 测试通过 | 全部包通过，退出码 0 | PASS |
| 构建临时 `<release>/bin/wt-media-cloud`，从 `/private/tmp` 启动且不给该 release 创建 `config/app.toml` | 输出以二进制的 release 为根，明确报缺少绝对配置路径与 `config` 步骤 | `cloud_runtime_paths` 给出 `<release>/{config,logs,web,migrations}`；`cloud_bootstrap_failed step=config` 与最终错误都指向 `<release>/config/app.toml`，退出码 1 | PASS |
| 从 `/private/tmp` 执行临时发布包的 `bin/migrate -h` 与 `bin/config-check -h` | 默认目录由临时发布根路径派生 | 帮助信息分别显示绝对 `<release>/migrations` 和 `<release>/config` | PASS |
| `git diff --check` | 无空白错误 | 退出码 0 | PASS |

真实宝塔进程、私有配置、日志权限与外部 HTTPS/登录仍须在服务器验收中核对。
独立代码复核未发现需修改的问题；第三方初始化错误的脱敏行为未作专项验证。
