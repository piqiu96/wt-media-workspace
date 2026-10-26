# CHG-20261023-101 最终交付报告

日期：2026-10-23
状态：实现及用户 GUI 验收完成，待四仓合并；CHG 保持 `IMPLEMENTING`
证据：`delivery/active/CHG-20261023-101/evidence/T-02..T-14`

## 1. 变更摘要

### wt-media-cloud

| 提交 | 内容 |
| --- | --- |
| `0907c40` | `user_sessions` 成为唯一认证事实源：Web 多会话、Desktop 单有效会话、冲突/替换、批量失效、带 `code` 的认证错误 |
| `b95d18a` | 签发会话绑定 Agent Token（HMAC、无服务端状态、严格/上报两档）；删除设备/节点/绑定票据/presence/`agent_nodes` 与 `runtimebinding` |
| `e50906b` | BitBrowser 首次绑定只接受 Agent 实读的 `main_user_id`；Profile 按 `user_id + main_user_id` 双作用域；扫描缺失只标记不删除 |
| `411319f` | Task 收敛到 `user_id + attempt_id + last_report_at`：用户范围 claim、attempt 递增、迟到/幂等、同行走重试、`task-recovery` 超时扫描、按副作用决定错误码 |
| `50f2757` | 统一 Execution Preflight：11 项检查、严格/已 claim 两档、permit 只保留互斥、所有入口复用同一 evaluator |
| `9e32a4a` | Web 只读遮蔽后的 Bit 主账号（首 4 + `****` + 末 4） |
| `b3e224e` | Web/Desktop 共用前端：冲突/替换文案、错误码映射、去设备化、下载与任务状态文案 |
| `3f3b054` | Cloud/Agent/业务 Contract 与错误码推进到 `2026.10.23.1` |
| `cc2aacc` | 070 迁移对非数字历史 payload id 加 `REGEXP + CAST` 守卫（T-10 发现） |
| `98c08dd` | 文件传输业务 schema 删除内部审计标签 `claimed_by`（T-10 发现） |
| `146f267` | `session-cleanup` 作业按保留期清理过期会话；072 为 `expires_at` 加索引（T-11） |

### wt-media-agent

| 提交 | 内容 |
| --- | --- |
| `e034910` | Agent Token 只存内存、每次调用读取；claim/report/activity 全部 Bearer + `attempt_id`；SQLite `0004_task_recovery_outbox`；终态先落盘、启动先补报、无 Token 不 claim、activity 线程统一保活 |
| `c98e6d8` | 本机 API 只上报本机实读的 BitBrowser 事实，不接受调用方传入的 main/事实 |
| `6b67b50` | 本机 Contract、错误码与版本 `0.3.0` 对齐 |
| `d5097f5` | 两个测试夹具竞态修复（契约路由读取、SIGTERM 在飞请求） |
| `8749193` | 非 Cloud 信封的网关应答归为传输失败，进度上报不再把任务打成 `executor_error`（T-10 发现） |

### wt-media-desktop

| 提交 | 内容 |
| --- | --- |
| `3de1a94` | Desktop 用 desktop session 换取并递交 Agent Token；删除设备身份、RuntimeBinding、节点注册与本地重复 Preflight；登录冲突/被替换 UI；下载去设备化 |
| `79e9086` | `contracts.lock.json` 顶层改为 `desktop-single-login-20261023.1`，Agent 兼容版本 `0.3.0` |

### wt-media-workspace

- 新建 CHG-20261023-101 与证据；ADR-0022；M2-F 锚点；Product/Architecture/Communication Spec/Contract map 按新事实回写；T-10 全量验证证据与本报告。

## 2. 数据库变更

本轮不新增业务表。

### Cloud 068–072

