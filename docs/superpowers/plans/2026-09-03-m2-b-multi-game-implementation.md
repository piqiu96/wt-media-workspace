# M2-B 媒体账号多游戏切换 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将媒体账号从单一 `game_id` 切换为 Cloud 事实源的多游戏关系，并完成 Cloud Web 管理界面、API 兼容、真实 MySQL 迁移和 M2-B 治理收口。

**Architecture:** Cloud 的 `media_account_games` 关系表保存完整游戏集合，Cloud 服务在同一数据库事务中保存账号基础事实与关系。Cloud API 以 `game_ids` 为正式契约、以 `game_id` 为只读/旧请求兼容字段；Web 使用正式数组字段。Agent 和 Desktop 不保存游戏业务关系，Desktop 只消费由 Cloud Web 构建出的静态页面资产。

**Tech Stack:** Go、Hertz、MySQL 8、sqlmock、Vue 3、Vitest、TDesign、Tauri 静态资源。

**Spec:** `docs/superpowers/specs/2026-09-03-m2-b-multi-game-design.md`

## Global Constraints

- `media_account_games` 是账号—游戏关系唯一事实源；不再在 `media_accounts` 保存 `game_id`。
- 保留媒体账号、标签、Cookie、检查记录和 Browser Profile 绑定；只清理关系表中的历史/测试关联数据。
- 已启用游戏在媒体账号域对所有已登录角色公开；保留但不使用 `users.game_ids` 限制本域。
- `game_ids` 出现时完整替换关系；空数组合法并清空关系；旧 `game_id` 请求映射为单元素集合。
- Cloud 是 API/业务事实提供者；Agent 不改；Desktop 仅在 Cloud Web 构建后刷新生成资产。
- 不使用 Mock、异步任务创建或 HTTP 成功替代数据库关系写入、读回和页面可见结果。
- 每个运行时代码任务遵循：失败测试 → 最小实现 → 通过测试 → `git diff --check` → Evidence/Checkpoint → 独立提交。

---

## File Map

| 文件 | 责任 |
|---|---|
| `wt-media-workspace/docs/decisions/0011-media-account-multi-game-and-public-game-access.md` | 接受多游戏及媒体账号域公开游戏规则，限定对 ADR-0009 的覆盖范围。 |
| `wt-media-workspace/docs/product/prd/详细文档/第三章_用户与账号管理.md` | 将稳定产品规则从单游戏更新为多游戏和公开游戏。 |
| `wt-media-workspace/delivery/milestones/M2-account-runtime.md` | 写入本期 M2-B 操作、关系替换、失败行为与延期 7/8 验收。 |
| `wt-media-workspace/delivery/active/CHG-20260805-032/change.md` | 将多游戏加入当前活跃 CHG，关闭 Q-01/Q-02 并记录任务状态。 |
| `wt-media-workspace/delivery/planned/CHG-20260903-034/change.md` | 承接检查项 7/8 真实样本验收，不与 M2-C 混合。 |
| `wt-media-cloud/migrations/20260903_025_media_account_games.sql` | 创建关系表、迁移旧值、移除单值列/索引。 |
| `wt-media-cloud/internal/modules/identity/service.go` | 向可信进程内消费者暴露启用游戏解析能力。 |
| `wt-media-cloud/internal/app/app.go` | 将 identity 游戏解析器注入 mediaaccount 服务。 |
| `wt-media-cloud/internal/modules/mediaaccount/service.go` | 账号模型、规范化、公开游戏校验、关系替换、授权及执行资格。 |
| `wt-media-cloud/internal/modules/mediaaccount/store_mysql.go` | MySQL 事务写入、批量读取关系、`EXISTS` 多游戏筛选。 |
| `wt-media-cloud/internal/modules/mediaaccount/routes.go` | `game_ids` JSON 和查询参数，保留旧字段兼容。 |
| `wt-media-cloud/internal/modules/mediaaccount/*_test.go` | 服务、路由、MySQL Store 的可观察多游戏行为。 |
| `wt-media-cloud/web/src/shared/api/mediaAccounts.js` | 序列化正式 `gameIds`/`game_ids`，兼容旧字段。 |
| `wt-media-cloud/web/src/mediaAccounts.test.js` | API 请求数组、查询数组和 Cookie 安全回归。 |
| `wt-media-cloud/web/src/modules/accounts/pages/AccountsPage.vue` | 创建/编辑/列表/详情/筛选的多游戏交互。 |
| `wt-media-cloud/web/dist-cloud/`、`web/dist-desktop/` | 从当前 Web 源码重新生成的跟踪部署快照。 |
| `wt-media-desktop/.generated/frontend/` | 从 Cloud `dist-desktop` 刷新的 Tauri 前端资产。 |

