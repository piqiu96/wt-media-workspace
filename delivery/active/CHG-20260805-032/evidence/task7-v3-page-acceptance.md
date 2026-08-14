# Task 7：社媒账号页 v3 页面收口 — 实现 + 环境就绪记录

> CHG-20260805-032 / Task 7 / 2026-08-06
> 范围：社媒账号页最终实现清单（v3，全量锁定）代码改动 + 验收环境拉起
> 状态：代码完成 + 自动化验证通过；**GUI 人工验收待执行**

## 1. 代码改动（wt-media-cloud，分支 main，未提交）

| 文件 | 改动 |
|---|---|
| `internal/modules/mediaaccount/service.go` | `CreateAccountInput`/`UpdateAccountInput` 加 `Name`；`ApplyLocalAccountCheckResult` 的 name **空才回填**（UID/头像保持无条件）；`AccountFilter` + `ListAccounts` 加 `ProfileSearch` 校验 |
| `internal/modules/mediaaccount/routes.go` | create/update request 加 `name`；GET list 透传 `profile_search` |
| `internal/modules/mediaaccount/store_mysql.go` | `List` 加 `EXISTS(browser_profiles ...)` 窗口模糊匹配（name/seq/bit_profile_id/id LIKE） |
| `web/src/shared/api/mediaAccounts.js` | `list` 透传 `profile→profile_search`；`create`/`update` 支持 `name` |
| `web/src/modules/accounts/pages/AccountsPage.vue` | Cookie 列 + 任意行弹窗 + Desktop 读真实 Cookie（openCookieDialog/readProfileCookieFor）；检查→检查同步；账号信息/窗口弹窗去多余按钮；查看抽屉转 view-only（去底部按钮与可编辑表单，留 8 项明细）；编辑/新增加「账号名称」、编辑加「绑定窗口」（bind/unbindProfile）；标签改多选 allow-create（回车新建，TDesign creatable）；删标签管理（openTagManage/deleteTagFromAll/tagManageVisible）；批量栏只留 [批量检查][批量启用][批量停用]；筛选栏加「窗口绑定」模糊匹配 |
| `web/src/mediaAccounts.test.js` | 更新 2 处受影响边界断言（检查同步/批量检查）；补 profile_search 与 create/update name 用例 |

## 2. 自动化验证（PASS）

| 项 | 命令 | 结果 |
|---|---|---|
| Cloud 构建 | `go build ./...` + `go vet ./internal/modules/mediaaccount/` | PASS |
| Cloud 测试 | `go test ./internal/modules/mediaaccount/...`（新增 5 用例：Create/Update name、name 空才回填、ProfileSearch store 过滤、路由 name 透传） | PASS 全绿 |
| Web 测试 | `cd web && npm run test` | PASS **38 tests**（原 36 + 2） |
| Web 构建 | `npm run build` | PASS |

## 3. 环境拉起（m2b-local-acceptance all --force-restart）

命令：`bash scripts/m2b-local-acceptance.sh all --force-restart`（退出码 0）

| 门 | 期望 | 实际 |
|---|---|---|
| Cloud `GET /api/v1/health` | `{"errcode":0}` | PASS |
| Agent `GET /healthz` + `GET /api/v1/status` | bitbrowser_status=normal | PASS |
| Desktop assets（含 127.0.0.1:18080/api/v1 基址） | fresh + 基址存在 | PASS |
| DMG | 非空、fresh、已挂载 `/Volumes/WT Media` | PASS |
| 登录冒烟（admin/admin123 + replace_existing） | errcode 0 | PASS |

Desktop 应用已启动：`/Volumes/WT Media/WT Media.app/Contents/MacOS/wt-media-desktop-shell`（pid 记录于运行日志）。

## 4. GUI 人工验收清单（待用户执行）

- [ ] 列表 10 列（含 Cookie 列，点击弹出该行 Cookie 弹窗）
- [ ] 操作列 5 按钮：`[打开/关闭窗口] [检查同步] [查看] [编辑] [启用/停用]`，无去上号入口
- [ ] 账号信息弹窗/浏览器窗口弹窗：无「查看完整详情/关闭/查看窗口详情」按钮，只 X/外部关闭
- [ ] 查看抽屉：底部无按钮，只读，含检查明细 8 项
- [ ] 编辑对话框：含「账号名称」+「绑定窗口」（序号-名称-系统ID）
- [ ] 标签控件：多选 + 回车新建（重点核对 TDesign `creatable` 行为）
- [ ] 批量栏只留 [批量检查][批量启用][批量停用]，未选 disabled
- [ ] 新增账号对话框：含「账号名称」
- [ ] 检查同步真实回填 name/UID/头像（name 空才回填）
- [ ] Cookie 弹窗：复制 active/original + 从 Profile 读真实 Cookie
- [ ] 筛选栏「窗口绑定」文本模糊匹配命中对应行
- [ ] 无标签管理入口/按钮/弹窗