| 迁移 | 变更 | 读回 |
| --- | --- | --- |
| `068_identity_session_state` | `user_sessions` 增加 `expires_at DATETIME(6) NOT NULL`、`invalidated_reason VARCHAR(32)`；索引 `(user_id, client_type, invalidated_at, expires_at)`；回填 `created_at + 30d`；多有效 Desktop 行保留最新、其余 `superseded` | 迁移后 `active_desktop_dup=0`；有效行 `expiry_days=30` |
| `069_browser_profile_scope` | 删除全局 `UNIQUE(bit_profile_id)` 与 `UNIQUE(user_id, bit_profile_id)`；新增 `UNIQUE(user_id, main_user_id, bit_profile_id)`、索引 `(user_id, main_user_id)` | 两个索引读回一致；迁移前三列重复 0 |
| `070_task_execution_recovery` | `tasks` 增加 `user_id/attempt/attempt_id/started_at/last_report_at/finished_at/error_message/execution_timeout_seconds/external_side_effect/retryable/recovery_action/settled_by`；删除全局 `uq_idempotency_key`，改为 `UNIQUE(user_id, idempotency_key)`；新增 `(user_id,status,created_at)`、`(status,last_report_at)` | 13 列与 3 个索引读回；`attempt=1`、`attempt_id=legacy:<task_id>`、`last_report_at` 回填、`execution_timeout_seconds=300` |
| `071_remove_agent_device_model` | 删除 `users.device_*`；删除 `local_agent_nodes`、`local_agent_binding_tickets`、`browser_profile_runtime_presence`、`agent_nodes`；删除 `sensitive_browser_tasks.node_id`、`sensitive_profile_permits.node_id` 与 permit `credential_hash`；`file_transfer_tasks` 删除 `assigned_node_id/assigned_device_id`，`claimed_by_node_id` 改名 `claimed_by`，新增 `attempt_id` | `remaining_dropped_tables=0`、`users_device_columns=0`、`sensitive_node_columns=0`；传输表列读回无 node/device |
| `072_user_sessions_expires_at_index` | 新增 `idx_user_sessions_expires_at (expires_at)`，供过期会话清理按过期时间扫描 | `Non_unique=1`、`Seq_in_index=1`、`Column_name=expires_at` |

历史数据处置：

- 能从 `payload_json.account_id/cloud_profile_id/profile_id` 关联到归属的任务回填 `user_id`；关联不到的 3 行非终态任务以 `failed`、`EXECUTION_INTERRUPTED`、`retryable=1`、`recovery_action=retry`、`settled_by=legacy` 终结，不伪造用户。
- 历史 payload 的非数字 id 跳过（`REGEXP '^[0-9]+$'` + `CAST`），避免 MySQL 1292 中止整个迁移。
- 切换 Bit 主账号不删除、不迁移旧 Profile：同一 `bit_profile_id` 在新 main 下插入新行，切回旧 main 自然恢复可见。

### Agent `0004_task_recovery_outbox`

- `task_checkpoints` 新增 13 列：`attempt_id/task_payload_json/last_stage/checkpoint_json/final_status/final_result_json/error_message/report_pending/last_report_at/started_at/finished_at/execution_timeout_seconds/external_side_effect`。
- `offline_results` 新增 7 列：`attempt_id/result_json/error_message/retryable/recovery_action/delivery_attempts/delivered_at`。
- 终态 checkpoint、`report_pending=1` 与完整 outbox 行在同一 SQLite 事务写入，提交后才调用 Cloud。
- 迁移在全新库与 0003 形态库上各跑一次：`storage migration ok: 4 applied, 4 total`，旧行保留。

## 3. API / Contract 变更

### 新增

- `POST /api/v1/auth/login` 的 Desktop 冲突/确认语义：`replace_existing=true` + `replace_session_id`；冲突 409 `errcode=20010`，`error.details.active_session_id`。
- `POST /api/v1/users/:user_id/force-logout`：批量失效 + 审计。
- `POST /api/v1/local-agent/agent-token`（session 认证）：返回 `{token, expires_at}`；Agent Token 为 `v1.<payload>.<sig>`，claims `{ver,sub,sid,scope,iat,exp,jti}`，`exp == session.expires_at`。
- `POST /api/v1/local-agent/bit-account/bind`（严格档）：`{main_user_id, observed_at, rebind}`，无 node/credential。
- `POST /api/v1/local-agent/execution-preflight`：统一 11 项检查；已 claim 任务带 `attempt_id` 走上报档。
- `POST /api/v1/cloud-agent/tasks/:task_id/activity`（上报档）：只刷新 `last_report_at`。
- `GET /api/v1/tasks/:task_id`（session）：本人任务，供 UI。
- Agent 本机 `POST /api/v1/agent-token`：只接收 `{token, expires_at}`，状态只回 `has_agent_token`/`expires_at`。

### 修改

