# Task 7：社媒账号页 v3 页面收口 — 实现 + 环境就绪记录

> CHG-20260805-032 / Task 7 / 2026-08-06
> 范围：社媒账号页最终实现清单（v3，全量锁定）代码改动 + 验收环境拉起
> 状态：代码完成 + 自动化验证通过；**GUI 人工验收通过（2026-08-14）**

## 1. 代码改动（wt-media-cloud，分支 main，未提交）

| 文件 | 改动 |
|---|---|
| `internal/modules/mediaaccount/service.go` | `CreateAccountInput`/`UpdateAccountInput` 加 `Name`；`ApplyLocalAccountCheckResult` 的 name **空才回填**（UID/头像保持无条件）；`AccountFilter` + `ListAccounts` 加 `ProfileSearch` 校验 |
| `internal/modules/mediaaccount/routes.go` | create/update request 加 `name`；GET list 透传 `profile_search` |
| `internal/modules/mediaaccount/store_mysql.go` | `List` 加 `EXISTS(browser_profiles ...)` 窗口模糊匹配（name/seq/bit_profile_id/id LIKE） |
| `web/src/shared/api/mediaAccounts.js` | `list` 透传 `profile→profile_search`；`create`/`update` 支持 `name` |
| `web/src/modules/accounts/pages/AccountsPage.vue` | Cookie 列 + 任意行弹窗 + Desktop 读真实 Cookie；账号信息/窗口弹窗去多余按钮；查看抽屉转 view-only 并保留 8 项明细；编辑/新增加「账号名称」、编辑加「绑定窗口」；标签改多选 allow-create；筛选栏加「窗口绑定」模糊匹配；主操作固定为 [新增账号][批量检查][刷新]，移除批量启停工具栏，操作列使用「检查」 |
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

## 4. GUI 人工验收结果（2026-08-14，PASS）

- [x] 列表含 Cookie 列，点击可弹出该行 Cookie 弹窗
- [x] 操作列使用「检查」，保留行级打开/关闭窗口、查看、编辑、启用/停用
- [x] 账号信息弹窗/浏览器窗口弹窗移除多余按钮；查看抽屉只读并展示 8 项明细
- [x] 编辑对话框含「账号名称」和「绑定窗口」；新增账号含「账号名称」
- [x] 标签控件支持多选与新建；同一用户可在不同账号复用同名标签
- [x] 主操作为 [新增账号][批量检查][刷新]；唯一批量入口为列表勾选后的批量检查
- [x] Cookie 弹窗支持复制当前值与从 Profile 读取真实 Cookie
- [x] 「窗口绑定」文本模糊筛选生效

## 5. GUI 验收发现及修复

GUI 点验曾发现同一用户在不同账号复用标签时，第二个账号保存后标签缺失。根因是迁移 022 删除 `media_account_id` 时，MySQL 将旧复合唯一键折叠为 `(user_id, tag_name)`；`INSERT IGNORE` 因而静默忽略第二条关系。

修复迁移 `20260814_024_media_account_tags_unique_account_scope.sql` 恢复 `(user_id, media_account_id, tag_name)`。迁移已应用，`SHOW INDEX` 已确认列顺序，跨账号同名标签 SQL 复现和 GUI 复核均通过。
