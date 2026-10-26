# T-13 无负责人历史数据清理

日期：2026-10-27

## 结论

用户走查确认通过后，在本机开发库 `wt_media_cloud` 用一个受守卫的单事务物理删除无负责人历史数据：

- 无负责人任务 19 条、成片 17 条、策略 7 条；
- 子行：任务尝试 23 条、成片下载 transfer 2 条、调度运行 16 条；无待清理 review（0 条）；
- 审计日志 1213 条全部保留（其中 52 条引用被删任务/策略 ID）；
- 对象存储未删除，17 个成片对象逐个用 SigV4 Range GET 复核仍存在（HTTP 206）；
- 保留夹具 328/329/330/331、成片 72/73/74/75、策略 46/47/48、`material_usages` 92/93/94 与既有 usage 62。

## 执行前状态

停止 compose worker/scheduler 后，`pgrep -fl 'compose-scheduler|compose-worker'` 为空；`compose_tasks` 中 `pending`/`running` 为 0。

```text
compose_tasks WHERE operator_id IS NULL                 19
composite_outputs WHERE operator_id IS NULL             17
compose_strategies WHERE operator_id IS NULL             7
compose_task_attempts（上述任务）                        23
compose_uncertain_reviews（上述任务）                     0
file_transfer_tasks（上述成片，asset_type=composite_output） 2
compose_schedule_runs（上述策略）                        16
audit_logs                                              1213
audit 引用上述任务/策略的悬挂行                           52（23 任务 + 29 策略）
```

删除集合：

| 表 | ID |
| --- | --- |
| `compose_tasks` | 299,300,301,302,303,304,306,312,314,315,316,317,318,319,320,321,322,323,324 |
| `composite_outputs` | 49,50,51,52,53,58,59,60,61,62,63,64,65,66,67,68,76 |
| `compose_strategies` | 34,36,37,38,39,42,43 |

`compose_schedule_runs` 按策略分布：36×6、37×4、38×1、39×1、42×4。下载 transfer 为 `transfer_75b40509a620bd8bb08ac77b`（asset 59）与 `transfer_43489a35d82b4cd258a9d855`（asset 68），均为 `user_download`。成片 76 属于任务 312/素材 153，不是素材 161。

预检确认：上述 7 条策略没有被其他任务引用（`compose_tasks WHERE compose_strategy_id IN (...) AND operator_id IS NOT NULL` = 0；不在清理集合内的任务 = 0）。

## 事务与删除顺序

先用同一组 `DELETE` 在事务内做 dry-run，再 `ROLLBACK`，受影响行数为 0/23/2/17/19/16/7，与预期一致。

正式执行使用临时存储过程，`SELECT ... FOR UPDATE` 锁定任务、成片、策略行，按子到父顺序删除，并在每条 `DELETE` 后用 `ROW_COUNT()` 断言；任一不符即 `ROLLBACK` 并 `RESIGNAL`。顺序：

```text
compose_uncertain_reviews    0
compose_task_attempts       23
file_transfer_tasks          2
composite_outputs           17
compose_tasks               19
compose_schedule_runs       16
compose_strategies           7
```

全部断言通过后 `COMMIT`，临时过程已删除。

## 执行后复核

```text
unowned_tasks       0
unowned_outputs     0
unowned_strategies  0
audit_total        1213
audit_refs            52
orphan_attempts        0
orphan_outputs         0
orphan_transfers       0
orphan_runs            0
```

保留夹具：

| 对象 | 读回 |
| --- | --- |
| 任务 328/329/330/331 | 均为 `success`，负责人 `operator01`（3）；329 成片 74、331 成片 75 |
| 成片 72/73/74/75 | 均在；72 属任务 328/素材 170，73 属 330，74 属 329，75 属 331 |
| review 11/12 | 均在；11 属 329（actor 1），12 属 331（actor 2） |
| attempts 256/257/258/259/261/262 | 均在 |
| 策略 46/47/48 | 均 `enabled`，负责人 `operator01` |
| `material_usages` 92/93/94 | 92/93 为 active，94 为 removed |
| `material_usage` 62 | 保留（任务 328 在用） |
| 素材 170 | 成片 1 条，保留 |

素材与 API 读回（operator01，团队 1）：

```text
GET /api/v1/materials/161   usage.output_count=0, operator_count=0
GET /api/v1/materials/17    usage.output_count=3, operator_count=1
GET /api/v1/compose-tasks?page=1&page_size=100      1 条：328 success
GET /api/v1/compose-outputs?page=1&page_size=100    1 条：72（任务 328/素材 170/hy/负责人 3）
GET /api/v1/compose-tasks/312    404
GET /api/v1/compose-outputs/76   404
GET /api/v1/compose-tasks/299    404
GET /api/v1/materials?page=1&page_size=5        200，返回 59 条，含 161
```

素材 161 的使用情况由清理前的 `成片 6` 变为 `0`，页面按 `—` 展示的口径见 T-10。

## 对象存储

未执行任何删除。17 个对象键逐个用 `curl --aws-sigv4` + Range `0-0` 读取，全部返回 HTTP 206：

```text
compose-outputs/300/1/output.mp4
compose-outputs/301/1/output.mp4
compose-outputs/302/1/output.mp4
compose-outputs/304/1/output.mp4
compose-outputs/306/1/output.mp4
compose-outputs/314/1/output.mp4
compose-outputs/315/1/output.mp4
compose-outputs/316/1/output.mp4
compose-outputs/318/1/output.mp4
compose-outputs/317/1/output.mp4
compose-outputs/319/2/output.mp4
compose-outputs/321/2/output.mp4
compose-outputs/320/2/output.mp4
compose-outputs/323/1/output.mp4
compose-outputs/324/1/output.mp4
compose-outputs/322/1/output.mp4
compose-outputs/312/2/output.mp4
```

这些对象登记为“未处理”，不在本 CHG 的删除范围；后续如需清理另立任务。

## 覆盖边界

- 已验证：删除集合与依赖、事务回滚守卫、删除后计数、审计保留、保留夹具、素材 161 使用事实、operator01 可见的 API 列表与 404、17 个对象仍可读。
- 未复测：管理员/高级运营的 329/331 详情页在清理后的重新打开。本机检出没有这两个账号的可验证会话，且清理未改动这两条任务/成片；用户走查已覆盖其页面展示，DB 读回证明行仍在。
- 不可恢复：本次按用户决定不备份，删除后的旧任务/成片/策略行只能依据本记录重建，不能从数据库回滚。
