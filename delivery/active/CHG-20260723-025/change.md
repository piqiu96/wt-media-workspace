# CHG-20260723-025：M2-B1 浏览器窗口扫描与 Diff 只读闭环

> 日期：2026-07-23  
> 状态：TODO  
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环  
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`  
> 当前仓库：`wt-media-workspace`  
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`、`wt-media-workspace`

## 1. 用户可见目标

普通运营在 Desktop 登录并通过 M2-A 本地身份校验后，可以触发一次真实 BitBrowser 窗口扫描，系统只生成并在 Desktop 展示窗口差异，不修改 Cloud 正式 Profile 镜像，不应用 Diff，不执行账号绑定。Cloud Web 没有 Agent 执行环境，只能查看 Cloud 已保存的浏览器窗口基本信息。

本 CHG 完成后，用户应能回答：

- 当前电脑的 BitBrowser 里有哪些窗口；
- 哪些窗口是 Cloud 没有记录的新增窗口；
- 哪些 Cloud 窗口在本地疑似缺失；
- 哪些窗口的名称、分组、代理、运行状态或已绑账号影响发生变化；
- 当前差异是否需要后续“接受本地变化”或“恢复 Cloud 配置”处理。

## 2. 当前背景

M2-A 已完成人工验收，普通运营、管理员、高级运营的 Cloud/Desktop 入口边界已经建立。

M2-B 的完整闭环包含：

```text
Desktop登录后扫描Profile
→ 生成Diff但不应用
→ 用户接受BitBrowser变化或恢复Cloud配置
→ 单个或批量创建窗口并读回
→ 管理员分配未授权窗口
→ 普通运营创建媒体账号台账
→ 绑定或换绑窗口
→ 单个或批量账号检查
→ 回填平台UID、名称、头像和登录状态
```

本 CHG 只做第一段：

```text
Desktop登录后扫描Profile
→ 生成Diff但不应用
→ 页面展示Diff
```

## 3. 本 CHG 范围

### 包含

- 审计当前 Cloud / Web / Agent / Desktop 中已有 Profile 扫描、快照提交和 Diff 代码；
- 明确 Desktop 发起扫描的安全路径，不能让 Cloud Web 直接承担本机 BitBrowser 操作入口；
- 明确 Cloud Web 与 Desktop 的页面能力边界：Cloud Web只看Cloud基本信息和已保存历史摘要，Desktop展示和处理BitBrowser扫描Diff；
- 普通运营触发本机 BitBrowser Profile 扫描；
- Local Agent 同步调用 BitBrowser 读取当前窗口列表；
- Cloud 接收扫描快照并生成只读 Diff；
- Diff 至少覆盖：
  - 新增窗口；
  - Cloud存在但本地缺失；
  - 名称变化；
  - 分组变化；
  - 代理变化；
  - 运行状态变化；
  - 已绑定媒体账号可能受影响；
- Desktop页面展示本次扫描结果和 Diff 列表；
- 扫描结果不得包含 Cookie、平台密码、代理密码等敏感明文；
- 生成自动测试和 evidence，证明“扫描只读、不应用”。

### 不包含

- 不接受本地变化；
- 不恢复 Cloud 配置到 BitBrowser；
- 不创建、编辑、打开、关闭 Browser Profile；
- 不分配未授权窗口；
- 不绑定、解绑或换绑媒体账号；
- 不执行账号检查；
- 不写入代理；
- 不写入、读取或修改 Cookie；
- 不远程删除 BitBrowser 本地窗口；
- 不用异步任务替代本次单项同步扫描。

## 4. 关键规则

- 页面面向用户使用“浏览器窗口”表达，代码和数据库仍使用 `browser_profile`；
- 本机 BitBrowser 扫描必须在 Desktop / Local Agent 可信环境下进行；
- Desktop Vue必须通过Tauri/Rust调用Local Agent，后续严格禁止直接访问Local Agent动态端口或token；
- Cloud Web没有Agent执行环境，不得展示或触发依赖BitBrowser的扫描、Diff处理、读回、打开、关闭、创建、更新等本机能力，只能展示Cloud已保存的基本信息；
- 扫描前必须继承 M2-A 的本地身份前置条件：当前用户、Desktop节点、Local Agent、BitBrowser `main_user_id` 匹配；
- 扫描只生成 Diff，不得修改 Cloud 正式 Profile 镜像；
- Cloud授权用户、账号绑定、游戏、标签、备注、Cookie 和业务状态不能被扫描覆盖；
- HTTP成功、Agent返回成功、BitBrowser接口返回成功都不等于业务完成，必须能在页面看到明确 Diff 或“无差异”结果；
- 如果身份不匹配、BitBrowser不可用或读回失败，页面必须显示运营能理解的失败原因，不得写入正式镜像。

