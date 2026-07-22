# CHG-20260723-025：M2-B1 浏览器窗口扫描与 Diff 只读闭环

> 日期：2026-07-23  
> 状态：DONE  
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环  
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`  
> 当前仓库：`wt-media-workspace`  
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`、`wt-media-workspace`

## 1. 用户可见目标

普通运营在 Desktop 登录并通过 M2-A 本地身份校验后，可以触发一次真实 BitBrowser 窗口扫描，系统只生成并在 Desktop 展示窗口差异，不修改 Cloud 正式 Profile 镜像，不应用 Diff，不执行账号绑定。Cloud Web 没有 Agent 执行环境，只能查看 Cloud 已保存的浏览器窗口基本信息。

本 CHG 完成后，用户应能回答：

- 当前电脑的 BitBrowser 里有哪些窗口；
- 哪些窗口是 Cloud 没有记录的新增窗口；
- 哪些 Cloud 窗口在本地疑似缺失；
- 哪些窗口的名称、分组、代理、运行状态或已绑账号影响发生变化；
- 当前差异是否需要后续“接受本地变化”或“恢复 Cloud 配置”处理。

## 2. 当前背景

M2-A 已完成人工验收，普通运营、管理员、高级运营的 Cloud/Desktop 入口边界已经建立。

M2-B 的完整闭环包含：

```text
Desktop登录后扫描Profile
→ 生成Diff但不应用
→ 用户接受BitBrowser变化或恢复Cloud配置
→ 单个或批量创建窗口并读回
→ 管理员分配未授权窗口
→ 普通运营创建媒体账号台账
→ 绑定或换绑窗口
→ 单个或批量账号检查
→ 回填平台UID、名称、头像和登录状态
```

本 CHG 只做第一段：

```text
Desktop登录后扫描Profile
→ 生成Diff但不应用
→ 页面展示Diff
```

## 3. 本 CHG 范围

### 包含

- 审计当前 Cloud / Web / Agent / Desktop 中已有 Profile 扫描、快照提交和 Diff 代码；
- 明确 Desktop 发起扫描的安全路径，不能让 Cloud Web 直接承担本机 BitBrowser 操作入口；
- 明确 Cloud Web 与 Desktop 的页面能力边界：Cloud Web只看Cloud基本信息和已保存历史摘要，Desktop展示和处理BitBrowser扫描Diff；
- 普通运营触发本机 BitBrowser Profile 扫描；
- Local Agent 同步调用 BitBrowser 读取当前窗口列表；
- Cloud 接收扫描快照并生成只读 Diff；
- Diff 至少覆盖：
  - 新增窗口；
  - Cloud存在但本地缺失；
  - 名称变化；
  - 分组变化；
  - 代理变化；
  - 运行状态变化；
  - 已绑定媒体账号可能受影响；
- Desktop页面展示本次扫描结果和 Diff 列表；
- 扫描结果不得包含 Cookie、平台密码、代理密码等敏感明文；
- 生成自动测试和 evidence，证明“扫描只读、不应用”。

### 不包含

- 不接受本地变化；
- 不恢复 Cloud 配置到 BitBrowser；
- 不创建、编辑、打开、关闭 Browser Profile；
- 不分配未授权窗口；
- 不绑定、解绑或换绑媒体账号；
- 不执行账号检查；
- 不写入代理；
- 不写入、读取或修改 Cookie；
- 不远程删除 BitBrowser 本地窗口；
- 不用异步任务替代本次单项同步扫描。

## 4. 关键规则

- 页面面向用户使用“浏览器窗口”表达，代码和数据库仍使用 `browser_profile`；
- 本机 BitBrowser 扫描必须在 Desktop / Local Agent 可信环境下进行；
- Desktop Vue必须通过Tauri/Rust调用Local Agent，后续严格禁止直接访问Local Agent动态端口或token；
- Cloud Web没有Agent执行环境，不得展示或触发依赖BitBrowser的扫描、Diff处理、读回、打开、关闭、创建、更新等本机能力，只能展示Cloud已保存的基本信息；
- 扫描前必须继承 M2-A 的本地身份前置条件：当前用户、Desktop节点、Local Agent、BitBrowser `main_user_id` 匹配；
- 扫描只生成 Diff，不得修改 Cloud 正式 Profile 镜像；
- Cloud授权用户、账号绑定、游戏、标签、备注、Cookie 和业务状态不能被扫描覆盖；
- HTTP成功、Agent返回成功、BitBrowser接口返回成功都不等于业务完成，必须能在页面看到明确 Diff 或“无差异”结果；
- 如果身份不匹配、BitBrowser不可用或读回失败，页面必须显示运营能理解的失败原因，不得写入正式镜像。

