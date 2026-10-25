---
id: CHG-20261026-103
parent: delivery/milestones/M4-content-production.md#m4-i-production-operator
status: PLANNED
depends_on: ["CHG-20261026-102"]
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261026-103：合成策略到成片的运营负责人

## Change

交付一条可验收的负责人链路：合成策略必须指定团队、一个游戏和该团队有效的运营负责人；人工任务分别保存创建人与负责人，成功成片继承负责人。普通运营仅为自己使用指定策略；高级运营和管理员可从**自己的**“我的素材”代创建，负责人必须匹配策略。合成任务与成片管理在同一页面体系按负责人查询，服务端授权与页面筛选一致。

## Done When

- Cloud 正式 migration、提供方合同、API 和共用页面有负责人字段；历史任务／成片只在可核实依据存在时回填，无法确认的保持未知并限制展示，不以 `created_by` 冒充。
- 高级运营创建策略时团队自动为本团队，管理员选择目标团队；团队、游戏、负责人有效性和引导配置的一致性在服务端校验。普通运营只能使用指定给自己的已启用策略。
- 普通运营仅从自己的“我的素材”为本人创建；高级运营／管理员可从自己的工作集为有权管理的运营代创建。任务保存创建人和负责人快照，策略负责人之后变化不改历史，成片继承任务负责人。
- 普通运营伪造负责人或查询参数被拒绝；高级运营默认“我”且可筛本团队全部／指定运营，不能跨团队；管理员按目标团队查看。代创建后能直达任务与成片，普通运营不被他人任务干扰。
- 同一素材经不同策略可产生归不同负责人的成片，既有 `(策略, 素材)` 防重、重试、下载与 M4/M5 Worker 链路回归；数据库、API、Cloud Web/Desktop 页面和真实成片逐层对账。

## Constraints / Not In Scope

- 不建立成片池、领取或新任务对象；不开放他人的 `material_usage`、BitBrowser、Profile、Cookie 或本机文件。
- 不改变 Scheduler 候选来源；它由 M5-F（CHG-105）单独交付。M6 发布流程和统计不在本 CHG。
- 启动前定向核实当前 Schema、合同和调用方，确认迁移及历史兼容策略；发现跨仓合同变化先回 Workspace。

## References

- `docs/product/prd/详细文档/第五章_素材生产.md`
- `docs/decisions/0023-m3-m5-team-resources-and-production-operator.md`
- `delivery/milestones/M4-content-production.md#m4-i-production-operator`
