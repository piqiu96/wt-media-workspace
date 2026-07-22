# CHG-20260723-022: M2-A2 确认式会话与Desktop环境可信

## 1. Basic Information

- Level: M
- Status: IN_PROGRESS
- Created: 2026-07-23
- Affected repositories: `wt-media-cloud`, `wt-media-agent`, `wt-media-desktop`, `wt-media-workspace`
- Current repository: `wt-media-workspace`
- Milestone: `delivery/milestones/M2-account-runtime.md#m2-a-用户权限会话与运行环境可信闭环`
- Implementation plan: `docs/superpowers/plans/2026-07-23-m2-account-runtime-detailed-implementation-plan.md#chg-m2-a2确认式会话与desktop环境可信`
- Inherited evidence: `delivery/completed/CHG-20260722-021/evidence/task-5-m2-a1-acceptance.md`

## 2. Change Goal

在 M2-A1 用户、分组、角色和权限模型基础上，补齐登录会话替换确认、Desktop/Local Agent/BitBrowser 本机身份可信检测和 `main_user_id` 确认绑定。完成后，用户只有在 Cloud 会话、Desktop、Local Agent 和 BitBrowser 主账号树可信时，才能继续发起后续 M2 本地敏感操作。

本 CHG 的用户可见纵向结果是：用户登录时可以明确处理旧会话；Desktop 可以显示当前本机环境是否可信；主账号身份来自真实 BitBrowser 扫描和用户确认；身份不匹配时本地敏感入口被阻止。

## 3. Current Proven Facts

- M2-A1 已完成自增UID、三角色、运营分组、游戏交集权限、用户管理Web和真实MySQL/Web验收；
- Cloud 已有基础会话、Local Agent binding ticket、Agent node、Profile身份字段和部分Profile身份错误阻断；
- Desktop 和 Agent 已有本地Agent、BitBrowser扫描、Profile扫描和状态页基础；
- M2 Milestone 已确认：M2-A 只验证身份，不应用 Profile 同步结果。

## 4. Remaining Gap

- 登录发现旧会话时，目前没有确认式替换流程；
- 会话替换后旧 Web、Desktop、Agent 是否停止新敏感操作缺少统一验证；
- Desktop 工作台/环境状态未形成 Cloud、Local Agent、BitBrowser 和主账号匹配的可信展示；
- `main_user_id` 绑定需要来自真实BitBrowser身份扫描和用户确认，不能手填；
- 身份扫描需要验证所有 `main_user_id` 一致且 `profile_user_id` 完整，但不能创建或更新正式Profile；
- M2本地敏感入口需要统一检查环境可信状态。

## 5. Ordered Tasks

### Task 1：会话替换确认

- 审计 Cloud 当前登录、会话、绑定 ticket 和 Agent node 实现；
- 增加“存在旧会话，需要确认替换”的登录响应或预检；
- 用户确认后再替换旧会话；
- 替换后旧会话不能继续访问敏感入口；
- 记录脱敏审计。

### Task 2：Desktop环境状态投影

- 审计 Desktop 当前环境状态页和 Local Agent 状态接口；
- 在 Desktop 显示 Cloud登录状态、Local Agent状态、BitBrowser可用性、`main_user_id`绑定状态和身份匹配结果；
- Web Cloud页面不直接操作本机，只提示需要Desktop。

### Task 3：BitBrowser主账号身份扫描

- Agent同步读取真实BitBrowser Profile身份；
- Cloud只接收身份扫描结果用于验证主账号一致性和 `profile_user_id` 完整性；
- 用户确认后绑定 `main_user_id`；
- 不应用Profile同步结果，不创建、不更新正式Profile。

### Task 4：本地敏感入口阻断

- 定义并接入 M2 本地敏感入口的统一可信检查；
- `main_user_id` 不匹配、多个主账号、身份字段缺失、Agent不可用或BitBrowser不可用时阻断；
- 阻断结果在页面可见且不产生外部副作用。

### Task 5：真实验收

- 使用真实 Cloud、Desktop、Local Agent 和 BitBrowser 验证；
- 覆盖登录旧会话确认/取消、Desktop状态展示、身份绑定、不匹配阻断；
- Evidence 记录脱敏环境、操作、期望、实际结果和 PASS/FAIL。

## 6. Acceptance

### 用户验收

- 用户发现已有会话时，可以取消替换或确认替换；
- 取消替换不影响旧会话；
- 确认替换后旧 Web、Desktop 和 Agent 不能继续发起新敏感操作；
- Desktop 能解释当前电脑是否可执行、为什么不可执行以及如何恢复；
- 用户只能通过真实BitBrowser身份扫描确认绑定 `main_user_id`。

### 系统验收

- 身份扫描只验证 `main_user_id` 一致和 `profile_user_id` 完整；
- 绑定结果持久化到Cloud；
- 本地敏感入口统一调用可信检查；
- 阻断时零外部副作用；
- 审计不记录密码、Cookie、代理密码、token或验证码。

### 真实依赖验收

