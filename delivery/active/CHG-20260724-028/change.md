# CHG-20260724-028：M2-B4-1 单个媒体账号检查与身份回填闭环

> 日期：2026-07-24  
> 状态：ACTIVE  
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环  
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`  
> 当前仓库：`wt-media-workspace`  
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`

## 1. 用户可见目标

在 B3 已经完成“媒体账号台账与授权浏览器窗口绑定”的基础上，B4-1 让普通运营可以在 Desktop 对一个已绑定窗口的媒体账号发起真实账号检查：

```text
普通运营打开媒体账号详情
→ 选择一个已绑定浏览器窗口的账号
→ 点击检查账号
→ Desktop 通过 Tauri/Rust 调用 Local Agent
→ Local Agent 同步调用 BitBrowser / 平台适配器读取当前登录身份
→ Cloud 保存平台UID、昵称、头像、登录状态和最近检查时间
→ 页面展示账号是否可进入后续预检
```

本 CHG 只做单个账号检查与身份回填，不做批量检查、不写入 Cookie、不做 CK 上号、不建设任务中心。

## 2. 当前背景

已完成/继承：

- M2-A 已完成人员、权限、会话、本机可信基础；
- B1/B2 已完成 Desktop 扫描、Diff、接受本地变化、恢复 Cloud 配置和窗口授权；
- B3 已完成媒体账号台账与授权浏览器窗口绑定；
- 用户确认：Cloud Web 对所有角色只展示 Cloud 已保存业务信息，不展示 Agent / BitBrowser 操作入口；
- 用户确认：Desktop 必须通过 Tauri/Rust 调用 Local Agent，不允许 Vue 直接访问 Local Agent 动态端口或动态凭据；
- 用户确认：BitBrowser 单项操作是同步操作，不需要创建异步任务；复杂发布等长流程才走正式异步任务。

## 3. 本 CHG 范围

### 包含

- 审计现有账号检查 API、Agent executor、Desktop入口和平台适配器能力；
- 收敛单个账号检查链路为 Desktop 本地敏感操作：
  - Cloud 做权限和业务预检；
  - Desktop 通过 Tauri/Rust 调 Local Agent；
  - Local Agent 同步调用 BitBrowser / 平台适配器；
  - 读回结果后回写 Cloud；
  - 页面显示最终状态；
- 账号检查前必须校验：
  - 当前用户是普通运营；
  - 当前 Desktop 本机节点可信；
  - 当前 BitBrowser 主账号与用户绑定主账号一致；
  - 账号已绑定授权窗口；
  - 账号业务状态为 `enabled`；
  - 绑定窗口未归档且未被本地敏感操作占用；
- 检查成功后回填：
  - 平台 UID；
  - 昵称；
  - 头像；
  - 登录状态；
  - 最近检查时间；
- 检查失败后保留账号台账和绑定关系，并显示可理解失败原因；
- Cloud Web 只展示历史检查结果和 Cloud 已保存状态，不提供“检查账号”入口；
- 自动测试覆盖权限、状态回写和页面边界。

### 不包含

- 不做批量账号检查；
- 不写入、读取、导入或导出 Cookie；
- 不做 CK 上号、接码链接、人工验证码或人工接管；
- 不创建、打开、关闭或修改浏览器窗口，除非账号检查适配器读取当前窗口状态必须打开已绑定窗口；
- 不分配、更换或读回代理；
- 不建设通用任务中心；
- 不把 Cloud Web 做成本机执行入口。

## 4. 关键规则

- Cloud 不能直接调用 Local Agent 或 BitBrowser；
- Desktop Vue 不能直接调用 Local Agent HTTP 动态端口，必须通过 Tauri/Rust；
- HTTP 成功、Agent 调用成功、BitBrowser 接口调用成功都不等于账号检查成功；
- 只有平台身份、登录状态和 Cloud 回写都成功后，账号才算完成本次检查；
- 检查结果必须来自真实窗口当前状态，不能用手工补录代替；
- 检查失败不得清空原账号台账、标签、备注、Cookie字段或绑定关系；
- 如果窗口当前登录的是其他同平台账号，必须提示账号不一致，不能静默覆盖；
- 换绑后的账号必须重新检查，不能沿用旧窗口检查结果。

