# CHG-20261003-077 实施进度

- Status: IMPLEMENTING
- 当前：用户已确认仓库 `config/` 只用于本地测试，打包时由 `config_online/` 替换为部署包 `config/`，部署时按预发/生产变量表渲染并校验；部署包不保留 `config_test/`。运行目录统一由 `www` 管理。CHG-077 正在据此追加版本自包含目录、宝塔进程托管和 Server 提供 Cloud Web 的实施任务。RC8 保留为旧候选，不用于这套新方案的服务器部署。
- 已完成：部署包、配置模板、数据库 SQL 示例、进程模板、Cloud Web 站点配置与宝塔手册；本地 MySQL 8.4 空库迁移 50 个、重复迁移 0 个，管理员登录和三进程启动通过；Cloud CI、联合构建、Pre-release 附件回读与包摘要校验通过。
- 未完成：Cloud 追加逻辑、新组件与产品 RC、Artifact 校验、宝塔实际部署及人工验收。
- 阻塞：当前无代码阻塞；最终服务器数据库/账号创建与宝塔操作需要用户执行。
- 最近验证：RC8 Cloud Artifact 摘要 `c02b55ec6d52432fdd54e2fab0d4a045f066f67bbc7c23c83eb4cf80082c5865` 与 Pre-release `build-info.json` 一致；解压后 `deploy/verify-package.sh` 通过。
