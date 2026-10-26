# T-05 合同缺口：`/runs/tasks` 与批次视图

Cloud 提交：`fbbda88`

## 合同变更

- `contracts/cloud-api/v1/content-production.openapi.yaml`：`info.version` `2026.10.27.1 → 2026.10.27.2`
  - 新增 `GET /api/v1/compose-strategies/{strategy_id}/runs/tasks`：`schedule_slot` 必填、`format: date-time`（RFC3339）；200 返回 `ComposeBatchView`；400 为缺失/非法 slot；404 为策略不存在、越界或该 slot 没有 run。
  - 新增 `ComposeBatchView`（`run`/`tasks`/`counts` 均 required）与 `ComposeBatchCounts`（`pending`/`running`/`success`/`failed`/`cancelled` 均 required、`minimum: 0`）。
  - `ComposeTask.material_usage_id`、`ComposeOutput.material_usage_id` 与 trace 的可空对象在 T-02 已完成，本 Task 不重复修改。
- `contracts/business-schemas/v1/content-production.yaml`：`revision` `2026.10.26.1 → 2026.10.27.1`；`ComposeSchedule.material_scope` 枚举改为 `[team_materials, creator_usages]`，并注明 `team_materials` 是当前执行语义、`creator_usages` 为历史持久值且旧 `schedule_json` 不重写。
- Workspace `config/contract-map.yaml`：`cloud_api.contract_revision → 2026.10.27.2`，`business_schemas.schema_revision → 2026.10.27.1`，两处注释登记本次变更。

## 代码变更

- `service/compose_scheduler.go` 的 `Batch` 先 `FindRun`；`found=false` 时返回 `ErrStrategyNotFound`（404），不再返回零值 run，也不再读取该 slot 的任务。

## 验证

OpenAPI 解析（Python PyYAML，本机）：

```text
version 2026.10.27.2
op listComposeStrategyRunTasks
params [('schedule_slot', True, {'type': 'string', 'format': 'date-time'})]
responses ['200', '400', '404']
counts required ['pending', 'running', 'success', 'failed', 'cancelled']
business revision 2026.10.27.1
scope enum ['team_materials', 'creator_usages']
```

- 新增 `TestTheComposeBatchViewResponseMatchesTheOpenAPISchema`：`ComposeBatchView` 与 `ComposeBatchCounts` 的 JSON 键集必须等于 schema properties，且六项 required 必须齐全。
- 扩展 `TestComposeBatchViewScopesReadbackAndCarriesCounts`：有 run 时仍返回 run/tasks/counts；无 run 时返回 `ErrStrategyNotFound`，且 `BatchTasks` 不被调用（`slot` 保持零值）。
- 变异对照：临时移除 `!found` 分支后，该用例失败 `slot without a run must be not found: <nil>`；改动已还原。
- 解析阶段发现 `tasks.description` 未加引号，YAML 流式映射把逗号后的文字解析成额外键；加引号后复核为单一 `description`。该问题不会被键集测试发现，但会静默改变合同形状，记录在此。

## 门禁

- `go build ./...`：通过。
- `go test ./...`：exit 0；72 包 ok，0 FAIL。
- `python3 scripts/verify/verify_m0_config.py`：`Workspace config verification ok`（exit 0）。

## 覆盖边界

- `creator_usages` 的兼容目前是 schema 层声明：本机 `compose_strategies` 当前 0 行，`schedule_json LIKE '%material_scope%'` 为 0，没有可回放的历史行；不据此声称旧数据链路已实测。
- `/runs/tasks` 的 400 分支由 handler 的 `time.Parse` 覆盖，T-05 只改 service 的 404 语义；真实 HTTP 调用与页面读回放在 T-06/T-07。
