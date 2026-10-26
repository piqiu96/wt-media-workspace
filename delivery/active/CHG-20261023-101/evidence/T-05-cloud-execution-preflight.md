# T-05 Cloud 统一 Execution Preflight 证据

日期：2026-10-23
CHG：CHG-20261023-101

## 范围

- 新增 `internal/modules/executionpreflight`：唯一的准入 evaluator、Cloud 事实读取、HTTP 入口。
- `POST /api/v1/local-agent/execution-preflight`（Agent Token）：带 `attempt_id` 的请求按已领取任务处理，否则按新操作处理并自行做严格会话校验。
- 敏感任务 preflight 改为复用同一 evaluator；`sensitive_profile_permits` 只保留 Profile 互斥，不再重复环境/账号检查，也不再发放独立凭证。
- BitBrowser 观察新鲜窗口由 bootstrap 从 `App.BitBrowser.ObservationFreshFor` 同时装到 profilebinding 与 executionpreflight。

## 判定模型

`Evaluate(Request)` 是无 IO 的纯函数，按固定顺序返回第一个失败：

| # | 检查 | 事实来源 | 失败码 |
| --- | --- | --- | --- |
| 1 | 用户 enabled（仅新操作） | `users.status` | `AUTH_SESSION_INVALIDATED` |
| 2/3 | Desktop 会话仍是当前会话（仅新操作） | `token.sid` 对应的 session | `AUTH_DESKTOP_REPLACED` / `DESKTOP_LOGIN_REQUIRED` / `AUTH_SESSION_INVALID*` |
| 4 | 已绑定 BitBrowser 主账号 | `users.bit_main_user_id` | `BIT_NOT_BOUND` |
| 5 | BitBrowser 正在运行且观察新鲜 | Agent 实时事实 + `observed_at` | `BIT_BROWSER_OFFLINE` |
| 6 | 实际主账号 == 绑定主账号 | Agent `main_user_id` | `BIT_MAIN_USER_MISMATCH` |
| 7 | Profile 属于当前用户 | `browser_profiles.user_id` | `PROFILE_ASSIGNED_TO_OTHER_USER` / `PROFILE_NOT_FOUND` |
| 8 | Profile 属于当前主账号 | `browser_profiles.main_user_id` | `PROFILE_NOT_FOUND` |
| 9 | 本地 Profile 存在且可见 | `local_status='active'` + Agent `profile_visible` | `PROFILE_NOT_FOUND` |
| 10 | 动作要求的平台登录态 | `media_accounts.login_status` | `PROFILE_LOGIN_INVALID` |
| 11 | 动作要求的本地文件 | Agent `files_ready` | `FILE_PREPARE_FAILED` |

- 动作决定检查子集：`account_check`/`cookie_read` 不要求平台登录与文件；`profile_create`/`proxy_check` 不要求 Profile；发布与互动要求 Profile + 平台登录 + 文件。
- 未知动作失败关闭（`UNSUPPORTED_TASK_TYPE`），不降级为不需要任何检查的动作。
- 已领取任务跳过 1/2/3：claim 时的严格档已是准入证据，抢占不能中断已在执行的任务；用户与 attempt 由 handler 校验。
- 失败 envelope 统一为 `{code, message, retryable, recovery_action}`，HTTP 状态与 errcode 见 `failureStatus`（复用现有数值，不新增数字表）。

## 行为测试

### evaluator

```bash
cd /Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud
go test ./internal/modules/executionpreflight -count=1
```

| 用例 | 证明 |
| --- | --- |
| `TestEvaluateAdmitsAHealthyInteraction` | 基线满足全部检查 |
| `TestEvaluateFailsClosedOnEveryCheck` | 16 个单点变异各自只触发预期失败码：用户停用、Desktop 被替换、未绑定、BitBrowser 停止/观察过期/观察缺失、主账号不一致、他人 Profile、Profile 缺失/旧主账号/本地缺失/不可见、平台登录过期/账号缺失、文件未就绪、未知动作 |
| `TestEvaluateClaimedTaskSkipsTheCurrentSessionChecks` | 已领取任务在用户停用、会话失效时仍通过 |
| `TestEvaluateActionsOnlyRequireWhatTheyUse` | `account_check` 不要求平台登录/文件；`profile_create` 不要求 Profile |
| `TestObservationFreshBoundary` | 恰好 120s 仍新鲜，超 1ns 即过期 |
| `TestActionForSensitiveOperationCoversEveryOperation` | 7 个敏感操作全部映射；未知操作拒绝 |
| `TestFailureStatusMapsEveryCodeToItsEnvelope` | 14 个错误码的 HTTP/errcode 映射；未知码落到 500/50000 |

### handler 与事实读取

