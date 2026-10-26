# T-07 Agent 运行时证据

日期：2026-10-23
CHG：CHG-20261023-101
仓库：`wt-media-agent`，分支 `chg/CHG-20261023-101`
Agent 提交：`e034910 feat(agent): adopt session-bound Agent Token and durable task outbox`

## 范围

- Agent Token：`runtime/agent_token.py` 只在进程内存保存 Token 与 `expires_at`；`__repr__` 不输出 Token，按设计不提供 clear。Runner 与 transfer loop 通过 `Credential = Callable[[], Optional[str]]` 每次调用读取，Desktop 重新登录后替换的是同一个对象的内容。
- 本机路由 `POST /api/v1/agent-token`：只接收 `{token, expires_at}`；空 Token → 400 `agent_token_required`；未装配存储 → 503 `agent_token_unavailable`；状态读取只返回 `has_agent_token` 与 `expires_at`，不回显 Token。
- Cloud 客户端：claim/report/activity 与 transfer 的 claim/heartbeat/progress/complete 全部使用 Bearer Token；report 必须携带 `attempt_id`；活动上报成功时 Cloud 返回 `data: null`。
- Runner：无 Token 不 claim；claim 被严格档拒绝（`AUTH_*`）时暂停 claim，但仍先补报 outbox；每个运行中任务一个 activity 线程，间隔取 `max(5, min(30, timeout/3))` 秒；`start()` 只执行一次 `_recover()`，丢弃无 `attempt_id` 的旧 checkpoint，有外部副作用且未终结的行上报 `RESULT_UNKNOWN`，无副作用的行用同一 `attempt_id` 重跑。
- SQLite `0004_task_recovery_outbox`：checkpoint 新增 13 列、outbox 新增 7 列，`TaskCheckpoint`/`OfflineResult` 同步；终态与 outbox 行在同一事务写入，提交后才调用 Cloud。
- `account_check`：按真实检测结果上报 `login_status`；Cloud 的 `projectResult` 只把 `logged_in` 投影为 `normal`，`not_logged_in` 投影为 `expired`，其余为 `environment_error`。
- 退场：`runtime/node_credential.py`、`services/profile_guard.py`、`cloud_agent_client.py`、`cloud_agent_contract.py` 及对应测试；`contracts/local-error-codes/v1/transfer.yaml` revision 升到 `2026.10.23.1`，`secret_policy.forbidden_fields` 为 `[source_address, storage_credential, agent_token]`。

## 顺序保证

1. `DurableTaskReporter.finish` 调用 `CheckpointStore.finish_task`，后者在一个事务里写 checkpoint 终态（`report_pending=1`）和完整 outbox 行。
2. `finish_task` 返回、事务提交后，`OutboxDelivery.flush` 才调用 Cloud。
3. 投递成功 → `mark_delivered` 并删除 checkpoint；`STALE_ATTEMPT` → `drop_result`；其它失败 → `record_delivery_failure`，行保留待下轮。
4. `TaskRunner._poll_once` 的顺序固定为：flush → 处理恢复行 → 若仍有未投递结果则不 claim → claim → 执行。

## 实施中发现并修复的缺陷

| 缺陷 | 暴露方式 | 修复 |
| --- | --- | --- |
| 终态被重复上报：reporter 用 checkpoint 是否存在判断“是否已终结”，而投递成功后 checkpoint 会被删除，Runner 在 executor 正常返回后又发了一次 `succeeded`。 | `test_new_task_type` 收到两条终态上报。 | `DurableTaskReporter.finished` 在写盘后置位，Runner 改用这个标志判断，不再依赖 checkpoint 的生命周期。 |

## 行为测试

```bash
PYTHONPATH=src python3 -B -X pycache_prefix=/tmp/wt-pycache-empty -m unittest tests.<module>
```