- claim/report/get：Bearer Agent Token；claim 用户范围 + 事务 + `attempt_id`；report 必须带 `attempt_id`，终态/迟到/幂等规则；`agent_id` 不再作为身份。
- 文件传输 claim/heartbeat/progress/complete：严格/上报档 + `attempt_id`，去 node/device；`dedupe_key` 用 `v2:` 用户范围。
- BitBrowser 扫描提交/确认：必须携带 `main_user_id/observed_at`，扫描不再承担绑定。
- Profile/媒体账号查询/更新/删除/分配：`user_id + main_user_id` 双作用域。

### 删除

- `/api/v1/cloud-agent/agents/register|heartbeat`、`/api/v1/local-agent/nodes/register|runtime-report|current-login|device-binding`、`POST /api/v1/tasks/noop`、`/api/v1/bit-browser/main-identity|confirm-main-identity`。
- `runtime-binding.openapi.yaml`、`registration-heartbeat.openapi.yaml`。

### 错误码

| code | HTTP | retryable | recovery_action |
| --- | ---: | --- | --- |
| `DESKTOP_LOGIN_CONFLICT` | 409（20010） | false | `confirm_desktop_takeover` |
| `AUTH_DESKTOP_REPLACED` | 401（11001） | false | `login_again` |
| `AUTH_SESSION_INVALID/INVALIDATED/EXPIRED` | 401（11001） | false | `login_again` |
| `DESKTOP_LOGIN_REQUIRED` | 401（11001） | false | `login_desktop` |
| `AUTH_AGENT_TOKEN_INVALID/EXPIRED` | 401（11001） | false | `reissue_agent_token` |
| `AGENT_SCOPE_FORBIDDEN` | 403（11003） | false | `none` |
| `BIT_NOT_BOUND` | 409（23008） | false | `bind_bitbrowser` |
| `BIT_BROWSER_OFFLINE` | 409（23009） | true | `start_bitbrowser` |
| `BIT_MAIN_USER_MISMATCH` | 409（23002） | false | `rebind_bitbrowser` |
| `PROFILE_NOT_FOUND` | 404（20004） | false | `choose_profile` |
| `PROFILE_ASSIGNED_TO_OTHER_USER` | 403 | false | `choose_own_profile` |
| `PROFILE_LOGIN_INVALID` | 409（23010） | false | `login_platform` |
| `FILE_PREPARE_FAILED` | 422（23011） | true | `retry_prepare` |
| `STALE_ATTEMPT` | 409（30009） | false | `none` |
| `UNSUPPORTED_TASK_TYPE` | 400（10002） | false | `none` |
| `EXECUTION_INTERRUPTED` | task 结果 | true | `retry` |
| `RESULT_UNKNOWN` | task 结果（30010） | false | `check_platform_state` |

### Revision 与兼容

- Cloud/Agent Contract、业务 schema/enum、错误码统一为 `2026.10.23.1`；Desktop `contract_revision` 为 `desktop-single-login-20261023.1`，消费 `cloud_agent_api/task_schemas/local_agent_api v1@2026.10.23.1`。
- Agent 版本 `0.3.0`；Desktop `agent-compat.json` 固定该版本，Cloud 最低 Agent revision 为 `2026.10.23.1`。旧 Agent/Desktop 在新 Cloud 上失败关闭，不保留无认证或设备路径的兼容旁路。
- Agent Token 无服务端状态，不能单独吊销；需要立即吊销时轮换签名密钥。旧 Token 在 `exp` 前仍可走上报档收敛已领取任务，严格档立即失败。

## 4. 删除 / 退役的旧逻辑

- **设备绑定**：`users.device_*`、Ed25519 设备证明、`device_id` 去重、`device_unbound`、Desktop `device_identity.rs`/`local_device_identity`/`bind_device`。
- **节点与在线态**：`local_agent_nodes`、`local_agent_binding_tickets`、`browser_profile_runtime_presence`、`agent_nodes`、`runtimebinding` 模块、节点注册/runtime-report/current-login、节点凭证与 permit credential。
- **旧登录**：“存在同用户名 session 就不校验密码直接成功”的早退；按 `client_type` 无差别替换；Web 二次登录要求替换。
- **手工 Bit 绑定**：`ConfirmMainIdentityDirect`、`mark-identity`/`confirm-main-identity`、前端手工 `mainUserId`、`ConfirmScan` 的自动绑定分支。
- **无认证任务入口**：公开 `/tasks/noop`、未认证 claim/report、body `agent_id` 作为身份、`agent_nodes` registry。
- **旧结果通道**：executor 自己直接上报终态、成功后立即删 checkpoint、只启动时 flush 一次的 offline 队列；改为 Runner/DurableReporter 统一落盘与补报。
- **Web/Desktop 设备入口**：PersonalInfoPage 设备区、下载中心按本机设备 id 判悬置、工作环境状态按设备/节点匹配、LoginPage 的旧 20010 文案。

