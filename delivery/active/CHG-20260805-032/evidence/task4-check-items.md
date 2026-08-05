# Task 4 证据：账号检查 8 项明细（check_items）

日期：2026-08-06
CHG：CHG-20260805-032（M2-B 社媒账号收口）
状态：完成（7/8 判定为骨架，真实样本对齐留待）

## 目标

账号检查结果逐项展示 8 项明细（PRD 3.3.10），7/8（验证码/账号限制）先做判定骨架，真实受限样本到位后对齐。

## 语义澄清（用户确认）

- **检查项 7「需验证码/安全验证」** = 临时验证门禁（verification_needed）：账号能登录，但执行操作时平台弹验证码，通过后继续，非永久限制
- **检查项 8「账号限制」** = 受限状态（restricted）：比封号广——封号/限流降权/风控标记
- 7/8 检测需真实受限账号样本 → 用户暂时无法提供，当前标记 na

## 设计

- `AccountCheckItem {key, label, status(pass|fail|skip|na), message}`
- **Agent** 返回 5-8 项（5 平台登录、6 账号一致真实判定；7/8 na 骨架）
- **Cloud `ApplyLocalAccountCheckResult`** 用 `mergeCheckItems` 合成 8 项：1/2（身份匹配/窗口存在，能执行即 pass）+ 3/4（代理 na，延后 M2-C）+ 5-8（Agent 返回）
- **持久化**：media_accounts 加 `check_items JSON`（迁移 020），Create/Update/scan 读写
- **前端**：账号详情抽屉展示 8 项明细（通过/未通过/不适用 + 说明）

## 链路（Agent → Tauri → 前端 → Cloud）

- Agent `account_check_response` 附带 `check_items`
- Desktop Tauri `AccountCheckResult` 加 `check_items` 透传
- 前端 `runSingleAccountCheck` → `submitCheckResult` 传 `check_items`
- Cloud `check/result` 路由接收 → Apply 合成存储 → 账号详情读取展示

## 提交

- Agent `7ad508c`、Desktop `1aae1b1`、Cloud `deaa90e`

## 验证

- Agent 测试通过；Cloud 全绿；Web 36（更新 submitCheckResult 断言）；Desktop cargo check
- 迁移 020 应用成功（21 total）

## 待办

- **7/8 真实样本对齐**：用户提供受限账号样本后，在 Agent `_build_account_check_items` 补 7/8 的页面/响应特征判定（如平台返回"请完成安全验证"→verification_needed；"账号被封禁/受限"→restricted）
- Task 6 端到端验收（重建环境 + 真实平台账号跑完整检查链路）