## Task 1: 固化治理、产品和 CHG 边界

**Files:**

- Create: `wt-media-workspace/docs/decisions/0011-media-account-multi-game-and-public-game-access.md`
- Create: `wt-media-workspace/delivery/planned/CHG-20260903-034/change.md`
- Modify: `wt-media-workspace/docs/product/prd/详细文档/第三章_用户与账号管理.md`
- Modify: `wt-media-workspace/delivery/milestones/M2-account-runtime.md`
- Modify: `wt-media-workspace/delivery/active/CHG-20260805-032/change.md`
- Modify: `wt-media-workspace/delivery/LEDGER.md`
- Test: `wt-media-workspace` governance consistency inspection

**Interfaces:**

- Consumes: approved design specification and user decisions “多游戏；7/8 延期；已启用游戏默认公开”。
- Produces: a single active CHG-032 scope with no unresolved business choice; CHG-034 planned for only real 7/8 sample acceptance.

- [ ] **Step 1: Write the failing governance checklist**

Create `delivery/active/CHG-20260805-032/evidence/multi-game-governance-checklist.md` with these literal assertions marked failing: Decision 0011 exists; PRD says multi-game; M2 says enabled games are public in media-account management; Q-01 and Q-02 are resolved; CHG-034 is planned and owns only 7/8 real-sample acceptance.

- [ ] **Step 2: Inspect the failing checklist**

Run: `rg -n "一个社媒账号首版只归属一个游戏|Q-01（BLOCKING）|Q-02（BLOCKING）" docs/product delivery/active/CHG-20260805-032/change.md`

Expected: the old single-game requirement and both blocking questions are present.

- [ ] **Step 3: Write the governing facts**

Add Decision 0011 with `Status: Accepted`; state that `media_account_games` is canonical, accounts may have zero or more games, and enabled games are public only in the media-account domain. Update PRD 3.3.1/3.3.2, M2-B rules, CHG-032 scope/checkpoint, ledger, and CHG-034 scope so no record claims 7/8 is complete or blocks M2-C after CHG-032 closes.

- [ ] **Step 4: Verify governance consistency**

Run: `rg -n "一个社媒账号首版只归属一个游戏|Q-01（BLOCKING）|Q-02（BLOCKING）" docs/product delivery/active/CHG-20260805-032/change.md; git diff --check`

Expected: no match for the retired rules; diff check exits 0.

- [ ] **Step 5: Commit Workspace governance**

```bash
git -C wt-media-workspace add docs/decisions/0011-media-account-multi-game-and-public-game-access.md docs/product/prd/详细文档/第三章_用户与账号管理.md delivery/milestones/M2-account-runtime.md delivery/active/CHG-20260805-032/change.md delivery/active/CHG-20260805-032/evidence/multi-game-governance-checklist.md delivery/planned/CHG-20260903-034/change.md delivery/LEDGER.md
git -C wt-media-workspace commit -m "docs(m2-b): approve multi-game account closure"
```

## Task 2: 建立多游戏领域模型和公开游戏校验

**Files:**

- Modify: `wt-media-cloud/internal/modules/identity/service.go`
- Modify: `wt-media-cloud/internal/app/app.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/service.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/service_test.go`
- Test: `wt-media-cloud/internal/modules/identity/service_test.go`

**Interfaces:**

