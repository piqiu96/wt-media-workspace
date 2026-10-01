# Task 22 证据：下载「正在取消」卡死——transfer-reconcile 从未被调度（走查反馈）

- 日期：2026-10-01
- CHG：CHG-20260930-069（走查反馈折入）
- 仓库：`wt-media-cloud`（唯一改动仓）
- 提交：Cloud `d200bb1`
- 用户反馈：走查中「一直卡在正在取消过程中，状态卡住无法处理」

## 根因（已核实）

取消是**两阶段**设计：`CancelTask` 对 `pending` 任务直接写终态 `cancelled`；对 `running` 任务**只写 `cancel_requested_at`**，终态由执行器（Agent/worker）在下次 heartbeat/progress/complete 撞上 `cancel_requested_at IS NOT NULL` 谓词时自己写入（`service.go` `CancelTask` + `store_mysql.go` `cancelTask` 两臂）。执行器失联（关机/进程被杀）就永远不写终态；且 `leaseable` 谓词要求 `cancel_requested_at IS NULL`，带取消请求的任务**不可被认领**——没有任何东西能收尾。

兜底机制早已写好、单测通过，但**从未被调度**（死代码）：
- `ReconcileCancelledTasks`（`repository/store_mysql.go:801`）：`running` + `cancel_requested_at IS NOT NULL` + 租约过期 → 终态 `cancelled`（`cancelled_by_user`），并释放依赖它的下载；
- `ReconcileExhaustedTasks`（`:829`）：`running` + 无取消请求 + `attempt_count >= max_attempts` + 租约过期 → 终态 `failed`（`lease_expired`）；
- 两者的 repo 级测试已在 `store_mysql_test.go:425/449` 覆盖（含依赖下载释放计数），本轮重跑 PASS。

注册缺口：`internal/bootstrap/jobs.go` 里 `runSchedulerProcess` 只注册 discovery-schedule/proxy-expiry，`runWorkerProcess`（`:30`）只注册 discovery-worker/material-prepare-worker——**没有任何进程注册 transfer-reconcile**。而当前部署只跑 `cmd/server` + `cmd/discovery-worker`（worker 在用），**scheduler 进程根本没起**，所以修复只能落在 worker 进程。

线上库实证 3 行卡死（走查中用户两次取消留下的）：

| task_id | attempt | status | cancel_requested_at | claimed_by |
| --- | --- | --- | --- | --- |
| `transfer_56c2ae6c` | 1/3 | running | 12:14 | `agent-node_737c`（已死） |
| `transfer_7ee630f9` | 3/3 | running | 12:14 | 已死节点 |
| `transfer_a00ea9d6` | 3/3 | running | 12:14 | 已死节点 |

三者都是 `user_download`/`local_agent`、租约早已过期、`claimed_by` 于已死节点 → 前端的「正在取消」永远等不到终态。三者都有取消请求 → 归 `ReconcileCancelledTasks` 收成 `cancelled`。前端 `downloadFacts.js` `taskState` 终态优先（success/failed/cancelled 先判），行一落终态「正在取消」即清——**前端无缺陷，未改**。

## 改动（仅 `wt-media-cloud`）

1. **新增 `internal/jobs/transfer_reconcile.go`**：`RunTransferReconcile(ctx)` 依次调 `transferrepo.ReconcileCancelledTasks(time.Now())` 与 `ReconcileExhaustedTasks(time.Now())`，汇总计数；仅当本趟实际收走行（>0）才打一条 `logger.Job().Infof`（每 5s 一趟的空跑是噪声，静默原则同 material-prepare）。依赖组装照抄 `RunMaterialPrepareWorker`/`NewPreparer` 范式——reconcile 走全局 `database.DB()`，**不需要对象存储**，不做 `storage.Configured()` 早退。
2. **`internal/bootstrap/jobs.go` `runWorkerProcess` 增注册**（material-prepare-worker 之后）：
   `runner.Register("transfer-reconcile", cfg.Scheduler.WorkerInterval.Duration, func(ctx) error { return jobs.RunTransferReconcile(ctx) })`
   复用 `worker_interval`（5s），**零 config 改动**（`config/scheduler/scheduler.toml` 无 reconcile key，也不新增）。挂 worker 进程而非 scheduler 进程，因为部署只跑 server+worker——挂 scheduler 仍是死代码。

## 测试

- **新增 `internal/jobs/transfer_reconcile_test.go`**：编译期绑定 `var run func(context.Context) error = RunTransferReconcile`，证明出口以 `scheduler.JobFunc` 形状存在（照抄 `discovery_test.go:8` 范式）。
- **既有 repo 机制测试重跑**：`TestReconcileCancelledTasksFinishesCancellationsTheirExecutorAbandoned`、`TestReconcileExhaustedTasksFailsTasksThatUsedEveryAttempt` PASS（含「租约未过期不动」「依赖下载随行释放」的阳性对照）。

## 读数

- `gofmt -l internal/jobs/ internal/bootstrap/` → 空
- `go build ./...` → 干净
- 定向：`go test -count=1 ./internal/jobs/ ./internal/modules/filetransfer/... ./internal/bootstrap/` → 全部 ok
- 全量：`go test -count=1 ./...` → **66 包 ok / 0 FAIL**

## 相关提交

- `wt-media-cloud`（本任务提交，见文末 commit）
- 本 Workspace（证据 + checkpoint + change.md §5 任务 22，随本记录提交）

## 验证 / 剩余

端到端（重建 Cloud，**Agent 保留不重启**——沿用节点绑定约束）：杀掉旧 Cloud（18080）→ m2b `up`（新后端含 transfer-reconcile 调度）→ 只重启 worker 进程；一个 `worker_interval`（≤5s）内 3 行卡死自愈成 `cancelled`：

```sql
SELECT id, status, cancel_requested_at, error_code, claimed_by_node_id FROM file_transfer_tasks WHERE status='running';
```

→ 0 行。走查界面：下载中心两处「正在取消」清成「已取消」，可再次点下载产生新行，不再卡死。