## 5. 执行任务

### Task 1：Start Gate 与现状审计

- 阅读 `M2-account-runtime.md` 的 M2-B 闭环；
- 审计当前 Profile 扫描、Diff、Cloud镜像、Agent BitBrowser adapter、Desktop入口和页面实现；
- 输出可复用、需修正、需新增的文件映射；
- 确认本 CHG 不会与当前未提交 runtime 改动冲突。

### Task 2：扫描输入与 Diff 数据边界

- 明确扫描快照字段；
- 确保快照可以表达窗口ID、名称、分组、代理摘要、运行状态、`main_user_id`、`profile_user_id` 和本地存在性；
- 明确敏感字段禁止出现在扫描快照、Diff、日志和页面。

### Task 3：Cloud 只读 Diff

- Cloud 接收 Desktop 提交的 Local Agent / BitBrowser 扫描快照；
- Cloud 基于扫描快照与Cloud已保存 `browser_profiles` 镜像计算只读 Diff；
- 不应用到正式 Profile 镜像；
- 不改变 Profile 授权、账号绑定和业务对象；
- 不调用 Local Agent，不连接 BitBrowser，不读取本机环境；
- 必要时复用或修正已有扫描历史/差异模型。

### Task 4：Desktop / Agent 同步扫描路径

- 普通运营从 Desktop 触发扫描；
- Desktop Vue 通过 Tauri/Rust 本地可信通道调用 Local Agent；
- Local Agent 同步调用 BitBrowser 并读回窗口列表；
- 身份不匹配或 BitBrowser不可用时阻断并返回可理解错误。

### Task 5：Cloud / Desktop 浏览器窗口页面展示边界

- Desktop浏览器窗口页面展示扫描入口；
- Desktop展示本次扫描时间、扫描状态和 Diff 列表；
- Cloud Web浏览器窗口页面只展示Cloud已保存的基本信息、授权关系、绑定账号摘要和历史同步摘要；
- Cloud Web不展示也不触发扫描、Diff处理、读回、打开、关闭、创建、更新、账号检查等依赖本机Agent或BitBrowser的能力；
- Diff 分类清晰表达新增、缺失、变化和受影响账号；
- “接受本地变化”“恢复Cloud配置”等后续操作可以隐藏、禁用或标记为后续 CHG，不得假装已经完成。

### Task 6：验证与 Evidence

- 自动测试覆盖 Cloud Diff 只读逻辑；
- Agent / Desktop 路径至少提供 mock BitBrowser 或真实 BitBrowser 证据；
- 页面证据证明用户能看到 Diff 或无差异结果；
- 证据证明扫描不会修改 Cloud 正式镜像。

## 6. 验收标准

本 CHG 只有同时满足以下条件，才能进入 VERIFIED：

- 普通运营在 Desktop 可信环境下可以发起浏览器窗口扫描；
- Cloud Web不能发起扫描，也不能展示依赖本机BitBrowser实时读回的Diff处理入口；
- Local Agent 实际读取 BitBrowser Profile 列表，或在测试中使用明确的 BitBrowser mock adapter；
- Cloud 能生成并返回只读 Diff；
- Desktop页面能展示 Diff 分类和无差异结果；
- 扫描前后 Cloud 正式 Profile 镜像、授权用户和媒体账号绑定没有被自动修改；
- 身份不匹配、BitBrowser不可用、读回失败时，页面显示明确失败原因；
- 没有 Cookie、平台密码、代理密码等敏感明文进入接口响应、日志或页面；
- Evidence 记录 API、Agent/Desktop路径、页面结果和只读副作用验证。

## 7. Evidence 要求

完成后在 `evidence/` 中至少提供：

- `start-gate.md`：现状审计、复用判断、文件映射和风险；
- `tests.md`：自动测试命令、结果和覆盖说明；
- `scan-diff-readonly.md`：扫描前后 Cloud 镜像不被修改的证据；
- `desktop-agent-scan.md`：Desktop / Local Agent 调用链路证据；
- `manual-acceptance.md`：人工验收步骤、账号、页面和结果记录。

## 8. 交付边界

