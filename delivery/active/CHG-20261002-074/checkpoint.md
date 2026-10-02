# CHG-20261002-074 实施进度（2026-10-02）

契约 v2 主线：**阶段 1（会话 client_type 解耦）与阶段 2（执行凭据独立 + 设备级持久化）已完成**；阶段 3 未开始。范围与验收以 [change.md](change.md) 为准。

## 阶段 2 完成（cloud / desktop / 前端，2026-10-02）

- **node 拆两层（契约 v2 核心）**：`local_agent_nodes` 去掉 `session_id` 列与外键（迁移 `20261002_047`），凭据有效 = device 绑定存在 + 节点在线，与会话无关；注册仍经票据 `session_id` 闸门（`isSessionActive` 保留）。
- **cloud 执行层去会话耦合（逐点枚举，非仅 runtimebinding）**：
  - `runtimebinding`：`authenticateCredential` / `FindTrustedLocalNode` / `CheckLocalTrust` 去掉 `invalidated_at IS NULL` / `IsSessionActive` / `JOIN user_sessions`（上一会话已完成，本轮验证）。
  - `cloudagent` heartbeat：移除「会话失效即 draining/replaced + 11001」的旧 v1 检查；`ErrSessionInvalid`（model/service/handler 三处）已死码删除。该 SQL 引用 `n.session_id`，迁移 047 落列后必炸——删除是正确性要求，不只是语义清理。
  - `profileguard` `acquirePermit`：`JOIN user_sessions` + `s.invalidated_at IS NULL` 移除；新增 sqlmock 阳性对照 `TestAcquirePermitRequiresOnlineNodeButNotALiveSession` 钉死无 session 的完整 SQL。
  - `identity`（`user_sessions` 归属）/ `profilebinding` 对 `local_agent_nodes` 的引用本就不涉 `session_id`，无需改动。
  - 残留 grep 全清：`n.session_id` / `JOIN user_sessions` 在执行层 0 命中；`invalidated_at IS NULL` 仅剩 identity 会话层与注册闸门（均为应有语义）。
- **Desktop 凭据落盘**：`RuntimeBindingState` 新增 `persist`/`restore` + `write_binding`/`read_binding`（temp+rename+0600，复用 device_identity 先例）；bind.rs 落盘、main.rs `.setup()` 恢复、agent.rs 过期注释修正。`RuntimeBinding::node_credential` 安全边界（diagnostic.rs:15）不变——永不进 Vue，0600 落盘与 device_identity.pk8 同级。
- **前端**：WorkEnvPill「重新同步本机环境」过渡入口移除（resync/syncing/按钮/import，死代码 `canBindTrustedNode` 分支不渲染）；`bindTrustedLocalAgent` 本体保留（init.js 预览与 PersonalInfoPage 仍用）。
- **契约**：`runtime-binding.openapi.yaml` 补 node 两层语义（info description），runtime-report 401 由「Node credential or bound session invalid.」改为「Node credential invalid (device unbound or node superseded).」。wire schema 未变，contracts.lock 不 bump（与阶段 1 同判）。
- **验证**：cloud `go build ./...` + vet + `go test`（cloudagent/profileguard/runtimebinding 全绿）；desktop `cargo test` 505 通过（新增 2 条持久化单测：回读 + 0600 权限、缺失/损坏文件视为无绑定）；web `vitest run` 448 通过。
- **待办**：跨仓提交（cloud / desktop / workspace checkpoint）尚未落地；实机走查（迁移 047 应用真库、Desktop 重启凭据存活、会话失效后 authenticate 仍过）待用户执行。

## 阶段 1 完成（wt-media-cloud `11ce766`，2026-10-02）

## 阶段 1 完成（wt-media-cloud `11ce766`，2026-10-02）

- `user_sessions` 新增 `client_type` 列（迁移 `20261002_046`，存量会话回填 `web`）。
- client_type 由服务端从 `Origin` 头推断（`tauri.localhost` → desktop，其余 → web），复用既有 `isLocalDesktopOrigin`；落库 `Session.ClientType`，**非客户端自报字段**（浏览器 Origin 为 forbidden header 不可伪造）。
- 登录替换只失效**同类型**旧会话（20010 仅同类型活跃会话存在时触发）；desktop 与 web 会话共存互不挤。
- `Logout` 改为只失效当前会话；用户停用/更新仍全量失效（安全动作，语义与登录替换不同）。
- 契约 `identity.openapi.yaml` 登录接口补充 client_type 推断语义。
- 单测：`go test ./internal/modules/identity/...` 全绿；新增登录矩阵（共存、同类型冲突、跨类型不冲突、Logout 只清自身）。
- 前端零改动（Origin 由 desktop webview 自动携带）。

## 下一步

- **实机走查**（用户驱动，阶段 1+2 一并）：迁移 046/047 先经 `scripts/migrate.sh` 应用到真实 MySQL；验 desktop 与 web 双会话并存不互挤、同类型才 20010、会话失效后凭据仍可 authenticate、Desktop 重启后凭据仍在无需重走登录同步。
- 阶段 3：数据模型（dedupe 改维、解绑重分配、DownloadCentre 重取、profilebinding 自助、23002/23003）。