- 使用真实MySQL、Cloud、Desktop、Local Agent和BitBrowser；
- Mock只覆盖确定性逻辑，不能替代真实环境退出条件；
- Evidence 不保存真实敏感凭据。

## 7. Explicitly Not Doing

- 不实现 M2-B Profile正式同步、Diff应用、Profile生命周期或账号检查；
- 不实现 M2-C 代理导入、检测、写入或读回；
- 不实现 M2-D Cookie写入、读取、接码、人工验证码或上号批次；
- 不实现 M2-E 本机执行抽屉、互斥恢复和综合验收；
- 不应用Profile同步结果；
- 不创建或更新正式 `browser_profile`；
- 不检测FFmpeg、本地业务目录、发布或互动能力；
- 不通过手填 `main_user_id` 完成绑定。

## 8. Checkpoint

- Completed: Start Gate evidence 已记录；Task 1 会话替换确认已完成；Task 2 Desktop环境状态投影已完成；Task 3 BitBrowser主账号身份确认已完成；Task 4 本地敏感入口阻断已完成；Task 5 自动验证与真实 MySQL + Cloud API 综合验收已完成；用户 smoke review 发现并修复 Desktop 环境状态页不应展示“当前任务/待回传结果”、顶部“退出”必须真实调用 Cloud logout。Agent `/api/v1/status` 上报运行环境事实，Desktop状态页展示Cloud登录、Agent、BitBrowser、主账号和可执行结论；Cloud 新增 A2-only `confirm-main-identity` API，只绑定/验证 `main_user_id`，不应用 Profile Diff；Profile 本地敏感入口在创建 task 前统一校验 Cloud用户、Desktop节点、会话、BitBrowser状态和 `main_user_id` 匹配。
- Current: M2-A 用户可见验收回修已完成代码修正和证据补充。用户反馈“用户管理功能为空白页”，复核发现 Cloud-only `/users` 路由被公共侧边栏暴露到 Desktop 入口；同时本地启动曾存在 Cloud Web 代理目标与 Cloud API 端口不一致，导致当前环境无法按用户实际入口验收。已修复 Desktop 菜单隐藏 `/users`；Cloud Web `5173`、Desktop Web `5174`、Cloud API `18080` 均可访问；Cloud API 登录后 `/api/v1/users` 返回用户列表。
- Next: 用户从 Cloud Web `http://127.0.0.1:5173/users` 进行人工验收；通过后再关闭 A2，并恢复执行计划中的 M2-B1。
- Blockers: 无。
- Recent verification: `go test ./internal/modules/runtimebinding ./internal/modules/profilebinding ./internal/modules/profileguard ./internal/modules/identity ./internal/app` PASS；Cloud Web `npm run test` PASS；Agent `python3 -m unittest tests.test_app tests.test_runtime_environment tests.test_local_state` PASS；Desktop `cargo test` PASS；真实 MySQL + Cloud API 会话替换 PASS；Web 登录页观察到替换确认弹窗并确认进入 Dashboard；真实 MySQL + Cloud API `confirm-main-identity` PASS，`users.bit_main_user_id` 已绑定且 `browser_profiles` 对验收 Profile 行数为 0；真实 MySQL + Cloud API 本地敏感入口阻断 PASS，缺少 `node_id` 与 BitBrowser不可用均不创建 task，可信节点只创建一个 task 且 `node_id` 不进入 payload；真实 MySQL + Cloud API 综合验收库 `wt_media_m2_a2_task5_acceptance` PASS；用户 smoke review 发现 Desktop 环境状态页不应展示“当前任务/待回传结果”，已移除并 rerun Cloud Web `npm run test` PASS；用户 smoke review 发现顶部退出仅跳转未注销，已改为调用 `POST /api/v1/auth/logout`，真实 Cloud API 验证 logout 后同 cookie `/auth/me` 返回 401 / `errcode=11001`；用户 smoke review 发现用户管理空白页，已修复 Desktop 误显示 Cloud-only `/users` 菜单，Cloud API `/api/v1/users` 登录后返回用户列表，Cloud Web `5173` 与 Desktop Web `5174` 均可访问，详见 `evidence/task-5-m2-a2-acceptance.md`。

## 9. Evidence Requirements

- `evidence/governance-start-gate.md`；
- `evidence/task-1-session-replacement.md`；
- `evidence/task-2-desktop-environment-status.md`；
- `evidence/task-3-bitbrowser-main-identity.md`；
- `evidence/task-4-sensitive-entry-guard.md`；
- `evidence/task-5-m2-a2-acceptance.md`。

## 10. Pending Questions

### Q-01：A2主账号确认是否新增 identity-only API？

当前 `profilebinding.ConfirmScan` 会同时绑定 `main_user_id` 并应用 Profile 同步结果。A2 明确不允许创建或更新正式 `browser_profile`。

推荐决策：新增 A2-only 确认 API，只绑定/验证 `main_user_id`，Profile Diff 应用保留给 M2-B。

Status: RESOLVED. User confirmed the recommended decision. Implemented as `POST /api/v1/bit-browser/profile-scans/:scan_id/confirm-main-identity`; evidence recorded in `evidence/task-3-bitbrowser-main-identity.md`.
