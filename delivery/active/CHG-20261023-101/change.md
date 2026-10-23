---
id: CHG-20261023-101
parent: delivery/milestones/M2-account-runtime.md#m2-f-登录会话与本地运行时边界收敛
status: IMPLEMENTING
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: H
---

# CHG-20261023-101：登录、BitBrowser 与本地任务运行时边界收敛

## Change

按用户 2026-10-23 裁定收敛三条相互纠缠的边界：

- 登录只以 `user_sessions` 为唯一认证事实源：Web 允许同一用户多条有效 session；Desktop 同一用户只允许一条有效 session，冲突由 session 行表达并支持取消/确认替换；密码修改、重置、停用、强制下线批量失效 session；不在 `users` 增加任何认证状态字段。
- 删除固定设备/节点模型（`users.device_*`、Ed25519 设备证明、`local_agent_nodes`、binding ticket、runtime presence、`agent_nodes`、`file_transfer_tasks.assigned_device_id`）。Desktop 登录后用当前有效 desktop session 换取会话绑定、限权、无服务端状态的签名 Agent Token；Token 的 `exp` 等于该 session 的 `expires_at`，不设独立 TTL 或刷新定时器。
- BitBrowser 首次绑定只接受 Agent 实读的 `main_user_id`；`browser_profiles` 按 `user_id + main_user_id` 双作用域；切换主账号不删除、不迁移旧数据。
- 统一 Execution Preflight 覆盖普通与敏感本地操作；Task 不绑定设备/节点，使用 `user_id`、`attempt_id`、`last_report_at`、`execution_timeout_seconds`、`external_side_effect` 统一收敛；Agent SQLite 实现 checkpoint + result outbox，终态先落盘再上报。

## Done When

- 两个 Web 会话并存；Web 与 Desktop 会话并存；第二台 Desktop 登录先返回冲突，取消零写入，确认后旧 Desktop 收到 `AUTH_DESKTOP_REPLACED`；旧 Desktop 的 sidecar 仍可上报已领取任务。
- Agent Token 只能调用受限 Agent API；严格档在 Desktop 被替换后拒绝 claim/bind/preflight，上报档在 `exp` 前仍可收敛已领取任务；Token `exp == session.expires_at`，登录/续期/app 或 sidecar 重启时重取，无独立刷新定时器。
- 设备/节点相关表、列、路由、错误码、Tauri 设备身份、Web 设备入口与下载设备逻辑全部退场，无兼容旁路。
- BitBrowser 首绑、同主验证、临时不一致、正式重绑、切回旧主账号、跨系统 UID 隔离、扫描缺失只标记不删除、媒体账号越界行为均有自动化与真实读数。
- 统一 Preflight 的 11 项检查按 `code` 失败关闭；普通任务不能绕过；敏感 permit 只保留互斥语义。
- Task pending→leased→running→terminal、静默超时两分支、迟到结果、新 attempt 拒绝旧结果、重复上报幂等、用户范围 claim、同行走重试、结果投影用户范围全部有测试读数。
- Agent 终态在调用 Cloud 前写入 SQLite outbox；重启先补报不重跑；无副作用可安全重跑，有副作用报 `RESULT_UNKNOWN`；`account_check` 按真实检查结果上报。
- Cloud 068–071、Agent 0004 在 scratch schema 与实际 SQLite 上实跑并读回列/索引/约束/回填；破坏性迁移从旧 fixture 起跑。
- `user_sessions` 过期行由 `session-cleanup` 按小时清理，过期后保留 7 天；未过期的失效行保留到过期，旧 Desktop 仍可区分 `AUTH_DESKTOP_REPLACED`。
- Contract、Product、Architecture、Communication Spec、ADR-0022、M2-F、LEDGER 与 CHG 记录回写完成；Workspace 治理校验全绿。
- 四仓测试、真实 Agent/BitBrowser/打包 Desktop 回归按测试矩阵留读数；未覆盖项如实登记。

