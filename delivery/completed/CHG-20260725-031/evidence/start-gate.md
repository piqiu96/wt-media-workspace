# CHG-20260725-031 Start Gate

日期：2026-07-25

## 核对结果

- Active CHG：`CHG-20260725-031`
- `CURRENT_CONTEXT`：指向 `CHG-20260725-031`
- `delivery/LEDGER.md`：仅列出 `CHG-20260725-031`
- 关联 Milestone：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`
- 影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`、`wt-media-workspace`

## 当前事实

- B6 已完成单个账号“检查/同步账号信息”：
  - Cloud `StartLocalAccountCheck` 创建本地敏感操作授权；
  - Desktop Tauri/Rust 调 Cloud preflight；
  - Local Agent `/api/v1/account-check` 打开 BitBrowser Profile 并读取平台身份；
  - Cloud `ApplyLocalAccountCheckResult` 回填平台 UID、昵称、头像、登录状态和最近检查时间。
- 账号页已有多选能力，用于批量标签操作。
- 账号页已有 `selectedAccountIds`、`canCheckAccount`、`executableText`、`profileForAccount`、`refreshRuntimeWithCooldown` 和单项 `checkDetailAccount` 可复用。
- 现有 Cloud 侧没有账号检查专用 batch/item 模型。
- M2-B milestone 要求“单个/批量账号检查真实回填平台身份、头像、登录状态和最近检查时间”。

## 批量模型判断

首版 B7 采用 Desktop 页面串行逐项同步执行，不新增 Cloud 通用 task 或账号检查 batch/item。

原因：

- 每个账号检查都可以复用单项链路，逐项完成 Cloud preflight、Local Agent 检查和 Cloud 回填；
- 逐项串行可以避免同一 Profile 或账号并发本地敏感操作；
- 页面内批量结果可以明确展示成功、失败、跳过和失败项重试；
- 不会出现“批量任务已创建”冒充检查成功。

后续如果 M2-D 上号批次需要持久化恢复，再建设专用 batch/item，不在 B7 中提前抽象。

## 缺口

- Desktop 账号页缺少批量检查/同步入口。
- 选择多个账号后，当前只支持批量标签，不支持批量检查。
- 需要逐项跳过不可执行账号并展示原因。
- 需要逐项串行调用单个检查链路并回填 Cloud。
- 需要展示批量统计和逐项结果。
- 需要失败项精确重试。
- Cloud Web 不能出现批量检查入口。

## 文件映射

- Web 账号页：
  - `wt-media-cloud/web/src/modules/accounts/pages/AccountsPage.vue`
- Web API 客户端：
  - `wt-media-cloud/web/src/shared/api/mediaAccounts.js`
- Desktop Local Agent service：
  - `wt-media-cloud/web/src/apps/desktop/features/local-agent/service.js`
- Cloud 单项检查服务：
  - `wt-media-cloud/internal/modules/mediaaccount/service.go`
  - `wt-media-cloud/internal/modules/mediaaccount/routes.go`
- Desktop Rust 单项检查命令：
  - `wt-media-desktop/src-tauri/src/main.rs`
- Local Agent 单项检查：
  - `wt-media-agent/src/wt_media_agent/local_api/server.py`

## 测试计划

- Web：`npm test` 覆盖批量检查入口、Cloud/Desktop 边界、失败项重试文案和不创建批量 Cloud task。
- Web build：`npm run build`。
- Cloud：`go test ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/profileguard` 确认单项检查授权与绑定规则未回归。
- Agent/Desktop：本轮不修改 Agent 和 Desktop Rust，继承 B6/B5 测试；如实现中触及 Tauri 或 Agent 再运行对应测试。

## 风险

- 页面内串行批量检查不是持久化 batch；关闭页面会丢失本次批量过程视图，但每项已经回填的 Cloud 结果不会丢失。
- 如果 Local Agent 调用返回网络级错误，当前项标记失败或待确认，不自动重试。
- 真实平台身份读取仍依赖 BitBrowser 与平台登录态，自动测试只能覆盖确定性控制流，真实依赖需人工验收。
