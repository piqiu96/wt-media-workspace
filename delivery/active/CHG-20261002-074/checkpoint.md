# CHG-20261002-074 实施进度（2026-10-02）

契约 v2 主线：**阶段 1、2、3 代码全部提交，收尾项完成；走查发现的面板误报已修复（`416489f`），待用户重打 DMG 复验**。范围与验收以 [change.md](change.md) 为准。

## 走查修复（2026-10-02，cloud `416489f` + `9d54203`）

- **走查发现**：DMG 安装版（迁移已应用、Agent/比特浏览器/Cloud 全部健康）面板误报「需检查」：本机服务=未连接执行节点、比特浏览器=未知、blocker 落在比特浏览器条。
- **根因（实证）**：WorkEnvPill 把 snake_case 快照直喂读 camelCase 的页面工厂——真实运行时 camel 键全 undefined；`status` 键两形状同名存活（读到 idle），blocker 才落在比特浏览器条，与截图逐字吻合。单测漏报因夹具手写 camelCase 绕过真实形状边界。
- **修复**：`localAgentStateFromStatus` 唯一映射源（service.js）＋ store/aggregate 复用；三行各说各话（`serviceText`/`bitbrowserText`）；文案白话化（未连接云端/未运行/未检测，blocker 去术语）。
- **走查发现 2（20010 文案 v1 遗留，`9d54203`）**：用户同机重复登录桌面端命中 20010 确认框——条件是「同 client_type 活跃会话存在」（`HasActiveSessionForClientType`，无设备维度；会话无过期机制，旧会话一直挂着），同机再登录也会命中，属阶段 1 设计语义。但两处文案是 v1 遗留：「已在其他位置登录」暗示另一台设备；「旧设备不能继续领取新的本地任务」在凭据解耦后**不成立**（执行由设备绑定决定，会话替换不夺权）。change.md 阶段 1「文案仍成立」的假设被走查证伪。两处文案已按 v2 语义改写。
- **验证**：web vitest 462 用例全绿（净增 5：夹具改真实线格式 + 接线用例 + 行语义用例）；双构建通过；变异对照（撤适配）6 例红证明判别力。读数见 [evidence/walkthrough-panel-false-alarm.md](evidence/walkthrough-panel-false-alarm.md)。
- **待复验**：重打 DMG 后面板应全绿；停比特浏览器应只落比特浏览器条 blocker 且本机服务行仍「已连接」；同机再登录的 20010 确认框显示新文案。

## 收尾（2026-10-02）

- **ADR**：`docs/decisions/0019-node-two-layer-and-device-scoped-credential.md`（node 两层拆分、凭据 = 设备绑定 + 未被取代、单实例互斥、落盘边界、按设备投递；Refines 0018，Supersede 其执行层 active-session 校验语义）。
- **双构建补齐**：`build:desktop` 收尾会话首次补跑通过（8.02s，仅既有 chunk 提示）；与已记录的 `build:cloud` 合为任务 5 的双构建。
- **全量重跑（对 `00028ac` 提交树）**：cloud `go build` + `go vet` + `go test -count=1 ./internal/...` 62 包 ok；web `vitest run` 49 文件 / 457 用例通过。
- **验收 grep 复核（带阳性对照）**：G1 `ClearMainIdentity|clearBitBrowserBinding` 代码 0 命中（对照 `91c58e5` 命中，模式有效；历史 handoff 叙述 1 处按「叙述判留」保留）；G2 `invalidated_at IS NULL` 仅剩 identity 会话层 4 处 + runtimebinding:75 注册票据闸门；G3 执行层 `n.session_id|JOIN user_sessions` 0 命中（对照 `11ce766` 命中 6 处，正是阶段 2 清理的文件）；G4 dedupe 键实测 device 维（`user_download|assetID|userID|deviceID|generation`）。读数详见 [evidence/closing-readings.md](evidence/closing-readings.md)。
- **跨仓提交落地**：cloud 阶段 3 `00028ac`（40 文件，含迁移 048）；阶段 1 `11ce766`、阶段 2 `91c58e5`（cloud）/`75860f7`（desktop）此前已提交；agent 无代码触点。workspace 侧本 checkpoint + ADR + evidence + CURRENT_CONTEXT 快照随收尾提交。
- **CURRENT_CONTEXT**：由 `scripts/prepare_ai_workspace.py` 重新生成（此前快照仍指向已归档的 072）。

## 阶段 3 完成（cloud / 前端，2026-10-02）

