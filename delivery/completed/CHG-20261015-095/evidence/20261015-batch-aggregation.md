# CHG095 批次结果归集与部分失败对账（2026-10-15）

## T-01 先红

新增门禁真库测试 `TestLiveComposeBatchTasksReadTheRunSlot`（`WT_MEDIA_TEST_LIVE_DB=1`）：播种同策略同 `schedule_slot`、跨 2 个素材的混合状态批次（1 成功 + 1 失败），读取批次任务与统计。在 `BatchTasks` 只有签名无行为（返回空）时运行：

- 预期：2 任务、`Success=1 Failed=1`；
- 实际：`batch must read all 2 seeded tasks, got 0` —— 先红成立（红在行为缺失，不是编译失败）。

播种形态说明：批次天然是每素材一行（唯一键 `(compose_strategy_id, schedule_slot, material_id)`），测试按策略 11 的 2 个不同素材各克隆一行；播种行在回滚事务内，读路径走同一事务的包内函数 `composeBatchTasks`。

## T-02 批次读取与统计

| 动作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 实现 `composeBatchTasks`（任务按 `material_id` 排序 + `GROUP BY status` 计数）后复跑批次测试 | 2 任务、统计诚实 | PASS | PASS |
| 服务层 `TestComposeBatchViewScopesReadbackAndCarriesCounts`（假 store）：scope 校验、计数与 run（含 skipped）透传 | 越权/缺策略/空槽拒绝，正常路径带 counts 与 run | PASS | PASS |
| 路由接线 `TestComposeStrategyRoutesRequireAuthentication` 增加 `GET /compose-strategies/5/runs/tasks` | 401（未认证） | PASS | PASS |

## T-03 API 与页面

- API：`GET /api/v1/compose-strategies/:strategy_id/runs/tasks?schedule_slot=<RFC3339>`，返回 `{ run, tasks, counts }`；`run` 取该槽最新一次运行记录（跳过原因随之）。
- 页面：策略详情「最近运行」每条创建数 > 0 的运行可「查看批次任务」懒加载——逐素材列出任务 ID、素材 ID、状态、成片 ID、错误；统计行直接渲染服务端 `counts`（成功/失败/执行中/排队中/已取消），页面不二次推算。
- 客户端测试：`listStrategyRunTasks` 请求串与 query 断言；页面测试断言统计取自服务端 view、错误可见。

## T-04 防重与数量控制对账回归

| 动作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| `WT_MEDIA_TEST_SCHEDULER_PROCESS=1 TestLiveComposeSchedulerProcessesDeduplicate`（真实 compose-scheduler 二进制、双进程 + 重启） | 同槽只建一次 | 独立进程 strategy=20 runs=1 tasks=1，重启后仍 1 | PASS |
| `WT_MEDIA_TEST_LIVE_DB=1` 全部门禁真库测试（含到点扫描、单次/每日上限路径、策略计划读回、新批次测试） | 全绿 | 3 PASS + 2 SKIP（属进程门禁，各自门禁下已跑） | PASS |
| 全量 `go test ./...` | 0 失败 | 71 包 ok | PASS |
| 全量 web `npx vitest run`（web/ 目录下执行） | 0 失败 | 564 passed | PASS |

覆盖面登记：批次读取的真库证据覆盖 success/failed 两状态形态（dev 库策略最多 2 个素材）；pending/running/cancelled 与 success/failed 走同一条 `GROUP BY` 查询分支，由服务层假测试覆盖计数字段形状。批次统计的「与数据库逐状态对账」由先红测试里的播种真值比对承担。
