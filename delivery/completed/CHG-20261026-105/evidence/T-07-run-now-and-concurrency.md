# T-07 立即执行与并发回归

日期：2026-10-27

本 Task 不新增产品代码；使用当前分支源码（测试文件外的生产代码自 T-06 未变）跑真实 HTTP、双调度进程、双 worker 进程与真实对象存储。

## 夹具

| 对象 | 实测 |
| --- | --- |
| 策略 93「CHG-105 立即执行 A」 | 团队 1 / `hy` / 负责人 3 / `manual` / 规则 `like_count eq 258365` / 单次 1 / 每日 2 |
| 策略 94「CHG-105 立即执行 B」 | 同 93，另一条策略，用于同一素材的第二个任务 |
| 策略 95「CHG-105 双调度」 | 团队 1 / `hy` / 负责人 3 / `scheduled` / `interval` 1 分钟 / 规则 `like_count eq 258365` / 单次 1 / 每日 2 |
| 策略 96「CHG-105 额度回归」 | 团队 1 / `hy` / 负责人 3 / `manual` / 规则 `like_count gte 0` / 单次 1 / 每日 1 |
| 策略 97「CHG-105 负责人缺失」 | 同 96，`operator_id=NULL` |
| 策略 98「CHG-105 人工入口」 | 团队 1 / `sjz` / 负责人 3 / `manual` / 规则 `like_count gte 0` / 单次 1 / 每日 1 |
| 素材 176 | 团队 1 / `hy` / `available` / `ready`，T-06 已准备，双 worker 复用同一源对象 |
| 素材 153 | 团队 1 / `sjz` / `available`，管理员（用户 1）有活动 usage 1 |

策略 93–98 均为本 Task 建在本机开发库的夹具，CHG 归档后按 T-01 登记清理；对象存储对象不删除。

## 立即执行（真实 HTTP）

管理员会话（`X-Session-Token`，令牌只存 `/tmp/chg105-session-token`）调用 `POST /api/v1/compose-strategies/{id}/run-now`：

| 请求 | 结果 |
| --- | --- |
| 93，`chg105-run-now-A-001` | 200；`run_key=e034933c…5a041f2`、`trigger_type=manual`、`candidate_count=60`、`created_count=1`、跳过 45 条 `other_game` |
| 93，同 key 重放 | 200；同一 `run_key`、`created_count=1`，未新增任务 |
| 93，`chg105-run-now-A-002` | 200；新 `run_key=ba28bbd2…352dbb7`、`created_count=0`，跳过 45 条 `other_game` + 素材 176 `previously_run` |
| 93，`short`（5 字符） | 400（`15210 compose_strategy_invalid`，`request_key must be 8-64 characters`） |
| 94，`chg105-run-now-B-001` | 200；`run_key=66db4858…287f3a0c`、`created_count=1` |

任务：

```text
387  strategy 93  material 176  material_usage_id NULL  operator 3  created_by 1  trigger manual  pending
388  strategy 94  material 176  material_usage_id NULL  operator 3  created_by 1  trigger manual  pending
```

重放响应里的 `schedule_slot` 首次为 `2026-10-26T19:48:46.436551Z`、重放为同一时刻的 `2026-10-27T03:48:46.436551+08:00`；`run_key` 相同，读回的是同一行。这与 T-06 记录的槽位序列化口径一致，未产生第二条 run。

## 双调度进程与重启（策略 95）

`sched-a` pid 83987、`sched-b` pid 83988 由同一 Cloud home 同时启动，两个进程都在启动后立即扫描到策略 95：

| 阶段 | 实测 |
| --- | --- |
| 双进程并发扫描 | `compose_schedule_runs` 该策略 1 行；`created_count=1`；`schedule_slot` 为该行原 `next_run_at`；任务 389 仅 1 条 |
| 停止后改 `next_run_at` 为过去，单进程重启（pid 84015） | 新增 1 条 run（`created_count=0`）；任务总数仍为 1 |

