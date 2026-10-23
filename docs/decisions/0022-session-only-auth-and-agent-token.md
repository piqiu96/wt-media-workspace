# ADR-0022：会话唯一认证源、会话绑定 Agent Token 与设备节点模型退场

- Status: Accepted
- Date: 2026-10-23
- Scope: Cloud identity/cloudagent/runtimebinding/filetransfer/profilebinding/profileguard、Desktop 登录与本地执行、Agent 认证与恢复、Contract
- Supersedes: ADR-0018、ADR-0019
- Partially supersedes: ADR-0003 的设备证明与 node credential 部分；票据作为一次性注册闸门的思路不再保留

## Context

ADR-0018 引入稳定设备绑定，ADR-0019 又把执行在场从登录会话中拆出，形成 `users.device_*`、Ed25519 安装身份、`local_agent_nodes`、node credential、runtime presence 和按设备去重的下载模型。该模型把「用户身份」「登录会话」「安装实例」「BitBrowser 主账号」「任务执行」混在多个长期状态对象中：换电脑需要手工解绑，登录替换与执行资格相互牵连，节点/在线/presence 又需要额外观测与清理。普通 task claim/report 甚至没有认证。

本轮用户裁定：`users` 只保存业务身份，`user_sessions` 是唯一认证事实源；Web 多会话、Desktop 单有效会话；Agent 不是设备或节点，而是由当前 desktop session 换取短期、限权、无服务端状态的签名凭证。同时 BitBrowser Profile 必须以 `user_id + main_user_id` 双作用域隔离，任务按 attempt 与活动时间收敛，而不是按设备迁移。

## Decision

1. **认证唯一源。** `users` 不保存 `auth_version`、`desktop_login_version`、`active_session_id` 或设备字段。`user_sessions` 保存 `client_type`、`expires_at`、`invalidated_at`、`invalidated_reason`。Web 登录只新增自己的 session，不替换其他 Web session；Desktop 每用户最多一条有效 session，由用户行锁串行化冲突判定。第二台 Desktop 登录先返回 `DESKTOP_LOGIN_CONFLICT`；确认替换时旧行置 `desktop_replaced` 并新建 session，旧 Desktop 得到 `AUTH_DESKTOP_REPLACED`。密码修改、管理员重置、停用、强制下线批量失效该用户 session。
2. **Agent Token。** 删除 `local_agent_nodes`、`local_agent_binding_tickets`、`browser_profile_runtime_presence`、`agent_nodes`、`users.device_*`、设备证明和 node credential。Desktop 的当前有效 desktop session 通过 `POST /api/v1/local-agent/agent-token` 换取 HMAC-SHA256 签名 Token。payload 为 `{ver:1, sub:user_id, sid:desktop_session_id, scope:"agent", iat, exp, jti}`，`exp = session.expires_at`，不落库、不设独立 TTL 或刷新定时器。Token 在登录、session 续期、应用重启或 sidecar 重启时获取，只进入 Tauri/Agent 内存。
3. **两档鉴权。** 严格档要求签名/`ver`/`scope`/`exp` 有效、用户 enabled，且 `sid` 等于当前有效 desktop session；用于 claim、新操作 preflight、BitBrowser 绑定。上报档只要求签名/`scope`/`exp` 有效、`sub` 匹配任务所属用户且 `attempt_id` 匹配；用于 report、activity、文件传输收尾和已领取任务的 preflight。Agent Token 不能调用用户业务 API；用户 session 不能调用 Agent API。
4. **BitBrowser 双作用域。** 首次绑定只接受 Agent 实读的 `main_user_id`，UI 不提供手工输入。正常 Profile 查询、更新、删除、分配与执行预检同时限制 `browser_profiles.user_id` 与当前 `bit_main_user_id`；唯一键改为 `(user_id, main_user_id, bit_profile_id)`。重绑只更新用户绑定，旧 Profile 原样保留；切回旧主账号自然恢复。
5. **任务不绑定设备。** `tasks` 增加 `user_id`、`attempt`、`attempt_id`、`started_at`、`last_report_at`、`finished_at`、`execution_timeout_seconds`、`external_side_effect`、`retryable`、`recovery_action`、`settled_by`，不增加设备、节点、交接、迁移、主账号快照或 execution ticket。Scheduler 只有一个 `task-recovery` 扫描 `running` 且 `last_report_at` 超时的任务；无副作用返回 `EXECUTION_INTERRUPTED`，有副作用返回 `RESULT_UNKNOWN`，均不自动重试。
6. **Agent 结果 outbox。** Agent 最终结果先写 SQLite checkpoint/outbox，再上报 Cloud；重启或网络恢复先补报，不重跑已完成工作。Cloud report 以 `task_id + attempt_id + user_id` 幂等收敛；迟到结果只在没有新 attempt 时生效。
7. **统一 Preflight。** 普通与敏感本地操作复用同一 evaluator 和错误码；`sensitive_profile_permits` 只保留 Profile 互斥语义，不再保存 node 或独立 credential。
8. **下载去设备化。** `file_transfer_tasks` 删除 `assigned_node_id` / `assigned_device_id`；领取按 `requested_by` 用户范围，写 `claimed_by` 审计字段和 `attempt_id`。去重键不再包含设备或节点。

## Consequences

- 正面：登录、执行和外部环境不再需要长期设备/节点状态；换电脑只影响新操作，不迁移运行中任务；Profile 切换主账号不会丢数据；任务结果在断网/重启后可收敛。
- 负面：Agent Token 无单 Token 吊销，停用/改密/抢占只使严格档失败，上报档保留到原 session `exp`；需要立即吊销全部 Token 时轮换签名密钥。服务端无法独立复核 BitBrowser/本地文件事实，只能信任准入请求中的 Agent 实时事实。
- 迁移：删除设备/节点表与列是破坏性变更，Cloud、Agent、Desktop 必须同版本停服升级。历史无 `user_id` 的 task 不伪造归属，非终态行在迁移中终结。线上仍处体验期，2026-10-23 用户裁定不提供新旧版本兼容，破坏性变更直接执行。
- 清理：`user_sessions` 的过期行由 `session-cleanup` 作业定期删除，过期后保留 7 天；未过期的失效行保留到过期，避免旧 Desktop 的 `AUTH_DESKTOP_REPLACED` 退化为通用会话无效。
- 后续：若需要即时吊销、在线状态或任务跨机迁移，必须另立 Decision，不恢复本 ADR 已删除的对象。
