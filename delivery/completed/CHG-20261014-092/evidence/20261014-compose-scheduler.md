# CHG092 机器验证

| 动作 | 预期 | 实际 | 结论 |
| --- | --- | --- | --- |
| 本地 MySQL 应用迁移 058 | 计划时间槽唯一键与运行表就绪 | `scripts/migrate.sh` 输出 1 applied，60 total；事务读回成功 | PASS |
| 本地真实数据库执行 `TestLiveComposeScheduleDueAndRepeatScan` | 到点入队、重复扫描不再入队、手动执行不推进计划、跳过原因可读 | strategy 11：2 个候选、1 个创建、1 个 `other_game`；每日/单次上限与 `already_produced` 检查通过 | PASS |
| 本地真实数据库执行 `TestLiveComposeSchedulerProcessesDeduplicate` | 两个独立进程竞争同一时间槽，重启不重复 | 测试专用策略 14：1 条运行记录、1 条 `scheduled` 任务；重启后仍 1 条；测试数据已清理 | PASS |
| `go test ./internal/modules/production/... ./internal/config ./internal/bootstrap ./internal/jobs -count=1` | 相关 Go 测试通过 | 所有目标 package 通过 | PASS |
| `npm run test -- src/modules/compose src/shared/api/compose.test.js` | 调度页面/API 定向回归通过 | 7 个文件、35 个测试通过 | PASS |
| `npm run build:cloud` 与 `npm run build:desktop` | 共用页面可分别构建 | 双构建通过；现有 bundle size 提示 | PASS |
| `go build -o /tmp/wt-compose-scheduler-check ./cmd/compose-scheduler` 与 Linux 打包单测 | 独立可执行进程进入发布清单 | 编译成功；打包 3 个测试通过 | PASS |
| Contract YAML 解析与 `git diff --check` | 合同格式和 diff 清洁 | 解析与检查通过 | PASS |

用户的 M4/M5 页面视觉走查按里程碑约定最后统一进行。

Cloud 实现提交：`d6aad32`。
