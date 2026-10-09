# wtmctl 一键部署收敛验证

## 目标

将 Cloud 部署从「Python + shell + curl/mysql CLI 逐条执行」收敛为单个自包含 Go 二进制 `bin/wtmctl`，并用 TOML 变量表替代 JSON。宝塔仍是唯一的进程管理器，`wtmctl` 不启停任何 Cloud 进程。

## 源码与 CI

- Cloud Commit：`1d6457f97006742d5e4d743a01a06767de66b2c6`，组件 Tag `v0.1.0-rc.9`。
- Cloud CI：[Run 37182796598](https://github.com/piqiu96/wt-media-cloud/actions/runs/37182796598)，结论 success。
- 覆盖：`go test ./...`、Web 测试、MySQL Migration、Linux amd64 六个二进制构建（含 `wtmctl`）、打包测试。

## 实现

- `cmd/wtmctl`、`internal/deploy/*` 提供：`version`、`doctor`、`vars pull|check`、`artifact verify`、`config render|check`、`db migrate|verify`、`deploy plan|apply|verify`、`release rollback`、`service check`、`status`。
- `deploy apply` 一键完成：校验 Artifact → 拉取远端 `online.toml` → 校验 Schema/必填/Secret → 安装 `releases/<tag>` → 渲染私有 `config/` → Migration → 数据库验证 → 原子切换 `current` → 输出需宝塔重启的进程。
- 删除 `deploy/init-config.sh`、`render-config.py`、`install.sh`、`activate.sh`、`rollback.sh`、`migrate.sh`、`verify-package.sh`、`verify-database.sh`、`verify-runtime.sh` 及 `scripts/verify/test_deployment_package.py`。
- 变量 Schema `deploy/config-variable-schema.toml` 声明 11 个变量；打包前校验 Schema 与模板一致，部署前校验实际取值。

## 本地验证

- `go test ./cmd/wtmctl ./internal/deploy`、`go test ./...`、`go vet`、`gofmt -l` 通过；`git diff --check` 干净。
- `scripts/verify/test_package_release_linux`、`test_stamp_desktop_web` 通过；新增用例要求包内 `bin/wtmctl` + Schema，且不含 `deploy/*.py`。
- `wtmctl vars check --file online.toml` 通过（11 个变量）；`wtmctl vars pull` 用真实预签名 URL 拉取并落盘（mode 0600）；`wtmctl config render` 对真实 `config_online` 模板渲染并通过 Cloud 自身 `LoadFromDir` 校验（`database/primary.toml`、`credentials/*`、`storage/object_storage.toml` 均生成，无 `.tpl` 残留）。

## 变量迁移

- 本地 helper `/Users/aqiuye/.wt-media/upload-config-variables.py` 改为 TOML：`--init-variables-file` 生成 TOML、上传对象键 `wt-media/vars/cloud/<env>.toml`、预签名文件 `<env>.url`。
- 已把 `~/.wt-media/vars/cloud/{online,pre}.json` 迁移为 `{online,pre}.toml`（各 11 个变量，round-trip 校验一致），上传到 `wt-media/vars/cloud/{online,pre}.toml`，远端回读 SHA-256 与本地一致；旧 `*.json`/`online.json.url` 已删除。
- helper 与变量文件均不入 Git；未打印未提交任何密钥值。

## GitHub RC12 回读

- 产品 Tag `v0.1.0-rc.12`，Release Run `37182978601` 全绿（validate、build-cloud、build-agent×3、build-desktop×3、package、publish-pre）。
- `package` 作业对真实 Cloud Artifact 运行 `verify_cloud`（要求 `bin/wtmctl`、`deploy/config-variable-schema.toml`、`deploy/examples/*`，禁止 `deploy/*.py|*.sh`，校验占位符与 `release-info.json`）并通过。
- `build-info.json`：Cloud Artifact `wt-media-cloud_v0.1.0-rc.12_linux-amd64.tar.gz` SHA-256 `90026317ef333c6609a7bedd5d51aadfbdedc056a3365c1be00bb1dfab956fb6`；Desktop Web `desktop-web_v0.1.0-rc.12.tar.gz` SHA-256 `15dc93cb4cf912f6bc17f524686b17bfb211381e33d0926a2b3970d085e33e52`；workspace `82de3ce`、cloud `1d6457f`。

## 边界

- 尚未执行真实宝塔安装、外部 HTTPS 验收或生产对象存储写入；这些由用户在服务器验收中执行并回填 `server-acceptance.md`。