- Consumes: `identity.OperationGame{ID, Status}` and `identity.GameStatusEnabled`.
- Produces: `Account.GameIDs []string`, `CreateAccountInput.GameIDs []string`, `UpdateAccountInput.GameIDs *[]string`, `AccountFilter.GameIDs []string`, `AccountGroupFilters.GameIDs []string`, and `GameResolver.ResolveGame(id) (identity.OperationGame, bool, error)`.

- [ ] **Step 1: Write failing service tests**

Add these tests with hand-written expected values:

```go
func TestServiceCreateAccountStoresDeduplicatedEnabledGameIDs(t *testing.T) {
    store := newMemoryStore()
    service := newTestServiceWithGames(store, fakeGameResolver{
        games: map[string]identity.OperationGame{
            "game-a": {ID: "game-a", Status: identity.GameStatusEnabled},
            "game-b": {ID: "game-b", Status: identity.GameStatusEnabled},
        },
    })
    actor := mediaActor(1, 10, identity.RoleOperator)

    account, err := service.CreateAccount(actor, CreateAccountInput{
        GameIDs: []string{"game-b", "game-a", "game-b"}, Platform: PlatformBilibili,
    })

    if err != nil || !reflect.DeepEqual(account.GameIDs, []string{"game-a", "game-b"}) {
        t.Fatalf("account=%#v err=%v", account, err)
    }
}

func TestServiceUpdateAccountReplacesAndClearsGameIDs(t *testing.T) {
    // Create with [game-a, game-b], replace with [game-c], then replace with [].
    // Assert the three observable responses are [game-a, game-b], [game-c], and [].
}
```

Also add a test where an operator whose historical `GameIDs` contains only `game-a` creates an account for enabled `game-b`; it must succeed. Add a disabled-game fixture and assert `ErrInvalidInput`.

- [ ] **Step 2: Run service tests to verify red**

Run: `go test ./internal/modules/mediaaccount -run 'TestService(CreateAccountStoresDeduplicatedEnabledGameIDs|UpdateAccountReplacesAndClearsGameIDs)' -count=1`

Expected: compile/test failure because `GameIDs`, `GameResolver`, and relationship-aware Store behavior do not exist.

- [ ] **Step 3: Implement minimal domain changes**

Add `GameIDs []string` to the API-safe account, preserve `GameID` only as the sorted-first compatibility projection, and normalize strings by trim/dedupe/sort. Add `GameIDs []string` to account-group filters; preserve JSON `game_id` only as a singleton compatibility input and normalize it before `ListAccountsByGroup` calls `ListAccounts`. Add `GameResolver` plus `WithGameResolver`; expose a thin `ResolveGame` method from identity service and inject it in `internal/app/app.go`. Reject unknown/disabled game IDs; do not call `actor.CanAccess(..., gameID)` for media-account game associations. Replace account visibility checks with `actor.CanAccessOwnedResource(record.UserID, record.TeamID)`.

Revise the in-memory Store test double so account game relationships are retained independently of the base account record, and so an update receives an explicit replacement pointer rather than silently altering games during unrelated updates.

- [ ] **Step 4: Run focused green tests**

Run: `go test ./internal/modules/mediaaccount ./internal/modules/identity -run 'Test(Service(CreateAccountStoresDeduplicatedEnabledGameIDs|UpdateAccountReplacesAndClearsGameIDs)|PublicUserCanAccessOwnedResource)' -count=1`

Expected: PASS.

- [ ] **Step 5: Commit Cloud domain contract**

```bash
git -C wt-media-cloud add internal/modules/identity/service.go internal/modules/identity/service_test.go internal/app/app.go internal/modules/mediaaccount/service.go internal/modules/mediaaccount/service_test.go
git -C wt-media-cloud commit -m "feat(m2-b): model media account game sets"
```

## Task 3: 迁移关系表并实现 MySQL 原子读写

**Files:**

