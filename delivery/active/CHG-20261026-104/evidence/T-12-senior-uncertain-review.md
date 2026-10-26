# T-12 高级运营核对执行结果不明确的任务

日期：2026-10-27

## 用户反馈与既有事实

用户走查第 4 项：高级运营应能处理任务 329（执行结果不明确），不需要管理员。

既有事实：2026-10-27 01:42:26，管理员（用户 ID 1）已对任务 329 第 1 次执行提交核对（`compose_uncertain_reviews` 11）；01:42:28–01:42:36 第 2 次执行成功，生成成片 74。任务 329 现为 `success`，不再满足核对表单的 `status=failed` 条件。**不回退、不改写 329、成片 74 或 review 11。**

为覆盖高级运营核对入口，走查前在本地开发库新建同形态夹具 331（见下节）。

## 修订

| 文件 | 修订 |
| --- | --- |
| `internal/modules/production/service/uncertain_review.go` | `visibleAdminTask` 更名为 `visibleReviewTask`；在 `canReadComposeTask` 之后允许 `admin` 或 `senior_operator`；普通运营在可见范围内 403，跨团队高级运营 404；`Resolve` 与 `List` 共用 |
| `internal/modules/production/model/task_json.go` | 默认脱敏错误文案改为“执行异常，请联系高级运营或管理员查看诊断摘要” |
| `web/src/modules/compose/pages/ComposeTasksPage.vue` | `canReviewUncertain` 放行 `senior_operator`；核对区标题“待人工核对”，提示“请联系高级运营或管理员核对”；核对记录显示“核对人 {{ review.actor_user_id }}”；失败原因/待核对块只在 `detail.status === 'failed'` 时渲染 |
| `web/src/modules/compose/retryPolicy.js` | 注释改为“人工核对通道（高级运营或管理员）” |
| `web/src/modules/compose/uncertainReview.js` | 默认兜底错误文案同步 |
| `contracts/cloud-api/v1/content-production.openapi.yaml` | uncertain-review GET/POST 改为“管理员或同团队高级运营”，403 说明同步；schema 的 Administrator→Reviewer 文案；版本 `2026.10.27.1` |
| `config/contract-map.yaml` | `cloud_api.contract_revision: "2026.10.27.1"` |
| 文档 | PRD 第五章 §5.6.6/§5.8.6、工程规格 §5.3/§5.5、M5-C6 追加、ADR-0023 追加 2026-10-27 决议 |

核对规则不变：旧 FFmpeg 已停止、没有已提交成片两项必须同时确认；证据至少 20 字、不超过 2000 字且不含 `://`；重复处置 409；审计与 review 行保留。

## 夹具 331（仅本地开发库，走查后删除）

| 字段 | 值 |
| --- | --- |
| `id` | 331（当前最大 330；插入前确认无同 ID） |
| `display_name` / `request_key` | `CHG104 高级运营核对-素材17` / `chg104-senior-review-17` |
| `status` / `error_code` / `attempt_count` | `failed` / `execution_uncertain` / `1` |
| 团队 / 游戏 / 负责人 / 素材 / 策略 | 1 / `other` / `operator01`(3) / 17 / 47 |
| `material_usage_id` / `created_by` / `max_attempts` | 94 / 3 / 4 |
| `stage` / `progress` / `output_object_key` / `composite_output_id` | `validating_input` / 0 / `''` / `NULL` |
| `template_code` / `template_version` / `config_snapshot_json` | `basic_cut` / 1 / `{"start_seconds":1,"end_seconds":5}` |

同时插入第 1 次 `compose_task_attempts`：`attempt=1, source=auto, outcome=failed, stage=validating_input, error_code=execution_uncertain`。夹具满足 `resolveComposeUncertain` 守卫（`status=failed`、`error_code=execution_uncertain`、`attempt_count>0`、`composite_output_id IS NULL`、`output_object_key=''`、无同任务成片）。

走查前停 compose worker/scheduler；高级运营提交核对后任务变为 `pending`，不会真正执行。

### 夹具实测（2026-10-27 02:28）

- compose worker（pid 60633）已停止，scheduler 未运行；停止前 `compose_tasks` 无 `running` 行。
- 插入前 `id=331` 与 `request_key=chg104-senior-review-17` 均不存在。
- 插入任务 331 与第 1 次失败 attempt（id 261）成功；守卫查询返回 `1`。
- 旧 API 进程重启后，operator01 访问 `/compose-tasks/331/uncertain-review` 返回 404：331 属于 `other`，不在普通运营 `hy,sjz` 的可见游戏范围，属于“按不可见处理”，不是核对角色 403。普通运营在可见范围内的 403 由 `TestUncertainReviewRefusesOperatorsAndOtherTeams` 覆盖；高级运营的可见性与提交由走查 A6a/B5 覆盖。

## 自动验证

### Cloud Go

```text
go test ./internal/modules/production/service -run 'Uncertain|OutputsNarrows' -v -count=1
go test ./...
```

读数：

```text
--- PASS: TestSameTeamSeniorResolvesUncertainExecution
--- PASS: TestUncertainReviewRefusesOperatorsAndOtherTeams
--- PASS: TestUncertainReviewKeepsTheEvidenceAndConfirmationRules
go test ./...  ok=72 fail=0 no_test_files=11
```

- `TestSameTeamSeniorResolvesUncertainExecution`：同团队高级运营可成功核对并生成新人工尝试；重复处置 409。
- `TestUncertainReviewRefusesOperatorsAndOtherTeams`：普通运营在可见范围内 Resolve/List 均 403；跨团队高级运营 404。
- `TestUncertainReviewKeepsTheEvidenceAndConfirmationRules`：管理员路径的两项确认、证据长度与格式规则不变。

### Vitest（`web/` 下）

```text
npm test -- --run src/modules/compose
```

`ComposeTasksPage.test.js` 32 个用例通过，包含：

- `canReviewUncertain` 同时接受 `senior_operator` 与 `admin`；
- 标题“待人工核对”、记录“核对人 {{ review.actor_user_id }}”，不出现“待管理员核对”“仅管理员”“管理员才能核对”；
- 成功任务不渲染失败原因/待核对块（`detail.status === 'failed'` 双重门禁）。

全量：Vitest 80 文件 / 736 用例通过。

### 合同

`python3 scripts/verify/verify_m0_config.py` → `Workspace config verification ok`。

## 覆盖边界

- 已验证：服务端五条角色/证据路径；页面角色门槛、文案与成功任务展示。
- 待用户走查：A6（329 历史对照：已完成、成片 74、无核对表单）、A6a/B5（331 显示人工核对表单，高级运营/管理员可提交）、A7（312 普通重试按钮）。
- 未覆盖：331 的真实核对提交结果取决于用户是否点击；若点击，任务应回到 `pending`，由 T-13/T-14 记录。
- 不回写：CHG-097 的“仅管理员”机器验收记录保留为当时事实。
