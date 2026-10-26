# T-04 Cloud BitBrowser 绑定与 Profile 双作用域证据

日期：2026-10-23
CHG：CHG-20261023-101

## 范围

- `POST /api/v1/local-agent/bit-account/bind`：Agent Token 严格档；body `{main_user_id, observed_at, rebind}`。`users.bit_main_user_id` 为空时首绑；相同主账号只刷新 `last_verified_at`（历史 NULL `bound_at` 顺带补齐）；不同且 `rebind=false` 返回 `BIT_MAIN_USER_MISMATCH`，不写任何行；不同且 `rebind=true` 只更新 `bit_main_user_id/bit_account_bound_at/bit_account_last_verified_at`。绑定事务先 `SELECT ... FOR UPDATE` 锁用户行，审计记录 `bitbrowser.main_account.bind|verify|rebind`（重绑带 `previous_main_user_id`）。
- 手工绑定路径退场：路由 `/api/v1/bit-browser/main-identity`、`/api/v1/bit-browser/profile-scans/:scan_id/confirm-main-identity` 及 `ConfirmMainIdentityDirect`/`ConfirmMainIdentity`、`MainIdentityInput`、store/service 方法与 operations 包装全部删除；`ConfirmScan` 只应用 Profile，不写 `users`。
- Profile 双作用域：列表/详情/更新/删除/分配/同步删除全部要求 `bp.main_user_id = users.bit_main_user_id`（owner 为用户自己）。`ResolveProfile`、`ResolveProfileForAccountCheck`、`ResolveProxyForAccountCheck` 返回 `inScope`，媒体账号据此区分 `PROFILE_NOT_FOUND`、`PROFILE_ASSIGNED_TO_OTHER_USER`、`PROFILE_UNAVAILABLE`。
- 扫描：`SubmitScan` 要求已绑定、`main_user_id` 与绑定一致、`observed_at` 在新鲜窗口内（`[bitbrowser] observation_fresh_for`，默认 `2m`，零值拒绝、未来时间接受）。`ApplyScan` 在新键上 upsert，缺失行只标 `local_missing`，无 DELETE；跨主账号扫描直接 `BIT_MAIN_USER_MISMATCH`。
- `AssignProfileOwner` 拒绝目标未绑定（`BIT_NOT_BOUND`）或目标绑定与 Profile 的主账号不一致（`BIT_MAIN_USER_MISMATCH`）。
- 迁移 `20261023_069_browser_profile_scope.sql`：先以守卫表证明 `(user_id, main_user_id, bit_profile_id)` 无重复，再删旧唯一键并加 `uq_browser_profiles_user_main_bit` 与 `idx_browser_profiles_user_main`。

## 行为单测

命令：

```bash
cd /Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud
go test ./internal/modules/profilebinding/... ./internal/modules/mediaaccount/... ./internal/infra/database/migration/ -count=1
```

结果：全部 `ok`。关键用例：

| 文件 | 用例 | 证明 |
| --- | --- | --- |
| `profilebinding/service/service_test.go` | `TestBindBitAccountTransitions` | 首绑、同主只刷新验证时间、临时不一致拒绝且绑定不变、正式重绑换主、旧值进审计 |
| 同上 | `TestRebindKeepsOtherMainProfilesAndSwitchingBackRestoresThem` | 重绑不删旧主 Profile；切回旧主后旧 Profile 重新可见 |
| 同上 | `TestSubmitScanRequiresBindingFreshObservationAndMatchingMain` | 未绑定 `BIT_NOT_BOUND`、过期/零值 `BIT_BROWSER_OFFLINE`、主账号不一致 `BIT_MAIN_USER_MISMATCH` |
| 同上 | `TestSensitiveObservationCannotBypassFreshness` | 敏感入口同样走新鲜度校验 |
| 同上 | `TestSubmitScanRejectsUnverifiableIdentity` | 缺 `main_user_id`/`observed_at`/profiles 失败关闭 |
| 同上 | `TestConfirmScanAppliesProfilesWithoutChangingBinding` | 确认扫描只应用 Profile，不写绑定 |
| 同上 | `TestConfirmScanRejectsScanFromPreviousMainAccount` | 旧主账号的扫描不能应用到新主账号 |
| 同上 | `TestScanDiffAndConfirmationUpdateAndMarkMissing` | 缺失只标 `local_missing`，其他主账号行的 Profile 原样保留 |
| 同上 | `TestOutOfMainScopeProfileIsNotFound` | 旧主 Profile 详情/更新/删除均 `PROFILE_NOT_FOUND` |
| 同上 | `TestListsRequireBindingForSelfButNotForSeniorPeeking` | 本人/管理员列表要求绑定；同队 senior 可看但不因未绑定失败，行可见性仍受限 |
| 同上 | `TestAssignProfileOwnerRejectsUnboundOrMismatchedTarget` | 目标未绑定/主账号不匹配拒绝分配 |
| `profilebinding/repository/store_mysql_test.go` | `TestBindBitAccountFirstBindWritesBindingAndAudit` 等 4 个 | 首绑/拒绝不一致/重绑审计/扫描缺失范围的 SQL 形状 |
| `profilebinding/repository/store_mysql_test.go` | `TestGetProfileInScopeJoinsTheOwnerBinding` | 作用域查询 join `users` 绑定 |
| `profilebinding/handler_test.go` | `TestRegisterRoutesBindsProfileEndpoints` | Profile 列表与 bind 路由裸访问 401；两个手工身份路由 404 |
| `mediaaccount/service/service_test.go` | `TestServiceBindsOnlySameUserActiveProfileAndOnePlatform` 等 | 越界 Profile 返回 `PROFILE_NOT_FOUND`、他人 Profile 返回 `PROFILE_ASSIGNED_TO_OTHER_USER` |
| `migration/browser_profile_scope_test.go` | `TestBrowserProfileScopeMigration` | 迁移含两条 DROP、新唯一键与索引、守卫先于 ALTER、无 `CREATE TABLE` |