| 模块 | 用例数 | 证明 |
| --- | ---: | --- |
| `test_runner_outbox` | 9 | 上报时结果已在 SQLite（`undelivered_at_report == [True]`）；投递成功不重复上报；重启先补报再 claim；claim 被拒不影响补报；被取代的 attempt 丢弃结果；无副作用任务同一 attempt 重跑；有副作用任务报 `RESULT_UNKNOWN`；无 attempt 的旧行被丢弃；运行中刷新 activity |
| `test_runner_error_fields` | 4 | executor 异常 → 本地终态 `executor_error/retryable`；`STALE_ATTEMPT` → 清理 checkpoint；缺 executor 只记 warning；claim 被拒记录 `AUTH_DESKTOP_REPLACED` 且不产生 task_id |
| `test_local_api_server` | 24 | Agent Token 路由回读、400/503、Token 不出现在响应；transfer 错误码前缀与声明一致 |
| `test_account_check_executor` | 8 | 登录态读取、`logged_in`/`not_logged_in` 上报、无 Cookie 分支 |
| `test_cookie_executor` | 7 | Cookie 读写执行器在新 report 签名下工作 |
| `test_new_task_type` | 4 | 工厂注入 `DurableTaskReporter`，任务执行只产生一条终态 |
| `test_bootstrap` | 15 | Agent Token 接入 executor 与 transfer runner；本地 API 与下载共享同一个 Token 对象 |
| `test_storage_migration` | 2 | 0001–0004 全量迁移；0004 两表新增列与默认值 |
| `test_transfer_resume` | 11 | 0004 从 0003 形态数据库升级，旧行保留 |
| `test_dependency_boundaries` | 33 | 分层边集与 storage 符号冻结 |
| `test_no_external_services` | 11 | 测试不连真实外部服务、标记数冻结 |
| `test_contract_docs` | 8 | `transfer.yaml` revision 与 README 一致 |

## 变异对照

| 变异 | 期望 | 实际 |
| --- | --- | --- |
| 删除 `DurableTaskReporter.finish` 里的 `store.finish_task(...)`，只保留 `finished` 标志 | “先落盘再上报”用例变红 | FAIL `AssertionError: Lists differ: [] != [True]`；恢复后 `cmp` 与备份一致，模块 9 个用例重新 OK |

## 迁移实测

```bash
PYTHONPATH=src python3 -B -X pycache_prefix=/tmp/wt-pycache-empty -m unittest tests.test_storage_migration
```

- 全新建库：`storage migration ok: 4 applied, 4 total`，版本为 `0001_base`、`0002_task_checkpoints`、`0003_transfer_resume`、`0004_task_recovery_outbox`。
- checkpoint 读回：13 个新列全部存在，默认值 `report_pending=("INTEGER","0")`、`execution_timeout_seconds=("INTEGER","300")`、`external_side_effect=("INTEGER","0")`。
- outbox 读回：7 个新列全部存在。
- 从 0003 形态数据库升级：只应用 `0004_task_recovery_outbox`；预置行读回 `('old-1', 40, 'half', None, 0, 300)`，未被改写。

## 全量读数

```bash
./scripts/test.sh
```

- 最后一次改动后：`Ran 710 tests` → `OK`；迁移脚本同时输出 `storage migration ok: 4 applied, 4 total`。
- 同一实现另外连续运行 9 次（3 次前台 + 6 次后台循环）均为 `OK`。
- 期间有 1 次全量运行出现单条 `FAILED`，失败用例名未保留；此后连续 9 次未复现。作为已知不稳定项带入 T-10 观察，若真实环境回归中再次出现再定位。

## 未覆盖项

- 真实 Agent 领取任务、真实 BitBrowser 登录态检测与断网 outbox 补报留到 T-10 的真实环境回归；本任务只用替身传输与真实 SQLite。
- Desktop 侧换取并递交 Agent Token 尚未实现（T-08），因此“登录/续期/app 重启时重取”只有 Agent 单侧的存储与读取测试。
- `file_transfer_tasks` 的真实 lease 续租与 takeover 仍由既有机制覆盖，本任务只改认证参数与 `attempt_id`。
