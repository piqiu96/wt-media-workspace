# CHG094 T-03 磁盘容量停领与既守卫收口（2026-10-14）

heartbeat 失联终止与过期租约 `execution_uncertain` 隔离在 T-01/T-02 段已实现并有证据；本段补齐 T-03 剩余项：本机磁盘容量不足暂停领取，恢复后自动继续，读不到容量事实同样停领。

| 动作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 先红：新增 `TestComposeWorkerPausesClaimingWhileDiskIsBelowTheMinimum` / `...CannotBeRead`（注入 DiskFree 假实现）在暂停逻辑落地前运行 | 两个测试必须失败 | 均超时于「pausing claims 日志未出现」，且低容量期间领取数仍增长（未实现停领） | PASS（先红成立） |
| 实现后 `go test ./internal/jobs -count=1` | 停领、恢复日志、读容量失败停领、恢复续领全部成立；既有 loop 回归不破 | 包 ok | PASS |
| `go test ./internal/config -count=1`（fixture 增加 `min_free_bytes`，`TestLoadFromDirRefusesInvalidComposeWorkerSettings` 增加 `min_free_bytes = 0` 用例） | 配置缺失/非法拒绝启动 | 包 ok，新用例通过 | PASS |
| `go test ./internal/config ./internal/jobs ./cmd/compose-worker ./internal/modules/production/repository -count=1`；live 门禁测试复跑 | 全量回归 | 全部 ok | PASS |
| 故障注入：DiskFree 返回 error（模拟 statfs 失败） | 不领取新任务，记录「cannot read free disk space」，容量可读后恢复 | 单测断言成立 | PASS |

实现：`ComposeWorkerConfig.MinFreeBytes`（两份 compose.toml 均为 10 GiB）→ `ComposeWorkerSettings` 校验拒绝非正值；slot 领取前探测 workspace 卷剩余空间，低于门槛或读取失败进入停领态（只记一条进入日志），恢复后记一条 resume 日志继续领取。默认实现为 `syscall.Statfs` 的 `Bavail*Bsize`。
