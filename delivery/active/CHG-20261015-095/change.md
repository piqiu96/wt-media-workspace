# CHG-20261015-095：M5-C4 批次结果归集与部分失败对账

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M5-automatic-production.md`
- Closure anchor: §3 M5-D 的批次结果归集段（批次仅按计划时间、策略汇总展示，不合并执行实体）与 §8 M5-AC-09
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.5.7、§5.6
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §4.2、§8
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`
- Current repository: `wt-media-cloud`
- Affected repositories: `wt-media-cloud`

## 目标

一次调度命中多个素材产生的一批任务（同策略、同 `schedule_slot`），高级运营能在策略的运行记录处看到这批每个素材的任务与结果；批次有成功也有失败时，部分失败统计准确、逐素材可追溯。防重与数量控制的既有事实经对账复核保持成立。

## 当前事实与缺口

- `compose_schedule_runs` 已记录每次运行的候选数、创建数与跳过原因（CHG092）；策略详情已显示最近运行摘要。
- 合成任务列表支持 `status`、`trigger_type` 过滤（CHG092），但没有按批次（策略 + `schedule_slot`）聚合的读取路径；部分失败时无法从一处看到这批每个素材的任务与结果。
- 防重唯一键 `(compose_strategy_id, schedule_slot, material_id)`、单次/每日上限与跳过原因已在 CHG092 机器验证（M5-AC-03/04 PASS）；本 CHG 只做对账复核，不重建。
- M5-C4 的"批次结果归集"仅指基于计划时间、策略的汇总展示（里程碑 §1 第 26 行），不把多个任务合成一个执行实体，不引入核心批次表。

## 有序任务

| Task | 结果 | 验证 |
| --- | --- | --- |
| T-01 | 固化缺口：批次读取路径不存在时，混合状态批次无法按（策略，槽）取出每素材任务与状态统计 | Repository/Service 测试先红 |
| T-02 | 按批次读取任务（每素材状态、错误、成片关联）与批次状态统计；统计与库内事实一致 | 混合状态批次测试：逐状态计数对账 |
| T-03 | 策略详情运行记录展开批次明细：每素材任务与结果、部分失败统计、跳过原因 | API/UI 定向测试；跳过原因与 `skipped_json` 一致 |
| T-04 | 防重与数量控制对账回归：双进程调度幂等、唯一键防重、单次/每日上限既有测试复跑；批次统计与数据库逐状态计数对账 | 既有测试复跑 + 对账证据 |

## 验收

1. 同策略同 `schedule_slot` 的一批任务能在一个视图中逐素材列出，状态、错误与成片关联和数据库一致。
2. 批次统计（成功/失败/进行中/已跳过）与逐条任务对账一致；部分失败不显示为全部成功。
3. 跳过素材的原因与 `compose_schedule_runs.skipped_json` 一致。
4. 防重与数量控制回归通过：唯一键防重、单次/每日上限、双进程幂等的既有测试复跑全绿。
5. 不出现批次实体、第二套任务状态或合并执行；页面不展示尚无服务端事实的统计。

## 不做

- 不建批次表或批次实体，不把多个任务合成执行实体（里程碑 §1 边界）。
- 不做技术失败重试与退避（M5-C5）、结果不明确人工处置页（M5-C6）。
- 不做跨策略运行统计聚合页与日志摘要（M5-C6）。

## Pending Questions

None.
