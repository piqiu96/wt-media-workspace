# CHG-20260725-030：M2-B6 媒体账号操作与检查收口

> 日期：2026-07-25  
> 状态：DONE  
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环  
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`  
> 当前仓库：`wt-media-workspace`  
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`

## 1. 用户可见目标

在 B5 已收口浏览器窗口真实操作后，普通运营可以在 Desktop 完成媒体账号侧剩余闭环：

```text
进入媒体账号台账
→ 创建或编辑账号的基础信息、标签、游戏、备注和状态
→ 绑定或更换本人授权浏览器窗口
→ 从账号行打开/关闭绑定窗口
→ 人工在 BitBrowser 登录后点击“检查/同步账号信息”
→ 系统真实读取平台身份、头像和登录状态并回填 Cloud
→ 页面展示账号是否可执行、失败原因和最近检查结果
```

本 CHG 只收口 M2-B 媒体账号台账、窗口绑定入口和账号检查/同步体验，不做代理写入，不做 Cookie 上号，不建设批量上号或通用任务中心。

## 2. 当前背景

已完成/继承：

- M2-A 已完成人员、权限、会话和本机可信基础；
- B1/B2 已完成浏览器窗口扫描、Diff、接受本地变化、恢复 Cloud 配置和授权；
- B3 已完成媒体账号台账与 Profile 绑定基础；
- B4-1 已完成单个媒体账号检查与身份回填基础链路；
- B5 已完成浏览器窗口列表、真实创建、打开、关闭、停用和 Diff 交互收口；
- 用户确认：Cloud Web 只展示 Cloud 保存数据；Desktop 才展示和操作 Local Agent / BitBrowser；
- 用户确认：打开、关闭、新建、扫描、账号检查等 BitBrowser 单项操作是同步操作，不创建 Cloud 异步任务。

## 3. 本 CHG 范围

### 包含

- 媒体账号台账页面字段与筛选收口：
  - 列表、详情、搜索、平台/游戏/标签/业务状态/登录状态筛选、分页；
  - 展示账号系统记录ID、平台、平台UID、昵称、头像、绑定窗口、游戏、标签、业务状态、登录状态、最近检查时间和备注；
  - 未绑定窗口账号明确展示不可执行原因。
- 新增/编辑账号规则收口：
  - 新增账号入口命名为“新增账号”；
  - 支持平台、游戏、标签、备注和业务状态维护；
  - 可以先不绑定游戏，但进入可执行、发布或互动预检前必须至少绑定一个游戏；
  - 换绑窗口后登录状态必须回到未检查/未知状态，不能沿用旧窗口检查结果。
- 绑定/换绑窗口体验收口：
  - 绑定选择项必须能识别系统记录ID、窗口名称和 BitBrowser Profile ID；
  - 只能选择本人授权、未归档的浏览器窗口；
  - 一个账号最多绑定一个 Profile；一个 Profile 同平台最多一个账号。
- 账号行打开/关闭窗口入口：
  - 仅 Desktop 展示；
  - 通过 Tauri/Rust → Local Agent → BitBrowser 同步打开/关闭绑定窗口；
  - Cloud Web 不展示本机打开/关闭入口。
- 检查/同步账号信息收口：
  - 仅 Desktop 触发；
  - 检查前校验当前用户、Desktop 节点、BitBrowser 主账号、绑定窗口和账号状态；
  - Agent 真实读取当前平台身份，Cloud 回填平台UID、昵称、头像、登录状态和最近检查时间；
  - 自动登录失败后的人工登录场景，可回到 Desktop 点击“检查/同步账号信息”完成回填；
  - 失败时保留账号台账和绑定关系，并显示运营可理解原因。
- Cloud Web 与 Desktop 边界：
  - Cloud Web 只展示 Cloud 已保存账号、窗口、绑定和历史检查结果；
  - Desktop 才出现打开/关闭窗口、检查/同步账号信息等本机操作入口。

### 不包含

- 不做批量账号检查，除非实现审计证明已有代码只需小范围收口；
- 不导入、写入、读取或导出 Cookie；
- 不做 CK 上号、接码链接、人工验证码或人工接管批次；
- 不写入、更换或解绑代理；
- 不清理原窗口 Cookie；
- 不建设通用任务中心；
- 不改变 B5 已完成的浏览器窗口创建、扫描、Diff、停用语义。

## 4. 关键规则

- Cloud 不能直接调用 Local Agent 或 BitBrowser；
- Desktop Vue 不能直接访问 Local Agent 动态端口或持有动态凭据；
- HTTP成功、Agent调用成功、BitBrowser接口调用成功都不等于账号检查成功；
- 只有平台身份、登录状态和 Cloud 回写都成功后，账号才算完成本次检查；
- 手工补录平台UID、昵称或备注不能授予执行资格；
- 实际账号与 Cloud 记录不一致时不自动覆盖，必须给出可理解结果或处理入口；
- 归档/停用窗口不能作为新的账号绑定目标。

