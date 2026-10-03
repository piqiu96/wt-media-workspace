# CHG-20261003-077 实施进度

- Status: IMPLEMENTING
- 当前：Cloud `v0.1.0-rc.7`（`99eaf30`）已通过 CI `37151385427` 完成版本自包含部署实现。RC9 的全部组件构建成功，但 Workspace 旧版 Cloud payload 单测仍要求 systemd/Nginx，`package` 在任何下载前失败；已补齐模板态 payload 单测并准备 RC10。RC8/RC9 保留为旧候选。
- 已完成：Cloud 版本自包含安装、`pre|online` 模板渲染、`config-check`、宝塔 Go 项目/进程管理器手册、Cloud Web 与 SPA 回退；Cloud CI、Go/Web、部署/打包测试和本地 MySQL/三进程验收通过。
- 未完成：产品 RC10 GitHub Run、Cloud Artifact/Pre-release 回读、宝塔实际部署及人工验收。
- 阻塞：当前无代码阻塞；最终服务器数据库/账号创建与宝塔操作需要用户执行。
- 最近验证：Cloud CI `37151385427` 成功；Workspace RC9 Run `37151749201` 的 Cloud/Agent/Desktop 构建全部通过，失败仅在旧 payload 单测检查；修正后 11 项 Workspace release 测试通过。本地 MySQL 8.4 首次 Migration 50、重复 0，登录、三进程、Web/API 404、第二版本切换与回退均通过。

- 本地私有变量：`~/.wt-media/upload-config-variables.py`；环境目录 `~/.wt-media/vars/cloud/{pre,online}.json`，当前只 dry-run online，未执行真实上传，脚本不入 Git。
