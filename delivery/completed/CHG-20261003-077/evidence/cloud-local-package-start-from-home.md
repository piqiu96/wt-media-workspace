# Cloud 本机打包与 Home 目录启动演练

- 日期：2026-10-07；源码：Cloud commit `be1d1a1`；平台：macOS arm64。正式 `scripts/dev/build-release-linux.sh` 只接受 Linux amd64，因此本次构建同目录结构的本机演练包，不充当 Linux 发布制品。
- 产物：`/tmp/wt-media-cloud-local-smoke.n8Tlu5/`；本机编译 6 个 Go 程序，`npm run build:cloud --prefix web` 重新生成 Cloud Web，并组装 `bin/`、`web/`、`migrations/`、`deploy/`、`config/`、`logs/`。本地配置目录用链接复用现有开发配置；演练 `app.toml` 将初始管理员置空并改监听 `127.0.0.1:18081`，避免写入管理员或占用已有 `18080` 服务。目录权限为当前用户私有。该演练包依赖本机配置链接，不是可分发的独立制品。
- 配置验证：从 `/Users/aqiuye` 执行包内 `bin/config-check`，期望配置有效，实际输出 `configuration valid`，PASS。
- 启动：从 `/Users/aqiuye` 执行包内 `bin/wt-media-cloud`，期望根据二进制位置解析发布根目录并持续运行。实际启动日志显示 home、config、logs、web、migrations 全部位于 `/private/tmp/wt-media-cloud-local-smoke.n8Tlu5/`；`lsof -d cwd` 显示进程工作目录为 `/Users/aqiuye`，监听 `127.0.0.1:18081`，PASS。
- HTTP 验证：`GET /healthz` = 200 `ok`；`GET /api/v1/health` = 200；`GET /login` = 200 HTML；未知 `GET /api/v1/no-such-route` = 404，PASS。
- 日志验证：演练包的 `logs/app.log` 存在并包含 `cloud_logger_ready`；`logs/access.log` 存在并记录健康请求，PASS。
- 收尾：向本次演练进程发送 SIGINT 后，`18081` 关闭，原有 `18080` 保持监听，PASS。Cloud 工作树无新增修改。