## 5. 执行任务

### Task 1：Start Gate 与现状审计

- 阅读 `M2-account-runtime.md` 的 M2-B 闭环；
- 审计当前 Profile 扫描、Diff、Cloud镜像、Agent BitBrowser adapter、Desktop入口和页面实现；
- 输出可复用、需修正、需新增的文件映射；
- 确认本 CHG 不会与当前未提交 runtime 改动冲突。

### Task 2：扫描输入与 Diff 数据边界

- 明确扫描快照字段；
- 确保快照可以表达窗口ID、名称、分组、代理摘要、运行状态、`main_user_id`、`profile_user_id` 和本地存在性；
- 明确敏感字段禁止出现在扫描快照、Diff、日志和页面。

### Task 3：Cloud 只读 Diff

- Cloud 接收 Desktop 提交的 Local Agent / BitBrowser 扫描快照；
- Cloud 基于扫描快照与Cloud已保存 `browser_profiles` 镜像计算只读 Diff；
- 不应用到正式 Profile 镜像；
- 不改变 Profile 授权、账号绑定和业务对象；
- 不调用 Local Agent，不连接 BitBrowser，不读取本机环境；
- 必要时复用或修正已有扫描历史/差异模型。

### Task 4：Desktop / Agent 同步扫描路径

- 普通运营从 Desktop 触发扫描；
- Desktop Vue 通过 Tauri/Rust 本地可信通道调用 Local Agent；
- Local Agent 同步调用 BitBrowser 并读回窗口列表；
- 身份不匹配或 BitBrowser不可用时阻断并返回可理解错误。

### Task 5：Cloud / Desktop 浏览器窗口页面展示边界

- Desktop浏览器窗口页面展示扫描入口；
- Desktop展示本次扫描时间、扫描状态和 Diff 列表；
- Cloud Web浏览器窗口页面只展示Cloud已保存的基本信息、授权关系、绑定账号摘要和历史同步摘要；
- Cloud Web不展示也不触发扫描、Diff处理、读回、打开、关闭、创建、更新、账号检查等依赖本机Agent或BitBrowser的能力；
- Diff 分类清晰表达新增、缺失、变化和受影响账号；
- “接受本地变化”“恢复Cloud配置”等后续操作可以隐藏、禁用或标记为后续 CHG，不得假装已经完成。

### Task 6：验证与 Evidence

- 自动测试覆盖 Cloud Diff 只读逻辑；
- Agent / Desktop 路径至少提供 mock BitBrowser 或真实 BitBrowser 证据；
- 页面证据证明用户能看到 Diff 或无差异结果；
- 证据证明扫描不会修改 Cloud 正式镜像。

## 6. 验收标准

本 CHG 只有同时满足以下条件，才能进入 VERIFIED：

- 普通运营在 Desktop 可信环境下可以发起浏览器窗口扫描；
- Cloud Web不能发起扫描，也不能展示依赖本机BitBrowser实时读回的Diff处理入口；
- Local Agent 实际读取 BitBrowser Profile 列表，或在测试中使用明确的 BitBrowser mock adapter；
- Cloud 能生成并返回只读 Diff；
- Desktop页面能展示 Diff 分类和无差异结果；
- 扫描前后 Cloud 正式 Profile 镜像、授权用户和媒体账号绑定没有被自动修改；
- 身份不匹配、BitBrowser不可用、读回失败时，页面显示明确失败原因；
- 没有 Cookie、平台密码、代理密码等敏感明文进入接口响应、日志或页面；
- Evidence 记录 API、Agent/Desktop路径、页面结果和只读副作用验证。

## 7. Evidence 要求

完成后在 `evidence/` 中至少提供：

