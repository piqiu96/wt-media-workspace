# CHG-20261013-089：M4-G 任务执行尝试记录与人工失败重试

- Status: PLANNED
- Level: L
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §3 M4-G；§「页面缺口的独立闭环」M4-G 行
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.8.4～§5.8.6、§5.10.3
- Affected repository: `wt-media-cloud`（Cloud API、MySQL、Cloud Web/Desktop 共用 Vue）

## 目标

运营能在任务详情看到每次执行的独立记录；失败任务按明确分类获得人工重试，重试有权限、幂等和审计；成功任务详情能关联成片。不能拿任务摘要冒充执行日志。

## 当前事实

- `compose_tasks` 只有 `attempt_count/max_attempts` 与最近一次 `error_code/error_message`，无逐次尝试记录表。
- Worker 自动重试：`storage_error`/`task_timeout` 经 `ReleaseComposeForRetry` 回 pending；`template_unavailable`/`input_missing`/`input_invalid`/`execution_failed` 终态失败。
- 审计设施已有（`appendComposeTaskAudit`）；角色已有 `RoleSeniorOperator`/`RoleAdmin`（PRD §5.10.3 重试属高级运营）。
- 无人工重试端点；任务详情不输出成功任务的成片关联（`composite_output_id` JSON 隐藏）。

## 范围与决定（用户已确认）

1. 新表 `compose_task_attempts`：每次尝试一条——task_id、attempt 序号、来源（auto/manual）、开始/结束时间、结果（success/failed/cancelled）、阶段、错误码与消息。Worker 在领取时开行、终态或回队列时收行。
2. 人工重试边界（用户 2026-10-13 确认「边界能定义清楚按规则，定义不清的交人工判断」）：
   - 明确不可重试：`input_missing`、`input_invalid`、`template_unavailable`——服务端拒绝，页面不显示入口并引导新建任务；
   - 明确可重试：`storage_error`、`task_timeout`；
   - 人工判断：`execution_failed`——按钮照给，是否重试由运营看错误信息决定。
3. `POST /compose-tasks/{id}/retry`：仅 `failed` 终态；非 failed 返回命名冲突错误；状态迁移 failed → pending，策略快照不变，`attempt_count` 保留累计、`max_attempts` +1，写任务审计并生成 `source=manual` 的尝试行。范围权限沿任务 scope，角色限高级运营及以上。
4. `GET /compose-tasks/{id}/attempts` 返回逐次执行记录；任务详情输出 `composite_output_id`（可空，只给 ID 不给对象地址）。
5. 页面：任务详情按「当前任务及状态 → 素材与策略快照 → 执行记录 → 成片结果」组织；执行记录列表展示每次尝试的时间、结果与失败原因；重试按钮按第 2 条分类显示，普通运营不显示。
6. 排除：不做任务归并/分组、不做批量重试、不做脱敏日志文件查看（尝试记录已带错误消息，日志能力后续按需另立）；M5 调度不受影响。

## 有序任务

| Task | 结果 | 验证 |
| --- | --- | --- |
| T-01 | 合同、`compose_task_attempts` 迁移、详情输出成片关联 | 迁移包测试、OpenAPI 解析 |
| T-02 | Worker 尝试记录写入、执行记录端点、人工重试端点（分类/权限/幂等/审计/状态迁移） | 服务与仓库单测、SQL 断言 |
| T-03 | 任务详情执行记录、重试按钮与分类引导、成片关联展示 | 页面接线测试、Cloud/Desktop 构建 |
| T-04 | 回归与真实 MySQL 迁移读回、交付收口 | 全量 Go/Web、真实库读回；真实失败任务的重试链路走查留 M4-H |

## 验收

1. 失败任务详情可见每次尝试的独立记录（时间、来源、结果、失败原因），与任务摘要字段不混用。
2. `storage_error`/`task_timeout`/`execution_failed` 的 failed 任务可被高级运营重试；`input_missing`/`input_invalid`/`template_unavailable` 重试被服务端拒绝且页面无入口；普通运营无重试能力。
3. 重试后任务回 pending、快照不变、`attempt_count` 保留、`max_attempts` 增加 1，审计与 `source=manual` 尝试行可见；对非 failed 任务重试得到明确冲突错误。
4. 成功任务详情输出成片 ID 并能跳转；页面构建 Cloud/Desktop 通过。

## Pending Questions

None. 重试边界规则已由用户 2026-10-13 确认。
