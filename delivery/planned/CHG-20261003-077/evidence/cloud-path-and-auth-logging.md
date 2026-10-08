# Cloud 启动路径、二进制名与认证日志修正

## 现场故障

线上宝塔启动 Server 时报：

```text
stat config config/app.toml: stat config/app.toml: no such file or directory
/www/server/go_project/vhost/scripts/server.sh: line 6: ./bin/server: No such file or directory
```

读宝塔生成的脚本确认它执行 `cd /home/www/wt-media-cloud/current/bin` 后再启动二进制；而 Server/Worker/Scheduler 当时按**当前工作目录**解析 `config/`、`web/`、`logs/`，所以从 `current/bin` 启动必然找不到配置。这是路径解析缺陷，不是包或数据库问题。

## 修正

- 根路径（ENV_PATH）解析顺序：`WT_MEDIA_CLOUD_HOME` → 运行中二进制的 `<home>/bin/<binary>` 上级目录 → 当前工作目录；结果始终绝对化。
- 子路径默认由根路径派生，并可单独覆盖：`WT_MEDIA_CLOUD_CONFIG_PATH`、`WT_MEDIA_CLOUD_LOG_PATH`、`WT_MEDIA_CLOUD_WEB_PATH`。
- 日志配置里的相对 `path` 锚定到日志目录（模板从 `logs/app.log` 改为 `app.log`）。
- 发布二进制改名 `bin/server` → `bin/wt-media-cloud`；`cmd/server` 源目录不变，打包、包结构校验、`wtmctl` 进程检查与手册同步更新。
- `wtmctl` 从包的 `release-info.json` 推导 `release`/`package_root`，安装类命令回退 `current`；示例 profile 不再固化版本。

## 认证日志

线上 401 无法定位，因此在认证关键路径补日志：

- 登录成功/失败：`module=identity action=login result=ok|failed`，带 `username`、`client_type`、`replace_existing`、`origin`、`ip`、`reason`。
- 鉴权失败：`module=auth result=denied`，带 `credential_present`、`ip`、`origin`、`path`、`reason`。
- reason 取值稳定可检索：`invalid_credentials`、`session_replace_needed`、`session_invalid`、`missing_credential`、`forbidden`、`internal_error`。
- 不记录密码与会话 token；意外错误按 error 级别记录。日志经 Hertz 全局 logger 输出，生产落到 `app.log`，且在 logger 初始化前不会 panic。

## 验证

- `go test ./...`、`go vet`、`gofmt`、`git diff --check` 通过；Cloud CI `37198945138` 通过。
- 新增 `TestLogAuthenticationFailureWritesReason` 断言拒绝原因确实写入日志文件；新增 `TestAuthenticationFailureReason`、`TestLoginFailureReasonIsGreppable`。
- 新增 `TestResolvePackageReleaseDerivesFromPackage`、`TestResolveInstalledReleaseFallsBackToCurrent`。
- 本地结构等价包上，profile 省略 `release`/`package_root` 时 `wtmctl artifact verify`、`doctor`（`release=v0.1.0-rc.13`）、`deploy plan`（拉取 11 个变量并渲染）均通过。

## 边界

- 尚未执行真实宝塔安装、外部 HTTPS 验收；这些由用户在服务器验收中执行并回填 `server-acceptance.md`。
