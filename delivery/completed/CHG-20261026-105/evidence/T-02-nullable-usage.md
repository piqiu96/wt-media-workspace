# T-02 可空 `material_usage_id`

Cloud 提交：`3fe596b`

## 迁移

- `migrations/20261027_075_compose_optional_usage.sql` 只做两条 `ALTER TABLE ... MODIFY COLUMN material_usage_id BIGINT UNSIGNED NULL`，不删外键、不回填、不搬数据。
- 应用命令 `bash scripts/migrate.sh`：`migration ok: 1 applied, 77 total`。
- 读回（`mysql --defaults-file=/tmp/chg103-db.cnf`）：

| 检查 | 实测 |
| --- | --- |
| `compose_tasks.material_usage_id` | `bigint unsigned` / `IS_NULLABLE=YES` |
| `composite_outputs.material_usage_id` | `bigint unsigned` / `IS_NULLABLE=YES` |
| `fk_compose_tasks_usage` | 仍在，引用 `material_usages(id)` |
| `fk_composite_outputs_usage` | 仍在，引用 `material_usages(id)` |
| `schema_migrations` | 含 `20261027_075_compose_optional_usage`，共 77 条 |

`content_production_m4_c3_test.go` / `m4_c5_test.go` 断言的是 053/054 文件里当时的 `NOT NULL`，历史事实未变，保持原样；新增 `content_production_m4_j_test.go` 断言 075 的两处列变更、不重新引入 `NOT NULL`，且不含 `DROP FOREIGN KEY`／`DROP COLUMN`／`UPDATE`／`INSERT INTO`。

## 代码路径

- 模型：`ComposeTask.MaterialUsageID`、`CompositeOutput.MaterialUsageID` 改为 `*int64`，JSON tag 不加 `omitempty`，键仍在、值为 `null`。
- 读：`scanComposeTask` / `scanComposeOutput` 用 `sql.NullInt64` 中转后赋指针，不直接扫 `*int64`。
- 写：人工路径 `createForUsage` 写 `&usage.ID`；自动路径暂由 `&candidate.UsageID` 编译桥接，T-03 切到 `nil`。
- 成片来源追踪：`ComposeOutputTrace.MaterialUsage` 改为 `*ComposeOutputTraceUsage`，`output.MaterialUsageID` 为空时不再调用 `FindUsage`。
- Web：`ComposeOutputDetail.vue` 的「素材使用」在 trace 为空时显示 `—`。
- 合同：`content-production.openapi.yaml` 的 `ComposeTask.material_usage_id`、`ComposeOutput.material_usage_id` 改为 `[integer, 'null']`，`ComposeOutputTrace.material_usage` 改为 `[object, 'null']`；键仍在 `required` 内，只允许值为 null。revision 的 bump 与 `/runs/tasks` 一并放在 T-05。

## 自动门禁

| 命令 | 结果 |
| --- | --- |
| `go build ./...` | 通过 |
| `go test ./...` | exit 0；72 包 ok，0 FAIL，11 包无测试 |
| `go test ./internal/infra/database/migration/...` | ok |
| `npm test -- --run`（`web/`） | exit 0；80 文件 / 737 用例通过 |
| `python3 scripts/verify/verify_m0_config.py` | `Workspace config verification ok` |

## 变异对照（证明用例能失败）

| 变异 | 观察 | 已还原 |
| --- | --- | --- |
| `ComposeOutputDetail.vue` 的 `v-if="detail.trace?.material_usage"` 改成 `v-if="true"` | null-trace 用例失败（1 failed / 5 passed） | 是 |
| `service/output.go` 的 `if output.MaterialUsageID != nil` 改成 `if true` | `TestGetComposeOutputDetailLeavesUsageTraceEmptyForPoolOutputs` 空指针 panic | 是 |

## live DB 覆盖边界

以 `WT_MEDIA_TEST_LIVE_DB=1 WT_MEDIA_CLOUD_HOME=$PWD` 跑 repository live 用例：

- `TestLiveComposeScheduleDueAndRepeatScan`：**SKIP**，`no active strategy with creator usages`（CHG-104 清理后本机库已无符合旧“创建者 usage”查询的活动策略；该用例在 T-03/T-07 改造）。
- `TestLiveStrategyRulesRoundTripAndImmediateRun`：**FAIL**，跳过原因是 `operator_unavailable`。夹具策略未设 `OperatorID`，而 CHG-103 起负责人必填，`composeOperatorAvailable` 在候选查询之前就返回不可用；与本次 diff 无关（未进入任何 T-02 改动路径），属既有 live 用例未跟进，T-04/T-07 重写。

因此本 Task 只证明迁移、扫描、合同与页面可承载 NULL；**真实 NULL 行的端到端读回在 T-06/T-07 的真实调度链路里取证**，这里不冒充已覆盖。
