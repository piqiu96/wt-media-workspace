# T-05：任务／成片负责人快照与查询范围

原始响应见 `T-05-task-scope-and-snapshot.json`。

## 列表范围

| 角色 | 请求 | 实际 | 结果 |
| --- | --- | --- | --- |
| operator01 | 任务默认 | 8 条；含负责人为 pika 的 325、326 与本人创建的历史行；不含负责人为 CHG103高级的 327 | PASS |
| operator01 | `operator_scope=team` | `15215 compose_task_forbidden` | PASS |
| operator01 | `operator_id=9` | `15215 compose_task_forbidden` | PASS |
| chg103senior | 任务默认 | 1 条：327（本人） | PASS |
| chg103senior | `operator_scope=team` | 22 条，团队全部 | PASS |
| chg103senior | `operator_id=3` | 2 条：325、326 | PASS |
| chg103senior | `team_id=2` | `15215`，不跨团队 | PASS |
| chg103admin | 任务默认 / `team_id=1` | 22 条；`team_id=2` 为 0 条 | PASS |
| chg103admin | `operator_id=3` | 2 条：325、326 | PASS |
| operator01 | 成片默认 | 8 条；含 69、70；不含 71 | PASS |
| operator01 | `operator_id=9` | `15215 compose_output_forbidden` | PASS |
| chg103senior | 成片默认 / 团队 / `operator_id=3` | 1 条（71）／19 条／2 条（70、69） | PASS |
| chg103admin | 成片默认 / `team_id=2` / `operator_id=3` | 19 条／0 条／2 条 | PASS |

“默认我”的 SQL 口径为 `operator_id = 当前用户 OR (operator_id IS NULL AND created_by = 当前用户)`：历史行继续对创建人可见，但负责人字段保持空。

## 创建门禁

| 场景 | 实际 | 结果 |
| --- | --- | --- |
| 高级运营为策略 45（负责人 9）创建任务，请求里伪造 `operator_id=3` | 请求级 `15214 compose_task_invalid`：“operator_id must match the strategy's operator”；任务总数 22 → 22 | PASS |
| 请求不带 `operator_id` | 服务端从策略冻结负责人；任务 326 的 `operator_id=3`、`created_by=9` | PASS |
| 策略改派后历史不变 | 策略 45 由 9 改为 3，任务 327 仍 `operator_id=9`，成片 71 仍 `operator_id=9`；随后把策略改回 9 | PASS |

## 调度与 Worker

| 场景 | 实际 | 结果 |
| --- | --- | --- |
| 历史策略无负责人 | `compose_schedule_runs` 记录 `run_key=d243637…`、策略 42、`trigger_type=scheduled`、`candidate_count=0`、`created_count=0`、`skipped_json=[{"reason":"operator_unavailable","material_id":0}]` | PASS |
| Worker 成功事务 | 任务 325/326 负责人 3 → 成片 70/69 负责人 3；任务 327 负责人 9 → 成片 71 负责人 9；创建人分别保留 3/9/9 | PASS |
| 历史不回填 | 清理验收行后，策略 7 / 任务 19 / 成片 16 的 `operator_id` 全部为 NULL；按 id 分段历史非空计数为 0 | PASS |

- 单测覆盖任务创建、列表范围、调度跳过、Worker 成片继承，生产模块包测试全绿（T-02）。
