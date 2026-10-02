# ADR-0019：node 拆身份会话层与执行在场层，执行凭据绑定设备

- Status: Accepted
- Date: 2026-10-02
- Scope: Cloud identity/runtimebinding/cloudagent/profileguard/filetransfer 执行层、Desktop 凭据落盘、契约 v2（runtime-binding、file-transfer、browser-profiles、agent-runtime、profile-guard、browser-profile）
- Refines: ADR-0018（设备绑定、一次性票据与 node 凭据、审计边界不变）
- Supersedes: ADR-0018 第 3 点中「active-session validation」作为执行层校验语义——登录会话失效不再连坐执行在场；ADR-0003 的会话绑定票据仅保留为注册闸门，不再是执行凭据的有效性条件。

## Context

ADR-0018 交付了稳定设备绑定，但执行在场仍挂在登录会话上：web 登录会全量失效 desktop 会话；任何会话失效（登出、被替换、过期）都会连带夺走 node 凭据；凭据只存在于 Desktop/Agent 进程内存，重启即失；下载任务按 node 维度去重，换设备后重投递被旧键吞掉；比特主账号确认依赖管理员入口。2026-10-02 走查确认这批联动功能全部缺失，用户裁定以契约 v2 承载解耦（CHG-20261002-074）。

矛盾的本质：会话回答「哪个人在哪类客户端登录」，执行在场回答「哪台设备正在干活」。两者的生命周期不同——会话随时可能因另一端登录而失效，而设备上的任务不应因此中断。

## Decision

1. 会话层引入 `client_type`（`desktop` / `web`），由服务端从 `Origin` 头推断落库，**不是客户端自报字段**（浏览器禁止脚本伪造 Origin）。登录替换只失效同 `client_type` 的旧会话；desktop 与 web 会话共存互不挤，20010 只在同类型活跃会话存在时触发。`Logout` 只失效当前会话；用户停用/更新仍全量失效（安全动作，语义不同）。
2. node 拆两层：**身份/会话层**（登录、`user_sessions`）与**执行在场层**（`local_agent_nodes`、runtime presence、敏感任务 node_id、credential）。执行在场层绑定 `device_id`，`local_agent_nodes` 不再持有 `session_id`（迁移 `20261002_047`）。
3. 凭据有效 = **设备绑定存在 + 节点未被取代**。`authenticateCredential` / `FindTrustedLocalNode` / `CheckLocalTrust` / heartbeat / `acquirePermit` 一律不再检查会话；收回执行权的途径只剩三个：解绑设备、节点离线（信任检查的心跳窗口）、同设备后续注册取代旧节点。注册闸门保留一次性票据 + 活跃会话校验（`isSessionActive` 仅存于此）——注册仍需一个登录中的人，执行不再需要。
4. 设备级单实例互斥：同 `device_id` 只允许一个执行实例持有凭据并领任务；新实例注册即取代旧实例（`AgentStatusReplaced`，旧凭据立刻失效）。
5. Desktop 将 `RuntimeBinding`（含 node 凭据）落盘持久化：0600 + temp+rename 原子写，与 `device_identity.pk8` 同级同边界；启动时恢复，进程重启无需重走登录同步。`node_credential` 永不进 WebView、日志与诊断。
6. 下载任务投递按设备算：去重键 `user_download|assetID|userID|deviceID|generation`（node→device）；解绑设备时该设备名下 pending/running 的 `local_agent` 任务置 `cancelled` + `error_code='device_unbound'`（可重取）；23002/23003（环境自助确认、重投递）语义入契约，比特主账号由用户在个人信息页自助「以当前环境为准」，不再依赖管理员删除入口。

## Consequences

- Cloud 执行层 SQL 禁止 `JOIN user_sessions` 或检查 `invalidated_at`；唯一例外是身份会话层自身与注册票据闸门。
- 会话失效不再是执行层故障：登出、另一端登录、会话过期都不中断在途任务；执行权的回收只能通过解绑或节点离线/被取代。这是有意的安全权衡——设备是执行信任边界，会话只是人的在场证明。
- Desktop 重启后凭据仍在即可领任务，「重新同步本机环境」类过渡入口不再需要。
- 契约 v2 wire schema 与 v1 兼容（列删除经迁移，接口形状未变），`contracts.lock.json` 不因本决策 bump；行为语义差异由 OpenAPI 描述与错误码承载。
- 测试必须钉住：登录矩阵（跨类型共存、同类型 20010、`Logout` 只清自身）、无 session 的完整 SQL（sqlmock 阳性对照）、凭据落盘回读与 0600、解绑后任务可重取、被取代节点凭据拒绝。
