# CHG-20261003-077：Cloud 预发布部署包与数据库初始化

- Status: IMPLEMENTING
- Level: L
- Milestone: `delivery/milestones/M-first-production-release.md#cloud-预发布部署与数据库初始化`
- References: `docs/superpowers/specs/2026-10-02-first-production-deployment-plan.md` §5.1、§7；`docs/superpowers/specs/2026-10-04-baota-cloud-deployment-layout-design.md`；`docs/decisions/0020-tagged-release-and-environment-config.md`；已完成 [CHG-20261003-076](../../completed/CHG-20261003-076/change.md)。
- Affected repositories: `wt-media-cloud`、`wt-media-workspace`。
- 用户目标：基于 RC6 后的固定源码产出可上传宝塔的 Cloud 独立部署包、可执行数据库初始化/迁移步骤，并初始化管理员。

## 目标与范围

1. Cloud Linux 部署包包含现有可执行程序、Cloud Web、FFmpeg/FFprobe、`migrations/`、从 `config_online/` 生成的包内 `config/` 模板、版本/摘要记录和服务器安装/验收脚本；本地 `config/` 不得进入制品。
2. 提供数据库准备模板：用户可先创建专用数据库和账号；部署脚本只对显式目标库执行迁移，不隐式创建生产库。
3. 提供宝塔/服务器可执行步骤：每个版本自包含私有 `config/`、`logs/`、`data/tmp/`，由单一 `current` 软链切换；执行迁移后，以宝塔 Go 项目启动 Server、宝塔进程管理器启动 Scheduler/Worker，并验证 Web、健康与登录。
4. 用新的 Cloud 组件 Tag 和产品 Tag 重新生成可部署 Cloud Artifact；客户端无变更时沿用已验证组件 Tag。
5. 记录预发布部署边界：不宣称对象存储、BitBrowser、业务发布或正式稳定版上线通过。
6. Cloud Server 提供包内 Cloud Web 静态文件与 Vue history 路由回退，使宝塔 Go 项目能统一管理域名、反向代理与 HTTPS。

## Explicitly Not Doing

- 不把数据库密码、对象存储密钥或平台凭据写入仓库、Manifest或制品。
- 不自动 SSH 到生产服务器。
- 不使用或移动 RC6 之前的旧 Tag。
- 不把 RC 部署成功宣称为正式生产验收完成。
- 不使用 `shared/` 保存跨版本配置或日志。
- 不使用 systemd 管理 Cloud 三个常驻进程。
- 不为 Scheduler/Worker 配置虚假监听端口。

## 有序任务

1. 裁定 Q-01 初始管理员口令策略。
2. Cloud Server 增加 Cloud Web 静态文件服务和 Vue history 路由回退，保持 API 与健康路由优先。
3. Cloud 部署脚本改为版本自包含目录，通过 `.toml.tpl` 和指定 `pre|online` 环境的远程变量表生成并校验实际配置，通过 `current` 原子切换；预发与生产复用同一制品和渲染能力。
4. 宝塔手册改为 Go 项目管理 Server、进程管理器管理 Scheduler/Worker，移除 systemd 与手工 Nginx 静态站点方案。
5. 增加 Web 路由、包结构与部署脚本测试；验证空库迁移、重复迁移和管理员初始化。
6. Workspace 固定新 Cloud 组件 Tag 与产品 Tag，重新运行 GitHub 打包工作流。
7. 输出服务器部署手册和人工验收记录模板；用户按手册在宝塔执行并回填实际结果。

## 验收

- 编译和打包会双向校验 `config/` 与 `config_online/` 的归一化运行路径一一对应；缺失、多出或重复映射时失败。
- 新 Cloud Artifact 包含全部运行程序、Web、FFmpeg/FFprobe、全部 SQL Migration、部署脚本，以及仅由 `config_online/` 生成的非敏感 `config/` 模板；不包含本地 `config/` 或 `config_test/`。
- 在用户预先创建的 MySQL 空库上，包内 `bin/migrate --dir migrations --create-database=false` 能完整应用并重复执行通过。
- 初始管理员能按 Q-01 裁定结果登录；密码不明文进入制品或交付记录。
- Server、Discovery Scheduler、Discovery Worker 可按提供的进程管理模板启动，`/healthz` 与 `/api/v1/health` 通过。
- `/`、真实静态资源和 `/login` 等深层路由由 Cloud Server 正确返回 Cloud Web，未知 `/api/` 路径仍返回 API 404 而不是前端页面。
- 新版本安装后拥有独立配置、日志和临时目录；部署脚本能按显式环境拉取变量表、渲染 `.toml.tpl`、拒绝缺失/未知/残留变量，并通过 Cloud 配置校验；`current` 切换前不改变正在使用的版本。
- 宝塔 Go 项目与两个进程管理器条目使用固定 `current` 路径、`www` 用户和正确工作目录，不依赖 systemd 或虚假端口。
- 部署手册明确备份、校验、失败停止、回退和未验证业务边界。

## Open Questions

- **Q-01（RESOLVED）**：用户于 2026-10-03 裁定保留 6 位密码下限，RC 初始管理员固定为 `admin / admin123`。该值由部署脚本写入服务器私有配置，不进入 Git。
