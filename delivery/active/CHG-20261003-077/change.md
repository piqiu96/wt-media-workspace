# CHG-20261003-077：Cloud 预发布部署包与数据库初始化

- Status: IMPLEMENTING
- Level: L
- Milestone: `delivery/milestones/M-first-production-release.md#cloud-预发布部署与数据库初始化`
- References: `docs/superpowers/specs/2026-10-02-first-production-deployment-plan.md` §5.1、§7；`docs/decisions/0020-tagged-release-and-environment-config.md`；已完成 [CHG-20261003-076](../../completed/CHG-20261003-076/change.md)。
- Affected repositories: `wt-media-cloud`、`wt-media-workspace`。
- 用户目标：基于 RC6 后的固定源码产出可上传宝塔的 Cloud 独立部署包、可执行数据库初始化/迁移步骤，并初始化管理员。

## 目标与范围

1. Cloud Linux 部署包包含现有可执行程序、Cloud Web、FFmpeg/FFprobe、`migrations/`、非敏感配置模板、版本/摘要记录和服务器安装/验收脚本。
2. 提供数据库准备模板：用户可先创建专用数据库和账号；部署脚本只对显式目标库执行迁移，不隐式创建生产库。
3. 提供宝塔/服务器可执行步骤：校验包摘要、解压固定版本、注入私有 `config/`、执行迁移、启动 Server/Scheduler/Worker、验证健康与登录。
4. 用新的 Cloud 组件 Tag 和产品 Tag 重新生成可部署 Cloud Artifact；客户端无变更时沿用已验证组件 Tag。
5. 记录预发布部署边界：不宣称对象存储、BitBrowser、业务发布或正式稳定版上线通过。

## Explicitly Not Doing

- 不把数据库密码、对象存储密钥或平台凭据写入仓库、Manifest或制品。
- 不自动 SSH 到生产服务器。
- 不使用或移动 RC6 之前的旧 Tag。
- 不把 RC 部署成功宣称为正式生产验收完成。

## 有序任务

1. 裁定 Q-01 初始管理员口令策略。
2. Cloud 补齐部署包内容：迁移、配置模板、版本记录、安装/迁移/验证/回退脚本和进程管理模板。
3. 增加包结构与部署脚本测试；验证空库迁移、重复迁移和管理员初始化。
4. Workspace 固定新 Cloud 组件 Tag 与产品 Tag，重新运行 GitHub 打包工作流。
5. 输出服务器部署手册和人工验收记录模板；用户按手册在宝塔执行并回填实际结果。

## 验收

- 新 Cloud Artifact 包含全部运行程序、Web、FFmpeg/FFprobe、全部 SQL Migration、部署脚本和非敏感配置模板。
- 在用户预先创建的 MySQL 空库上，包内 `bin/migrate --dir migrations --create-database=false` 能完整应用并重复执行通过。
- 初始管理员能按 Q-01 裁定结果登录；密码不明文进入制品或交付记录。
- Server、Discovery Scheduler、Discovery Worker 可按提供的进程管理模板启动，`/healthz` 与 `/api/v1/health` 通过。
- 部署手册明确备份、校验、失败停止、回退和未验证业务边界。

## Open Questions

- **Q-01（RESOLVED）**：用户于 2026-10-03 裁定保留 6 位密码下限，RC 初始管理员固定为 `admin / admin123`。该值由部署脚本写入服务器私有配置，不进入 Git。
