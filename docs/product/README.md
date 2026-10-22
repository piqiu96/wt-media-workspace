<!-- governance: class=stable default_load=task -->

# Product Documents

Current effective product facts live here.

Rules:

- Product requirements used for implementation must reference this directory.
- Do not store implementation plans, handoffs, progress notes, or temporary decisions here.
- Do not keep a legacy PRD copy outside this tree: the PRD lives under `prd/` below, and the execution root `wt-media/` carries no `docs/` directory of its own.

## Current M3 baseline

[PRD 第四章：内容挖掘](prd/详细文档/第四章_内容挖掘.md) 是当前 M3 产品事实源（ADR-0013）。旧版“内容发现”规则已被其取代，历史由 Git 承担。已确认要求见本章，实施状态与待决细节见 M3 Milestone。

M3 范围内对旧规则的改动（自动转素材、`partial_success`）已回写本章与 ADR-0013。M3 已完整验收并签收；按 `delivery/milestones/README.md` 的 Milestone-first 规则，稳定产品规则已融合回 PRD 第四章。

## Current M4-M5 baseline

[第五章：素材生产](prd/详细文档/第五章_素材生产.md) 是 M4 内容生产与 M5 自动生产的产品事实源。视频合成统一由 Cloud Scheduler / Worker / FFmpeg 执行；`material_usage`、`compose_strategy`、`compose_task`、`composite_output` 语义冻结，文件传输统一使用 `file_transfer_task`。工程边界见 ADR-0017。

## Public site

[公开官网与桌面下载](公开官网与桌面下载.md) 是 `/home`、共享登录页与三平台安装包入口的产品事实源。部署与清单生成见 `docs/devops/服务部署.md` 与 ADR-0020。
