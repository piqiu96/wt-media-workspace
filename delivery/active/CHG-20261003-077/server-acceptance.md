# CHG-20261003-077 宝塔预发布人工验收记录

本记录在实际服务器部署时填写。Cloud 包内步骤见 `wt-media-cloud/deploy/DEPLOYMENT.md`；这里不记录数据库密码、管理员密码、平台密钥或对象存储密钥。

## 版本与安装

| 项目 | 实际值 / 证据 |
| --- | --- |
| 产品 Tag | `v0.1.0-rc.10` |
| Cloud 组件 Tag | `v0.1.0-rc.7` |
| GitHub Actions Run URL | [RC10 Run 37153380541](https://github.com/piqiu96/wt-media-workspace/actions/runs/37153380541)，结论 success |
| Cloud Artifact 文件名与 SHA-256 | `wt-media-cloud_v0.1.0-rc.10_linux-amd64.tar.gz`；`5844a1e2da2bc95b40135d74e6fa58c400584959a4a5cc063ba64e7df1a4c0d1` |
| Cloud 源码 Commit | `99eaf30cdf08fdaa87c6799dce5cc8ca56b336cd` |
| 服务器系统、CPU 架构、宝塔版本 | 待填写 |
| 安装路径与 `current` 指向 | 待填写 |
| 维护提示开始/结束时间 | 待填写 |

## 数据与配置

| 检查项 | 结果 / 证据 |
| --- | --- |
| 已手动创建预发布 MySQL 库与专用账号；目标库名/主机 | 待填写 |
| 迁移前 MySQL 备份位置与恢复演练结果 | 待填写 |
| 对象存储备份或隔离前缀 | 待填写 |
| 版本内 `config/` 权限、`online` 环境记录、HTTP 监听地址、HTTPS 域名 | 待填写 |
| 首次迁移结果（应为 50 个） | 待填写 |
| 重复迁移结果（应为 0 个） | 待填写 |
| `schema_migrations` 与 `users` 管理员行检查 | 待填写 |

## 运行验收

| 检查项 | 结果 / 证据 |
| --- | --- |
| 宝塔 Go 项目 Server / 进程管理器 Scheduler、Worker 状态 | 待填写 |
| 本机 `/healthz` 和 `/api/v1/health` | 待填写 |
| HTTPS 域名健康接口与 Web 页面 | 待填写 |
| HTTPS `/login` 刷新后仍能加载 Cloud Web；`/api/v1/health` 为 JSON | 待填写 |
| 初始管理员 `admin/admin123` 登录 | 待填写 |
| 回退切换演练或未执行原因 | 待填写 |
| 异常、处理与发布结论 | 待填写 |

此记录只覆盖 Cloud 预发布安装与基础运行。对象存储业务写入、BitBrowser、真实发布流程和正式版上线另行验收。

变量表：`wt-media/vars/cloud/online.json`；本地私有上传工具 `/Users/aqiuye/.wt-media/upload-config-variables.py`（不入 Git）。