- Create: `wt-media-cloud/migrations/20260903_025_media_account_games.sql`
- Modify: `wt-media-cloud/migrations/README.md`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/store_mysql.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/store_mysql_test.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/service.go`
- Test: `wt-media-cloud/internal/modules/migration/...`

**Interfaces:**

- Consumes: `AccountRecord.GameIDs`, `Create(record)` and `Update(record, replaceGameIDs)` behavior from Task 2.
- Produces: one transaction for base-account insert/update plus relationship replacement; sorted account game IDs on all Store reads.

- [ ] **Step 1: Write failing MySQL Store tests**

Add sqlmock cases that prove observable persistence behavior:

```go
func TestMySQLStoreUpdateReplacesGameRelationshipsAtomically(t *testing.T) {
    // Expect BEGIN; UPDATE media_accounts; DELETE FROM media_account_games
    // for account 42; INSERT rows for game-a and game-b; COMMIT.
    // A missing DELETE or an INSERT for a duplicate game must fail the test.
}

func TestMySQLStoreListFiltersAnyGameWithoutDuplicateAccountRows(t *testing.T) {
    // Query GameIDs [game-a, game-b]; return one account row even when it has both links.
    // Expect GameIDs read back in lexical order [game-a, game-b].
}
```

- [ ] **Step 2: Run Store tests to verify red**

Run: `go test ./internal/modules/mediaaccount -run 'TestMySQLStore(UpdateReplacesGameRelationshipsAtomically|ListFiltersAnyGameWithoutDuplicateAccountRows)' -count=1`

Expected: failure because the old Store writes/reads `media_accounts.game_id`.

- [ ] **Step 3: Add migration and Store implementation**

Create migration 025 in lexical order. It must create `media_account_games` with `BIGINT UNSIGNED media_account_id`, `VARCHAR(32) game_id`, composite primary/unique key and lookup index, plus restrictive foreign keys to `media_accounts(id)` and `operation_games(id)`; clear only that new relation table; insert every non-empty legacy game relation; remove `idx_media_accounts_user_game`; then drop `media_accounts.game_id`.

Implement Store helpers that load all relationship rows in one batched query and attach sorted values to records. `Create` and `Update` must begin a transaction; `Update` deletes/rewrites relationships only when `replaceGameIDs != nil`. `List` must use a correlated `EXISTS` with `game_id IN (...)` and never join directly into result rows. Remove every base-table `game_id` column from selects, scans, inserts, updates and filters.

Document affected tables, forward migration, verification SQL and non-lossless rollback in `migrations/README.md`.

- [ ] **Step 4: Run focused green tests**

Run: `go test ./internal/modules/mediaaccount/... ./internal/modules/migration/... -count=1`

Expected: PASS, including new Store tests.

- [ ] **Step 5: Commit Cloud persistence layer**

```bash
git -C wt-media-cloud add migrations/20260903_025_media_account_games.sql migrations/README.md internal/modules/mediaaccount/store_mysql.go internal/modules/mediaaccount/store_mysql_test.go internal/modules/mediaaccount/service.go internal/modules/mediaaccount/service_test.go
git -C wt-media-cloud commit -m "feat(m2-b): persist media account game relations"
```

## Task 4: 发布 Cloud `game_ids` 契约和兼容路由

**Files:**

- Modify: `wt-media-cloud/internal/modules/mediaaccount/routes.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/routes_test.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/service.go`
- Modify: `wt-media-workspace/docs/contracts/contract-map.md`
- Test: `wt-media-cloud/internal/modules/mediaaccount/routes_test.go`

**Interfaces:**

- Consumes: service `CreateAccount`/`UpdateAccount` with `GameIDs`, and `AccountFilter.GameIDs`.
- Produces: compatible JSON request/response contract: `game_ids` canonical; `game_id` accepted as a singleton only when canonical field is absent; inconsistent dual fields rejected.

- [ ] **Step 1: Write failing route tests**

```go
func TestRoutesCreateAndUpdateMultiGameAccount(t *testing.T) {
    // POST with {"game_ids":["game-b","game-a"]}; assert 201 and
    // response contains "game_ids":["game-a","game-b"] plus "game_id":"game-a".
    // PATCH with {"game_ids":[]}; assert success and an empty response array.
}

func TestRoutesRejectConflictingGameIDCompatibilityFields(t *testing.T) {
    // POST with game_id=game-a and game_ids=[game-b] returns invalid-input status.
}

