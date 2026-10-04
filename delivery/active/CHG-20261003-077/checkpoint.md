# CHG-20261003-077 实施进度

- Status: IMPLEMENTING
- 当前：用户要求缩减 TPL 变量并清理旧本地变量目录后，Cloud `v0.1.0-rc.8`（`48d57d8`）已通过 CI `37175720841`。固定配置已内联，变量由 25 个缩减到 11 个；产品 `v0.1.0-rc.11` 已准备。RC10 的发布回读已验证；RC11 将验证缩减变量后的制品，再由用户按手册执行 online 上线并回填 `server-acceptance.md`。
- 已完成：Cloud 版本自包含安装、`pre|online` 模板渲染、`config-check`、宝塔 Go 项目/进程管理器手册、Cloud Web 与 SPA 回退；Cloud CI、Go/Web、部署/打包测试和本地 MySQL/三进程验收通过。
- 未完成：RC11 产品 Run/Artifact 回读、宝塔实际部署与人工验收。
- 阻塞：当前无代码阻塞；最终服务器数据库/账号创建与宝塔操作需要用户执行。
- 最近验证：RC10 Run `37153380541` 全部成功；Pre-release 附件 SHA256SUMS 回读通过；Cloud tar 摘要 `5844a1e2...c0d1`、Workspace 源码 `25ee311`。本地 MySQL 8.4 首次 Migration 50、重复 0，登录、三进程、Web/API 404、第二版本切换与回退均通过。

- 本地私有变量：已删除旧 `~/.wt-media/config-variables/`；当前使用 `~/.wt-media/upload-config-variables.py` 和 `~/.wt-media/vars/cloud/{pre,online}.json`，两者各 11 个变量，当前只 dry-run online，脚本不入 Git。