本 CHG 完成后，M2-B 只证明“浏览器窗口扫描与 Diff 只读闭环”成立。

后续独立 CHG 继续处理：

- B2：接受本地变化 / 恢复 Cloud 配置 / 窗口生命周期与授权；
- B3：媒体账号台账与 Profile 绑定；
- B4：媒体账号真实检查与身份回填。

## 9. Checkpoint

### 2026-07-23 Task 1 Start Gate

- 已完成：读取 AGENTS、CURRENT_CONTEXT、LEDGER、M2-B Milestone、Active CHG 和受影响仓库规则；审计 Cloud ProfileBinding、Agent BitBrowser扫描、Desktop Rust桥、Web浏览器窗口页面；生成 `evidence/start-gate.md`。
- 当前结论：现有 Cloud/Agent/Web 有可复用扫描与Diff骨架，但 Desktop路径违反“Vue不直连Local Agent动态端口/token”的规则，Cloud Diff字段也未覆盖代理、备注、运行状态和已绑账号影响。用户已确认：后续 Desktop 必须通过 Rust 调 Local Agent；Cloud Web 无 Agent 执行环境，只能看 Cloud 基本信息，不能承载依赖 BitBrowser 的扫描/Diff处理入口。
- 当前阻断：`wt-media-agent` 和 `wt-media-desktop` 存在未提交 runtime 改动，且命中后续会修改的 Local Agent 状态与 Rust桥文件；进入 Task 2/4 实现前需确认这些改动归属。
- 下一步：确认脏改动后执行 Task 2，统一扫描快照字段和敏感字段边界。
- 最近验证：本步骤为只读代码审计与治理证据记录，未运行自动测试，未修改 runtime 代码。

### 2026-07-23 Task 2 Snapshot Boundary

- 已完成：将进入 Task 2 前的 `wt-media-agent` / `wt-media-desktop` 未提交改动归属为 M2-A 本地环境状态投影尾项，并分别提交 `8eb5a82`、`51c7ce3`；新增 `evidence/dirty-runtime-ownership.md`。
- 已完成：统一扫描快照字段边界。Cloud `ProfileInput`、staged scan 存储和 Diff 字段比较已支持代理摘要、运行状态和备注；Web `safeProfile` 继续使用 allow-list，并将 Agent `status` 映射为 Cloud `bit_status`；Agent 测试补充运行状态和代理摘要断言。
- 当前结论：Task 2 只完成“安全扫描快照字段和 Diff 数据边界”，未触碰 Desktop Rust 扫描路径、页面入口、Diff应用和账号绑定。
- 当前阻断：无。
- 下一步：进入 Task 3，补 Cloud 只读 Diff 的业务对象边界与正式镜像不变证据。
- 最近验证：`go test ./internal/modules/profilebinding/...` PASS；`npm test -- profileBindings` PASS；`python3 -m unittest tests/test_local_profile_scan.py` PASS。

### 2026-07-23 Task 3 Boundary Correction

- 已完成：根据用户确认修正 Task 3 边界。Cloud 不读取本机 BitBrowser，也不调用 Local Agent；Cloud 只接收 Desktop 提交的扫描快照，并与 Cloud 已保存 `browser_profiles` 镜像计算只读 Diff。
- 已完成：补充 Cloud Web / Desktop 功能展示边界。Cloud Web 只能展示 Cloud 已保存基本信息和历史摘要；Desktop 才展示扫描入口、本机读回、Diff处理、打开/关闭/创建/更新、账号检查等依赖 Local Agent / BitBrowser 的能力。
- 当前阻断：无。
- 下一步：按修正后的 Task 3 口径实现 Cloud 只读 Diff 的正式镜像不变验证。
- 最近验证：本步骤为 CHG/Milestone 边界矫正，未修改 runtime 代码。

### 2026-07-23 Task 3 Cloud Readonly Diff

- 已完成：Cloud `POST /api/v1/bit-browser/profile-scans` 接收扫描快照前要求 `node_id` 并校验 M2-A 本地信任；缺少 `node_id` 或本地信任不可用时拒绝请求，且不创建 scan。
- 已完成：Cloud Service 继续只基于 Desktop 提交的快照与 Cloud 已保存 `browser_profiles` 镜像计算只读 Diff，不调用 Local Agent，不连接 BitBrowser，不应用 Diff。
- 已完成：Web profile binding client 支持 `submit(snapshot, { nodeId })`，为后续 Desktop Tauri/Rust 路径提交可信 node 做准备。
- 当前阻断：无。
- 下一步：进入 Task 4，新增 Desktop / Rust / Local Agent 同步扫描路径，替换页面直连 `127.0.0.1:8765` 的实现。
- 最近验证：`go test ./internal/modules/profilebinding/...` PASS；`npm test -- profileBindings` PASS。

