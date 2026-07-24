# CHG-20260725-030 Start Gate

日期：2026-07-25

## 核对结果

- Active CHG：`CHG-20260725-030`
- `CURRENT_CONTEXT`：指向 `CHG-20260725-030`
- `delivery/LEDGER.md`：仅列出 `CHG-20260725-030`
- 关联 Milestone：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`
- 影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`、`wt-media-workspace`

## 当前事实

- B5 已完成并归档：
  - Cloud 旧浏览器窗口本机操作入口拒绝执行；
  - Desktop 已有 `profileOpen`、`profileClose`、`profileCreate` 本地服务；
  - Tauri 已有 `local_agent_profile_open`、`local_agent_profile_close`、`local_agent_profile_create`；
  - Local Agent 已有 Profile 分组、创建、打开、关闭接口。
- `AccountsPage.vue` 已有媒体账号台账基础：
  - 列表、搜索、平台/游戏/业务状态/登录状态/标签筛选；
  - 新建账号台账；
  - 标签批量添加/移除；
  - 详情抽屉；
  - Desktop 端绑定/解绑/换绑窗口；
  - Desktop 端单个账号检查。
- `mediaaccount.Service` 已有核心规则：
  - 普通运营只看本人账号；
  - 授权范围使用 `actor.CanAccess`；
  - 绑定 Profile 时校验授权、激活状态和同 Profile 同平台唯一性；
  - 绑定/解绑后登录状态重置为 `unknown`，最近检查时间清空；
  - `StartLocalAccountCheck` 只允许普通运营发起，要求本地节点、绑定窗口、账号启用和敏感任务授权；
  - `ApplyLocalAccountCheckResult` 回填平台 UID、昵称、头像、登录状态和最近检查时间。
- `wt-media-desktop/src-tauri/src/main.rs` 已有 `local_agent_account_check`：
  - 先刷新本机运行时到 Cloud；
  - 调 Cloud sensitive task preflight；
  - 调 Local Agent `/api/v1/account-check`；
  - 完成后释放本机敏感操作 permit；
  - 返回安全的账号身份结果。
- `wt-media-agent/src/wt_media_agent/local_api/server.py` 已有 `/api/v1/account-check`：
  - 打开目标 BitBrowser Profile；
  - 读取 Cookie；
  - 根据平台识别账号身份；
  - 发现期望平台账号不一致时返回 `account_mismatch`。

## 缺口

- 页面命名仍是“新建账号台账”，Milestone 要求新增账号入口命名为“新增账号”。
- 媒体账号列表字段不完整：
  - 缺少系统记录ID列；
  - 未直接展示平台 UID、头像、最近检查时间；
  - 绑定窗口展示未包含系统记录ID、窗口名称和 BitBrowser Profile ID 的完整识别信息。
- 账号列表分页目前是前端固定 pageSize，没有与过滤结果或后端分页明确收口。
- 当前游戏在新建表单中仍偏必填；Milestone 允许新增账号时先不绑定游戏，但进入可执行、发布或互动预检前必须至少绑定一个游戏。
- 业务状态枚举和登录状态文案仍沿用历史值：
  - Milestone 业务状态包含 `draft`、`enabled`、`disabled`、`abnormal`、`retired`；
  - Milestone 登录状态包含 `unchecked`、`logged_in`、`not_logged_in`、`expired`、`mismatch`、`check_failed`；
  - 当前代码使用 `unknown`、`normal`、`verification_needed`、`restricted`、`account_mismatch`、`environment_error`。
- 账号行缺少打开/关闭绑定窗口入口；目前只能进入详情检查账号。
- 详情里的按钮仍叫“检查账号”，需要收口为“检查/同步账号信息”，以覆盖人工登录后回填场景。
- Cloud Web 边界提示存在，但仍需用测试确认 Cloud Web 不出现绑定/换绑、本机检查、打开/关闭入口。
- 当前 CHG 不处理 Cookie 读写、CK 上号、接码、人工验证码和代理写入。

## 文件映射

- Cloud 媒体账号路由与服务：
  - `wt-media-cloud/internal/modules/mediaaccount/routes.go`
  - `wt-media-cloud/internal/modules/mediaaccount/service.go`
  - `wt-media-cloud/internal/modules/mediaaccount/store_mysql.go`
  - `wt-media-cloud/internal/modules/mediaaccount/*_test.go`
- Cloud/Profile 绑定只读辅助：
  - `wt-media-cloud/internal/modules/profilebinding/service.go`
  - `wt-media-cloud/web/src/shared/api/profileBindings.js`
- Web/Desktop 共用账号页面：
  - `wt-media-cloud/web/src/modules/accounts/pages/AccountsPage.vue`
  - `wt-media-cloud/web/src/shared/api/mediaAccounts.js`
  - `wt-media-cloud/web/src/apps/desktop/features/local-agent/service.js`
- Desktop Rust：
  - `wt-media-desktop/src-tauri/src/main.rs`
- Local Agent：
  - `wt-media-agent/src/wt_media_agent/local_api/server.py`
  - `wt-media-agent/tests/test_local_account_check.py`

## 测试计划

- Cloud：`go test ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/profileguard`。
- Web：`npm test` 覆盖账号页面文本、Cloud/Desktop 边界、local agent service；`npm run build`。
- Agent：`python3 -m unittest tests/test_local_account_check.py`。
- Desktop：`cargo test` 覆盖 Tauri payload 和已有账号检查命令逻辑。

## 风险

- 登录状态和业务状态枚举若直接改数据库值，可能影响历史数据和已有测试；本 CHG 需要先判断是做兼容映射，还是迁移正式枚举。
- 批量账号检查在 Milestone 中属于 M2-B 完成标准，但本 CHG 暂按“单项检查/同步收口”执行；若审计发现已有批量检查只需小范围收口，可以补入，否则应单独 CHG。
- 真实平台身份识别当前主要通过 Cookie 简化推断，人工验收仍需要真实 BitBrowser 与平台登录状态验证。
