# CHG094 T-04 真实 Worker 进程回归与 logger 缺陷修复（2026-10-14）

门禁测试 `cmd/compose-worker/live_worker_test.go`（`WT_MEDIA_TEST_COMPOSE_WORKER_PROCESS=1`）：`go build` 出真实 compose-worker 二进制，打真 MySQL + 对象存储 + FFmpeg；各测试自种子任务（按 `chg094-worker-<nanos>` 前缀清理）。最终二进制完整复跑（6 项，共 94.1s）：

| 动作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 容量不一致拒启：DB 容量 = 配置+1，启动真实进程 | 拒绝启动且报出容量不一致 | 1.25s PASS，报文含 "differs from database capacity" | PASS |
| 真实任务到 success：克隆最近成功 basic_cut 任务 | success + 输出落库 + 正式对象可读 + run 目录清理 | 首轮 209.99s：任务 163 → output 30 → `compose-outputs/163/output.mp4`，storage.Stat 通过；最终轮 31.19s（源已缓存） | PASS |
| 等待输入期取消：源未就绪素材使 attempt 停在等待输入，置 `cancel_requested` | cancelled 且无 composite_outputs 行 | 首轮 5.24s PASS（任务 158）；最终轮 SKIP——素材 35 已被准备好，环境无未就绪素材，前置条件缺失 | PASS（首轮）/ SKIP（复跑） |
| 中途取消（cutting 阶段）：FFmpeg 运行中置 `cancel_requested` | cancel watcher 停 FFmpeg、确认取消、无输出无 run 目录 | 首轮 72.36s（任务 166）、最终轮 39.50s PASS；无 composite_outputs 行，`task-<id>-` 目录无残留 | PASS |
| 磁盘停领与恢复：`min_free_bytes` 临时抬到 1 TiB 启动真实进程，恢复配置后重启 | 暂停期 pending 任务不被领取且 job.log 记录；恢复后被领取 | 17.07s PASS：任务 168 暂停期保持 pending、job.log 含 "pausing claims"；恢复配置重启后进入 running | PASS |
| 启动期过期租约隔离：种 running + 过期租约 + 他节点 888 的 attempt | 隔离为 `execution_uncertain`，attempt 记 failed，不重排 | 3.20s PASS（任务 165；首轮任务 162） | PASS |

## 发现并修复的真缺陷：compose-worker 从未初始化 logger

成功测试的进程输出暴露：SIGTERM 时 `panic: logger: resources called before Initialize`（栈到 main.go `logger.Job()`），且 `logs/job.log` 在当日运行期间 mtime 不动——worker 的全部日志写不进文件。

- 先红：`stopWorkerProcess` 增加「SIGTERM 后进程输出不得含 panic」断言，隔离测试复跑 1.93s FAIL，panic 栈直指 `logger.Job()`。
- 修复：`cmd/compose-worker/main.go` runWorker 在配置加载后 `logger.Initialize(cfg.Loggers)` + `defer logger.Close()`。
- 阳性对照：修复后 `logs/job.log` 出现 `compose worker stopped node_id=1`（2026-10-14T23:25:02，即隔离测试的 SIGTERM 收尾），停机日志真正落盘。

## 覆盖面登记

- 双进程领取竞争与旧代次写入拒绝：T-02 的真 MySQL 双进程测试覆盖（证据 `20261014-t02-generation-constraint.md`）。
- 取消家族：等待输入期（任务 158）与 FFmpeg 中途（任务 166）均真实进程覆盖；后者最终轮复跑成立。
- 任务超时路径：仅单测覆盖（真实进程下超时需要缩配置超时并等待，机制与取消共用 attempt ctx 终止路径）。
- 磁盘停领与恢复：真实进程覆盖（抬高/恢复 `min_free_bytes` 实测）。

## 收尾读数

- 最终二进制门禁套件：5 PASS + 1 SKIP（前置条件缺失），共 94.1s，进程输出无 panic。
- 全量 `WT_MEDIA_CLOUD_HOME="$PWD" go test ./...`（非门禁）：71 包 ok，0 失败。
