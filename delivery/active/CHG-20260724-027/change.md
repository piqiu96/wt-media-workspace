# CHG-20260724-027：M2-B3 媒体账号台账与 Profile 真实绑定闭环

> 日期：2026-07-24  
> 状态：DONE  
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环  
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`  
> 当前仓库：`wt-media-workspace`  
> 预计影响仓库：`wt-media-cloud`、`wt-media-desktop`、`wt-media-workspace`

## 1. 用户可见目标

在 B1/B2 已能扫描、应用和授权浏览器窗口的基础上，B3 让普通运营可以把媒体账号台账与一个已授权的 Cloud 浏览器窗口建立真实业务关系：

```text
普通运营创建或编辑媒体账号
→ 选择平台、游戏、标签、备注
→ 绑定本人已授权浏览器窗口
→ 系统校验同平台同窗口最多一个账号
→ 页面展示账号与窗口绑定关系
→ 未绑定窗口的账号明确显示不可执行
```

本 CHG 只处理媒体账号台账与 Profile 绑定/解绑/换绑，不执行真实账号检查，不读取或写入 Cookie，不调用 BitBrowser。

## 2. 当前背景

已完成/继承：

- M2-A 已完成用户、权限、分组、游戏管理和本地可信基础；
- CHG-20260723-025 已完成 B1：Desktop 扫描 BitBrowser 并生成只读 Diff；
- CHG-20260723-026 已完成 B2：接受本地变化、恢复 Cloud 配置、窗口授权与只读摘要；
- 用户确认：Cloud Web 对所有角色只展示 Cloud 已保存业务信息；Desktop 才展示 Agent / BitBrowser / 本机读回能力；
- Milestone 规则：一个账号最多绑定一个 Profile；一个 Profile 可绑定多个不同平台账号，同平台最多一个；未绑定 Profile 的账号可作为台账存在，但不可执行。

## 3. 本 CHG 范围

### 包含

- 审计现有媒体账号列表、创建、编辑、标签、状态和 Profile 绑定实现；
- 补齐媒体账号台账页面的列表、搜索、分页、平台/游戏/标签/业务状态/登录状态筛选和备注维护；
- 创建和编辑媒体账号时支持选择游戏、平台、标签、备注和授权浏览器窗口；
- 绑定 Profile 时校验：
  - 目标窗口存在于 Cloud 镜像；
  - 目标窗口已授权给当前普通运营；
  - 同一 Profile 下同平台最多一个媒体账号；
  - 换绑后账号登录状态变为 `unknown`，需要后续 B4 重新检查；
- 解绑 Profile 后账号保留为台账，但页面明确显示不可执行；
- Cloud Web 只展示 Cloud 保存的账号、窗口和绑定摘要，不出现本机 Agent / BitBrowser 操作入口；
- Desktop 可展示同样账号台账，并为本人授权窗口提供绑定/解绑/换绑入口，但不在本 CHG 执行账号检查；
- 自动测试覆盖权限、绑定唯一性、解绑/换绑状态变化和页面边界。

### 不包含

- 不执行账号检查；
- 不回填平台 UID、昵称、头像或真实登录状态；
- 不写入、读取或导出 Cookie；
- 不打开、关闭、创建或修改 BitBrowser 窗口；
- 不写入、更换或读回代理；
- 不做上号任务、接码链接或人工验证码；
- 不建设通用任务中心。

## 4. 关键规则

- 媒体账号台账可以先创建，未绑定窗口时必须显示“不可执行”；
- 绑定/换绑只修改 Cloud 业务关系，不调用 Agent / BitBrowser；
- 只有 Desktop 才能承载后续本机账号检查入口；Cloud Web 只看已保存结果；
- 手工补录平台 UID / 昵称不能让账号获得可执行资格；
- 换绑 Profile 后登录状态必须回到 `unknown`，不能沿用旧窗口检查结果；
- 绑定关系不得覆盖账号标签、备注、业务状态、Cookie 或历史检查记录；
- 被禁用或归档的 Profile 不允许作为新的绑定目标；
- 被禁用账号不允许发起新的绑定/换绑，但历史关系可查看。

## 5. 执行任务

### Task 1：Start Gate 与现状审计

- 核对 `CURRENT_CONTEXT`、`LEDGER`、active CHG 和 M2-B milestone；
- 审计 `media_account`、`browser_profile`、标签、游戏、用户权限和现有页面；
- 明确 Cloud / Desktop 页面边界和真实文件映射；
- 记录当前 gap、风险和可复用代码。

### Task 2：后端绑定规则与 API 收敛

- 补齐或修正媒体账号创建、编辑、绑定、解绑、换绑 API；
- 实现授权窗口校验、同 Profile 同平台唯一校验；
- 换绑/解绑时更新登录状态和可执行结论；
- 保证普通运营、高级运营、管理员的数据范围正确。

### Task 3：Cloud Web 台账展示边界

- Cloud Web 仅展示 Cloud 保存的账号、窗口绑定摘要、筛选和分页；
- 不展示本机扫描、打开窗口、账号检查、Cookie读写等 Agent / BitBrowser 入口；
- 普通运营看本人账号；高级运营按组看；管理员看全部。

### Task 4：Desktop 绑定操作入口

- Desktop 展示账号台账和本人授权窗口选择；
- 提供绑定、解绑、换绑入口；
- 显示未绑定不可执行、换绑需重新检查等运营可理解状态；
- 不执行账号检查。

### Task 5：验证与 Evidence

- 自动测试覆盖后端规则、前端页面边界和绑定状态；
- Evidence 记录 API、页面和数据库状态；
- 更新 checkpoint，准备进入 B4 账号检查。

## 6. 验收标准

- 账号可创建、编辑、绑定、解绑、换绑、加减标签和筛选；
- 账号列表支持搜索、分页、平台/游戏/标签/业务状态/登录状态筛选和备注维护；
- 普通运营只能绑定本人授权窗口；
- 同一 Profile 同平台最多一个账号；
- 换绑后登录状态变为 `unknown`，页面提示需要重新检查；
- 未绑定窗口账号保留台账，但明确不可执行；
- Cloud Web 不出现任何依赖本机 Agent / BitBrowser 的操作入口；
- Desktop 只提供绑定关系操作，不在本 CHG 做账号检查。

## 7. Evidence 要求

完成后在 `evidence/` 中至少提供：

- `start-gate.md`：现状审计、文件映射和风险；
- `backend-binding-rules.md`：API、权限、唯一性、状态变化验证；
- `cloud-web-account-ledger.md`：Cloud Web 只读边界和筛选分页验证；
- `desktop-account-binding.md`：Desktop 绑定/解绑/换绑入口验证；
- `tests.md`：自动测试和构建结果。

## 8. 交付边界

本 CHG 完成后，M2-B 证明“媒体账号台账与授权浏览器窗口可以建立可信业务关系”成立。

后续独立 CHG 继续处理：

- B4：账号检查与身份回填。

## 9. Checkpoint

- Completed：CHG 已创建并关联 M2-B 闭环；B1/B2 已完成为继承证据。
- Completed：Task 1 Start Gate 与现状审计已完成，见 `evidence/start-gate.md`。
- Completed：Task 2 后端绑定规则与 API 收敛已完成，见 `evidence/backend-binding-rules.md`。
- Completed：Task 3 Cloud Web 台账展示边界已完成，见 `evidence/cloud-web-account-ledger.md`。
- Completed：Task 4 Desktop 账号与窗口绑定入口已完成，见 `evidence/desktop-account-binding.md`。
- Completed：Task 5 验证与 Evidence 已完成，见 `evidence/tests.md`。
- Current：本 CHG 已完成，等待提交并进入 B4 账号检查与身份回填。
- Next：创建 B4 独立 CHG，不在本 CHG 继续扩展账号检查、Cookie 或 BitBrowser 调用。
- Blockers：无。
- Recent verification：`go test ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/identity ./internal/modules/migration` PASS；`npm --prefix web test -- --run mediaAccounts profileBindings usersApi` PASS；`npm run build:cloud --prefix web` PASS；`npm run build:desktop --prefix web` PASS；`scripts/migrate.sh` PASS；`git diff --check` PASS。

## 10. Pending Questions

None.
