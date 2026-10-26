# T-06 Cloud Task 运行时证据

日期：2026-10-23
CHG：CHG-20261023-101

## 顺序说明

T-06 先于 T-05 实施。统一 Preflight 的“已 claim 任务走上报档”判据依赖
`tasks.user_id/attempt_id`，而这两列由迁移 070 引入；先做 T-05 会得到一个
查询不存在列的中间提交。T-05 在本证据之后实施，届时复用本任务的 claim 语义。

## 范围

- 迁移 `20261023_070_task_execution_recovery.sql`：`tasks` 新增 `user_id`、`attempt`、`attempt_id`、`started_at`、`last_report_at`、`finished_at`、`error_message`、`execution_timeout_seconds`、`external_side_effect`、`retryable`、`recovery_action`、`settled_by`；全局 `uq_idempotency_key` 改为 `uq_tasks_user_idempotency (user_id, idempotency_key)`；新增 `(user_id, status, created_at)` 与 `(status, last_report_at)` 索引。历史行回填归属与 `legacy:<task_id>` attempt，无法归属的非终态行以 `EXECUTION_INTERRUPTED` 收口。
- 任务类型元数据：`model.TaskTypeSpec` 按类型给出 `execution_timeout_seconds` 与 `external_side_effect`（`profile_open/close` 120s，其余 300s；`cookie_write/profile_create/profile_update/proxy_mutation` 有副作用）。未知或空类型返回 `UNSUPPORTED_TASK_TYPE`，不再降级 noop。
- 创建：`user_id` 必填；幂等键按用户作用域查询与插入；无幂等键写 NULL（唯一键不能把空串当成真实值）。
- 领取：事务内 `FOR UPDATE SKIP LOCKED`，用户范围 `user_id=token.sub`，`pending` 或租约过期的 `leased`；递增 `attempt`、生成新 `attempt_id`、写 `started_at/last_report_at`，清空上一 attempt 的终态/错误/结果。
- 上报：必须携带 `attempt_id`；用户或 attempt 不匹配分别 `ErrTaskNotFound`/`STALE_ATTEMPT`。`running` 只推进 `leased/running`；终态只接受 `leased/running`，或同一 attempt 在超时收口后的迟到收敛；重复终态幂等且不重复投影；`settled_by='agent'`。
- `POST /api/v1/cloud-agent/tasks/:task_id/activity`：只刷新 `last_report_at`，任务/用户/attempt 任一不匹配返回 `STALE_ATTEMPT`。
- Scheduler 单一 `task-recovery` job（默认 30s，批量 100）：只扫 `status='running'` 且 `last_report_at` 超过该行 `execution_timeout_seconds` 的任务；每条更新重判超时。无副作用 → `EXECUTION_INTERRUPTED/retryable=true/retry`；有副作用 → `RESULT_UNKNOWN/retryable=false/check_platform_state`；`settled_by='timeout'`，不自动重试。
- 重试同一行：只允许 `failed/cancelled`；`RESULT_UNKNOWN` 必须 `confirm_result_unknown=true`；回到 `pending` 并清空 attempt 标识与终态字段，`attempt` 在下次 claim 递增。
- 投影按用户范围：`media_accounts` 更新带 `user_id`；`browser_profiles` 更新同时要求 `user_id` 与当前 `users.bit_main_user_id`。
- 路由：`GET /api/v1/tasks/:task_id` 为 session 认证的本人任务读取；`claim/get/report/activity` 走 Agent Token，`cancel/retry` 走 session。

## 实施中发现并修复的两处缺陷

| 缺陷 | 暴露方式 | 修复 |
| --- | --- | --- |
| 无幂等键时插入 `''`；在 `(user_id, idempotency_key)` 唯一键下，同一用户第二个无键任务报 1062。旧实现用 `ON DUPLICATE KEY UPDATE task_id=task_id` 吞掉冲突并返回一个未写入的 task_id。 | 首次跑 live 用例即 1062 | 空键写 NULL |
| `projectResult` 把 `logged_in` 映射成 `active`，不在 `chk_media_accounts_login_status` 允许集合内；错误被上报路径丢弃，`account_check` 结果不会落库。 | 投影 live 用例断言 `normal` | 映射改为 `normal`，与媒体账号的登录状态枚举一致 |

## 行为测试

### 纯函数

```bash
go test ./internal/modules/cloudagent/model -count=1
```

`TestTaskTypeSpecsAndParsing`：10 种类型的 timeout/side-effect 与字符串往返；`""`、`unknown`、`discovery_task`、`cookie_read` 全部拒绝。`TestCloudAgentContractJSONTagsRemainStable`：`attempt/external_side_effect/retryable` 即使为默认值也出现在任务 JSON。

### live MySQL（迁移 070 后）

```bash
cd /Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud
WT_MEDIA_CLOUD_CONFIG_PATH=/tmp/wt-cloud-chg101-t06-cfg \
WT_MEDIA_TEST_TASK_RUNTIME=1 \
go test ./internal/modules/cloudagent/repository -run TestLiveTaskRuntime -count=1 -v
```

结果：4 个用例全部 PASS（0.695s）。