- `start-gate.md`：现状审计、复用判断、文件映射和风险；
- `tests.md`：自动测试命令、结果和覆盖说明；
- `scan-diff-readonly.md`：扫描前后 Cloud 镜像不被修改的证据；
- `desktop-agent-scan.md`：Desktop / Local Agent 调用链路证据；
- `manual-acceptance.md`：人工验收步骤、账号、页面和结果记录。

## 8. 交付边界

本 CHG 完成后，M2-B 只证明“浏览器窗口扫描与 Diff 只读闭环”成立。

后续独立 CHG 继续处理：

- B2：接受本地变化 / 恢复 Cloud 配置 / 窗口生命周期与授权；
- B3：媒体账号台账与 Profile 绑定；
- B4：媒体账号真实检查与身份回填。

## 9. Checkpoint

### 2026-07-23 Task 1 Start Gate

- 已完成：读取 AGENTS、CURRENT_CONTEXT、LEDGER、M2-B Milestone、Active CHG 和受影响仓库规则；审计 Cloud ProfileBinding、Agent BitBrowser扫描、Desktop Rust桥、Web浏览器窗口页面；生成 `evidence/start-gate.md`。
- 当前结论：现有 Cloud/Agent/Web 有可复用扫描与Diff骨架，但 Desktop路径违反“Vue不直连Local Agent动态端口/token”的规则，Cloud Diff字段也未覆盖代理、备注、运行状态和已绑账号影响。用户已确认：后续 Desktop 必须通过 Rust 调 Local Agent；Cloud Web 无 Agent 执行环境，只能看 Cloud 基本信息，不能承载依赖 BitBrowser 的扫描/Diff处理入口。
- 当前阻断：`wt-media-agent` 和 `wt-media-desktop` 存在未提交 runtime 改动，且命中后续会修改的 Local Agent 状态与 Rust桥文件；进入 Task 2/4 实现前需确认这些改动归属。
- 下一步：确认脏改动后执行 Task 2，统一扫描快照字段和敏感字段边界。
- 最近验证：本步骤为只读代码审计与治理证据记录，未运行自动测试，未修改 runtime 代码。

### 2026-07-23 Task 2 Snapshot Boundary

- 已完成：将进入 Task 2 前的 `wt-media-agent` / `wt-media-desktop` 未提交改动归属为 M2-A 本地环境状态投影尾项，并分别提交 `8eb5a82`、`51c7ce3`；新增 `evidence/dirty-runtime-ownership.md`。
- 已完成：统一扫描快照字段边界。Cloud `ProfileInput`、staged scan 存储和 Diff 字段比较已支持代理摘要、运行状态和备注；Web `safeProfile` 继续使用 allow-list，并将 Agent `status` 映射为 Cloud `bit_status`；Agent 测试补充运行状态和代理摘要断言。
- 当前结论：Task 2 只完成“安全扫描快照字段和 Diff 数据边界”，未触碰 Desktop Rust 扫描路径、页面入口、Diff应用和账号绑定。
- 当前阻断：无。
- 下一步：进入 Task 3，补 Cloud 只读 Diff 的业务对象边界与正式镜像不变证据。
- 最近验证：`go test ./internal/modules/profilebinding/...` PASS；`npm test -- profileBindings` PASS；`python3 -m unittest tests/test_local_profile_scan.py` PASS。

### 2026-07-23 Task 3 Boundary Correction

- 已完成：根据用户确认修正 Task 3 边界。Cloud 不读取本机 BitBrowser，也不调用 Local Agent；Cloud 只接收 Desktop 提交的扫描快照，并与 Cloud 已保存 `browser_profiles` 镜像计算只读 Diff。
- 已完成：补充 Cloud Web / Desktop 功能展示边界。Cloud Web 只能展示 Cloud 已保存基本信息和历史摘要；Desktop 才展示扫描入口、本机读回、Diff处理、打开/关闭/创建/更新、账号检查等依赖 Local Agent / BitBrowser 的能力。
- 当前阻断：无。
- 下一步：按修正后的 Task 3 口径实现 Cloud 只读 Diff 的正式镜像不变验证。
- 最近验证：本步骤为 CHG/Milestone 边界矫正，未修改 runtime 代码。
