# Cloud 版本自包含部署验证

## 源码与 CI

- Cloud Commit：`99eaf30cdf08fdaa87c6799dce5cc8ca56b336cd`
- Cloud CI：[Run 37151385427](https://github.com/piqiu96/wt-media-cloud/actions/runs/37151385427)，结论 success。
- 覆盖：Bootstrap、Go 全量测试、Web 487 项测试、MySQL Migration、Linux amd64 六个二进制构建、部署/打包 Python 测试。

## 包结构

- Linux 单元测试确认 `config/` 与 `config_online/` 的归一化运行路径双向一致。
- 包内 `config/` 仅来自 `config_online/`，包含 `.toml.tpl` 和固定 `.toml`；不包含本地 `config/`、`config_test/`、真实凭据或旧 `deploy/config-template`。
- `deploy/verify-package.sh` 在结构等价包上通过，确认 50 个 SQL Migration、`bin/config-check`、环境渲染脚本和宝塔部署脚本齐全。

## 本地 MySQL 与进程验证

- 创建临时 MySQL 8.4 空库与专用账号。
- `online` 变量表渲染通过：`configuration valid`，模板全部转换为运行 `.toml`，无 `.tpl` 残留。
- 首次 Migration：`migration ok: 50 applied, 50 total`。
- 重复 Migration：`migration ok: 0 applied, 50 total`。
- 从 `current` 路径同时启动 Server、Discovery Worker、Discovery Scheduler，三个进程均保持运行。
- `/healthz`、`/api/v1/health`、`/`、`/login` 返回成功；未知 `/api/v1/not-found` 返回 404 且未回退 HTML。
- `admin / admin123` 登录通过；`users` 行为 `admin/admin/enabled`，`schema_migrations` 为 50。
- 安装第二版本、重新渲染 `pre` 配置并切换 `current` 后 Server 验收通过；随后切换回第一版本，确认 `current` 回退只改变软链。

## 本地变量上传辅助

- 用户要求的变量上传脚本仅存在于本机，不进入 Git：
  - `/Users/aqiuye/.wt-media/upload-config-variables.py`
  - `/Users/aqiuye/.wt-media/vars/cloud/online.json`
  - `/Users/aqiuye/.wt-media/vars/cloud/pre.json`
- 当前只做 dry-run；online 逻辑对象为 `wt-media/vars/cloud/online.json`。
- 未上传真实变量值，未记录数据库密码、管理员密码、对象存储密钥或平台凭据。

## 边界

- 尚未执行真实宝塔安装、外部 HTTPS 验收或生产对象存储写入。
- 临时 MySQL 数据库和账号已删除。