| 用例 | 证明 |
| --- | --- |
| `TestExecutionPreflightRequiresAnAgentToken` | 无凭证 401 `AUTH_AGENT_TOKEN_INVALID`，用户 session 不能代用 |
| `TestNewOperationStopsBeforeFactsWhenTheDesktopSessionWasReplaced` | 被替换的 Desktop 得到 `AUTH_DESKTOP_REPLACED`，且不读取任何业务事实 |
| `TestNewOperationAdmitsAHealthyInteraction` | 严格档通过；handler 把 `DesktopSessionValid=true` 重新并入事实 |
| `TestClaimedTaskSkipsTheDesktopSessionGate` | 已领取任务完全不调用会话检查 |
| `TestClaimedTaskIsStaleWhenTheAttemptOrTaskMovedOn` | 新 attempt、已终态、他人任务三种情况均 409 `STALE_ATTEMPT`，且不读事实 |
| `TestEvaluatorFailureKeepsItsRecoveryInTheEnvelope` | 422 `FILE_PREPARE_FAILED` 带 `retryable=true`、`recovery_action=retry_prepare` |
| `TestFactsLoadFailureIsAnInternalError` / `TestExecutionPreflightRejectsAnEmptyBody` | 数据库失败 500；空 body 400 |
| `TestLoadCloudFactsScopesProfileAndAccountToTheUser` | 他人 Profile 标记 `AssignedToOtherUser`；本人媒体账号返回登录态 |
| `TestLoadCloudFactsTreatsAMissingUserAsNotEnabled` | 用户行缺失即未启用，不再查 Profile |
| `TestLoadCloudFactsSkipsTheQueriesTheActionDoesNotNeed` | 未给 Profile/账号 id 时不发多余查询 |
| `TestLoadCloudFactsReportsOtherUsersMediaAccountAsAbsent` | 他人媒体账号等同于不存在 |

### 变异对照（17 项，全部变红）

每项只关闭一个检查或反转一个分支，然后运行对应用例：

| 变异 | 结果 |
| --- | --- |
| 未知动作不再失败关闭 | FAIL `unknown_action` |
| 忽略用户停用 | FAIL `user_disabled` |
| 忽略 Desktop 会话 | FAIL `desktop_session_replaced` |
| 忽略未绑定 | FAIL `bit_account_unbound` |
| 忽略 BitBrowser 运行/新鲜度 | FAIL `bitbrowser_stopped`/`observation_stale`/`observation_missing` |
| 新鲜窗口边界 `<=` 改 `<` | FAIL `TestObservationFreshBoundary` |
| 忽略主账号不一致 | FAIL `observed_main_differs` |
| 去掉他人 Profile 分支 | FAIL `profile_belongs_to_another_user`（落到 `PROFILE_NOT_FOUND`） |
| 忽略平台登录态 | FAIL `platform_login_expired`/`media_account_missing` |
| 忽略本地文件 | FAIL `files_not_ready` |
| 已领取任务也要求当前会话 | FAIL `TestEvaluateClaimedTaskSkipsTheCurrentSessionChecks` |
| handler 不走 attempt 分支 | FAIL `TestClaimedTaskIsStaleWhenTheAttemptOrTaskMovedOn` |
| 会话失败不拦截 | FAIL `TestNewOperationStopsBeforeFactsWhenTheDesktopSessionWasReplaced` |
| 不重新并入 `DesktopSessionValid` | FAIL `TestNewOperationAdmitsAHealthyInteraction` |
| Profile 归属不按用户 | FAIL `TestLoadCloudFactsScopesProfileAndAccountToTheUser` |
| 媒体账号归属不按用户 | FAIL `TestLoadCloudFactsReportsOtherUsersMediaAccountAsAbsent` |

变异后已从备份恢复，`gofmt -l` 无输出，全部用例重新通过。

## 敏感 permit 收敛

- `profileguard.Service.Preflight` 先映射敏感操作到统一动作、读取 Cloud 事实、按 `ModeNewOperation` 评估；失败以 `*executionpreflight.Failure` 透传，不取许可。
- `acquirePermit` 只做三件事：锁 `browser_profiles` 行、检查上一个许可、插入许可并把任务从 `authorized` 推到 `running`。原来的环境/账号 `COUNT(*)` 校验已删除，避免两处判据各说各话。
- `TestPreflightStopsAtTheUnifiedChecksWithoutTakingAPermit`：过期观察得到 `BIT_BROWSER_OFFLINE`，且没有许可落库。
- `TestAcquirePermitIsOnlyTheProfileMutex`：SQL 断言整段固定，只出现行锁、前一许可查询、插入与状态推进。

## 静态检查与全量测试

```bash
go build ./...      # exit 0
go vet ./...        # exit 0
go test ./...       # 日志 /tmp/cloud_full_test.txt
gofmt -l internal/modules/executionpreflight internal/modules/localagent internal/modules/profileguard internal/bootstrap
```

- `go test ./...`：exit 0；`ok` 71 包，`FAIL` 0 行，`no test files` 12 包。
- `go vet ./...`：exit 0。
- gofmt：本任务改动文件无输出。

## 未覆盖与后续接线

- Cloud 事实读取用 sqlmock 验证 SQL 形状与归属分支；三条 `SELECT` 都是单表主键查询，本任务没有新增 live MySQL 用例。
- Agent 尚未调用 `execution-preflight`；T-07 接入 Runner 后，“普通任务不能绕过 preflight”才有运行期读数。当前入口在 Cloud 侧已强制，任何新动作都只能经该 evaluator。
- 发布/互动仍为 ComingSoon，其平台登录与文件检查只有合成用例，没有真实发布任务。
