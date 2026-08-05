# Task 2 证据：账号台账收尾（business_status + Cookie 操作）

日期：2026-08-05
CHG：CHG-20260805-032（M2-B 社媒账号收口）
状态：完成

## B3-2：business_status 对齐 milestone 枚举

- **语义（用户确认）**：draft=待识别（创建后未完成真实识别）；abnormal=异常（检查发现问题需处理）
- **迁移** `20260805_018_media_accounts_business_status.sql`：CHECK 约束扩为 draft/enabled/disabled/abnormal/retired（已应用，19 total）
- **服务**：
  - 新增 `BusinessDraft`/`BusinessAbnormal` 常量 + `validBusinessStatus` 支持 5 值
  - `CreateAccount` 默认 `draft`（待识别）
  - 检查守卫/BindProfile/UnbindProfile 允许 draft（draft 需绑定窗口并检查后升级）
  - `ApplyLocalAccountCheckResult` 状态推进：识别成功+登录正常→enabled；登录异常（verification_needed/expired/restricted/account_mismatch/environment_error）→abnormal；未识别（not_logged_in/unknown）保持
- **前端**：统计卡（待识别/异常）、筛选、状态下拉、BusinessStatus 列、executableText（待识别/异常文案）、canCheckAccount 允许 draft
- 测试：mediaaccount 测试断言更新（create 默认 draft），Cloud 全通过

## B3-1：账号 Cookie 操作（查看/导出 + 从 Profile 同步读回）

- **边界（用户确认）**：含查看/导出当前 Cookie + 从 Profile 读真实 Cookie（同步）；写入/上号归 M2-D
- **同步读回垂直链路**（镜像账号检查，走 Profile 级互斥）：
  - Agent `POST /api/v1/cookie-read`（`cookie_read_response`）：打开 Profile → 读真实 Cookie → 返回 cookies
  - Desktop Tauri `local_agent_cookie_read`：preflight（互斥）→ Agent cookie-read → finish（completed/result_uncertain）
  - Cloud `StartCookieRead`（创建 cookie_read 敏感任务）+ `ApplyCookieReadResult`（更新 active_cookie/cookie_status/active_cookie_updated_at）+ 路由 `/cookies/read-sync` + `/cookies/read-sync/result`
  - 前端：详情抽屉「查看/导出 Cookie」「从 Profile 读真实 Cookie」按钮 + Cookie 对话框（复制 Active/原始）
- 原异步 `POST /cookies/read`（`cookie_read_task`）保留为 legacy，不纳入本链路

## 提交

- Cloud `f2f5931`（B3-2）、`b2ffad6`（B3-1）
- Agent `3796498`（cookie-read 端点）
- Desktop `b84346f`（Tauri 命令）

## 测试/回归

- Cloud mediaaccount go test 通过；完整 Cloud `go test ./internal/...` 全绿
- Web 36 tests；Desktop `cargo check` PASS
- Agent 69 tests（新增 cookie-read 3 tests）

## 待办

- Task 2 完成，进入 Task 3（平台识别：抖音/百家号 UID + 昵称/头像，需 Cookie 样本）。
