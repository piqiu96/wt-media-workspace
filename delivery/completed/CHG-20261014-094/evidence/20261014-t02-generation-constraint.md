# CHG094 T-02 领取代次约束验证（2026-10-14）

所有生命周期写入（续租、进度、取消确认、失败、成片提交、重排）统一带 `attempt_count = ?`（领取代次）与租约守卫；recover 扫描只做 `FailExpiredComposeLease`（execution_uncertain），不再自动重排。

| 动作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| `go test ./internal/jobs ./internal/modules/production/service ./internal/modules/production/repository ./internal/config ./cmd/compose-worker -count=1` | 代次参数接线后既有回归通过 | 五个包全部 ok | PASS |
| `WT_MEDIA_TEST_COMPOSE_CLAIM_PROCESS=1 WT_MEDIA_CLOUD_HOME=<cloud仓> go test ./internal/modules/production/repository -run 'TestLiveComposeClaimCapacityAcrossProcesses\|TestLiveComposeOldGenerationWritesAreRejected' -count=1 -v`（真 MySQL，连跑 5 轮） | 双进程竞争与旧代次拒绝成立 | 5 轮 × 2 测试全 PASS；容量轮 node1 领 2、node2 领 0，running=2 pending=2 | PASS |
| 变异对照：`renewComposeLease` 的 `attempt_count = ?` 改为 `attempt_count >= ?` 后重跑 live 旧代次测试 | 测试必须变红（同 node 旧代次可续租） | `old-generation renew must be refused: ok=true`，FAIL；恢复后 PASS | PASS（判别性变异确认测试能失败） |
| 排障记录：live 测试首轮出现种子任务被 node=1 领走并置 failed 的 flaky | 非本测试行为 | 发现 CHG093 验证残留的 `chg093-server` 与 `chg093-worker` 进程仍在领任务；停止两个进程后 5 轮连续稳定 | PASS（环境残留，非实现缺陷；容量门槛期间两进程合计领取数从未同时超过上限） |

新增测试文件 `internal/modules/production/repository/task_lifecycle_process_live_test.go`（门禁 `WT_MEDIA_TEST_COMPOSE_CLAIM_PROCESS=1`，真 MySQL，自建任务跑后清理，容量行恢复原值）。迁移 059 已通过 `scripts/migrate.sh` 应用到本地稳定库。
