# CHG-20260722-021: M2-A 用户权限与可信验收收口

## 1. Basic Information

- Level: M
- Status: IN_PROGRESS
- Created: 2026-07-22
- Affected repositories: `wt-media-cloud`, `wt-media-agent`, `wt-media-workspace`
- Current repository: `wt-media-workspace`
- Milestone: `delivery/milestones/M2-account-runtime.md#m2-a`
- Inherited evidence: `delivery/completed/CHG-20260721-020/evidence/governance-scope-audit.md`

## 2. Change Goal

证明管理员、运营人员和技术人员能够通过真实 Web/API 完成 M2-A 权限与会话链路，旧 Agent 会话失效后不能继续领取任务，BitBrowser 首次绑定与重绑产生正确脱敏审计，并将 M2-A 从“自动化基础已存在”收口为可人工验收的业务闭环。

本 CHG 的用户可见纵向结果是：不同角色登录后只看到并操作授权范围，权限变更与停用即时生效，越权被明确拒绝，管理员能查看关键审计结果。

## 3. Current Proven Facts

- Cloud、Agent、Web、Desktop 与 Workspace 自动化门禁可复验；
- 媒体账号跨游戏读取已有 403 回归测试；
- 失效 Agent 会话进入 draining/replaced 并停止继续 claim；
- BitBrowser 首次绑定和同身份重绑已有脱敏审计动作；
- 以上均为自动化或局部技术事实，尚未完成三角色真实 UI/API 和绑定人工验收。

## 4. Remaining Gap

- 缺少管理员、运营人员和技术人员在真实 MySQL/Cloud Web 下的完整权限矩阵；
- 缺少 401 登录失效跳转、403 越权反馈、角色/游戏范围变更和停用即时生效的页面验收；
- 缺少真实 Local Agent 会话替换后停止领取新任务的集成证据；
- 缺少 BitBrowser 主账号首次绑定/重绑及审计可见性的人工证据；
- 若验收暴露 M2-A 范围内缺陷，需要最小修复和回归；不得借机实现 M2-B～E。

## 5. Ordered Tasks

### Task 1：验收环境与角色数据

- 启动真实 MySQL、Cloud、Web 和 Local Agent；
- 创建非敏感的管理员、运营人员、技术人员及至少两个游戏范围；
- 记录脱敏 ID、运行端口、健康状态和清理方法；
- 验证任何失败的环境前置不会产生业务修改。

### Task 2：三角色 Web/API 权限矩阵

- 验证登录、页面菜单、用户管理、媒体账号、Profile 和代理入口的角色边界；
- 验证同角色跨游戏范围查询与操作返回 403 且无数据泄漏；
- 验证未登录或会话失效返回 401，Web 跳转登录并清除失效状态；
- 对发现的 M2-A 缺陷先写失败测试，再做最小修复。

### Task 3：权限变更、密码与停用

- 管理员修改角色和游戏范围，验证下一次请求即时使用新权限；
- 验证管理员重置密码、用户修改密码和旧会话失效；
- 停用用户后验证 Web/API 和 Agent 都不能继续使用旧会话；
- 记录正向与反向结果。

### Task 4：Local Agent 会话替换

- 使用受控测试节点建立 Local Agent 会话并领取可安全执行的测试任务；
- 触发同用户新登录或会话替换；
- 验证旧节点停止领取新任务，在途敏感任务按状态完成、失败或进入结果不确定，而不是盲目重试；
- 验证 Cloud 节点状态和 Agent 本地行为一致。

### Task 5：BitBrowser 绑定与审计

- 使用用户授权的测试 BitBrowser 主账号执行首次绑定和同身份重绑；
- 验证身份不匹配被阻止且不更新 Cloud 正式事实；
- 验证审计记录区分 bind/rebind，只包含允许的脱敏摘要；
- 不修改任何非测试 Profile。

### Task 6：M2-A 综合回归与收口

- 运行 Cloud、Agent、Web、Workspace 自动化与治理校验；
- 汇总三角色、会话替换、绑定审计的人工 Evidence；
- 对照 Milestone M2-A 的每个成功事实逐项判定；
- 仅在全部通过后关闭本 CHG，并建议创建 M2-B CHG；不自动执行 M2-B。

## 6. Acceptance

### 用户验收

- 三类角色登录后看到并操作各自授权内容；
- 越权和失效会话有明确且真实的 401/403 页面结果；
- 管理员修改权限、密码或停用用户后立即生效；
- 管理员能查看 BitBrowser 绑定/重绑审计结果。

### 系统验收

- API 与 UI 权限一致，跨游戏访问无数据泄漏；
- 旧 Local Agent 会话不再领取新任务；
- 在途敏感任务不产生重复副作用或假成功；
- 审计事件、节点状态、用户状态和会话状态正确持久化到真实 MySQL。

### 真实依赖验收

- 使用真实 MySQL、运行中的 Cloud/Web/Agent 和用户授权的 BitBrowser 测试身份；
- Evidence 只记录脱敏标识、命令、期望、实际结果、PASS/FAIL 和提交引用；
- 自动测试不能代替三角色与真实绑定人工验收。

## 7. Explicitly Not Doing

- 不实现 M2-B Profile 生命周期、Diff 双向处理或账号检查；
- 不实现 M2-C 代理导入、配额、分配和真实写入；
- 不实现 M2-D Cookie 写入、读取或开户；
- 不实现 M2-E 打包 Sidecar 和综合恢复；
- 不修改非测试 BitBrowser Profile；
- 不在 Evidence、日志、测试或仓库保存真实密码、Cookie、代理凭据、token 或验证码；
- 不因自动测试通过而跳过人工验收。

## 8. Checkpoint

- Completed: CHG 已按 Milestone M2-A 和 CHG-020 范围审计建立；治理上下文待最终同步验证。
- Current: 尚未开始运行时代码修改或人工验收。
- Next: 执行 Task 1，建立脱敏验收环境和三角色测试数据。
- Blockers: 真实验收需要用户授权的测试身份与 BitBrowser 绑定操作；开始 Task 1 时确认可用性。
- Recent verification: CHG-020 审计确认自动化基础可复验，但 M2-A 人工验收尚未证明。

## 9. Evidence Requirements

- `evidence/governance-start-gate.md`；
- `evidence/task-1-environment.md`；
- `evidence/task-2-role-matrix.md`；
- `evidence/task-3-user-lifecycle.md`；
- `evidence/task-4-agent-session.md`；
- `evidence/task-5-binding-audit.md`；
- `evidence/task-6-m2-a-acceptance.md`。

## 10. Pending Questions

None.