## 5. 执行任务

### Task 1：Start Gate 与现状审计

- 核对 `CURRENT_CONTEXT`、`LEDGER`、active CHG 和 M2-B milestone；
- 审计媒体账号 Cloud 模型、Web/Desktop 页面、Agent 平台检查适配器和 Tauri 命令；
- 明确 B3/B4-1/B5 可复用代码、当前缺口、风险和文件映射；
- 记录测试和验收方法。

### Task 2：媒体账号台账字段、筛选和状态规则收口

- 补齐列表、详情、搜索、筛选、分页和用户可读状态；
- 修正新增/编辑/绑定/换绑后的业务状态和登录状态投影；
- 未绑定、未检查、归档窗口等不可执行原因要清晰展示。

### Task 3：绑定/换绑窗口选择与唯一性验收

- 绑定选择项展示系统记录ID、窗口名称和 BitBrowser Profile ID；
- 校验授权、归档状态、同平台唯一性和换绑后登录状态重置；
- 覆盖 Cloud API 与页面边界测试。

### Task 4：账号行打开/关闭窗口入口

- Desktop 账号行通过已有 B5 本地窗口操作链路打开/关闭绑定窗口；
- Cloud Web 不展示本机入口；
- 成功和失败均在账号页面展示明确结果。

### Task 5：检查/同步账号信息体验收口

- Desktop 调用 Tauri/Rust → Local Agent → 平台适配器；
- 人工登录后点击“检查/同步账号信息”能回填真实平台身份；
- 失败、账号不一致、未绑定窗口、窗口归档和本机身份不匹配均给出明确结果。

### Task 6：验证与 Evidence

- 自动测试覆盖账号查询、绑定唯一性、状态变化、页面边界和本地检查入口；
- 记录无法真实验证的外部前置；
- 更新 checkpoint。

## 6. 验收标准

- Cloud Web 媒体账号页没有打开/关闭窗口、检查/同步账号信息等本机操作入口；
- Desktop 媒体账号页展示完整账号字段、搜索、筛选和分页；
- 新增/编辑/绑定/换绑账号后，业务状态和登录状态符合 M2-B milestone；
- 未绑定窗口、窗口归档、未授权、未检查或检查失败时，页面明确显示不可执行原因；
- 账号行打开/关闭窗口同步调用 BitBrowser，成功/失败结果可见；
- 人工在 BitBrowser 登录后，Desktop 点击“检查/同步账号信息”能真实读取并回填平台 UID、昵称、头像、登录状态和最近检查时间；
- 手工补录不能冒充真实检查成功；
- 失败不得产生 Cloud 假成功记录。

## 7. Evidence 要求

完成后在 `evidence/` 中至少提供：

- `start-gate.md`：当前事实、缺口、文件映射；
- `account-ledger.md`：媒体账号字段、筛选、分页和状态规则验证；
- `account-profile-binding.md`：绑定/换绑窗口唯一性和状态重置验证；
- `account-window-operations.md`：账号行打开/关闭窗口同步调用验证；
- `account-check-sync.md`：检查/同步账号信息与人工登录后回填验证；
- `tests.md`：自动测试和构建记录。

## 8. 交付边界

本 CHG 完成后，M2-B 的“浏览器窗口 + 媒体账号台账 + 绑定 + 单项检查/同步”应具备真实可用闭环。

后续独立 CHG 进入：

- M2-C：代理资源与窗口真实绑定闭环；
- M2-D：CK、接码、人工验证码、人工接管和 Cookie 闭环。

## 9. Checkpoint

- Completed：
  - B6 active CHG 已创建；
  - B5 已完成运行仓库提交并归档到 completed；
  - Task 1 Start Gate 与现状审计已完成，见 `evidence/start-gate.md`；
  - Task 2 媒体账号台账字段、筛选和状态规则已部分收口，见 `evidence/account-ledger.md`；
  - Task 3 绑定/换绑窗口选择与唯一性验收已完成，见 `evidence/account-profile-binding.md`；
  - Task 4 账号行打开/关闭窗口入口已接入 Desktop 本机操作路径，见 `evidence/account-window-operations.md`；
  - Task 5 检查/同步账号信息体验已收口，见 `evidence/account-check-sync.md`。
- Current：Task 6 验证与 Evidence 汇总已完成，准备 diff review 与分仓库提交。
- Next：B6 已关闭；M2-B 仍缺批量账号检查，已激活 B7 后再判断是否进入 M2-C。见 `evidence/closure-assessment.md`。
- Blockers：无。
- Recent verification：
  - 继承 B5 提交前复验：Agent unittest、Desktop `cargo test`、Web `npm test`、Web `npm run build`、Cloud profilebinding `go test` 均 PASS。
  - 2026-07-25 B6 Task 2/4 复验：`npm test` PASS，9 files / 32 tests；`npm run build` PASS；`env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/profileguard` PASS。

## 10. Pending Questions

None.