```text
run 1  scheduled  slot 2026-10-26 19:48:15.394102  candidates 60  created 1  created_at 2026-10-27 03:49:07.028951
run 2  scheduled  slot 2026-10-26 19:49:09.374596  candidates 60  created 0  created_at 2026-10-27 03:49:14.410577
tasks for strategy 95 = 1
```

`next_run_at` 写入的是 UTC 墙钟、读取按本地时区解释，夹具行因此处于到期状态；调度器自己推进后的 `next_run_at` 为本地墙钟 `2026-10-27 03:50:14.410577`。两种墙钟混用是既有开发库事实（T-06 同），本 Task 只记录读数。

第二个 run 的 `created_count=0` 来自素材 176 已在该策略下建过任务（`previously_run`），不是扫描失败。任务 389 随后由管理员 `POST /api/v1/compose-tasks/389/cancel` 置为 `cancelled`，使双 worker 阶段只剩 387/388 两条待领任务。

## 双 worker 进程抢同一素材

两个 worker 配置树在 `/tmp/chg105-t07/worker-{a,b}/config`，`scheduler/compose.toml` 指向各自 workspace，`node_id` 分别为 1/2、`concurrency=1`、`global_concurrency=2`（与数据库 `compose_worker_capacity.max_running=2` 相同），其余配置为 Cloud `config/` 的符号链接，凭据未复制。

首次以 `global_concurrency=1` 启动被拒绝：

```text
compose worker global concurrency 1 differs from database capacity 2
```

这是容量门禁的真实读数；改为与数据库一致后启动：worker A pid 84587（node 1）、worker B pid 84588（node 2），同时运行。

```text
task 387  claimed_node_id 2  attempt_count 1  success  started 03:53:00.164919  finished 03:53:11.570928
task 388  claimed_node_id 1  attempt_count 1  success  started 03:53:00.164920  finished 03:53:13.397172
```

两条任务的 `started_at` 相差 1 微秒，分别归 node 2 / node 1，说明两条待领任务被两个进程各领一条；`compose_task_attempts` 各只有 1 条 `attempt=1, source=auto, outcome=success`。

成片：

```text
78  task 387  strategy 93  object compose-outputs/387/1/output.mp4  size 1368540  sha256 b968e702…dd6a5  media {"duration_ms":3033}
79  task 388  strategy 94  object compose-outputs/388/1/output.mp4  size 1368540  sha256 b968e702…dd6a5  media {"duration_ms":3033}
```

两个对象键不同、成片行不同；因为同一素材与同一配置，两段成片字节相同，SHA-256 也相同（这是实测结果，不是“对象相同”）。对象探针（临时 `cmd/chg105-object-probe`，已删除）对两个键 `Stat` 均为 1368540；用预签名 URL 下载后本地 `shasum -a 256` 均为 `b968e702…dd6a5`、`ffprobe` 均为 `duration=3.033008 size=1368540`。

步骤耗时（attempt 387 / 388）：

| 步骤 | 387 | 388 |
| --- | --- | --- |
| `prepare_input` | 9,586 ms | 11,692 ms |
| `cut` | 1,252 ms | 1,130 ms |
| `upload` | 468 ms | 331 ms |
| `commit` | 51 ms | 38 ms |

两条任务与两个成片的 `material_usage_id` 均为 NULL、`operator_id=3`、`created_by=1`；双 worker 阶段没有为创建者或负责人创建任何 `material_usages`。

## 额度、负责人失效、跨团队/跨游戏

| 请求 | 结果 |
| --- | --- |
| 96，`chg105-quota-001` | 200；`created_count=1`（素材 162），其余 14 条同游戏候选 `daily_limit` |
| 96，`chg105-quota-002` | 200；`created_count=0`；素材 162 `previously_run`，其余 14 条 `daily_limit` |
| 97，`chg105-missing-op-001` | 400（`15210 compose_strategy_invalid`，`strategy operator is unavailable`），未建任务 |

