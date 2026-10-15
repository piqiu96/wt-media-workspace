# CHG-20261015-097：M5-C6 结果不明确任务的人工核对与处置

- Status: DONE
- Level: M
- Milestone: `delivery/milestones/M5-automatic-production.md`
- Closure anchor: §3 M5-D 的人工处置段、§5 M5-B 的管理员核对口径
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.6.7、§5.8.6～5.8.7、§5.10.4
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §5.3～5.5、§6.3
- Contract owner: `wt-media-cloud`，`contracts/cloud-api/v1/content-production.openapi.yaml`
- Current repository: `wt-media-cloud`
- Affected repositories: `wt-media-cloud`

## 目标

管理员在任务详情看到 `execution_uncertain` 的真实尝试与诊断摘要；核实旧 FFmpeg 已停止且没有已提交成片后，填写依据并原子地重新排队同一任务。无法核实的任务维持失败待处置。运营仍能按原有任务、策略运行记录查看状态与统计，系统不推断已安全恢复。

## 当前事实与差距

- CHG094 将过期租约终结为 `failed / execution_uncertain`；CHG096 禁止其自动重排和自动清理。现有人工 retry 明确拒绝该错误码。
- 任务详情已有逐次尝试记录；策略页已有运行记录及批次状态统计。尚无管理员确认依据、原子处置入口和处置读回；页面也没有明确的待处置提示与脱敏诊断摘要。
- Cloud 拥有任务、API 与共用 Vue 页面；Desktop 不复制业务页面，Agent 不参与 Cloud FFmpeg 处置。新增 Cloud API 为兼容性增量，正式合同先于实现更新。

## 有序任务

| Task | 可独立验证结果 | 验证 |
| --- | --- | --- |
| T-01 | 固定兼容性 Cloud 合同、管理员核对条件与失败语义 | OpenAPI/Service 先红测试、Contract 校验 |
| T-02 | 管理员填写核对依据后，在单事务中记录处置并重排同一任务；重复请求、无权限、仍有成片或状态已变均拒绝 | Repository/Service 单测和真库读回 |
| T-03 | 任务详情显示待处置提示、尝试事实和脱敏诊断摘要；仅管理员看见处置入口，完成后读回；现有策略运行统计继续与任务对账 | Vue 定向测试、API/UI 对账 |
| T-04 | 真 MySQL 对 `execution_uncertain` 及并发处置进行验证，回归重试、任务列表和 M5-C4 统计 | 真库、API、Web 测试与差异审查 |

## 验收

1. `execution_uncertain` 不自动重试；普通重试仍拒绝。仅管理员可提交非空核对依据，明确声明旧执行已停止、没有已提交成片。
2. 处置与人工重试同一事务，保留任务 ID、策略快照、旧尝试和错误事实，新增人工尝试及审计；重复或并发处置只成功一次。
3. 已存在成功成片、任务不再为 `failed / execution_uncertain`、或无法核实均不排队；页面不宣称系统自动验证管理员声明。
4. 任务详情按权限展示脱敏的阶段/时间/错误摘要和处置读回，不暴露原始命令、凭据、签名地址；现有策略批次统计和任务筛选回归。

## 不做

- 不做真实计划时间到成片下载的全链签收或 M4-H2 页面走查（M5-C7）。
- 不新增 Worker 服务、任务状态枚举、第二套任务表或自动解除 `execution_uncertain`。
- 不把任务操作日志当成 FFmpeg 原始日志提供给普通运营。

## Pending Questions

None.

## 验收记录

T-01～T-04 机器验收通过；逐项事实、命令和边界见 `evidence/`：

1. **PASS**：过期租约仍隔离为 `failed / execution_uncertain`，普通重试和自动重试都拒绝；只有管理员同时确认旧执行已停止、无已提交成片并填写依据，才能调用专用处置。
2. **PASS**：真库事务保留原任务、快照与旧尝试，写入核对依据和审计、打开新人工尝试；重复及并发请求只有一次成功。
3. **PASS**：已有成片、状态变化或无法核实均不排队。页面将核对标为管理员声明，不能以数据库中的租约到期冒充进程退出证明。
4. **PASS**：任务与尝试 API 错误文本为固定脱敏摘要，任务 API 参数快照隐藏引导视频下载地址；页面按权限展示核对入口与读回。全量 Web 测试、任务筛选及真库批次统计、双进程调度回归通过。

验证边界：旧的等待输入取消真库用例因当前无未准备素材跳过，真实 FFmpeg 中途取消仍通过；真实浏览器人工走查、实际计划时间端到端签收属于 M5-C7。Cloud 提交 `6ea61c7`、`0032eac`、`7c335b1`、`d14016a`、`fb6371b`。