## Ordered Tasks

| Task | Result |
| --- | --- |
| T-01 | Workspace 基线：CHG-101、ADR-0022、M2-F 新锚点、Contract revision 计划与四仓分支 |
| T-02 | Cloud 登录：session-only、Desktop 冲突、批量失效、typed auth errors |
| T-03 | Cloud Agent Token：签发/验签、严格/上报档、设备节点模型退场 |
| T-04 | Cloud BitBrowser：Agent 实读绑定、Profile 双作用域、扫描非破坏 |
| T-05 | Cloud 统一 Preflight：11 项 evaluator、permit 纯互斥、普通任务入口 |
| T-06 | Cloud Task Runtime：attempt、超时扫描、迟到/幂等、同行走重试、用户范围投影 |
| T-07 | Agent：Agent Token provider、SQLite 0004、outbox、activity、恢复 |
| T-08 | Desktop/Web：登录冲突/替换 UI、Agent Token 配置、去设备化、下载与错误文案 |
| T-09 | Contract 与正式文档回写、旧事实扫描 |
| T-10 | 四仓全量验证、真实回归、证据与最终报告 |
| T-11 | Cloud 过期会话清理：`session-cleanup` 作业、072 索引、配置与开发库实跑 |

## Verification

- 四仓全量测试、068–071 迁移实跑、真实 Agent/BitBrowser/打包 Desktop 回归、断网补报与真实超时扫描读数见 `evidence/T-10-full-verification.md`；七项交付报告见 `report.md`。
- T-11 会话清理：迁移 072、配置、批处理作业与开发库实跑读数见 `evidence/T-11-session-cleanup.md`（675→406，删除 269，保留带 55，有效 12 不变）。
- T-10 风险复核裁定（2026-10-23）：第 3 项过期 session 清理纳入本 CHG（T-11）；第 7 项本地 API CORS/空 runtime token 不加固；第 4 项 071 同版本停服升级不做新旧兼容，线上处于体验期，破坏性变更直接执行。
- T-10 期间发现并修复：非 Cloud 信封的网关 502 被记成 `executor_error`（Agent `8749193`）、070 对非数字历史 payload id 的 1292 中止（Cloud `cc2aacc`）、文件传输业务 schema 多声明内部标签 `claimed_by`（Cloud `98c08dd`）、两个测试夹具竞态（Agent `d5097f5`）。
- 未覆盖：第二台物理 Desktop、GUI 逐屏视觉、真实发布/互动任务、真实下载双机交接、常驻 `discovery-scheduler` tick。
- 状态保持 `IMPLEMENTING`，直至各仓 PR 合并与 GUI 视觉验收完成。

## Constraints / Not In Scope

- 不在 `users` 新增 `auth_version`、`desktop_login_version`、`active_session_id`；不建 `web_session` 表。
- 不新增 `local_agent_nodes`、`agent_presence`、设备在线状态、`execution_ticket` 或 task-scoped auth。
- 不实现任务迁移、交接、换电脑恢复或设备接管状态机。
- 不自动重试有外部副作用任务；不实现发布/互动业务。
- 不重写 `file_transfer_tasks` / `compose_tasks` 既有 lease/reconcile 生命周期；只改认证、attempt 与设备/节点字段。
- 不保留未认证 claim/report 或旧节点/设备兼容旁路；旧 Agent 在新 Cloud 上失败关闭。
- 不重写历史 ADR / 已完成交付记录；只加取代指针。
- 不建立第二套 Delivery、状态或 Context 源。

## References

- `docs/product/prd/详细文档/第三章_用户与账号管理.md`
- `delivery/milestones/M2-account-runtime.md#m2-f-登录会话与本地运行时边界收敛`
- `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- `docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md`
- `docs/decisions/0022-session-only-auth-and-agent-token.md`
- `config/contract-map.yaml`

## Pending Questions

None.
