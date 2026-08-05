# CHG-20260805-032：M2-B 社媒账号收口

> 日期：2026-08-05
> 状态：ACTIVE
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`
> 当前仓库：`wt-media-workspace`
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`

## 0. 继承与关联

- 前置已完成：M2-A、M2-B 浏览器窗口收口（CHG-20260725-031 DONE，见 `delivery/completed/CHG-20260725-031/`）
- 本 CHG 是 M2-B 的**社媒账号切片**，与 M2-C 代理收口（CHG-20260805-033，PLANNED）串行推进
- 共享前置：Profile 级互斥（E1/M2-E 切片）在本 CHG Task 1 实现，CHG-C 继承复用

## 1. 用户可见目标

普通运营管理自己的媒体账号台账，对已绑定窗口的账号执行单项/批量账号检查，**真实回填平台身份**（UID、昵称、头像、登录状态、最近检查时间），并在检查结果中看到逐项明细。

## 2. 当前背景（继承已完成）

- 账号 CRUD、标签增删/筛选、绑定/解绑/换绑 Profile、分页/搜索/筛选：已实现
- 单项账号检查（Bilibili 控制流）：已实现（StartLocalAccountCheck → Agent account_check → ApplyLocalAccountCheckResult 回填）
- 批量检查控制流 + 失败重试 + 结果面板：已实现（B7）
- 真实回填字段链路（platform_account_id/name/avatar_url/login_status/last_checked_at）：代码就绪
- 敏感任务创建（Profile 敏感操作锁雏形）：已有 `sensitive_browser_tasks`/`sensitive_profile_permits`

## 3. 本 CHG 范围

### 包含

- **共享互斥（E1/M2-E 切片）**：同一 Profile 同时仅一个本地敏感操作（Cloud acquire/release + Agent 守卫），账号检查接入；供 CHG-C 继承
- 账号台账收尾：`business_status` 补 draft=待识别/abnormal=异常（DB CHECK + 服务校验 + 页面统计筛选）；账号详情 Cookie 操作入口（**查看/导出当前 Cookie + 从 Profile 读真实 Cookie**，读回走 Agent 同步）
- 平台身份真实识别：抖音/百家号 Cookie→UID；Bilibili/抖音/百家号昵称与头像真实回填
- 账号检查 8 项完整化：**7/8（验证码/账号限制）本次实现**（需真实受限账号样本）；检查结果 8 项明细逐项展示
- **账号组（可保存筛选，PRD 3.3.6）**：account_groups 模型 + CRUD + 保存/应用筛选；发布/互动（M6/M8）依赖它筛目标账号
- 端到端验收：真实平台账号（Bilibili 单项 → 抖音/百家号 → 批量真实回填）+ 受限账号验证 7/8

### 不包含（延后/后续）

- 检查项 3/4（代理正常/到期）→ 延后 M2-C（CHG-C 完成后接入）
- CK **写入**/上号（CK 导入/接码/人工验证码）→ M2-D；本 CHG 只做查看/导出/读回
- 代理管理、配额、分配 → M2-C（CHG-C）
- 标签归属用户（前端传 user_id）→ 随标签交互补正（PRD 3.3.6）

## 4. 关键规则

- 检查回填必须真实读回，不能"任务创建=成功"；`result_uncertain` 不自动重查
- 同一 Profile 同时只能一个本地敏感操作（互斥）
- Cookie 为敏感数据，回填/导出遵守 `secret_policy`（不进日志/错误/Evidence）
- 页面、Cloud 镜像、Agent 读回、平台实际状态一致

## 5. 执行任务

### Task 1：共享互斥（E1/M2-E 切片）
- 复用 `sensitive_browser_tasks`/`sensitive_profile_permits`，扩展为通用 Profile 级锁（Cloud acquire/release + Agent 单操作守卫）
- 账号检查接入互斥
- 交付互斥契约，CHG-C 继承复用

### Task 2：账号台账收尾
- B3-2 `business_status` 补 draft=待识别/abnormal=异常（DB CHECK + 服务校验 + 页面统计/筛选）
- B3-1 Cookie 操作入口：账号详情「查看/导出当前 Cookie」+「从 Profile 读真实 Cookie」（Agent 同步读回）；写入/上号归 M2-D

### Task 3：平台身份真实识别
- B4-2 抖音/百家号 Cookie→UID（`_identify_platform_account` 补齐，需各平台 Cookie 样本）
- B4-3 昵称/头像真实回填（Bilibili/抖音/百家号）

### Task 4：账号检查 8 项完整化
- 已实现 1/2/5/6（身份/Profile存在/登录/匹配）
- 7/8 验证码/账号限制（跨平台，需真实受限账号样本）——本次实现
- 3/4 代理项 → 延后 M2-C（接代理收口后回接）
- B4-6 检查结果 8 项明细 UI（逐项展示，未实现/延后项标注状态）

### Task 5：账号组（可保存筛选，PRD 3.3.6）
- `account_groups` 模型 + CRUD + 保存/应用筛选条件；发布/互动（M6/M8）依赖

### Task 6：端到端验收与收口
- 真实平台账号：Bilibili 单项 → 抖音/百家号 → 批量真实回填；受限账号验证 7/8
- 更新 M2-B 账号收口矩阵，判定收口 DONE 或创建修复 CHG

## 6. 验收标准

- 单项/批量检查对真实已登录平台账号真实回填 UID/昵称/头像/登录状态/最近检查时间
- 同一 Profile 并发两个本地操作 → 第二个被拒绝/排队
- Cookie 查看/导出入口可用且遵守敏感数据规则
- `business_status` 枚举与 milestone 对齐
- 检查结果展示 8 项明细
- 页面、Cloud 镜像、Agent 读回、平台实际状态一致

## 7. Evidence 要求

`evidence/` 提供：互斥契约、平台识别（Cookie→UID 映射）、昵称/头像回填、8 项明细 UI、端到端验收（真实账号）、测试与构建记录。

## 8. Checkpoint

- Completed：
  - CHG 已创建；Start Gate 完成（继承窗口收口 + B7 检查控制流）；
  - **Task 1 共享互斥——验证通过，机制已存在**：Profile 级互斥由 M2-A profileguard 完整实现并在账号检查路径生效（Cloud AcquirePermit 行锁 + OutcomeWaiting 互斥 + Tauri preflight→check→finish 闭环）。Task 1 为验证 + 固化契约，见 `evidence/task1-profile-mutex.md`。CHG-C 需将代理写回接入同一 permit 路径。
  - **Task 2 账号台账收尾——完成**：B3-2 business_status 补 draft/abnormal（语义 draft=待识别、abnormal=异常，迁移 018 + 服务状态流转 + 前端）；B3-1 Cookie 操作（查看/导出 + 从 Profile 同步读回，走 Profile 级互斥，写入/上号归 M2-D）。见 `evidence/task2-ledger-cookie.md`。
- Current：Task 3 平台身份识别（抖音/百家号 Cookie→UID + 昵称/头像）待实施。
- Next：Task 3 平台识别 → Task 4 检查 8 项（7/8 + 明细 UI）→ Task 5 账号组 → Task 6 端到端验收。
- Blockers：平台识别需真实 Cookie 样本——用户已确认提供百家号（登录 BitBrowser 待提取）与 B站 登录链接。
- Recent verification：窗口收口 DONE（CHG-031）；Agent 66 tests、Web 36 tests 保持；互斥已覆盖（profileguard tests）。

## 9. Pending Questions

None.
