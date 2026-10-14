# CHG-20261014-094 Checkpoint

## Completed

- CHG093 已归档。对照 M5 §5、工程设计 §5 与现有 Worker，确认全局容量、领取代次和过期租约是首要缺口。
- T-01 首批失败用例复现：旧逻辑会自动重排未经确认的过期租约，heartbeat 数据库错误后仍继续执行。现已改为过期租约标记 `execution_uncertain`、续租失败即停止执行；定向测试通过。
- T-02 完成：迁移 059 增加跨进程容量锁行；领取事务在行锁下检查全局 running 数量，Worker 启动时校验配置与数据库容量一致。全部生命周期写入统一加领取代次（`attempt_count = ?`）守卫；recover 扫描移除自动重排，只保留 `FailExpiredComposeLease`。真 MySQL 双进程领取竞争测试与同 node 旧代次拒绝测试通过，判别性变异确认测试会红。期间清除 CHG093 残留 server/worker 进程（flaky 根因）。
- T-03 完成：领取前探测 workspace 卷剩余空间，低于 `min_free_bytes`（10 GiB）或读取失败即停领并记日志，恢复后自动续领；配置层拒绝非法值。先红成立。
- T-04 完成：真实进程门禁测试 `cmd/compose-worker/live_worker_test.go`——容量不一致拒启、真实任务到 success（任务 163 → output 30，正式对象可读、run 目录清理）、等待输入期取消（任务 158）、cutting 中途取消（任务 166，无输出无残留）、磁盘停领与恢复（任务 168：抬阈值停领 → 恢复后被领取）、启动期过期租约隔离（任务 165）。期间坐实并修复 compose-worker 从未初始化 logger 的真缺陷，先红后绿，job.log 停机日志为阳性对照。
- CHG 已归档：验收 1–5 逐项核对通过，工程规范 §5.1/5.2/5.3 与 M5 里程碑（C3 状态、AC-05/06/07）已回写。

## Current

- Cloud `3a32d91`、`9765610`、`82a3fa3` 已提交；CHG 归档至 `delivery/completed/`。

## Next

- 按 MASTER_IMPLEMENTATION_PLAN 与当前代码状态建议下一个 CHG（M5-C4 批次结果归集），不自动实施。

## Blockers

None.

## Recent verification

- 最终二进制门禁套件 6 项：5 PASS + 1 SKIP（等待输入期取消因素材就绪缺前置条件；首轮任务 158 已 PASS），共 94.1s，进程输出无 panic。
- `go test ./...` 71 包 ok、0 失败。
- 诚实边界：任务超时真实进程路径未单独演示，与取消共用 attempt ctx 终止，单测覆盖（见 T-04 证据「覆盖面登记」）。