func TestRoutesFilterAccountsByAnyGameID(t *testing.T) {
    // GET ?game_ids=game-a,game-b returns each matching account once.
}
```

- [ ] **Step 2: Run route tests to verify red**

Run: `go test ./internal/modules/mediaaccount -run 'TestRoutes(CreateAndUpdateMultiGameAccount|RejectConflictingGameIDCompatibilityFields|FilterAccountsByAnyGameID)' -count=1`

Expected: FAIL because request structs and query parsing only expose `game_id`.

- [ ] **Step 3: Implement provider contract**

Add `GameIDs []string`/`*[]string` to account and account-group route input structures. Use an explicit resolver that rejects simultaneous unequal `game_id` and `game_ids`, maps a legacy value to one ID, and preserves omission as “do not change games” on PATCH. Parse comma-separated `game_ids` with existing `commaValues`; retain `game_id` query compatibility. Update contract-map documentation to state Cloud owns the additive `game_ids` media-account API revision.

- [ ] **Step 4: Run route and service suite**

Run: `go test ./internal/modules/mediaaccount/... -count=1`

Expected: PASS.

- [ ] **Step 5: Commit Cloud API provider change**

```bash
git -C wt-media-cloud add internal/modules/mediaaccount/routes.go internal/modules/mediaaccount/routes_test.go internal/modules/mediaaccount/service.go
git -C wt-media-cloud commit -m "feat(m2-b): expose multi-game account API"
git -C wt-media-workspace add docs/contracts/contract-map.md
git -C wt-media-workspace commit -m "docs(contract): map multi-game account API"
```

## Task 5: 改造 Cloud Web 多游戏管理

**Files:**

- Modify: `wt-media-cloud/web/src/shared/api/mediaAccounts.js`
- Modify: `wt-media-cloud/web/src/mediaAccounts.test.js`
- Modify: `wt-media-cloud/web/src/modules/accounts/pages/AccountsPage.vue`
- Test: `wt-media-cloud/web/src/mediaAccounts.test.js`

**Interfaces:**

- Consumes: canonical Cloud request/response field `game_ids`, with compatibility `game_id` ignored by the page.
- Produces: create/edit multi-select and any-game filtering without accidental relationship deletion during unrelated edits.

- [ ] **Step 1: Write failing Web API tests**

```js
it('sends full gameIds sets for create and update', async () => {
  const fetch = vi.fn(async () => response({ id: '1', game_ids: ['game-a', 'game-b'] }))
  const client = createMediaAccountClient({ fetch })

  await client.create({ gameIds: ['game-b', 'game-a'], platform: 'bilibili' })
  await client.update('1', { gameIds: [] })

  expect(fetch).toHaveBeenNthCalledWith(1, '/api/v1/media-accounts', expect.objectContaining({
    body: JSON.stringify({ game_ids: ['game-b', 'game-a'], platform: 'bilibili' }),
  }))
  expect(fetch).toHaveBeenNthCalledWith(2, '/api/v1/media-accounts/1', expect.objectContaining({
    body: JSON.stringify({ game_ids: [] }),
  }))
})