- **Item A — dedupe 维度 node→device**：`userDownloadDedupeKey` / `CreateUserDownloadTask` 去重键改为 `user_download|assetID|userID|deviceID|generation`，换设备重投递不再被旧设备去重键吞；latest-success 检查与 generation 计数都按设备算，同设备行为兼容（键哈希进 `CHAR(64)`）。
- **Item B — UnbindDevice 重分配**：解绑时把该设备名下 pending/running 的 `local_agent` 用户下载任务置 `cancelled` + `error_code='device_unbound'`（可重取），不再把文件投到错误机器；`TestUnbindDeviceMarksTheUnboundDevicesInflightDownloadsReclaimable` 钉住。
- **Item C — DownloadCentre 重取**：抽屉打开时取本机持久化 device_id（`local_device_identity`，仅 Desktop 运行时），新增 `canRetake` / `isSuspendedOnDevice` / `isReclaimableAfterUnbind` 纯函数并穿到行对象：
  - 悬置行（`pending` 且 `assigned_device_id` = 本机）→「重取」先取消（pending 无执行器、取消即终态）再走 `materials.createDownload`，去重 generation +1，新任务落在**当前**可信节点；
  - 可重取行（`cancelled` + `device_unbound`）→「重取」直接重新发起，设备维去重把换机后的点击当成新目的地——即验收路径「设备 A 领任务→解绑→设备 B 绑定后可重取」。
  - 重取与重新下载互斥（模板 `v-else-if`）；web 读不到本机，只有可重取一支成立。
- **Item D — profilebinding 用户自助「以当前环境为准」**：`POST /api/v1/bit-browser/main-identity`（`MainIdentityInput{main_user_id, overwrite}`）handler/service/dto/仓库已接线；PersonalInfoPage 设备卡新增「以当前环境为准」入口（读本机 Agent `main_user_id` + `overwrite=true` 确认），替代 admin-only `DELETE /api/v1/users/:user_id/bit-browser-main-identity`；init.js 23002 话术改为指向自助入口。admin 删除入口清理（handler/router/仓库函数 + usersApi/UsersPage 及相关测试）全部完成；`service_test.go` 两条引用旧函数 `ClearMainIdentity` 的测试由用户执行移交命令删除。
- **Item E — 契约 23002/23003**：`browser-profile.yaml`（23002）、`profile-guard.yaml` / `agent-runtime.yaml`（23003）补 `code:` 字段与语义注释；`browser-profiles.openapi.yaml` 补「环境确认」自助语义与 `overwrite` 字段；`file-transfer.openapi.yaml` 补「重投递」语义（设备维去重、解绑可重取、下载中心对悬置任务重取）。
- **验证（本会话，用户删除两条旧测试后全量复核）**：cloud `go build ./...`、`go vet ./internal/modules/profilebinding/...`、`go test -count=1 ./internal/...`（62 包全绿）；web `npx vitest run` 49 文件 / 457 测试通过；`npm run build:cloud` 构建成功（仅 chunk-size 警告）。验收 grep 全清：`ClearMainIdentity`/`clearBitBrowserBinding` 0 命中；执行层 `invalidated_at IS NULL` 仅剩注册闸门 `isSessionActive`（应有语义）；执行层 `session_id` 仅剩 `binding_tickets` 票据表。

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

- `user_sessions` 新增 `client_type` 列（迁移 `20261002_046`，存量会话回填 `web`）。
- client_type 由服务端从 `Origin` 头推断（`tauri.localhost` → desktop，其余 → web），复用既有 `isLocalDesktopOrigin`；落库 `Session.ClientType`，**非客户端自报字段**（浏览器 Origin 为 forbidden header 不可伪造）。
- 登录替换只失效**同类型**旧会话（20010 仅同类型活跃会话存在时触发）；desktop 与 web 会话共存互不挤。
- `Logout` 改为只失效当前会话；用户停用/更新仍全量失效（安全动作，语义与登录替换不同）。
- 契约 `identity.openapi.yaml` 登录接口补充 client_type 推断语义。
- 单测：`go test ./internal/modules/identity/...` 全绿；新增登录矩阵（共存、同类型冲突、跨类型不冲突、Logout 只清自身）。
- 前端零改动（Origin 由 desktop webview 自动携带）。

## 下一步

- **重打 DMG + 面板复验**（先于其余走查）：刷新内嵌前端快照并重新打包安装；健康环境面板应「这台电脑可以工作」（正在这台电脑工作 / 已连接，当前无任务 / 已登录指定账号）；停比特浏览器应只落比特浏览器条 blocker、本机服务行仍「已连接」。
- **实机走查**（用户驱动，DONE 的前置）：迁移 046/047/048 已应用（用户确认）；剩余验 desktop 与 web 双会话共存不互挤、同类型才 20010、会话失效后凭据仍可 authenticate、Desktop 重启凭据仍在；阶段 3 走查「设备 A 领任务→解绑→设备 B 绑定后可重取」与「比特主账号切换后自助确认」、23002/23003 实发。走查结果记入 evidence，用户签收后按完成门关闭并归档。
- **待用户裁定（不阻塞走查）**：Level 级别定级（暂记 `L`）；`contracts.lock.json` 维持不 bump 的判断是否认可（wire schema 未变，见 ADR-0019 后果节）。