### 2026-07-23 Task 4 Desktop Agent Scan Path

- 已完成：Desktop Rust 新增 `local_agent_profile_scan` Tauri command，由 Rust 同步调用 Local Agent `/api/v1/bit-browser/profile-scans` 并透传安全快照。
- 已完成：Web Local Agent service 增加 `profileScan()`；浏览器窗口页扫描流程改为通过 Tauri/Rust 获取 `node_id` 和 BitBrowser 快照，再提交 Cloud 计算只读 Diff。
- 已完成：浏览器窗口页已移除对 `127.0.0.1:8765` 的直接扫描访问；非 Tauri Desktop 客户端环境阻断扫描。
- 当前阻断：无。
- 下一步：进入 Task 5，收口 Cloud Web / Desktop 浏览器窗口页面展示边界，隐藏或禁用本 CHG 不包含的 Diff应用类动作。
- 最近验证：`cargo check` PASS；`npm test -- profileBindings localAgentService` PASS；`npm run build:cloud` PASS；`npm run build:desktop` PASS。

### 2026-07-23 Desktop Trust Status Acceptance Repair

- 已完成：修复人工验收发现的状态不一致问题。Desktop Agent 状态页不再仅凭 Cloud 登录、Local Agent、BitBrowser 和主账号 ID 显示“本机环境可信”；必须存在 Cloud 可信 `node_id` 才显示“本机节点可信”。
- 已完成：Agent 状态页新增“重新检测”和“重新检测并绑定”入口；未绑定时显示“本机节点未绑定”和运营可理解提示。
- 已完成：新增 Cloud `POST /api/v1/bit-browser/main-identity`，用于确认当前用户 BitBrowser 主账号，不创建 scan、不应用 Profile Diff、不写入正式 Profile 镜像；Runtime report 允许只上报主账号身份，避免 M2-A 主账号确认与 M2-B Profile Diff 形成循环依赖。
- 已完成：Desktop Rust 新增 `local_agent_bind_session`，由 Rust 消费 Cloud 一次性绑定票据、注册本机节点、写入 Local Agent `node_id` 并上报运行状态；`node_credential` 不返回 Vue。
- 已完成：修复 Desktop 登录页旧会话替换按钮事件。登录表单不再通过 submit 触发登录；“登录”“替换旧会话并登录”“取消”全部使用显式 click 事件，确保替换按钮稳定发送 `replace_existing=true`。
- 已完成：确认登录后仍未进入系统的根因是本地 Cloud 以 `WT_MEDIA_SESSION_COOKIE_SECURE=true` 启动，HTTP Desktop WebView 无法稳定保存 secure cookie；已用 `WT_MEDIA_SESSION_COOKIE_SECURE=false` 重启本地 Cloud API。
- 当前阻断：需要用户在当前 Desktop 窗口重新点击“替换旧会话并登录”进行人工验收。若点击“重新检测并绑定”后 Cloud 返回身份不匹配，则说明当前 BitBrowser 主账号与 operator01 已绑定主账号不一致，需要先按 M2-A 重新确认主账号。
- 下一步：用户重新登录 operator01；如出现旧会话提示，点击“替换旧会话并登录”应进入系统，再到 Desktop 环境状态页点击“重新检测并绑定”。
- 最近验证：`go test ./internal/modules/profilebinding ./internal/modules/runtimebinding` PASS；`npm test -- profileBindings localAgentService` PASS；`npm test -- session desktopRoleGuard` PASS；`npm run build:desktop` PASS；`cargo check` PASS（仅 existing unused/dead_code warnings）；`curl -i http://127.0.0.1:5174/api/v1/auth/login` 确认本地 Set-Cookie 不再包含 `secure`；`curl -b ... /auth/me` PASS。

### 2026-07-23 Desktop Runtime Report Repair

