# CHG-20261014-094 Checkpoint

## Completed

- CHG093 已归档。对照 M5 §5、工程设计 §5 与现有 Worker，确认全局容量、领取代次和过期租约是首要缺口。
- T-01 首批失败用例复现：旧逻辑会自动重排未经确认的过期租约，heartbeat 数据库错误后仍继续执行。现已改为过期租约标记 `execution_uncertain`、续租失败即停止执行；定向测试通过。
- T-02 第一段：迁移 059 增加跨进程容量锁行；领取事务在行锁下检查全局 running 数量，Worker 启动时校验配置与数据库容量一致。定向测试通过。
- T-02 第二段完成：全部生命周期写入统一加领取代次（`attempt_count = ?`）守卫；recover 扫描移除自动重排，只保留 `FailExpiredComposeLease`。真 MySQL 双进程领取竞争测试与同 node 旧代次拒绝测试通过，判别性变异（放开 attempt 等值守卫）确认测试会红。期间发现并清除了 CHG093 残留的 server/worker 进程（flaky 根因）。

## Current

- 无进行中改动；T-02 已收口。

## Next

- T-03：本机磁盘容量不足暂停领取（故障注入验证）；heartbeat 失联与 execution_uncertain 的既有实现补充对照证据。
- T-04：真实 Worker 并发、重启、超时/取消、容量与对象存储回归。

## Blockers

None.

## Recent verification

- Cloud `93e6e94`、Workspace `6e98d87`；两个仓库工作区清洁。
- `go test ./internal/jobs ./internal/modules/production/service -count=1` 通过；新增测试改动前分别以自动重排和续租错误后继续运行失败。
- `go test ./internal/config ./internal/modules/production/repository ./cmd/compose-worker -count=1` 通过；容量测试改动前因没有全局容量查询失败。
