# CHG-20261003-076：四仓 Tag 驱动的 GitHub RC 打包试跑

- Status: DONE
- Level: L
- Milestone: `delivery/milestones/M-first-production-release.md#rc-打包验证闭环`
- References: `docs/superpowers/specs/2026-10-03-github-packaging-trial-plan.md`；`docs/superpowers/specs/2026-10-02-first-production-deployment-plan.md` §5.4、§6；`docs/decisions/0020-tagged-release-and-environment-config.md`。
- Affected repositories: `wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`、`wt-media-workspace`。
- 用户授权：2026-10-03 要求执行，并明确在当前四仓直接修改提交，无需隔离工作区。

## 目标与范围

从不可移动的组件 Tag 和 Workspace 产品 RC Tag 生成 Cloud Linux amd64 包、三平台原生 Agent Sidecar 与 Desktop 安装包。Workspace `release.yml` 由产品 Tag 推送触发；RC 生成 Pre-release，正式 Tag 生成 Draft Release，两者共用构建、校验、打包入口。Cloud 的 FFmpeg/FFprobe 仅进入 Cloud `bin/`，其来源与 SHA-256 锁定。

本 CHG 只执行一次 RC 打包试跑及报告；不部署宝塔，不操作生产数据库/对象存储，不验证真实 BitBrowser 账号或业务发布，不公开正式稳定版。

## 有序任务

1. 校验 GitHub 私有仓库访问、Runner 与 Tag 规则；锁定 RC Manifest 和非敏感预发布地址。
2. Cloud 增加 Linux 包与两个 Web 构建、FFmpeg/FFprobe 校验。
3. Agent 形成三平台 Sidecar 制品和启动/健康 smoke。
4. Desktop 消费锁定的 Web/Sidecar 制品，生成三平台安装包并校验包内版本、地址与完整性。
5. Workspace 接通单一 Tag 发布工作流及整组发布门禁。
6. 四仓独立提交，推送 Tag，观察 GitHub 运行，记录实际通过/失败与最终制品。

## 验收

- GitHub 上一次产品 RC Tag 的全部构建与校验 Job 通过，Pre-release 附件完整；Cloud 包作为受控 Artifact 可下载。
- Tag→Commit、Runner 架构、版本/环境、制品摘要和必要 smoke 可追溯；敏感信息未进入制品。
- 任何未验证路径在试跑报告中如实标明，不把 RC 打包通过写成线上可用。

## 完成记录

- 最终候选：`v0.1.0-rc.6`，GitHub Run `37091241538` 成功。
- Pre-release：`https://github.com/piqiu96/wt-media-workspace/releases/tag/v0.1.0-rc.6`。
- 最终验收与边界：[rc6-release-verification.md](evidence/rc6-release-verification.md)。

| 验收 | 结果 | 证据 |
| --- | --- | --- |
| 一次产品 RC Tag 的全部构建与校验 Job 通过，Pre-release 附件完整 | PASS | Run `37091241538`；三个平台附件、`build-info.json`、`SHA256SUMS`、Manifest 均存在 |
| Cloud 包作为受控 Artifact 可下载 | PASS | `cloud-linux-amd64` Artifact ID `11261989758`；`package` Job 下载并校验成功 |
| Tag→Commit、平台、版本/环境、摘要和必要 smoke 可追溯 | PASS | `build-info.json`、Run Matrix、Agent smoke 与发布附件校验 |
| 敏感信息未进入制品 | PASS | 发布制品仅含公开客户端/记录；数据库、对象存储和平台凭据不在 Manifest 或客户端附件中 |
| 未验证路径如实标明 | PASS | 未验证宝塔、生产数据库/对象存储、真实登录、BitBrowser 与业务发布 |