## 全量测试

```bash
go test ./...        # 日志 /tmp/chg101-t04-full2.log
go vet ./...
gofmt -l <本任务改动的 .go 文件>
```

- `go test ./...`：exit 0；`ok` 70 包，`FAIL` 0 行，`no test files` 12 包。
- `go vet ./...`：exit 0。
- `gofmt`：本任务改动的 Go 文件全部干净（无输出）。

## 迁移 069 实跑

### 空 scratch schema（001→071 全链）

临时配置指向 `wt_media_cloud_chg101_mig069`，`./scripts/migrate.sh -dir migrations`：

```text
migration ok；schema_migrations=72（71 条迁移 + 000_bootstrap_existing），表数=32
browser_profiles 唯一键: uq_browser_profiles_user_main_bit (user_id, main_user_id, bit_profile_id)
browser_profiles 索引: idx_browser_profiles_user_main (user_id, main_user_id)
旧 uq_browser_profiles_bit_profile / uq_browser_profiles_user_bit_profile: 不存在
schema_migrations 含 20261023_069_browser_profile_scope
```

### 旧主账号 fixture 起跑（067 后种数据，再跑 068/069/071）

库 `wt_media_cloud_chg101_mig069_fixture`：先只应用 001–067，插入 1 个 `users`（带 `device_id`、`bit_main_user_id='main-A'`）与 1 条 `browser_profiles`（`bp-1/main-A/active`），再应用 068/069/071。

```text
迁移前: profile id=1 bit_profile_id=bp-1 main_user_id=main-A local_status=active user_id=1
迁移后: profile id=1 bit_profile_id=bp-1 main_user_id=main-A local_status=active user_id=1（未改写、未删除）
users.device_* 列=0；local_agent_nodes/binding_tickets/runtime_presence/agent_nodes 表=0
schema_migrations 含 068/069/071
```

新约束行为读回：

```text
同一 user 下插入 (bp-1, main-B)           → 成功（id=2），双主账号共存
再插入重复的 (bp-1, main-A)               → ERROR 1062 Duplicate entry '1-main-A-bp-1'
                                             for key 'browser_profiles.uq_browser_profiles_user_main_bit'
```

## 旧手工绑定路径扫描

```bash
git add -A
git grep -n -E 'ConfirmMainIdentity|MainIdentityInput|main-identity|confirm-main-identity|ErrIdentityMismatch' \
  -- '*.go' ':!internal/infra/database/migration/*'
```

- 分母：358 个已跟踪 `.go` 文件（`git add -A` 之后，含新增迁移测试）。
- 生产代码命中 **0**；2 处命中均在 `handler_test.go`，是“这两个路由应返回 404”的断言，属阳性对照：同一模式确实能匹配，0 是真实清空。

## 未覆盖 / 风险

- `web/src/shared/api/profileBindings.js` 及其 Vitest 仍调用已删除的手工身份端点；按计划归 T-08 一并替换，本任务不动 Web。
- 错误码到 HTTP 的映射（`BIT_*`、`PROFILE_*`）由 handler 代码与 service 哨兵错误测试覆盖，尚无 handler 级 HTTP 断言；HTTP 行为在 T-10 真实回归复验。
- 迁移 070（Task Runtime）尚未写；069 已在空链与旧 fixture 两处实跑，070 落地后全链会在开发库再跑一遍。
- 真实 BitBrowser/Agent 的首绑、重绑、切回回归属 T-10。
