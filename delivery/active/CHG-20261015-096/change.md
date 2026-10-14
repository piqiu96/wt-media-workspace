# CHG-20261015-096：M5-C5 技术退避重试与存储异常安全处置

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M5-automatic-production.md`
- Closure anchor: §5 M5-B 的技术失败恢复与临时资源清理；§7 M5-AC-08
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.8.3～5.8.7
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §5.3～5.5、§6.2～6.3
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`
- Current repository: `wt-media-cloud`
- Affected repositories: `wt-media-cloud`

## 目标

已确认旧执行结束的技术失败在同一 `compose_task` 内按数据库记录的时间退避重试，到达上限后明确失败；业务失败和执行结果不明确均不自动重试。失败或取消后的本次临时对象能够安全清理，不删除正式成片或其他领取代次的对象。

## 当前事实与差距

- `compose_task` 已有 `attempt_count`、`max_attempts` 和逐次尝试记录；`storage_error` 与 `task_timeout` 会回到 `pending`，但领取仅按 ID，所谓退避只是单 Worker 的轮询间隔，跨进程立即可重新领取。
- 过期租约已隔离为 `execution_uncertain`；运行中取消与超时共用受控终止路径。不得因重试改回不安全的过期租约重排。
- 上传使用固定的任务级 staging key；存储失败和提交失败的清理不完整，失败的删除也没有独立可核对的恢复事实。
- M5-C4 已提供批次结果读取；本 CHG 不建立第二套任务或批次模型。

## 有序任务

| Task | 可独立验证结果 | 验证 |
| --- | --- | --- |
| T-01 | 持久化 `next_attempt_at`，领取只选到期任务；技术失败在同一任务内按有界指数退避，上限后失败 | Repository 先红后绿测试；真库到期资格读回。双 Worker 完整进程回归列入 T-04 |
| T-02 | 精确区分可重试技术失败与不可重试业务/不明确失败；取消或失租不会产生新的重试 | Service/Worker 分类与进程终止测试 |
| T-03 | 每次领取隔离临时对象，失败/取消/提交后清理；清理失败可扫描恢复且不触碰正式对象 | 存储故障注入、对象键和数据库对账 |
| T-04 | 真数据库、Worker、FFmpeg、对象存储验证重试、耗尽、取消和清理；回归 M5-C3/C4 | 实际进程与存储读回，定向测试和差异审查 |

## 验收

1. 可重试技术错误保留同一任务和策略快照，逐次尝试可追溯；数据库中的下次尝试时间控制所有 Worker，重启不会跳过退避。
2. 退避有界、最大次数生效；耗尽后稳定为 `failed`，没有不可领取的永久 `pending` 行。
3. 输入缺失、模板非法、媒体校验失败及 `execution_uncertain` 不自动重试；旧领取代次不能更新新尝试。
4. 取消/超时的真实 FFmpeg 进程退出后才结束任务；取消不能被重试覆盖。
5. 临时对象可恢复清理，正式对象和其他代次的临时对象不受误删；失败或取消不生成假成片。

## 不做

- 不做结果不明确的人工核对、处置页面、跨策略统计或日志摘要（M5-C6）。
- 不做全链真实时间综合签收和 M4-H2 页面走查（M5-C7 与最终签收）。
- 不引入 MQ、第二张任务表、生产规则表或新的 Worker 服务。

## Pending Questions

None.

## 验收记录

尚未验收；逐任务事实记录在 `evidence/`，进度见 `checkpoint.md`。
