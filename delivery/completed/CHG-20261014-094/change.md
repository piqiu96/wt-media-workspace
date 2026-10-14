# CHG-20261014-094：M5-C3 Worker 全局容量与安全恢复

- Status: DONE
- Level: M
- Milestone: `delivery/milestones/M5-automatic-production.md`
- Closure anchor: §5 M5-B（Worker 资源控制与恢复中的 C3）
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.8
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §5
- Current repository: `wt-media-cloud`
- Affected repositories: `wt-media-cloud`

## 目标

多个 Cloud Compose Worker 同时运行时，实际执行数不超过系统配置上限；旧执行失去租约后不能提交或覆盖新结果。任务超时、取消、Worker 退出和磁盘容量不足都有可验证的终止或停领结果。无法证明旧执行已停止的过期租约进入待人工处置的失败事实，不自动启动第二个 FFmpeg。

## 当前事实与缺口

- 每进程已有 `concurrency` 个 slot、原子领取、heartbeat、单任务超时和本机文件锁；但两个进程的 slot 会叠加，没有系统总上限。
- 现有生命周期写入只按 `node_id` 判断，进程误复用同一 ID 时旧执行可能误写；过期租约被直接重排，未证明旧进程或 FFmpeg 已结束。
- heartbeat 的数据库错误仅记日志并继续执行；没有临时目录可用容量门槛和跨进程的可观察容量事实。
- M5-C5 负责可恢复技术失败的退避重试，M5-C6 负责结果不明确的人工处置；本 CHG 不提前增加第二套重试或后台页面。

## 有序任务

| Task | 结果 | 验证 |
| --- | --- | --- |
| T-01 | 固化并发、同 ID 旧执行、过期租约与 heartbeat 中断的失败用例 | 最小 Repository/Worker 测试先复现 |
| T-02 | 领取事务统一执行全局容量门槛，按领取代次约束所有生命周期写入 | 双进程数据库竞争与旧代次拒绝测试 |
| T-03 | heartbeat 失联即受控终止；过期租约无终止证明时转为 `execution_uncertain`，不自动重排；本机磁盘容量不足暂停领取 | 故障注入、状态与进程对照 |
| T-04 | 真实 Worker 并发、重启、超时/取消、容量与对象存储回归 | 实际进程、MySQL、FFmpeg 和指标/日志证据 |

## 验收

1. 两个或更多 Worker 总运行数不超过统一上限；配置非法或不一致时拒绝启动/领取。
2. 同任务任何时刻只有一个有效领取代次；旧代次续租、进度、取消、失败和成片提交全部被拒绝。
3. heartbeat 不可续租、任务超时或取消后，Worker 停止 FFmpeg 并清理本次临时目录；任务状态与真实进程一致。
4. 对无法证明旧执行结束的过期租约，任务结束 `running` 但不自动重排，记录可供 M5-C6 处置的明确原因；不能产生双执行或假成片。
5. 磁盘容量不足时不领取新任务；恢复后可继续，队列与执行指标能从真实状态核对。

## 不做

- 不在本 CHG 增加批次结果页、批量重试、人工不明确结果处置页面；分别留 M5-C4～C6。
- 不增加 MQ、动态 Worker 注册中心或新业务执行实体。
- 不改变策略调度和逐素材任务模型。

## Pending Questions

None.

## 验收结论

T-01～T-04 机器验收通过：

1. 双进程真 MySQL 竞争下恰好领取上限数；配置与数据库容量不一致时拒绝启动/领取（容量测试 + 真实进程拒启）。
2. 同任务单一代次有效；旧代次续租、进度、取消、失败和成片提交在同 node 复现场景下全部被拒绝，判别性变异确认测试会红。
3. 真实进程 cutting 阶段中途取消：cancel watcher 停止 FFmpeg、确认 `cancelled`、无输出无 run 目录残留（任务 166）；任务超时与取消共用 attempt ctx 终止路径，单测覆盖。
4. 过期租约启动恢复隔离为 `execution_uncertain`，attempt 记 failed，不自动重排，不产生双执行或假成片（真实进程任务 165）。
5. 磁盘剩余空间低于阈值时真实进程暂停领取（任务 168 保持 pending，job.log 记录），恢复阈值后被重新领取。

期间发现并修复 compose-worker 从未初始化 logger 的缺陷（SIGTERM panic、job.log 空写），修复后停机日志落盘。诚实边界：等待输入期取消在首轮真实进程通过（任务 158），最终复跑因素材均已就绪而 SKIP。Cloud 提交 `3a32d91`、`9765610`、`82a3fa3`。
