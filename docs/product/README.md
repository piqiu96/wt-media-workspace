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

[第五章：素材生产](prd/详细文档/第五章_素材生产.md) 是内容生产与自动生产的正式产品事实源，已按用户确认的内容生产原型合并：多组成片设置、模板参数权限、三种创建来源、统一任务批次、人工再次制作、受权代选材与按素材聚合的成片管理。

Cloud 合成、Agent 下载和共用页面的边界继续有效；数据／接口收敛见[内容生产工程设计](../engineering/specs/2026-09-24-m4-m5-cloud-content-production.md)，与旧规则的替代关系见 [ADR-0031](../decisions/0031-content-production-batches-and-manual-reproduction.md)。[原型入口](../design/content-production.md)仅作体验与导航，不维护第二份 PRD。产品定稿不代表新增运行能力已实施，交付状态以 Delivery 为准。

## 发布管理与运营工具

[第六章：发布管理](prd/详细文档/第六章_发布管理.md)是计划、批次、任务、发布内容、图片库与封面模板的正式产品事实源，按已确认设计和原型流程重新组织为用户任务闭环。图片库和封面模板的菜单归属仍为运营工具。

[PRD 总纲](prd/社媒运营平台_产品需求说明书_V1.md)只保留模块摘要；[设计导航](../design/README.md)提供原型、专项交互和适配核验入口，不另立产品规则。产品规则定稿不代表正式生成、资源或平台发布服务已经实施或验收，具体以 Delivery 为准。

## Public site

[公开官网与桌面下载](公开官网与桌面下载.md) 是 `/home`、共享登录页与三平台安装包入口的产品事实源。部署与清单生成见 `docs/devops/服务部署.md` 与 ADR-0020。
