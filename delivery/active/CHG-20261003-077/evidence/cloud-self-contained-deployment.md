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

## GitHub RC10 回读

- 产品 Run：`37153380541`，全 Job success。
- Pre-release：https://github.com/piqiu96/wt-media-workspace/releases/tag/v0.1.0-rc.10
- Cloud Artifact ID `11284707837`；包内 Cloud tar SHA-256 `5844a1e2da2bc95b40135d74e6fa58c400584959a4a5cc063ba64e7df1a4c0d1`。
- Desktop Web SHA-256 `628ab41e68874da643b85d7610d077b92a4c4a7be51cea61388940a7ca4ffebb`。
- Pre-release 三平台附件、Manifest、build-info 和 SHA256SUMS 下载校验全部通过。
- Workspace source commit `25ee3110f2613083346f30653032848371518ef6`；Manifest environment=`online`。

## 变量缩减与旧目录清理

- 用户要求核对 `/Users/aqiuye/.wt-media/config-variables`：该目录已失效，已删除；当前只使用 `/Users/aqiuye/.wt-media/vars/cloud/{pre,online}.json`。
- 固定配置不再使用变量：app/admin/server、Agent API endpoint、抖音 endpoint、对象存储 endpoint/bucket/region/use_ssl。
- 当前模板变量 11 个：Primary DB 5 个、Agent/抖音/对象存储凭据 5 个、对象存储环境前缀 1 个。
- Cloud `v0.1.0-rc.8` 基于 `48d57d8`，CI `37175720841` 通过。
- 本地 online 变量 dry-run 通过：11 keys，SHA-256 `6da408b7314f29392e550c767289dc4ca103291ad9160fd525486f72d14b5bfe`；未上传真实变量。
