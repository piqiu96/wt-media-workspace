# CHG-20261003-077 实施进度

- Status: IMPLEMENTING
- 当前：Cloud `v0.1.0-rc.7`（`99eaf30`）已通过 CI `37151385427` 完成版本自包含部署实现。Workspace `v0.1.0-rc.9` Manifest 已固定 Cloud rc7、Agent rc2、Desktop rc3 和 `online` 环境；下一步推送产品 Tag 并核验完整 Artifact/Pre-release。RC8 保留为旧候选。
- 已完成：Cloud 版本自包含安装、`pre|online` 模板渲染、`config-check`、宝塔 Go 项目/进程管理器手册、Cloud Web 与 SPA 回退；Cloud CI、Go/Web、部署/打包测试和本地 MySQL/三进程验收通过。
- 未完成：产品 RC9 GitHub Run、Cloud Artifact/Pre-release 回读、宝塔实际部署及人工验收。
- 阻塞：当前无代码阻塞；最终服务器数据库/账号创建与宝塔操作需要用户执行。
- 最近验证：Cloud CI `37151385427` 成功；本地 MySQL 8.4 空库首次 Migration 50、重复 0，`admin/admin123` 登录、三进程、Web/API 404 边界、第二版本切换与回退均通过。

- 本地私有变量：`~/.wt-media/upload-config-variables.py`；环境目录 `~/.wt-media/vars/cloud/{pre,online}.json`，当前只 dry-run online，未执行真实上传，脚本不入 Git。
