---
id: CHG-20261026-105
parent: delivery/milestones/M5-automatic-production.md#m5-f-team-material-candidates
status: PLANNED
depends_on: ["CHG-20261026-103"]
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261026-105：合成策略从团队素材库自动选材

## Change

定时和策略“立即执行”从策略团队、指定游戏匹配的正式 `material` 取候选，不再依赖策略创建者的“我的素材”；每条任务和成片归策略指定的运营负责人。沿用现有条件组、额度、调度、Worker、运行记录、`(策略, 素材)` 防重与重试，不引入新池或工作流。

## Done When

- 策略创建者和负责人都未加入某条同团队同游戏素材时，Scheduler 到点和“立即执行”仍可选中该素材，任务创建、Cloud 源文件准备、真实 FFmpeg、对象存储与成片读回连贯；负责人快照一致。
- 跨团队、跨游戏、不合格或负责人失效的素材不创建任务，跳过原因可核查；管理员和高级运营的策略执行范围分别受全局目标团队、本团队限制。
- 并发／重启扫描仍幂等，条件组、单次／每日额度、部分失败、旧任务重试和人工“我的素材”入口均回归，Cloud Web/Desktop 共用页面展示同一结果。
- 原 M5-AC-01～13 的旧候选来源证据不冒充新口径；保存本 CHG 的真实数据库、任务、文件与页面证据。

## Constraints / Not In Scope

- 不把策略创建者或负责人工作集关系作为自动候选条件；不改人工选材来源，也不新建 `compose_pool` 或核心 batch 表。
- 不开放管理员或高级运营对他人本机文件、BitBrowser、Profile、Cookie 的访问；M6 发布不在范围。

## References

- `docs/product/prd/详细文档/第五章_素材生产.md`
- `docs/decisions/0023-m3-m5-team-resources-and-production-operator.md`
- `delivery/milestones/M5-automatic-production.md#m5-f-team-material-candidates`
