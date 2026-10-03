# CHG-20261003-077 实施进度

- Status: IMPLEMENTING
- 当前：产品 `v0.1.0-rc.10` 已成功发布 Pre-release，Cloud 使用 `v0.1.0-rc.7`（`99eaf30`）。Cloud Artifact、三平台附件、build-info 和 SHA256SUMS 已验证；当前唯一剩余工作是用户按手册在宝塔执行 online 部署并回填 `server-acceptance.md`。
- 已完成：Cloud 版本自包含安装、`pre|online` 模板渲染、`config-check`、宝塔 Go 项目/进程管理器手册、Cloud Web 与 SPA 回退；Cloud CI、Go/Web、部署/打包测试和本地 MySQL/三进程验收通过。
- 未完成：宝塔实际部署与人工验收。
- 阻塞：当前无代码阻塞；最终服务器数据库/账号创建与宝塔操作需要用户执行。
- 最近验证：RC10 Run `37153380541` 全部成功；Pre-release 附件 SHA256SUMS 回读通过；Cloud tar 摘要 `5844a1e2...c0d1`、Workspace 源码 `25ee311`。本地 MySQL 8.4 首次 Migration 50、重复 0，登录、三进程、Web/API 404、第二版本切换与回退均通过。

- 本地私有变量：`~/.wt-media/upload-config-variables.py`；环境目录 `~/.wt-media/vars/cloud/{pre,online}.json`，当前只 dry-run online，未执行真实上传，脚本不入 Git。
