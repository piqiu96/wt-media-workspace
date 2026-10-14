# CHG-20261015-095 Checkpoint

## Completed

- CHG094 已归档（M5-C3 机器验收通过）。按 MASTER_IMPLEMENTATION_PLAN 建立本 CHG。
- T-01：批次读取路径缺失的失败用例先红（stub 返回空，播种 2 任务读到 0）。
- T-02：`composeBatchTasks` 按槽读任务 + `GROUP BY status` 统计；服务层 scope 校验与 run/skips 透传；路由接线测试。
- T-03：`GET /compose-strategies/:id/runs/tasks?schedule_slot=` API；策略详情运行记录懒加载批次明细（逐素材任务、成片关联、错误、服务端统计行）。
- T-04：双进程 scheduler 幂等回归 PASS（runs=1/tasks=1/重启后 1）；`WT_MEDIA_TEST_LIVE_DB` 门禁套件全绿；`go test ./...` 71 包 ok；web vitest 564 passed。
- CHG 已归档：验收 1–5 逐项核对通过。

## Current

- Cloud `fcc297f` 已提交；CHG 归档至 `delivery/completed/`。

## Next

- 按 MASTER_IMPLEMENTATION_PLAN 与当前代码状态建议下一个 CHG（M5-C5 技术重试、卡死恢复、取消和对象存储异常处置），不自动实施。

## Blockers

None.

## Recent verification

- 门禁真库测试先红后绿；双进程调度幂等回归 PASS；全量 Go 71 包 ok、Web 564 测试通过。
- 诚实边界见证据「覆盖面登记」。
