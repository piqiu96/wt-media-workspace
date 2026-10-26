---
id: CHG-20261026-105
parent: delivery/milestones/M5-automatic-production.md#m5-f-team-material-candidates
status: VERIFYING
depends_on: ["CHG-20261026-103"]
dependency_merge_commits: {"CHG-20261026-103": {"wt-media-workspace": "f2d0e3bfca3d3a732c0d65130b2a16383dd77a27"}}
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
- 实施时同步合同缺口：`contracts/cloud-api/v1/content-production.openapi.yaml` 缺 `/runs/tasks`（策略运行记录下的任务列表）端点。
- 真实并发（多个任务同时认领同一素材）的补验归本 CHG；CHG-098 只验证过单进程不重复执行。

## 验收记录（2026-10-27）

| Done When | 实测证据 |
| --- | --- |
| 创建者和负责人都未加入的团队素材仍能自动生产，任务/成片归负责人 | T-06：真实 `compose-scheduler` + Cloud `worker` + `compose-worker`，任务 350 由来源 906 的素材 176 建成，真实 FFmpeg 与对象存储读回成片 77；T-07：策略 93/94 对素材 176 的立即执行与双 worker 成片 78/79；创建者（1）与负责人（3）均未新增 `material_usage` |
| 跨团队/跨游戏/不可用/负责人失效不建任务，跳过原因可查；管理员与高级运营范围正确 | T-03：团队全量候选、`other_game`/`material_unavailable`/`previously_run` 与人工非空 usage；T-04：高级运营本团队范围、普通运营与跨团队拒绝、禁用创建者仍生产；T-07：三条策略 `candidate_count=60`、团队 6 素材 0 条进入候选/跳过、45 条 `other_game`、`operator_unavailable` 0 任务 |
| 并发/重启幂等，额度、部分失败、重试与人工入口回归，页面读回一致 | T-07：双 scheduler 同槽 1 run/1 task、重启 0 新增；双 worker 各领一条（node 1/2）、各 1 次 attempt、两个成片对象键不同；`single_limit`/`daily_limit`、cancel/retry、人工入口写非空 usage 均实测；T-06 页面与 T-02 Vitest 空 trace 读回 |
| 旧候选来源证据不冒充新口径，保存真实证据 | 原 M5-AC 证据未改写；T-01～T-07 记录本 CHG 的真实进程、DB、对象与 HTTP 读数；M5-F 单独验收，M5 总体保持 `IN_PROGRESS` |

合同缺口已在同一 CHG 补齐：`/runs/tasks` 与无 run 404、`material_usage_id` 可空、`material_scope` enum（T-05），并同步 Workspace contract-map。

## References

- `docs/product/prd/详细文档/第五章_素材生产.md`
- `docs/decisions/0023-m3-m5-team-resources-and-production-operator.md`
- `delivery/milestones/M5-automatic-production.md#m5-f-team-material-candidates`
