# T-02：migration 074、模型与仓储字段

## 迁移

| 项目 | 实际 |
| --- | --- |
| 迁移文件 | `wt-media-cloud/migrations/20261026_074_compose_operator.sql` |
| 应用结果 | 首次应用后，`./scripts/migrate.sh` 输出 `migration ok: 0 applied, 76 total`（2026-10-26 19:35） |
| 列 | `compose_strategies`、`compose_tasks`、`composite_outputs` 均有可空 `operator_id bigint unsigned` |
| 索引 | 三表各有 `idx_*_operator` |
| 外键 | 三表各有 `fk_*_operator` 指向 `users.id` |

```text
+--------------------+-------------+-------------+-----------------+
| TABLE_NAME         | COLUMN_NAME | IS_NULLABLE | COLUMN_TYPE     |
+--------------------+-------------+-------------+-----------------+
| compose_strategies | operator_id | YES         | bigint unsigned |
| compose_tasks      | operator_id | YES         | bigint unsigned |
| composite_outputs  | operator_id | YES         | bigint unsigned |
+--------------------+-------------+-------------+-----------------+
```

## 历史行不回填

验收数据清理后（见 T-08），三张表全部回到历史行，`operator_id` 非空数均为 0：

| 表 | 总行数 | 未指派 | 历史行被写入 |
| --- | --- | --- | --- |
| `compose_strategies` | 7 | 7 | 0 |
| `compose_tasks` | 19 | 19 | 0 |
| `composite_outputs` | 16 | 16 | 0 |

清理前同样按 id 分段核对：策略 `id<44`、任务 `id<325`、成片 `id<69` 的 `operator_id` 非空数均为 0；非空只出现在本 CHG 新建的验收行。

## 自动测试

```text
$ go test ./internal/modules/production/... -count=1
ok  .../production            1.521s
ok  .../production/compose    5.365s
ok  .../production/executor   2.295s
ok  .../production/model      0.412s
ok  .../production/repository 0.972s
ok  .../production/service    3.141s
```

覆盖模型 JSON、仓储扫描列与过滤条件、迁移后的空负责人读回；完整套件读数在 T-09。
