# M-first-production-release：首次全端上线

- 状态：执行中；RC GitHub 打包闭环已完成，当前准备 Cloud 预发布部署与数据库初始化。
- 依据：[首次全端上线部署计划](../../docs/superpowers/specs/2026-10-02-first-production-deployment-plan.md)。

## RC 打包验证闭环

- 用户目标：仅用 GitHub 托管 Runner，从固定的四仓 Tag 生成 Cloud Linux 包和 Windows x64、macOS Intel、macOS ARM 客户端包，并发布可核对的 GitHub RC Pre-release。
- 前置：四仓源码与组件 Tag 固定；Workspace 产品 RC Tag 对应简版 Release Manifest；跨私有仓库只读访问可用；预发布 Cloud 地址或明确的不可连接测试地址已锁定。
- 用户操作：评审通过后要求执行；实施准备完成后推送产品 RC Tag。
- 系统动作：同一 `build → verify → package` 链路检查版本组合、平台、配置、Sidecar 和摘要，任何平台失败都不公开整组 Pre-release。
- 成功事实：Cloud、Agent、Desktop 目标制品及来源和摘要齐全，GitHub Pre-release 中三平台客户端附件完整，试跑报告说明烟测边界。
- 失败行为：不得从 `main` 或 `latest` 偷取源码；不得以编译成功宣称真实登录、BitBrowser、对象存储或宝塔部署通过；不得移动旧 Tag 或混用不同 RC 的包。
- 当前实施单元：[CHG-20261003-076](../completed/CHG-20261003-076/change.md)。

后续预发布环境与首次生产切换按部署计划另行实施，不由本闭环的打包通过自动宣布完成。

## Cloud 预发布部署与数据库初始化

- 用户目标：把已通过 GitHub 打包闭环的 Cloud Linux 制品变成可上传宝塔的独立部署包，并提供可重复执行的数据库准备、迁移、启动和验收步骤。
- 前置：RC 打包链路可用；用户能创建目标 MySQL 数据库/账号；服务器可托管 Cloud 进程并配置 HTTPS 反向代理；敏感生产配置只存在于服务器。
- 用户操作：创建数据库与专用账号，裁定初始管理员策略，上传/执行部署包，并按手册回填部署证据。
- 系统动作：校验固定版本与摘要，注入服务器私有配置，对显式目标库应用 Migration，启动 API Server、Discovery Scheduler、Discovery Worker，并验证健康、登录和关键表。
- 成功事实：Cloud 包、迁移、配置模板、进程模板和验收脚本齐全；空库迁移与重复迁移通过；初始管理员可登录；三个 Cloud 进程健康。
- 失败行为：不隐式创建或猜测生产库；迁移失败不得启动服务；不得把敏感凭据写入仓库或制品；不得把打包、部署或登录成功扩大为业务发布或正式稳定版上线。
- 当前实施单元：[CHG-20261003-077](../active/CHG-20261003-077/change.md)。