- 已完成：定位“重新检测并绑定”失败原因。Cloud 节点注册成功，但 Desktop 上报 runtime-report 返回 400，导致 `local_agent_nodes.reported_main_user_id` 与 `bitbrowser_status` 未落库，后续浏览器窗口扫描被 `CheckLocalTrust` 正确阻断。
- 已完成：修复 Desktop Rust `local_agent_bind_session`。runtime-report 改为使用 Local Agent `/api/v1/status` 的真实运行环境字段，上报 `python_version`、`ffmpeg`、`workdir_status`、`disk`、`bitbrowser_status` 和 `main_user_id`；本机可信绑定不再上报 `bit_profile_ids`，避免把 M2-B Profile Diff 归属验证提前塞进主账号绑定。
- 当前结论：当前修复符合用户确认的 A2-only 口径：可信绑定只验证系统用户、Desktop节点、Local Agent、BitBrowser主账号一致；Profile 列表扫描和 Diff 归属仍留在 M2-B 当前 CHG。
- 当前阻断：等待用户在新启动的 Desktop 窗口点击“重新检测并绑定”进行人工验证。
- 下一步：用户点击后检查 Cloud 日志和 `local_agent_nodes`，确认 runtime-report 成功落库；随后返回浏览器窗口页重新扫描。
- 最近验证：`curl http://127.0.0.1:8765/api/v1/status` PASS，返回 `ffmpeg.version=8.1.2`、`bitbrowser_status=normal`、`main_user_id=2c9bc06191effa4e0191f9589996619f`；`cargo check` PASS；已用 `cargo run` 启动新的 Desktop 壳。

### 2026-07-23 Task 5 Page Boundary

- 已完成：浏览器窗口页面按 Cloud Web / Desktop 边界展示。Cloud Web 只展示 Cloud 已保存列表、详情和刷新，不展示新建、扫描、打开、关闭、删除等本机操作入口；Desktop 才展示本机操作入口。
- 已完成：扫描结果抽屉移除“仅确认主账号”和“确认同步窗口”可点击动作，改为禁用的“接受本地变化（后续）”“恢复Cloud配置（后续）”，避免把 B2 能力伪装成本 CHG 完成项。
- 已完成：页面文案从“Profile”面向用户改为“浏览器窗口”，Cloud Web 增加只读提示。
- 当前阻断：无。
- 下一步：进入 Task 6，汇总自动测试、构建、扫描只读、Desktop路径和页面边界 evidence；如需真实人工验收，再启动环境验证。
- 最近验证：`npm test -- profileBindings localAgentService` PASS；`npm run build:cloud` PASS；`npm run build:desktop` PASS；关键词检查确认业务页无直连 Local Agent 端口、无可点击 Diff 应用动作。

### 2026-07-23 Task 6 Verification Evidence

- 已完成：补充 `evidence/tests.md`，记录 Agent、Cloud、Web、Desktop、双端构建、页面边界关键词和工作区差异检查结果。
- 已完成：补充 `evidence/manual-acceptance.md`，明确真实页面人工验收步骤和待补记录项。
- 当前结论：本 CHG 的代码实现和自动化验证已收口；Cloud 只读 Diff、Desktop/Rust/Local Agent 调用路径、Cloud Web/Desktop 页面边界均通过自动验证。
- 当前阻断：真实 Desktop 页面人工验收尚未执行，因此本 CHG 不进入 `CLOSED`。
- 下一步：启动 Cloud / Agent / Desktop 环境，由用户按 `manual-acceptance.md` 验收 Cloud Web 只读边界、Desktop 扫描 Diff/无差异结果、扫描不修改正式镜像和异常提示。
- 最近验证：`python3 -m unittest tests/test_local_profile_scan.py` PASS；`go test ./internal/modules/profilebinding/...` PASS；`npm test -- profileBindings localAgentService` PASS；`cargo check` PASS；`npm run build:cloud` PASS；`npm run build:desktop` PASS；关键词检查 PASS。

### 2026-07-23 Final Trust Binding Semantics

