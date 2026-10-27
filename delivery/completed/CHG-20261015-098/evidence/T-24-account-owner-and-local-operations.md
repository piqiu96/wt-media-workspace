# T-24 社媒账号使用人与本地操作按归属

日期：2026-10-27（Asia/Shanghai）
结论：PASS（机器腿）。账号读取带出使用人显示名，列表与详情可读、可筛选；本地检查 / 读 Cookie / 窗口绑定按「账号本人」放行，高级运营仅限本人创建的账号，管理员一律不执行本地动作且拿不到 Agent Token；sidecar 随角色启停。真实页面与 MySQL 上的联表读回并入 T-26 三账号走查。

## 提交

| 仓 | 分支 | 提交 |
| --- | --- | --- |
| wt-media-cloud | `chg/CHG-20261015-098-round3` | `f3e34d7`（mediaaccount + localagent + 账号页 + 合同） |
| wt-media-workspace | `chg/CHG-20261015-098-docs` | 本文件所在提交（ADR-0023 第 6 条、第三章 §3.3.11、contract-map、角色矩阵回填） |

## 一、落地口径

| 项 | operator | senior_operator | admin |
| --- | --- | --- | --- |
| 使用人列 / 详情 | 显示本人 | 显示成员名 | 显示成员名 |
| 使用人筛选 | 不显示（服务端固定本人） | 默认本人，可切「全部成员」 | 默认「全部成员」 |
| 本地检查 / 读 Cookie | 本人账号 | 仅本人创建的账号；他人按钮禁用并提示 | 全部禁用并提示「管理员不执行本地操作」 |
| 窗口绑定 / 解绑 | 本人账号 | 仅本人账号 | 全部禁用 |
| Agent Token / sidecar | 签发 / 启动 | 签发 / 启动 | 不签发 / 停止 |
| 查看已存 Cookie | 本人账号 | 仅本人账号 | 任意账号（只读导出，见矩阵 §三-2） |

筛选在已加载的团队账号范围内收窄，服务端可见边界不变；按钮禁用只是提示，权限仍由服务端判定。

## 二、服务端

| 位置 | 变更 |
| --- | --- |
| `mediaaccount/model/model.go` | `Account.UserName string`（json `user_name`），只读投影，不参与 INSERT |
| `mediaaccount/repository/store_mysql.go` | 新增 `accountReadColumns`（`ma.` 全列 + `COALESCE(NULLIF(u.nickname,''), u.username, '') AS user_name`）与 `accountReadFrom`（`FROM media_accounts ma LEFT JOIN users u ON u.id = ma.user_id`）；findByID / findByIdentity / findByProfilePlatform / list 共用；`scanAccount` 读第 22 列 |
| `mediaaccount/service/service.go` | `canStartLocalOperation(role)` = operator 或 senior_operator，`StartLocalAccountCheck` / `StartCookieRead` 共用；导出 `CanStartLocalOperation` 给不经该两条入口的 handler 复用；`GetOwnedAccountRecord` 仍要求 `actor.ID == record.UserID` |
| `mediaaccount/handler.go` | `ReadMediaAccountCookies` 在取记录前先过角色门禁，堵住管理员走异步 Cookie 读取（`GetAccountRecord` 允许管理员的旧路径） |
| `localagent/handler.go` | Agent Token 只签发给 operator + senior_operator；管理员 403 `DESKTOP_ROLE_FORBIDDEN` |

## 三、前端

- `web/src/utils.js`：新增 `canRunLocalAgent(user)` = operator 或 senior_operator；`canUseLocalAgent` 保持仅 operator（开户 / 浏览器窗口 / 代理仍为普通运营专属本地执行面）。
- `apps/desktop/main.ts`：`syncLocalAgentFor` 改用 `canRunLocalAgent`；高级运营启动 sidecar，管理员登录或切换后停止。
- `auth/pages/LoginPage.vue`：会话恢复与登录成功两处都按 `canRunLocalAgent` 决定 `ensureAgentToken` / `stopDesktopLocalAgent`。
- `auth/pages/PersonalInfoPage.vue`：本机 Agent 状态与比特浏览器绑定改用 `canRunLocalAgent`。
- `layout/AppLayout.vue`：`WorkEnvPill` 用 `localAgentRunnable`（`canRunLocalAgent`）；`localOnlyPaths` 隐藏继续用 `canUseLocalAgent`。
- `apps/desktop/features/local-agent/init.js`：停止逻辑注释同步（管理员不保留旧会话）。
- `modules/accounts/pages/AccountsPage.vue`：`user_name` 列（位于账号信息后）、详情与信息弹窗字段、`ownerOptions` + `ownerFilteredAccounts` 筛选、`defaultOwnerFilter()`（senior 默认本人 / admin 默认 `all`）、`isOwnAccount` / `canOperateLocalAccount` / `localOperationHint`、`showWindowToggle`、批量检查 `skippedOwnershipText`（「已跳过 N 条非本人账号」/「管理员不执行本地操作，已跳过 N 条」）、编辑表单窗口下拉 `disabled` 与提示、管理员新增账号时使用人下拉 `disabled`（只能为自己建）。

## 四、合同与文档