## 5. 新增测试与结果

### 四仓全量

| 仓 | 结果 |
| --- | --- |
| Cloud | Go 71 包 `ok`；Web 77 文件 / 710 用例通过；control 12/12 |
| Agent | `Ran 727 tests` → `OK`；SQLite 0001–0004 全量迁移通过 |
| Desktop | 536 passed / 0 failed / 6 ignored；control 12/12；release-versions 20/20 |
| Workspace | `docs/check.py`、delivery governance、product/master alignment、m0 config、skills、m2 acceptance 全部退出 0 |

### 真实环境回归（64/64）

覆盖真实 Cloud、真实 BitBrowser、真实 Agent 进程与打包 Desktop：两个 Web 会话并存；Desktop 冲突/取消零写入/错误 replace id/确认替换；旧 Desktop `AUTH_DESKTOP_REPLACED`；旧 Token 严格档失败、上报档收敛；Token `exp == session.expires_at`；Agent Token 与 session token 互不通用；同行走重试与 `STALE_ATTEMPT`；真实 BitBrowser 首绑/同主验证/临时不一致/正式重绑/切回/40 Profile 扫描；Preflight 绿路径与 403/404/409/409/400 失败码；真实 Agent 执行 `noop_task` 并落 outbox；日志密钥扫描 6 个 token 全 0 命中、阳性对照命中 694/492820。

### 断网与重启补报（17/17）

代理把 `/report` 答成 502：终态先写 SQLite、Cloud 保持 `leased`；恢复并重启 Agent 后先补报，Cloud `succeeded`，同一 attempt，不重跑。

首次运行暴露并修复了一个真实缺陷：非 Cloud 信封的网关 502 被 `_expect_data` 抛成 `ValueError`，绕过进度上报的异常捕获，把任务记成 `failed/executor_error`。修复后新增客户端与 Runner 回归用例各一。

### 迁移

068–071 在 scratch schema、开发库副本、开发库、fixture 二次实跑四种起点执行，读回列、索引、约束、回填与终结行；070 的 1292 守卫由开发库副本真实触发后修复。

### 过期会话清理（T-11）

`session-cleanup` 在 `discovery-scheduler` 进程注册，默认每 1h 删除过期超过 7 天的会话。开发库实跑：675 → 406 行（删除 269），保留带 55 行（最近 7 天内过期），有效会话 12 行（Desktop 1 / Web 11）不变；第二次运行删除 0 行。迁移 072 实跑并读回索引。细节见 `evidence/T-11-session-cleanup.md`。

### 真实超时扫描

`t10-real-timeout-noside` → `EXECUTION_INTERRUPTED / retryable=1 / retry`；`t10-real-timeout-side` → `RESULT_UNKNOWN / retryable=0 / check_platform_state`；均由 `settled_by=timeout` 收口。

### 未覆盖

- 第二台物理 Desktop；真实发布/互动任务（产品仍为 ComingSoon）；真实下载双机交接；常驻 `discovery-scheduler` 的 tick（开发环境不启动，扫描用同一 job 的一次性程序验证）；`outbox_test.py` 临时换发的 Token 未纳入日志字符串扫描（只用完即弃，未落盘）。GUI 逐屏视觉未由自动化执行，后续由用户确认验收。

## 6. 文档回写清单

