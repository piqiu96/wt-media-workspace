# ADR-0027：运营资源数据边界与本地代理执行

- Status: Accepted
- Date: 2026-10-29
- Scope: 社媒账号、浏览器窗口、代理资源及其 Cloud / Desktop / Local Agent 执行边界
- Related: ADR-0008、ADR-0022、ADR-0023
- Supersedes: ADR-0004、ADR-0008、ADR-0025、ADR-0026

## Context

运营资源当前把第三方镜像、Cloud 正式关系、检测结果和本机操作结果混在少量宽表中，同时由 Cloud 服务端直接访问运营电脑的 Local Agent。该实现既无法稳定表达“结果待确认”，也把当前页面不需要的审计、检测历史和通用操作状态引入了设计。

本决策只保留业务正确性所必需的状态，不建设通用工作流、通用审计或额外操作历史。

## Decision

1. **Cloud 是业务事实源，Agent SQLite 不保存运营资源业务数据。** `browser_profiles`、`proxies`、社媒账号关系及临时进行中状态只存在 Cloud；Agent 本地库只保存 file-transfer 租约的恢复记录。
2. **第三方镜像使用前缀。** 比特数据统一 `bit_`，平台账号数据统一 `platform_`，检测数据统一 `last_check_`。Cloud 自有字段不加第三方前缀。
3. **启停统一布尔语义。** 社媒账号、浏览器窗口和代理统一使用 `enabled`，接口返回布尔值；不再使用 `business_status`、`active/paused` 或 `enabled/disabled` 字符串表达同一件事。
4. **代理只保留当前事实。** `proxies` 保存资源、连接、配额、启停、最近检测结果和最近检测原因；不建立连接版本表、检测历史表或通用资源事件表。
5. **正式关系与临时额度预留分离。** `browser_profiles.proxy_id` 表示 Cloud 正式托管关系；`reserved_proxy_id`、`reserved_since` 只在一次代理写入进行中临时占用目标额度。不建立 operation 表；未知结果保留当前预留与必要恢复事实，页面可恢复核实。
6. **本机代理写入与动态提取由 Desktop 发起。** Cloud 创建代理写入意图并校验团队、可用性和额度；Desktop 通过 Tauri 调用 Local Agent，并回报明确结果。供应商动态地址从运营本机网络提取，Cloud 只保存提取结果并执行连接检测。Cloud 不直接访问运营电脑的 Agent 端口执行代理写入或动态提取。
7. **正常以比特明确成功响应为准，未知结果先核实。** 明确成功建立正式关系，不强制二次读取；明确拒绝释放预留。超时、断开、中断或损坏响应可能已经写入，保留预留，先由本机比较实际配置（含认证，仅回传比较结论），再收敛结果；禁止盲目重写。代理连接检测与比特写入结果是不同事实。
8. **同步扫描只保留当前快照。** 每个用户最多一条 `browser_profile_syncs` 记录，保存本次窗口实际配置快照；确认后在同一条记录保留最近确认回执，下一次扫描覆盖；拒绝可删除。新版确认带已审核的快照编号，重复确认只返回回执，不重放镜像。不保存扫描历史，不建立候选表。
9. **Cookie 读取走同步链路。** Cookie 读取由 Desktop 调用 Local Agent 后一次性回报 Cloud；删除旧异步 Cookie 任务入口、Cloud 通用 `tasks` 表和 Agent 通用任务执行器。Agent 本地只保留 file-transfer 所需的恢复记录与独立租约循环。
10. **敏感许可与审计不是本域状态机。** 账号检查/Cookie 使用短生命周期 operation id 和现有账号/窗口归属校验，不建立 sensitive task/permit 表；浏览器窗口和代理同样不新增敏感任务表。现有 `audit_logs` 不为每次代理操作强制扩展。

## Consequences

- Cloud 领域表收敛为社媒账号四表、`browser_profiles`、`proxies`、`browser_profile_syncs`。
- Desktop 增加代理 apply/unbind 与动态提取桥；`local_agent_profile_restore` 不得再顺带写代理字段。
- Agent 通用 task claim/report、preflight/permit、proxy-check 与浏览器 executors 退役；Cloud 不再调用代理写入或健康检测的 Agent 方法。
- 明确拒绝可重试；未知结果必须先核实，恢复事实不能因关闭页面或超时而释放，旧结果不得结算新操作。
- 不保留专用检测历史、操作历史、通用审计或敏感许可表，因此无法从这些表重建历史过程；需要追溯时以现有日志和 Git 记录为限。
