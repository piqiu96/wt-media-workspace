# 阶段 6：周期触发与双层防重

> 由 `tools/render-evidence.py` 从 `run-manifest.json` 渲染，每一步可回溯。
> 判定分布：FAIL=2，PASS=7。

| 步骤 | 判定 | 请求 | 期望 | 实际 |
| --- | --- | --- | --- | --- |
| 6.1 | PASS | POST /discovery-strategies schedule=interval:5 且 enabled | 201，创建即启用 | HTTP 201 id=29 |
| 6.2 | FAIL | 启动 cmd/discovery-scheduler 并观察 75s | 调度进程应持续存活并按 discovery_interval 触发 | 存活=False exit=2 panic=panic: douyin: Get called before Initialize |
| 6.3 | PASS | POST /discovery-scheduler/run-due（管理员受控，同一 runDue 实现） | triggered>=1，生成 schedule_key 非空的 discovery_task | HTTP 200 triggered=2 |
| 6.4 | PASS | SQL 读回调度窗口键 | schedule_key 形如 interval:5:<epoch/300> 且 task_type=discovery_task | task_id=72 schedule_key=interval:5:5967051 task_type=discovery_task |
| 6.5 | PASS | SQL 读回周期任务执行结果 | Worker 写入 started_at/finished_at 并给出终态 | status=success started=2026-09-23 06:16:12.500834 finished=2026-09-23 06:16:16.485304 stats={"added": 11, "found": 20, "failed": 0, "pending": 11, "scanned": 20, "duplicate": 9, "auto_materialized": 0} |
| 6.6 | PASS | 同一窗口内再调一次 run-due | triggered=0：同策略同计划周期不重复排队 | HTTP 200 triggered=0 |
| 6.7 | PASS | SQL 统计同 schedule_key 行数 | 同窗口只有 1 行 | count=1 |
| 6.8 | PASS | SHOW INDEX uq_crawl_tasks_strategy_schedule | 唯一键存在（第二层防重） | rows=2 列=['uq_crawl_tasks_strategy_schedule', 'uq_crawl_tasks_strategy_schedule'] |
| 6.9 | FAIL | POST /discovery-strategies/<id>/run 连调两次 | 基线 §5：同策略已有 pending/running 时不重复排队 | HTTP 201/201，pending 行 0 -> 2 |

## 备注

> **2026-09-23 复验补记（本页为原始渲染，保留不改）**：6.2 已修复并复验通过，
> 验收项 2 改判通过。**下方 6.2 的根因归因已被更正**：不是「`schedulerResourcePlan()`
> 不含 `clientsResource()`」，而是 `0699e8a` 拆分进程时只给 server/worker 补了 clients、
> 调度路径漏补的**未收尾迁移遗留**。详见 `15-dscheduler-fix-reverification.md`。

- **6.2**：~~schedulerResourcePlan() 不含 clientsResource()~~（归因已更正，见上方补记），
  而 RunDiscoverySchedule→RunDue→newDouyinCrawler()→douyin.Get() 要求已 Initialize，故首次 tick 即 panic 退出
- **6.3**：这一步验证调度语义，不主张等价于周期 tick（tick 执行者已崩溃）
- **6.9**：D3：/run 传空 schedule_key→NULL，唯一索引不拦 NULL，可重复排队
