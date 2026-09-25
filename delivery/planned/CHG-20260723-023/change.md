# CHG-20260723-023: M2-B1 浏览器窗口扫描与Diff基线

## 1. Basic Information

- Level: M
- Status: SUPERSEDED
- Created: 2026-07-23
- Affected repositories: `wt-media-cloud`, `wt-media-agent`, `wt-media-desktop`, `wt-media-workspace`
- Current repository: `wt-media-workspace`
- Milestone: `delivery/milestones/M2-account-runtime.md#m2-b-浏览器窗口与媒体账号真实闭环`
- Inherited evidence:
  - `delivery/completed/CHG-20260723-022/evidence/task-5-m2-a2-acceptance.md`

## 2. Change Goal

在 M2-A2 本机身份可信基础上，完成 M2-B 的第一个最小纵向闭环：用户在 Desktop 端触发真实 BitBrowser Profile 扫描，Cloud 只生成可审核的窗口 Diff，用户可以确认同步窗口到 Cloud 镜像或取消变更。

本 CHG 的用户可见结果是：运营能在“浏览器用户/浏览器窗口”页面看到真实 BitBrowser 扫描结果、Diff 分组和同步结果；确认前不修改正式窗口镜像，确认后 Cloud `browser_profiles` 与本次扫描结果一致。

## 3. Current Proven Facts

- M2-A2 已完成 Cloud 会话、Desktop/Local Agent/BitBrowser 主账号可信和本地敏感入口阻断；
- Local Agent 已能同步读取真实 BitBrowser Profile 列表和身份字段；
- Cloud 已有 `profile_sync_scans`、`browser_profiles`、`SubmitScan`、`ConfirmScan`、`ConfirmMainIdentity` 基础；
- Web Profile 页面已有扫描抽屉、Diff 展示、仅确认主账号和确认同步窗口入口；
- 用户已确认：M2-B 才允许应用 Profile Diff，M2-A 不应用 Profile 同步结果。

## 4. Current Gap

- 当前 Profile 页面需要按 M2-B 口径重新审计：扫描 payload、Diff 分组、确认同步、取消变更和错误提示不能混淆 A2 主账号确认；
- Desktop dev 入口、Local Agent 直接扫描和 Cloud 提交之间需要验证真实链路；
- 确认前必须零正式 `browser_profiles` 副作用；
- 确认同步后必须能在 Cloud 镜像读回；
- 不能把“任务创建”当作扫描成功；本 CHG 是短同步操作，不引入异步 task。

## 5. Ordered Tasks

### Task 1：Start Gate与当前实现审计

- 核对 `CURRENT_CONTEXT`、`LEDGER`、active CHG 和 M2-B milestone；
- 审计 Cloud Profile scan/diff/apply 实现；
- 审计 Local Agent BitBrowser scan response；
- 审计 Web Profile 页面扫描、Diff、确认同步和取消路径；
- 记录 gap evidence。

### Task 2：修复扫描与Diff页面基线

- 修复 Profile 页面现有语法/运行时问题；
- 保证 Desktop 端扫描使用 Local Agent 真实返回；
- 保证 Cloud 端提交 payload 只包含允许字段；
- 保证 Diff 分组和抽屉展示稳定；
- 保证 Cloud Web 非 Desktop 端提示不能扫描本机。

### Task 3：确认同步窗口到Cloud镜像

- 确认前：只保存 staged scan，不创建/更新正式 `browser_profiles`；
- 用户点击“确认同步窗口”后：应用新增、变更、缺失到 Cloud 镜像；
- `ConfirmMainIdentity` 继续只确认主账号，不应用 Profile；
- 取消变更不产生正式镜像副作用。

### Task 4：真实验收

- 使用真实 MySQL、Cloud、Desktop Web、Local Agent 和 BitBrowser 验证；
- 覆盖真实扫描、Diff 展示、确认前零副作用、确认后 Cloud 镜像读回；
- 覆盖非 Desktop 入口阻断或提示；
- Evidence 记录脱敏环境、操作、期望、实际结果和 PASS/FAIL。

## 6. Acceptance

### 用户验收

- 用户在 Desktop 的浏览器窗口页面点击扫描，可以看到真实 BitBrowser 窗口 Diff；
- 用户能区分“仅确认主账号”和“确认同步窗口”；
- 用户取消变更后，Cloud 正式窗口列表不变化；
- 用户确认同步后，Cloud 窗口列表出现/更新/标记缺失对应 Profile；
- Cloud Web 端不会伪装成本机扫描入口。

### 系统验收

- 扫描和 Diff 是同步短操作，不创建异步 task；
- `profile_sync_scans` 可记录 staged scan；
- `browser_profiles` 只在确认同步窗口后变化；
- 只保存允许字段，不保存 Cookie、代理密码、token 或验证码；
- 身份不匹配、多个主账号或 `profile_user_id` 缺失时拒绝扫描结果；
- API 返回统一 `errcode/message/data/logid`。

### 真实依赖验收

- 使用真实 MySQL、Cloud、Local Agent 和 BitBrowser；
- Mock 只能补充确定性单元测试，不能替代真实 BitBrowser scan evidence；
- Evidence 不保存真实敏感凭据。

## 7. Explicitly Not Doing

- 不实现 Profile 创建、编辑、打开、关闭、删除的真实 BitBrowser 生命周期；
- 不实现“恢复Cloud配置写回BitBrowser”；
- 不实现代理绑定、代理写入或代理读回；
- 不实现媒体账号绑定、账号检查或登录状态回填；
- 不实现 Cookie 写入、读取、接码、人工验证码或上号批次；
- 不新增通用任务中心；
- 不把 M2-B 全部塞进本 CHG。

## 8. Checkpoint

- Completed: CHG 已创建并关联 M2-B 闭环；M2-A2 已关闭为继承证据。
- Current: Task 1 Start Gate与当前实现审计待开始。
- Next: 使用 `executing-wt-media-change` 执行 Task 1，先记录现有扫描/Diff实现事实和差距，再进入最小修复。
- Blockers: 无。
- Recent verification: 继承 `CHG-20260723-022` 自动测试、真实 MySQL + Cloud API 和用户 smoke review 修复证据。

## 9. Evidence Requirements

- `evidence/governance-start-gate.md`；
- `evidence/task-1-current-scan-diff-audit.md`；
- `evidence/task-2-profile-scan-diff-ui.md`；
- `evidence/task-3-confirm-sync-cloud-mirror.md`；
- `evidence/task-4-m2-b1-acceptance.md`。

## 10. Pending Questions

None.