## 5. 执行任务

### Task 1：Start Gate 与现状审计

- 核对 `CURRENT_CONTEXT`、`LEDGER`、active CHG 和 M2-B milestone；
- 审计当前 Cloud 账号检查 API、Agent executor、Desktop调用方式和平台适配器；
- 明确当前实现是否仍有异步任务假动作或 Cloud 直接触达本机能力的问题；
- 记录文件映射、gap、风险和可复用代码。

### Task 2：Cloud 预检与结果回写 API

- 保留 Cloud 只做权限、账号、Profile授权和业务状态预检；
- 提供 Desktop 检查前预检接口或复用现有接口；
- 提供检查结果回写接口；
- 后端保证越权、未绑定窗口、禁用账号、归档窗口不会产生本机副作用。

### Task 3：Desktop → Rust → Local Agent 同步检查链路

- Desktop账号详情提供“检查账号”入口；
- Vue 调 Tauri/Rust command；
- Rust command 调 Local Agent；
- Local Agent 同步调用 BitBrowser / 平台适配器并返回结构化结果；
- 页面展示执行中、成功、失败和账号不一致。

### Task 4：账号身份回填与可执行结论

- 成功后 Cloud 回填平台 UID、昵称、头像、登录状态和最近检查时间；
- 页面刷新账号详情和列表；
- 登录正常账号显示“可进入后续预检”；
- 未检查、检查失败或账号不一致时显示运营可理解原因。

### Task 5：验证与 Evidence

- 自动测试覆盖 Cloud 预检/回写、权限、页面边界和 API 客户端；
- 尽可能使用本地 Agent/BitBrowser mock 或现有适配器做 smoke；
- 记录真实环境无法验证的前置条件，不用 mock-only 伪装真实完成；
- 更新 checkpoint，准备进入 B4-2 批量账号检查或 M2-C。

## 6. 验收标准

- Cloud Web 不出现“检查账号”本机操作入口；
- Desktop 普通运营可以对已绑定授权窗口的启用账号发起单个检查；
- 管理员和高级运营不能通过 Desktop 发起账号检查；
- 未绑定窗口、禁用账号、归档窗口、非授权窗口均被阻断且无本机副作用；
- Desktop 通过 Rust 调 Local Agent，不由 Vue 直接调用 Local Agent；
- 检查成功后平台 UID、昵称、头像、登录状态、最近检查时间回写 Cloud；
- 账号不一致、未登录、Cookie失效、BitBrowser不可用等失败原因能在页面表达；
- 失败不破坏账号台账、标签、备注、绑定关系或已有Cookie字段。

## 7. Evidence 要求

完成后在 `evidence/` 中至少提供：

- `start-gate.md`：现状审计、边界风险和文件映射；
- `cloud-precheck-readback.md`：Cloud预检、权限、回写和状态验证；
- `desktop-agent-check.md`：Desktop → Rust → Local Agent同步调用验证；
- `account-projection.md`：账号身份回填与页面结论验证；
- `tests.md`：自动测试、构建和已知真实环境限制。

## 8. 交付边界

本 CHG 完成后，M2-B 证明“单个已绑定媒体账号可以通过 Desktop 本机检查获得真实平台身份与登录状态”成立。

后续独立 CHG 继续处理：

- B4-2：批量账号检查、逐项结果和失败项重试；
- M2-D：CK上号、接码链接、人工验证码和人工接管。

## 9. Checkpoint

- Completed：CHG 已创建并关联 M2-B 闭环；B3 账号台账与 Profile 绑定闭环已完成。
- Current：Task 1 Start Gate 与现状审计待执行。
- Next：审计 Cloud、Desktop、Agent 的现有账号检查链路，确认同步边界后再改代码。
- Blockers：无。
- Recent verification：继承 CHG-20260724-027 的测试与构建通过结论。

## 10. Pending Questions

None.