| 文档 | 回写内容 |
| --- | --- |
| `docs/decisions/0022-session-only-auth-and-agent-token.md` | 新 ADR：session-only、Desktop 单有效会话、设备/节点退场、会话绑定 Agent Token、Task attempt/超时、SQLite outbox |
| `docs/decisions/0003-*`、`0018-*`、`0019-*` | 加 `Superseded by ADR-0022` / 部分取代注记，不改历史正文 |
| `docs/decisions/README.md` | 索引加入 0022 与取代关系 |
| `delivery/milestones/M2-account-runtime.md` | M2-F 改为 session-only + Agent Token + BitBrowser 双作用域 + 统一 Preflight + Task 恢复闭环，提供 CHG-101 锚点 |
| `docs/product/prd/详细文档/第三章_用户与账号管理.md` | Web 多端、Desktop 冲突/替换、批量失效、BitBrowser 绑定/重绑、双作用域与验收语义 |
| `docs/product/prd/详细文档/第二章_系统架构.md`、`第五章_素材生产.md` | 删除设备/节点/单会话旧事实，改为当前认证与下载事实 |
| `docs/product/prd/社媒运营平台_产品需求说明书_V1.md` | 登录与运营电脑相关表述对齐 |
| `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` | 会话失效、并发、Task、Scheduler、SQLite、禁止项；Agent Token 两档 |
| `docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md` | 本地操作准入、混合任务时序、认证、禁止项 |
| `config/contract-map.yaml`、`docs/contracts/contract-map.md` | revision、路径、认证、错误码、已验证版本组合 |
| `delivery/LEDGER.md`、`delivery/active/CHG-20261023-101/change.md` | CHG 状态、任务、Done When、证据入口 |
| `scripts/verify/verify_m2_acceptance.py` | 按新 M2-F 事实更新静态矩阵 |

历史归档与已完成记录未改写；旧事实扫描只命中历史叙述/任务夹具，当前文档与 Contract 无残留。

## 7. 剩余风险 / 未实现

- **Agent Token 无吊销**：无服务端 Token 状态；停用/改密/替换只让严格档立即失败，上报档保留到原 session `exp`。需要立即吊销全部 Token 只能轮换签名密钥；密钥必须显式配置，轮换会使全部 Token 失效。
- **信任边界**：BitBrowser/文件/可见性事实完全来自 Agent 的准入请求，服务端无法独立复核；排障依赖日志与 Agent 本地状态。
- **过期 session 清理**：已由 T-11 的 `session-cleanup` 作业实现（过期后保留 7 天）；常驻调度器 tick 与生产 I/O 影响未在开发环境验证。
- **破坏性迁移**：线上处于体验期，2026-10-23 用户裁定不做新旧版本兼容，071 等删除/修改直接执行；生产发布仍需备份，Cloud/Agent/Desktop 同版本部署。
- **历史任务**：无法归属的历史行已终结为 `EXECUTION_INTERRUPTED`，不会恢复执行。
- **发布/互动**：产品仍为 ComingSoon，Preflight 的登录态/文件检查没有真实发布任务读数。
- **文件传输/合成任务**：保留各自 lease/reconcile 生命周期，只改认证、attempt 与设备/节点字段；其“运行中结果不回来”的收敛仍由既有机制负责。
- **Agent 重启续跑**：只对声明可恢复的 executor 使用 checkpoint；无副作用任务从头重跑，有副作用任务报 `RESULT_UNKNOWN`。
- **同机多 Cloud 用户**：一个 sidecar 同时只持有一个 Agent Token；切换 Cloud 用户时旧用户在途任务可能只能靠 Cloud 超时收敛。
- **本地 API 既有边界**：CORS `*`、runtime token 为空时禁用认证是既有行为；2026-10-23 用户裁定不加固，继续只作为本机接口使用。
- **GUI 验收**：打包 Desktop 已构建、登录 smoke 通过并启动；用户于 2026-10-26 确认 CHG-101 GUI 已验收，具体环境与步骤未在本次回复中提供（见 T-14）。
- **开发环境差异**：`discovery-scheduler` 未启动，`task-recovery` 用一次性程序调用同一 job 验证；未测常驻调度器 tick。
- **开发数据**：本轮写入的 `t10-real-%` 任务、admin 的 40 个扫描 Profile、扫描记录与真实 main 绑定已清理并读回为 0/NULL；admin 的 10 个测试 Web session 未失效（无法与用户自己的开发浏览器会话区分），按 30 天过期。清理细节见 T-10 证据。
- **无关工作树差异**：Cloud 仓 `internal/modules/production/*` 存在与本 CHG 无关的纯 gofmt 差异（同一秒批量改写），未纳入提交、未还原，留给工作树所有者。

## 8. 2026-10-26 批量验收补记

用户反馈 101-1/2/3 为 OK；101-4 在 BitBrowser 未启动时暴露原始 502/JSON/连接拒绝错误，已在 Agent、Desktop、共用前端补上结构化错误和运营可执行提示，自动化验证通过。用户随后于 2026-10-26 确认 101-4 验收通过。101-5 从人工验收清单撤下，以本报告第 5 节已有 17/17 故障注入与 64/64 真实回归为当前证据。详情见 `evidence/T-13-bitbrowser-offline-feedback.md`。