| 用例 | 证明 |
| --- | --- |
| `TestLiveTaskRuntimeLifecycleAndUserIsolation` | 同用户同幂等键返回同一任务；不同用户同键得到各自任务；A 读/上报 B 的任务均 `ErrTaskNotFound`；错误 attempt `STALE_ATTEMPT`；`pending→leased→running→succeeded`；重复终态幂等；已成功任务不可重试；无待领任务；未知/空类型与缺失用户分别失败；`profile_open` 120s/无副作用、`cookie_write` 300s/有副作用 |
| `TestLiveTaskRuntimeConcurrentClaimHasSingleWinner` | 两个 goroutine 同时领取同一条任务，恰好 1 个成功、1 个 `ErrNoPendingTask` |
| `TestLiveTaskRuntimeSilentTimeoutAndLateResult` | 静默超时两分支（`EXECUTION_INTERRUPTED` vs `RESULT_UNKNOWN`）；同一 attempt 迟到成功收敛；`RESULT_UNKNOWN` 重试需显式确认；重试后新 claim `attempt=2`、新 `attempt_id`；旧 attempt 上报与 activity 均 `STALE_ATTEMPT`；activity 刷新 `last_report_at`；取消后终态不被迟到上报覆盖 |
| `TestLiveTaskRuntimeProjectionStaysInUserAndMainScope` | A 的任务结果不能写 B 的 Profile、不能写 A 名下旧主账号 Profile；命中当前主账号时写入 `bit_status=updated`；A 不能写 B 的媒体账号，写入本人账号得到 `login_status=normal` |

### 变异对照

| 变异 | 期望 | 实际 |
| --- | --- | --- |
| `media_accounts` 投影去掉 `user_id` 条件 | 跨用户断言变红 | FAIL `user A projection wrote user B account: login_status = "normal"` |
| `lateConvergence` 置为永假 | 迟到收敛断言变红 | FAIL `late result did not converge`，任务保持 `failed/EXECUTION_INTERRUPTED` |
| claim 去掉用户条件（`(? = ? OR TRUE)`） | 用户隔离断言变红 | FAIL `claim task: task not found`：B 领到了 A 的行，随后按用户范围读取被拒 |

变异后已恢复实现并重跑，4 个用例重新全部 PASS。

## 全量测试与静态检查

```bash
go test ./...   # 日志 /tmp/chg101-t06-suite.log
go vet ./...    # exit 0
gofmt -l internal/modules/cloudagent internal/jobs internal/config internal/bootstrap
```

- `go test ./...`：exit 0；`ok` 70 包，`FAIL` 0 行，`no test files` 12 包。
- `go vet ./...`：exit 0。
- gofmt：本任务改动文件无输出。

## 迁移 070 实跑

### 空 scratch schema（001→071 全链）

数据库 `wt_media_cloud_chg101_t06`，配置 `/tmp/wt-cloud-chg101-t06-cfg`：

```text
migration ok: 73 total
schema_migrations = 73 行，MAX(version)=20261023_071_remove_agent_device_model
tasks 列数 = 25；三个新索引均存在；uq_idempotency_key 计数 = 0
```

### 先停在 069 的旧数据 fixture

数据库 `wt_media_cloud_chg101_t06_legacy`：先只应用 001→069，再插入 5 条旧形状任务：

- `legacy-acct`（pending，payload `account_id`）
- `legacy-profile`（running，payload `cloud_profile_id`）
- `legacy-other-profile`（pending，payload `profile_id`）
- `legacy-orphan`（leased，无可归属 payload）
- `legacy-done`（succeeded，无可归属 payload）

随后应用 070/071（`migration ok: 2 applied, 73 total`），读回：

| task_id | status | user_id | attempt | attempt_id | error_code | retryable | recovery_action | settled_by |
| --- | --- | ---: | ---: | --- | --- | ---: | --- | --- |
| legacy-acct | pending | 1 | 1 | legacy:legacy-acct | NULL | 0 | NULL | NULL |
| legacy-profile | running | 1 | 1 | legacy:legacy-profile | NULL | 0 | NULL | NULL |
| legacy-other-profile | pending | 1 | 1 | legacy:legacy-other-profile | NULL | 0 | NULL | NULL |
| legacy-orphan | failed | NULL | 1 | legacy:legacy-orphan | EXECUTION_INTERRUPTED | 1 | retry | legacy |
| legacy-done | succeeded | NULL | 1 | legacy:legacy-done | NULL | 0 | NULL | NULL |

三列 payload 均可反查归属；没有归属的非终态行只终结一次；已成功的历史行不被改写。`SHOW COLUMNS` 的 12 个新列类型/默认值符合预期（`execution_timeout_seconds=300`、两个布尔列默认 0），`tasks` 上 `device_id/desktop_id/node_id/handover_state/migration_state/execution_ticket/bit_main_user_id` 列计数为 0。

## 本次未覆盖

- Agent（Python）仍使用旧 claim/report 协议与节点凭证；断网 outbox、activity 定时器、重启补报在 T-07 实施并单独取证。
- 真实 Agent 进程与真实 Desktop 的超时/迟到场景在 T-07、T-10 验证；本任务只证明 Cloud 行级语义。
- `file_transfer_tasks`/`compose_tasks` 不并入本扫描，仍按各自 lease/reconcile 生命周期运行。
- 迁移 070 在真实开发库副本上的停服窗口演练属于 T-10；本任务使用空 scratch 与 069 fixture 两个库实跑。
