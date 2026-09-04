# Task 1 证据：共享互斥（Profile 级锁）验证与契约

日期：2026-08-05
CHG：CHG-20260805-032（M2-B 社媒账号收口）
状态：**验证通过——互斥机制已存在并已生效，非从零实现**

## 结论

"同一 Profile 同时仅一个本地敏感操作"的 Profile 级互斥**已由 M2-A 的 profileguard 机制完整实现并在账号检查路径生效**。Task 1 为验证 + 固化契约，供 CHG-C（代理收口）继承复用。

## 机制链路（已验证）

```
Cloud: StartLocalAccountCheck 创建敏感任务（authorized）
  → Desktop Tauri local_agent_account_check：
      1. POST /api/v1/local-agent/sensitive-tasks/{task_id}/preflight
         → profileguard.AcquirePermit（互斥判定，见下）
      2. 执行 Agent POST /api/v1/account-check（真实读 Cookie/平台身份）
      3. finish_sensitive_permit（completed / result_uncertain）
```

## 互斥判定（Cloud profileguard/store_mysql.go AcquirePermit）

- `SELECT ... FROM browser_profiles WHERE id = ? FOR UPDATE`（行锁）
- 校验任务授权、归属、运行时新鲜（node online / bitbrowser normal / presence visible）
- 查该 profile 最近 permit：
  - `review_required` → `OutcomeReviewRequired`（阻断）
  - `active` 未过期 → `OutcomeWaiting`（**互斥：另一操作占用同一 Profile**）
  - `active` 已过期 → 标记 `review_required`
  - 否则授予新 permit（INSERT，任务转 running）

## Agent 侧守卫

- `core/profile_guard.py`：`guarded` 上下文（preflight → execute → finish），供执行器复用
- `cloud_agent_client.py`：`preflight_sensitive_task` / `finish_sensitive_permit`
- 账号检查同步路径（Tauri 封装）已强制 preflight/finish，互斥在 Cloud 层兜底

## 契约（CHG-C 代理收口继承）

代理 mutation（分配/更换/解绑）**当前走异步 `proxy_mutation_task` 轮询路径，未走 permit**。CHG-C 需将代理写回接入同一 preflight/finish 互斥路径（新增 Agent `/proxy-mutation` 同步端点 + Cloud 同步调用 + preflight），实现"同一 Profile 同时仅一个本地敏感操作"对代理也生效。

## 测试/回归

- profileguard：service_test.go + store_mysql_test.go + routes_test.go（AcquirePermit 互斥/Waiting/Review 已覆盖）
- 本 Task 未改代码，属验证；后续账号检查/代理写回变更时保持该互斥不破

## 待办

- 无代码改动。CHG-A 进入 Task 2（账号台账收尾）。
