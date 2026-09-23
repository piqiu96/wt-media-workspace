# M3 Scheduler / Worker 边界验证

- 日期：2026-09-16
- 范围：Cloud Scheduler 只创建任务、Discovery Worker 原子领取并执行、Cloud 本地独立 CMD/脚本入口。

| 验证 | 命令/动作 | 实际结果 | 状态 |
| --- | --- | --- | --- |
| 服务层 RED/GREEN | 为“入队不执行”“Worker 单次领取”“历史任务兼容”先编写失败测试，再执行 `go test ./internal/modules/contentpool` | 测试先因缺少 `RunNext` 失败；实现后通过 | PASS |
| 领取事务 | `go test ./internal/modules/contentpool` | sqlmock 验证 `FOR UPDATE SKIP LOCKED`、状态条件更新和空队列不更新 | PASS |
| Scheduler/Worker 基础设施 | `go test ./internal/infra/scheduler ./internal/infra/worker` | Scheduler 单次调用仅触发入队；Worker 以批量上限领取至空队列 | PASS |
| 全量回归 | `wt-media-cloud/scripts/test.sh` | Go 全包通过；Web Vitest 20 个文件、76 个测试通过 | PASS |
| 命令构建 | `go build ./cmd/server ./cmd/discovery-scheduler ./cmd/discovery-worker` | 三个命令均构建成功 | PASS |
| 本机迁移 | `scripts/migrate.sh` | `20260916_031_crawl_task_schedule_key` 已应用；共 32 条迁移 | PASS |
| 独立入口 | `scripts/run-discovery-scheduler.sh`、`scripts/run-discovery-worker.sh` | 分别返回 `queued=0`、`processed=0`；空队列下不产生副作用 | PASS |
| 本地运行时 | `scripts/start.sh` 后请求 `GET /api/v1/health` | 返回 `{"status":"ok"}` | PASS |

备注：真实外部 Douyin 调用的成功性仍依赖有效的服务端授权样本；本次验证不将空队列或 HTTP 健康成功误报为外部发现成功。
