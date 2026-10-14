# CHG-20261014-092：M5-C2 到点调度与幂等任务创建

- Status: DONE
- Level: M
- Milestone: `delivery/milestones/M5-automatic-production.md`
- Closure anchor: §4 M5-A（真实调度这一段）
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.5.7、§5.6
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §4.2
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`
- Current repository: `wt-media-cloud`
- Affected repositories: `wt-media-cloud`

## 目标

独立 Cloud Compose Scheduler 到点读取已启用策略，从策略创建人的有效“我的素材”中按团队/游戏选材，跳过该策略已成功生产或尚在队列/执行中的素材，在单次/每日上限内为每条素材创建独立 `pending compose_task`。重复扫描、并发扫描和进程重启不重复创建。

## 当前事实

- M5-C1 已保存计划与 `next_run_at`，没有任何调度进程或自动任务。
- M4 人工任务、快照和 Worker 底座可复用；自动任务须保留 `scheduled` 触发来源。
- 用户确认素材范围固定为策略创建人的“我的素材”，且同策略已生产的素材跳过。
- 调度运行记录是扫描事实与跳过原因，不是批量执行实体；每条 `compose_task` 独立。

## 有序任务

| Task | 结果 | 验证 |
| --- | --- | --- |
| T-01 | 调度键、计划时间槽、候选素材与跳过原因的存储结构 | MySQL 迁移、约束和 Repository 测试 |
| T-02 | 原子到点扫描、限额、幂等创建和下次计划推进 | Service/Repository 边界测试、并发及重启验证 |
| T-03 | 独立 `cmd/compose-scheduler` 与手动“立即执行”入口；任务列表触发方式筛选 | 进程单独运行、API/Web 测试与双构建 |
| T-04 | 本地真实到点入队、DB/API/UI 事实对账及故障回归 | Scheduler 进程、任务与运行记录对照，定向回归 |

## 验收

1. 到点只创建 `scheduled`、`pending` 的独立任务，不执行 FFmpeg；策略/计划停用不创建。
2. 相同策略、时间槽、素材并发/重启扫描只有一个任务；条件变化后跳过原因可查。
3. 仅从创建人的有效“我的素材”取当前团队/游戏且可用的素材；已成功生产、pending/running、数量超限均按原因跳过。每日限额跨进程生效。
4. “立即执行”单独触发一次筛选和入队，不改变原定 `next_run_at`；操作和权限由服务端控制。
5. 真实计划时间的运行记录、任务和页面查询一致，最终用户视觉/交互签收仍留统一走查。

## 不做

- 不增加核心批次任务表，不在 Scheduler 中下载视频或运行 FFmpeg。
- 不实现 Worker Pool 并发、自动失败恢复或批次结果页面；这些分别属于后续 C3～C6。

## Pending Questions

None.

## 验收结论

T-01～T-04 机器验收通过：本地 MySQL 迁移、独立 Scheduler 双进程并发与重启、策略筛选与限额、运行记录读回、API 路由、Cloud/Desktop 页面构建均有记录。Cloud commit `d6aad32`。M4/M5 用户视觉签收按里程碑决定留到最终统一走查。
