# CHG-20261003-077 实施进度

- Status: IMPLEMENTING
- 当前：Cloud 组件 `v0.1.0-rc.6` 和产品 `v0.1.0-rc.8` 已固定。Cloud CI Run `37115882244`、产品 Run `37116209229` 均成功；RC8 为 GitHub Pre-release。等待宝塔实际部署与人工验收。
- 已完成：部署包、配置模板、数据库 SQL 示例、进程模板、Cloud Web 站点配置与宝塔手册；本地 MySQL 8.4 空库迁移 50 个、重复迁移 0 个，管理员登录和三进程启动通过；Cloud CI、联合构建、Pre-release 附件回读与包摘要校验通过。
- 未完成：宝塔实际部署及人工验收，记录模板见 `server-acceptance.md`。
- 阻塞：服务器数据库/账号创建与宝塔操作需要用户执行；当前无自动 SSH 部署权限或服务器私有配置。
- 最近验证：RC8 Cloud Artifact 摘要 `c02b55ec6d52432fdd54e2fab0d4a045f066f67bbc7c23c83eb4cf80082c5865` 与 Pre-release `build-info.json` 一致；解压后 `deploy/verify-package.sh` 通过。
