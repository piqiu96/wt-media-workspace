# CHG-20261003-077 实施进度

- Status: IMPLEMENTING
- 当前：用户要求缩减 TPL 变量并清理旧本地变量目录后，Cloud `v0.1.0-rc.8`（`48d57d8`）已通过 CI `37175720841`。固定配置已内联，变量由 25 个缩减到 11 个；产品 `v0.1.0-rc.11` 已成功发布，Cloud 使用 `v0.1.0-rc.8`（`48d57d8`）。RC11 已将模板变量缩减为 11 个，并将 4 项测试环境凭据写入本地 `online/pre` 变量表（Agent token 在测试配置中为空）；Cloud Artifact、三平台附件、build-info 和 SHA256SUMS 已回读验证。
- 已完成：Cloud 版本自包含安装、`pre|online` 模板渲染、`config-check`、宝塔 Go 项目/进程管理器手册、Cloud Web 与 SPA 回退；Cloud CI、Go/Web、部署/打包测试和本地 MySQL/三进程验收通过。
- 未完成：宝塔实际部署与人工验收。
- 阻塞：当前无代码阻塞；最终服务器数据库/账号创建与宝塔操作需要用户执行。
- 最近验证：RC11 Run `37175924935` 全部成功；Pre-release 附件 SHA256SUMS 回读通过；Cloud tar 摘要 `205ff843...7d22`、Workspace 源码 `916c0be`、Cloud 源码 `48d57d8`。本地 MySQL 8.4 首次 Migration 50、重复 0，登录、三进程、Web/API 404、第二版本切换与回退均通过。

- 本地私有变量：已删除旧 `~/.wt-media/config-variables/`；当前使用 `~/.wt-media/upload-config-variables.py` 和 `~/.wt-media/vars/cloud/{pre,online}.json`，两者各 11 个变量，当前只 dry-run online，脚本不入 Git。