跨团队/跨游戏：策略 93/94/96 的 `candidate_count` 均为 60，等于团队 1 的素材总数；团队 6 的 8 条素材没有出现在任何 run 的候选或跳过里（对三条策略的全部 `skipped_json` 做 JSON 展开后 `materials.team_id <> 1` 计数为 0）。跨游戏候选按 `other_game` 记录（每个 run 45 条）。

## 人工“我的素材”入口与旧任务重试（策略 98）

管理员调用 `POST /api/v1/compose-tasks`：

```text
{"strategy_id":98,"items":[{"material_id":153,"request_key":"chg105-manual-153-001"}]}
→ 200；任务 391：trigger manual、material 153、material_usage_id 1（非空）、operator 3、created_by 1、pending
```

随后 `POST /api/v1/compose-tasks/391/cancel` → `cancelled`（usage 仍为 1）；`POST /api/v1/compose-tasks/391/retry` → `pending`（usage 仍为 1、created_by 1、operator 3）；再次 cancel → `cancelled`。人工入口仍写个人 usage，取消/重试不改变它。

## 测试同步

四个 live 用例改为不依赖开发库既有数据：

- `schedule_live_test.go`：在事务内复制一条合格策略作夹具并写显式规则；新增 `TestLiveComposeScheduleQuotaAndOperatorGate`，用真实 run 路径测 `single_limit`/`daily_limit` 与 `operator_unavailable`。
- `schedule_process_live_test.go`：夹具补 `operator_id` 与显式规则；来源条件从“创建者有 usage”改为“负责人可用且团队有该游戏素材”。
- `strategy_rules_live_test.go`：解析并写入合格负责人；部分失败的冲突素材改为调度器实际会先尝试的那一条（团队素材 id 序），不再取创建者第一条 usage。
- `batch_live_test.go`：批次夹具改为在事务内自建策略与两行任务，避免开发库无“两任务策略”时静默 skip。

读数：

- `WT_MEDIA_TEST_LIVE_DB=1 WT_MEDIA_TEST_SCHEDULER_PROCESS=1 WT_MEDIA_CLOUD_HOME=$PWD go test ./internal/modules/production/repository/ ./internal/modules/production/service/ -count=1`：全绿；上述四个用例均为 PASS（`TestLiveComposeSchedulerProcessesDeduplicate` 2.01s）。
- `go test ./...`：全绿。
- 仍按各自门禁 skip 的用例（`TestLiveComposeRetryEligibilityPersists`、`TestLiveComposeUncertainReview*`、`TestLiveComposeStagingCleanupCandidates`、`TestHelperComposeClaimProcess`、`TestLiveComposeClaimCapacityAcrossProcesses`、`TestLiveComposeOldGenerationWritesAreRejected`、`TestLiveGuideDownloadComposeAndStorageReadback`）需要各自的专用环境变量，本 Task 不改变其门禁；它们覆盖的是 CHG-095/097 的链路，不是本 Task 的并发口径。

## 覆盖边界

- 双 worker 各自 `concurrency=1`、共享数据库容量 2，验证的是“两个进程各领一条同一素材任务”；没有测试单进程并发 2 的吞吐。
- 两个成片字节相同，因此“对象不同”只成立在对象键与成片行层面，SHA-256 相同是预期结果。
- 调度进程只在策略 95 上验证了双进程与重启。策略 66 同时到期：双进程阶段的扫描（03:49:07）对它写 1 条 `created_count=0` 的 run，重启进程（03:49:14）时它未到期、未扫描；它的任务始终只有 350。之后运行“测试同步”里的 scheduler 进程用例时，用例启动的真实 scheduler 同样扫描所有到期策略——03:54:38 一轮同时给 66 与 95 各写 1 条 `created_count=0` 的 run（同一微秒，同一次扫描）。所以 66 的 run 行数跟着“起过几次真实 scheduler 进程”增长，是本机开发库的累计读数，不是本 Task 某一阶段的增量判据。
- 本 Task 未做页面读回；共用页面与详情页在 T-06 已读回，双 worker 产出的 78/79 只做了 DB 与对象层读回。
- 策略 93–98、任务 387–391、成片 78/79 留在本机开发库供 T-08 收尾，归档后清理。
