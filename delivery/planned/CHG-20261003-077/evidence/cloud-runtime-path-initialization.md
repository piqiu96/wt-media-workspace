# Cloud 启动路径一次初始化验证

- 变更：Cloud commit `be1d1a1`。路径在启动时通过 `MustInitializeRuntimePaths` 解析并保存；`GetRuntimePaths` 返回已保存值，未初始化读取 panic。`config.Initialize`、Bootstrap 配置资源、Migration 和配置检查入口先初始化；运行路径消费者只读取 getter。
- RED：`go test ./internal/config -run '^TestRuntimePathsProcessLifecycle$' -count=1` 因全局初始化接口缺失而构建失败；补接口后，`load-before-init` 子进程测试显示旧 `Load()` 未 panic，目标用例失败。
- RED：`go test ./internal/bootstrap -run '^TestConfigResourcePanicsOnBadRuntimeHome$' -count=1` 显示旧启动资源返回错误而未 panic；`TestInitializePublishesValidatedReadOnlyConfig` 显示直接调用配置初始化时没有先初始化路径。
- GREEN：`go test ./internal/config ./internal/bootstrap -count=1` 通过；`go test ./... -count=1` 全部通过；`go vet ./internal/config ./internal/bootstrap ./cmd/config-check ./cmd/migrate` 通过；Cloud 和 Workspace `git diff --check` 通过。
- 实际二进制：临时 `<release>/bin/wt-media-cloud` 从 `/tmp` 执行且缺少配置时，启动日志将 home/config/logs/web/migrations 均定位到该 release，并记录 `step=config` 和绝对配置路径；`WT_MEDIA_CLOUD_HOME=relative-release` 时进程 panic，错误包含变量名和绝对路径要求。
- 工作区治理：`python3 scripts/verify_delivery_governance.py` 通过。宝塔服务器安装与登录验收尚需用户在目标环境执行；本次未发布新 Tag/Artifact。
