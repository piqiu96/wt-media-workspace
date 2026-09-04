# CHG-20260805-033：M2-C 代理收口

> 日期：2026-08-05
> 状态：ACTIVE
> 所属 Milestone：M2-C 代理资源与窗口真实绑定闭环
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-C-代理资源与窗口真实绑定闭环`
> 当前仓库：`wt-media-workspace`
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`

## 0. 继承与关联

- 前置：M2-A、M2-B 窗口收口（CHG-031 DONE）、M2-B 账号收口（CHG-20260805-032，先行）、共享互斥（CHG-A Task 1 实现，本 CHG 继承复用）
- 本 CHG 与账号收口串行推进；CHG-20260805-032 已于 2026-09-04 验收完成，本 CHG 自该日激活。

## 1. 用户可见目标

普通运营管理代理台账（新增/批量导入/检测），将代理真实写入授权 Profile（分配/更换/解绑），写回 BitBrowser 后读回验证一致，并按统一配额（`max_profile_count`）获得推荐分配方案。

## 2. 当前背景（继承已完成）

- proxy_configs CRUD 后端、文本导入解析、TCP 连通性检测（同步 Cloud/同步 Agent/后台 Agent）：已实现
- `POST /proxies/:id/assign` 创建 `proxy_mutation_task`：已实现（校验归属/活跃/配额）
- Agent `ProxyMutationExecutor`：写入 BitBrowser + 扫描读回（已带 browserFingerPrint/proxyMethod 保留）：已实现
- ProxyPage：列表/筛选/详情/导入对话框/检测/状态/删除：已实现

## 3. 本 CHG 范围

### 包含

- 台账收尾：单个代理创建前端表单；导入预览**零副作用**（拆分 Parse/Import 端点）
- 配额模型：`proxy_platform_quotas` 迁移为统一 `max_profile_count`（DB 迁移 + CheckQuota 重构），页面展示已用/剩余
- 分配写回：ProxyPage 分配入口；Agent 同步写回端点（`/proxy-mutation`）；Cloud 同步 mutation 调用（复用互斥）
- 写回一致性：Cloud 写回 broker（mutation 结果更新 `browser_profiles`）、解绑、更换（先验新后释放旧）
- 推荐方案：推荐引擎（仅已启用/检测正常/未到期/有剩余配额）+ 推荐/人工调整/确认 UI
- 外部代理变化：扫描 Diff 中代理变化的处理（未知代理→待补充记录）
- 账号检查代理项：在代理闭环建立后实现检查项 3「窗口代理正常」和 4「代理到期/停用」，回填 M2-B 的 8 项检查明细
- 端到端验收：真实代理——分配写入→读回→更换→解绑全链路

### 不包含

- Cookie/上号/接码 → M2-D
- 代理刷新 URL（供应商 API）→ 待定

## 4. 关键规则

- 代理写入/更换/解绑后必须**读回验证一致**才更新正式关系与配额；失败不更新、不占配额
- 单代理检测/写入/更换/解绑为**同步调用 Agent**（非纯异步任务）
- 同一 Profile 同时只能一个本地敏感操作（复用共享互斥）
- 代理密码为敏感数据，遵守 `secret_policy`；预览阶段零副作用

## 5. 执行任务

### Task 1：台账收尾（零耦合）
- C1.1 单个代理创建前端表单
- C1.2 导入预览零副作用（拆分 Parse/Import 端点）

### Task 2：配额模型迁移
- C2.2 `proxy_platform_quotas` → 统一 `max_profile_count`（DB 迁移 + CheckQuota 重构）
- C2.3 页面展示统一最大配额；已用/剩余仅在 Task 3 读回并写入正式 `proxy_id` 关系后计算，禁止以地址猜测

### Task 3：分配写回链路
- C3.3 ProxyPage 分配入口
- C3.4 Agent 同步写回端点（`/proxy-mutation`）
- C3.5 Cloud 同步 mutation 调用（复用互斥）

### Task 4：写回一致性与生命周期
- C3.6 Cloud 写回 broker（mutation 结果更新 `browser_profiles`）
- C3.8 解绑、C3.9 更换（先验新后释放旧）

### Task 5：推荐方案
- C3.7 推荐引擎 + 推荐/人工调整/确认 UI

### Task 6：外部代理变化与收口
- C4 外部代理变化 Diff 处理
- 回接媒体账号检查项 3/4：基于已读回的 Profile—代理关系、代理检测状态、业务状态和过期时间生成真实结果
- 端到端验收（真实代理）→ 更新 M2-C 收口矩阵，判定 DONE 或修复

## 6. 验收标准

- 单个新增/批量导入/预览零副作用；配额统一 max_profile_count 且校验正确
- 分配/更换/解绑在 BitBrowser 读回一致后更新 Cloud 关系与配额；失败不更新不占配额
- 推荐仅选已启用/检测正常/未到期/有剩余配额代理
- 媒体账号检查项 3/4 不再为 `na`，并与该账号绑定 Profile 的真实代理读回事实一致
- 页面、Cloud 镜像、Agent 读回、BitBrowser 实际状态一致

## 7. Evidence 要求

`evidence/` 提供：台账收尾、配额迁移、同步写回端点、写回 broker、推荐引擎、外部代理 Diff、账号检查项 3/4、端到端验收（真实代理）、测试与构建记录。

## 8. Checkpoint

- Completed：CHG 已创建；继承 CHG-032 的 Profile 敏感操作互斥和 Cloud/Agent/Desktop 本地验收环境。
- Current：Task 1/2/3 完成；最新本地 Cloud/Agent 已重启，Agent `proxy-mutation` 空输入返回预期 400，Cloud/Agent/BitBrowser 健康检查通过。正在执行 Task 4 的解绑和更换生命周期。
- Next：以 BitBrowser 的正式 `proxyType: noproxy` 语义实现解绑读回；更换只在新代理读回成功后将 `proxy_id` 原子切换。
- Blockers：真实代理分配、读回、更换、解绑及端到端验收需要真实代理资源；无资源时不得把 mock/单元验证写成真实效果。
- Recent verification：Task 3 Agent 76 tests、Cloud `go test ./internal/modules/proxy ./internal/modules/profilebinding -count=1`、Web 41 tests、Cloud/Desktop Web build 均通过。见 `evidence/task1-proxy-create-and-zero-side-effect-preview.md`、`evidence/task2-unified-proxy-capacity.md`、`evidence/task3-synchronous-proxy-writeback.md`。

## 9. Pending Questions

None.