| 文件 | 变更 |
| --- | --- |
| `contracts/cloud-api/v1/media-accounts.openapi.yaml` | `2026.10.27.5 → 2026.10.27.6`；`MediaAccount.user_name`（必填、只读，用户行缺失时为空串）；补 `/api/v1/media-accounts/{account_id}/check`、`/cookies/read`、`/cookies/read-sync` 与三个请求/响应 schema，说明「运营可操作、高级运营仅限本人账号、管理员不可执行本地动作」 |
| `config/contract-map.yaml` | `cloud_api 2026.10.27.6` |
| `docs/contracts/contract-map.md` | 新增「Account owner projection and local-operation gates (CHG-20261015-098 T-24)」段 |
| `docs/decisions/0023-...md` | 系统管理追加决议加第 6 条：Agent Token 对运营 + 高级运营签发，管理员无凭证，sidecar 随角色启停，异步 Cookie 读取同一套判定 |
| `docs/product/prd/详细文档/第三章_用户与账号管理.md` | 新增 §3.3.11 使用人与本地操作归属 |
| `delivery/.../2026-10-27-round3-role-capability-matrix.md` | 回填「使用人列与筛选」「本地检查 / 读 Cookie」两行 |

```
$ python3 scripts/verify/verify_m0_config.py
Workspace config verification ok
```

## 五、测试读数

```
$ go test -count=1 ./internal/modules/mediaaccount/... ./internal/modules/localagent/...
ok  .../internal/modules/mediaaccount              1.015s
ok  .../internal/modules/mediaaccount/dto          0.340s
ok  .../internal/modules/mediaaccount/model        0.750s
ok  .../internal/modules/mediaaccount/repository   0.585s
ok  .../internal/modules/mediaaccount/service      1.260s
ok  .../internal/modules/localagent                1.506s

$ go build ./... ; go vet ./internal/modules/mediaaccount/... ./internal/modules/localagent/...
（无输出）
```

| 用例 | 覆盖 |
| --- | --- |
| `TestLocalOperationsFollowAccountOwnership` | senior 本人检查通过、同团队他人 403、admin 本人/他人均 403；成功任务数 2 |
| `TestCanStartLocalOperationExcludesAdmins` | 角色门禁表：operator / senior true，admin false |
| `TestFindByIDUsesGORM` | 读取 SQL 含 `FROM media_accounts ma LEFT JOIN users u`，22 列扫描，第 22 列为使用人昵称 |
| `TestIssueAgentTokenAllowsSeniorOperators` | senior 201、拿到 token、1 条审计 |
| `TestIssueAgentTokenRefusesAdmins` | admin 403 `DESKTOP_ROLE_FORBIDDEN`、无 token、0 审计 |

前端（`wt-media-cloud/web` 下 `npx vitest run`）：全量套件在最后一次改动后复跑，读数见下方「复跑」。

| 用例 | 覆盖 |
| --- | --- |
| `AccountsPage.test.js` +2 | 使用人列/筛选（`canFilterByOwner`、`defaultOwnerFilter`、服务端过滤后的分页分母）与归属门禁（`canOperateLocalAccount`、管理员与本人提示文案、批量跳过文案、编辑表单禁用） |
| `desktopRoleGuard.test.js` | `canRunLocalAgent` 三角色真值；Desktop `main.ts`、`LoginPage`、`AppLayout`（`canUseLocalAgent` 与 `canRunLocalAgent` 两条并存）、`PersonalInfoPage` 断言同步 |
| `filterPanelConvention.test.js` | 筛选下拉占位统一「全部」（使用人筛选最初写成「全部成员」被该用例拦下，已改） |

复跑：

```
$ npx vitest run   # wt-media-cloud/web
Test Files  86 passed (86)
     Tests  780 passed (780)
```

```
$ npm run build:cloud   # 成功
$ npm run build:desktop # 成功
```

## 六、覆盖边界（未覆盖项）

- **MySQL 联表未被单测执行**：`store_mysql_test.go` 走 sqlmock，只证明 SQL 形状与列序；`LEFT JOIN users` 在真实库上的结果（含用户行缺失时 `user_name` 为空串、停用用户仍显示名字）由 T-26 页面读回。
- **Desktop 视觉与真实本地动作**：本机不能程序化驱动 GUI，菜单、禁用态与提示文案由用户按打包产物确认；高级运营本人的真实本地检查 / 读 Cookie 需真实 BitBrowser 窗口，并入 T-26。
- **高级运营拿不到可绑定的窗口**：本地动作要求窗口归属本人，`/browser-windows` 在 Desktop 仍只对普通运营开放，`AssignProfileOwner` 也拒绝非 operator 目标。高级运营自建账号若无归属自己的窗口，本轮放开的能力在实机上无法执行。登记为待裁定，见角色矩阵 §三-5，不在本任务内静默放宽。
- **管理员读他人已存 Cookie**：`GetAccountRecord` 仍允许管理员只读导出（异步 `cookies/read` 已堵）。这是既有口径，是否保留见矩阵 §三-2。
- **账号云端编辑与窗口绑定的 senior 范围**：服务端仍按团队授权，未按「他人账号只读」收紧；见矩阵 §三-3。