it('maps multiple selected games to the canonical list query', async () => {
  // client.list({ gameIds: ['game-a', 'game-b'] }) emits ?game_ids=game-a%2Cgame-b
})
```

- [ ] **Step 2: Run Web API tests to verify red**

Run: `npm run test -- --run src/mediaAccounts.test.js`

Expected: FAIL because the client only serializes `game_id`.

- [ ] **Step 3: Implement client and page**

Change the client to serialize `gameIds` as `game_ids` and omit compatibility fields. In `AccountsPage.vue`, replace single refs (`searchGameId`, `createForm.gameId`, `editGameId`) with array refs; ensure save sends `gameIds` even for empty array; make game controls `multiple` and `clearable`; display `account.game_ids` by resolving every ID to an enabled-game name; update account information/detail display; and make filtering send the selected array.

Do not use `user.game_ids` to select defaults. Load enabled games from the existing games API and leave create selection empty by default. Keep all Desktop-only controls, Cookie handling, Profile binding and account checks unchanged.

- [ ] **Step 4: Run Web tests and build**

Run: `npm run test -- --run && npm run build:cloud && npm run build:desktop`

Expected: all Vitest files pass and both Vite builds exit 0.

- [ ] **Step 5: Commit Cloud Web and generated Cloud assets**

```bash
git -C wt-media-cloud add web/src/shared/api/mediaAccounts.js web/src/mediaAccounts.test.js web/src/modules/accounts/pages/AccountsPage.vue web/dist-cloud web/dist-desktop
git -C wt-media-cloud commit -m "feat(m2-b): manage account game sets in web"
```

## Task 6: 真实 MySQL 切换、跨端验收和收口提交

**Files:**

- Modify: `wt-media-workspace/delivery/active/CHG-20260805-032/change.md`
- Create: `wt-media-workspace/delivery/active/CHG-20260805-032/evidence/2026-09-03-multi-game-cutover.md`
- Modify: `wt-media-desktop/.generated/frontend/`
- Test: fixed local MySQL and `wt-media-workspace/scripts/m2b-local-acceptance.sh all`

**Interfaces:**

- Consumes: migration 025, current Cloud Web source, and provider API contract from Tasks 3–5.
- Produces: verified relation rows, no old `media_accounts.game_id`, Cloud/Web/DMG output matching current source, and a current CHG checkpoint.

- [ ] **Step 1: Capture pre-migration facts**

Run against the fixed local Cloud MySQL database: count non-empty `media_accounts.game_id`; list any legacy values absent from `operation_games` or not enabled; and record account/tag/Profile counts. Stop before migration if any invalid legacy game exists.

- [ ] **Step 2: Apply migration and verify real database state**

Run: `scripts/migrate.sh`

Then verify with SQL that: migration 025 is in `schema_migrations`; `media_account_games` has one row per migrated non-empty legacy account; its composite key rejects duplicate insertion; `media_accounts` no longer has `game_id`; and media account, tag, Cookie/non-null check-item, and Profile-binding counts match pre-migration values.

- [ ] **Step 3: Execute current-source cross-platform acceptance**

Run: `wt-media-workspace/scripts/m2b-local-acceptance.sh all`

Expected: Cloud health, Agent health, real BitBrowser check, Desktop assets freshness, DMG freshness and login smoke all PASS.

Manually verify in the packaged Desktop and Cloud Web: create account with two games, edit to one game, clear all games, filter by either game, and confirm a cleared account reports “未绑定游戏” for execution without changing its Profile or Cookie status.

- [ ] **Step 4: Record evidence and checkpoint**

Record commands, pre/post counts, migration version, results, manual actions and commit IDs in the evidence file. Update CHG-032 Current/Next/Blockers: multi-game PASS; 7/8 deferred to CHG-034; 3/4 remains CHG-033; do not mark CHG-032 DONE until every remaining scoped acceptance item has been transferred and recorded.

- [ ] **Step 5: Commit Desktop assets and Workspace evidence separately**

```bash
git -C wt-media-desktop add .generated/frontend
git -C wt-media-desktop commit -m "build(m2-b): refresh multi-game desktop assets"

git -C wt-media-workspace add delivery/active/CHG-20260805-032/change.md delivery/active/CHG-20260805-032/evidence/2026-09-03-multi-game-cutover.md
git -C wt-media-workspace commit -m "docs(m2-b): record multi-game cutover evidence"
```

## Plan Self-Review

- Spec coverage: Tasks 1–2 cover public game access and business semantics; Tasks 3–4 cover canonical persistence/API compatibility; Task 5 covers all requested page interactions; Task 6 covers data preservation, real MySQL, packaged Desktop and evidence. 7/8 and M2-C are explicitly excluded and assigned to CHG-034/033.
- Placeholder scan: no unassigned implementation or acceptance items remain; every task names files, verification and commit scope.
- Type consistency: canonical Go and JSON names are `GameIDs`/`game_ids`; compatibility names are `GameID`/`game_id`; relationship replacement is represented by `*[]string` on updates so omitted and empty can be distinguished.