- 已完成：按用户最终确认收口本机环境语义。「重新检测本机环境」只做只读检查，不写 Cloud、不重启 Agent、不扫描窗口；首次绑定与已绑定后的刷新分开表达；已绑定账号不允许静默从比特账号 A 改绑到账号 B。
- 已完成：新增管理员解除用户比特浏览器绑定能力。该操作只清空用户主账号绑定并失效本地节点，不删除 Cloud 已保存浏览器窗口、媒体账号或历史记录；用于系统写错绑定关系后的低成本修复路径。
- 已完成：Cloud Web / Desktop 边界再次确认。Cloud Web 对所有角色只展示 Cloud 已保存数据；Desktop 才展示本机 Agent / BitBrowser 依赖能力。
- 已完成：用户可见文案去内部化。源码和构建产物中已清理「M2」「敏感操作」「可信节点」「可执行结论」「当前Desktop身份不可信」等运营不理解或内部工程表达。
- 已完成：同步正式事实源。PRD 第三章和 `delivery/milestones/M2-account-runtime.md` 已更新为 A2-only 口径：主账号绑定只验证 `main_user_id`；完整 Profile 扫描、Diff 和授权同步归 M2-B；管理员解除错误绑定后由运营在 Desktop 重新绑定。
- 当前阻断：无代码阻断；仍需用户重新打开最新 Desktop 壳进行人工验收。
- 下一步：用户验证 Desktop 环境状态页：重新检测只刷新本地读取状态；账号一致时刷新本机状态成功；账号不一致时阻断；管理员可在 Cloud 用户管理解除错误绑定后再由运营重新绑定。
- 最近验证：`go test ./internal/modules/profilebinding ./internal/modules/runtimebinding` PASS；`npm test -- localAgentStatus usersApi UsersPage profileBindings localAgentService session desktopRoleGuard` PASS；`cargo check` PASS（仅既有 unused/dead_code warnings）；`npm run build:desktop` PASS；`npm run build:cloud` PASS；源码、PRD 和 Milestone 关键词检查无旧口径匹配。

### 2026-07-23 Milestone-first Governance Rule

- 已完成：沉淀 Milestone-first 回写规范。后续执行中发现的小变更、验收细节、页面口径、操作边界和异常处理，优先写当前 Milestone 和当前 CHG checkpoint/evidence；不再每次立即回写 PRD。
- 已完成：更新 `delivery/milestones/README.md`，明确 PRD 是长期产品事实，Milestone 是当前阶段业务闭环基线。
- 已完成：更新 `planning-wt-media-delivery` Skill 源文件，并同步到根工作区 `.codex/skills` 生成副本。
- 当前阻断：无。
- 下一步：后续 M2-B/C/D/E 按该规则执行；M2 完整验收后，再按需统一整理 PRD。
- 最近验证：`python3 scripts/sync_skills.py check --repo root --tool codex` PASS，输出 `skill outputs are up to date`。

### 2026-07-23 Next CHG Planning

- 已完成：按用户确认将“比特账号绑定信息需要让管理员知道什么、是否表格列和查看弹窗展示”归入 M2-B 窗口同步/详情后续设计，不在当前本机状态修复中继续追加页面。
- 已完成：更新 `delivery/milestones/M2-account-runtime.md`，明确比特账号绑定摘要可只读展示给有权限的管理员和当前用户；展示字段限于绑定状态、绑定时间、最近验证时间和脱敏主账号标识，不展示 Agent 凭据、本地端口、Token 或完整本机诊断信息。
- 已完成：创建 planned CHG `delivery/planned/CHG-20260723-026`，范围为 B2 窗口同步应用、恢复 Cloud 配置与授权闭环。
- 当前阻断：CHG-20260723-025 仍需 diff review、提交和正式收口后，才能激活 026。
- 下一步：对 025 做 diff review 和提交；随后将 026 从 planned 激活为 active 并执行 Task 1。
- 最近验证：本步骤为治理和计划更新，未修改 runtime 代码。

### 2026-07-23 Completion Review

- 已完成：补充 `evidence/completion-review.md`，记录最终 diff check、Go测试、前端测试、Cloud/Desktop构建、Desktop Rust检查和用户验收反馈。
- 已完成：确认 `CHG-20260723-025` 的用户可见结果、Cloud Web/Desktop边界、本机主账号确认语义、只读扫描Diff和后续B2规划均已收口。
- 当前阻断：无。
- 下一步：将本 CHG 移入 `delivery/completed`，从 `delivery/LEDGER.md` 移除；随后激活 `CHG-20260723-026`。
- 最近验证：`git diff --check` PASS；`go test ./internal/modules/profilebinding ./internal/modules/runtimebinding` PASS；`npm test -- localAgentStatus usersApi UsersPage profileBindings localAgentService session desktopRoleGuard` PASS；`npm run build:desktop` PASS；`npm run build:cloud` PASS；`cargo check` PASS（仅既有 warning）。
