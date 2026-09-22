# M2-C Proxy Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the M2-C proxy closure so Browser Profile proxy facts drive account checks and Desktop users can recommend and bind one checked proxy to several selected Profiles with real Agent readback.

**Architecture:** Cloud remains the source of the formal Profile–proxy relationship and eligibility facts. The profilebinding MySQL store exposes a narrow read-only account-check fact query to mediaaccount; it never exposes proxy credentials. The proxy route extracts the existing single-profile assign/readback transaction into one helper, then calls that helper once per selected Profile for a transparent, ordered batch result. Desktop owns the UI, while its Vue layer calls Cloud only and never receives Local Agent credentials.

**Tech Stack:** Go 1.26, Hertz, MySQL, Vue 3, Vitest, existing Local Agent `POST /proxy-mutation` contract.

**Spec:** `delivery/milestones/M2-account-runtime.md#M2-C-代理资源与窗口真实绑定闭环`, `delivery/active/CHG-20260805-033/change.md`

## Global Constraints

- M2-D Cookie, account opening and batch account onboarding are deferred and are out of scope.
- A proxy mutation is successful only after Agent readback matches the requested protocol, host and port; formal Cloud binding updates only then.
- Candidate proxies must be `active`, have `last_check_result == "ok"`, not be expired, and have capacity after considering the requested targets.
- Batch execution reuses the existing single Profile preflight/mutation path; it must not create a second relation model or asynchronous task model.
- Never return or log proxy username, password, extraction URL, Local Agent token, or dynamic Local Agent port to Vue.
- Existing uncommitted/generated Desktop artifacts are unrelated and must remain untouched.

---

### Task 1: Account check proxy facts

**Files:**
- Modify: `wt-media-cloud/internal/modules/mediaaccount/service.go:256-304,791-794,1040-1070`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/service_test.go:366-420,657-670,911-920`
- Modify: `wt-media-cloud/internal/modules/profilebinding/store_mysql.go:87-110`
- Modify: `wt-media-cloud/internal/app/app.go:77-88`
- Test: `wt-media-cloud/internal/modules/mediaaccount/service_test.go`

**Interfaces:**
- Consumes: `ProfileFactResolver.ResolveProfileForAccountCheck(profileID)` for ownership/activity facts.
- Produces: `ProfileFactResolver.ResolveProxyForAccountCheck(profileID string) (proxyID, businessStatus, lastCheckResult string, expiresAt *time.Time, bound bool, err error)`.
- Produces: `mergeCheckItems(agentItems []AccountCheckItem, proxyFact AccountCheckProxyFact, now time.Time) []AccountCheckItem` with `proxy_ok` and `proxy_expired` always `pass`, `fail`, or `skip`, never `na`.

- [ ] **Step 1: Write the failing media-account checks**

```go
func TestServiceAccountCheckReportsCheckedActiveProxy(t *testing.T) {
    // fake resolver returns bound=true, active/ok, future expiry.
    // ApplyLocalAccountCheckResult must return proxy_ok=pass and proxy_expired=pass.
}

func TestServiceAccountCheckReportsMissingOrUnhealthyProxy(t *testing.T) {
    // Table cases: unbound -> proxy_ok fail + proxy_expired skip;
    // paused -> both fail; expired -> both fail; unchecked -> proxy_ok fail + proxy_expired pass.
}
```

- [ ] **Step 2: Run the focused test to verify RED**

Run: `go test ./internal/modules/mediaaccount -run 'TestServiceAccountCheckReports' -count=1`

Expected: FAIL because proxy facts are not resolved and current results are `na`.

- [ ] **Step 3: Extend the narrow read model and synthesis code**

```go
type ProfileFactResolver interface {
    ResolveProfileForAccountCheck(string) (string, identity.UserID, string, bool, bool, error)
    ResolveProxyForAccountCheck(string) (string, string, string, *time.Time, bool, error)
}

// Profilebinding query joins browser_profiles.proxy_id to proxy_configs and
// returns only proxy ID, business status, last check, and expiry -- never secrets.
// ApplyLocalAccountCheckResult resolves the fact before mergeCheckItems.
```

Make `proxy_ok` pass only for an existing formal binding with `active` and `ok`; make `proxy_expired` pass for an active, non-expired proxy, fail for paused/expired, and skip only when no proxy is configured.

- [ ] **Step 4: Run the focused test to verify GREEN**

Run: `go test ./internal/modules/mediaaccount -run 'TestServiceAccountCheckReports' -count=1`

Expected: PASS.

- [ ] **Step 5: Run the module regression tests**

Run: `go test ./internal/modules/mediaaccount ./internal/modules/profilebinding -count=1`

Expected: PASS.

- [ ] **Step 6: Commit Cloud account-check facts**

```bash
git -C wt-media-cloud add internal/app/app.go internal/modules/mediaaccount internal/modules/profilebinding
git -C wt-media-cloud commit -m "feat: derive account proxy checks from bound profile facts"
```

### Task 2: Recommended and batch proxy assignment API

**Files:**
- Modify: `wt-media-cloud/internal/modules/proxy/routes.go:20-120,520-625`
- Modify: `wt-media-cloud/internal/modules/proxy/routes_test.go:237-313,503-563`
- Test: `wt-media-cloud/internal/modules/proxy/routes_test.go`

**Interfaces:**
- Consumes: existing `POST /api/v1/proxies/:id/assign` semantics and `ProfileProxyBinder`.
- Produces: `POST /api/v1/proxies/:id/assign-batch` body `{ "profile_ids": ["..."] }`, response `{ "succeeded": [BrowserProfile], "failed": [{ "profile_id": "...", "message": "..." }] }`.
- Produces: `GET /api/v1/proxies/recommendations?profile_ids=id1,id2`, returning only candidates whose formal quota can cover every selected Profile that is not already bound to that proxy.

- [ ] **Step 1: Write failing route tests**

```go
func TestBatchAssignMutatesEachAuthorizedProfileAndReturnsReadback(t *testing.T) {
    // two active profiles, capacity 2, matching Agent readback for each.
    // Expect 200, two succeeded, two BindProxy calls, no failure.
}

func TestBatchAssignReturnsPerProfileFailureWithoutBindingThatProfile(t *testing.T) {
    // second Agent response fails readback. Expect first success, second failure,
    // and no formal bind for second profile.
}

func TestRecommendationsRequireEnoughCheckedActiveCapacity(t *testing.T) {
    // Include checked/future/capacity candidate and exclude unchecked, paused,
    // expired, and insufficient-capacity candidates.
}
```

- [ ] **Step 2: Run focused route tests to verify RED**

Run: `go test ./internal/modules/proxy -run 'Test(BatchAssign|Recommendations)' -count=1`

Expected: FAIL because neither endpoint exists.

- [ ] **Step 3: Extract the single assign operation and expose batch/recommendations**

```go
func assignProfileProxy(ctx context.Context, actor identity.PublicUser, proxy ProxyConfig,
    profileID string, profiles ProfileLookup, bindings ProfileProxyBinder,
    mutator SyncProxyMutator, service *Service) (profilebinding.BrowserProfile, error)
```

The existing single route calls this helper unchanged. The batch route normalizes and deduplicates IDs, processes in request order, records a safe per-Profile error, and continues. The recommendation route validates only Profile IDs owned by the authenticated operator, calculates required new bindings per candidate, then calls the same `CheckAssignable` and capacity rules.

- [ ] **Step 4: Run focused route tests to verify GREEN**

Run: `go test ./internal/modules/proxy -run 'Test(BatchAssign|Recommendations)' -count=1`

Expected: PASS.

- [ ] **Step 5: Run proxy module regression tests**

Run: `go test ./internal/modules/proxy -count=1`

Expected: PASS.

- [ ] **Step 6: Commit Cloud proxy batch API**

```bash
git -C wt-media-cloud add internal/modules/proxy
git -C wt-media-cloud commit -m "feat: add recommended batch proxy binding"
```

### Task 3: Desktop batch recommendation and confirmation UI

**Files:**
- Modify: `wt-media-cloud/web/src/shared/api/proxy.js:1-58`
- Modify: `wt-media-cloud/web/src/modules/profiles/pages/ProfilesPage.vue:38-84,366-413,465-506,862-997`
- Modify: `wt-media-cloud/web/src/proxyOperationBoundary.test.js:1-42`
- Create: `wt-media-cloud/web/src/proxyClient.test.js`

**Interfaces:**
- Consumes: `proxyClient.recommend(profileIds)` and `proxyClient.assignBatch(proxyId, profileIds)`.
- Produces: a Desktop-only “批量绑定代理” action using selected active profiles; its dialog presents Cloud recommendations, permits an explicit manual eligible proxy selection, and requires a user confirmation click before mutation.

- [ ] **Step 1: Write failing API/client and operation-boundary tests**

```js
it('requests recommendations and batch assignment with cookie credentials', async () => {
  await client.recommend(['profile-1', 'profile-2'])
  await client.assignBatch('proxy-1', ['profile-1', 'profile-2'])
  expect(fetch).toHaveBeenCalledWith('/api/v1/proxies/recommendations?profile_ids=profile-1%2Cprofile-2', expect.anything())
  expect(JSON.parse(fetch.mock.calls[1][1].body)).toEqual({ profile_ids: ['profile-1', 'profile-2'] })
})
```

Add boundary assertions for the batch button, recommendation API and `assignBatch`; retain assertions that Cloud Web has no BitBrowser mutation entry.

- [ ] **Step 2: Run focused Web tests to verify RED**

Run: `npm test -- --run src/proxyClient.test.js src/proxyOperationBoundary.test.js`

Expected: FAIL because the client and UI references do not exist.

- [ ] **Step 3: Implement the minimal Desktop-only dialog**

```js
async function openBatchProxyBinding() {
  const targets = selectedProfilesForProxyBinding()
  const candidates = await proxyClient.recommend(targets.map(({ id }) => id))
  // Show recommendation first; retain all server-eligible alternatives for manual adjustment.
}

async function confirmBatchProxyBinding() {
  const result = await proxyClient.assignBatch(batchProxyId.value, selectedProfileIds.value)
  taskNotice.value = `批量绑定完成：成功 ${result.succeeded.length} 个，失败 ${result.failed.length} 个。`
}
```

Do not offer batch unbind in this task. Disable the action outside Desktop or with no eligible selected Profiles. Clear selection after the user-visible summary and reload Cloud profiles.

- [ ] **Step 4: Run focused Web tests to verify GREEN**

Run: `npm test -- --run src/proxyClient.test.js src/proxyOperationBoundary.test.js`

Expected: PASS.

- [ ] **Step 5: Run relevant Web tests and build**

Run: `npm test -- --run src/proxy.test.js src/proxyOperationBoundary.test.js src/profileBindings.test.js src/proxyClient.test.js && npm run build:cloud && npm run build:desktop`

Expected: all tests and both builds PASS.

- [ ] **Step 6: Commit Web batch binding UI**

```bash
git -C wt-media-cloud add web/src/shared/api/proxy.js web/src/modules/profiles/pages/ProfilesPage.vue web/src/proxyClient.test.js web/src/proxyOperationBoundary.test.js
git -C wt-media-cloud commit -m "feat: add desktop batch proxy recommendation"
```

### Task 4: Real local chain verification and governance checkpoint

**Files:**
- Modify: `wt-media-workspace/delivery/active/CHG-20260805-033/change.md:84-90`
- Create: `wt-media-workspace/delivery/active/CHG-20260805-033/evidence/2026-09-12-m2-c-proxy-closure.md`

**Interfaces:**
- Consumes: packaged Desktop, Local Agent and a dedicated disposable real Profile/proxy fixture.
- Produces: evidence for checked candidate selection, assign/readback, replacement, unbind/readback, account check items 3/4, and batch results.

- [ ] **Step 1: Identify or create an isolated M2-C fixture without exposing secrets**

Use the existing operator identity and a dedicated test Profile/proxy only. Record IDs in evidence only after masking them; do not mutate a customer Profile or a proxy with unknown owner.

- [ ] **Step 2: Verify candidate eligibility and batch capacity over the real APIs**

Expected: the recommendation response includes only checked, active, unexpired candidates with enough remaining capacity.

- [ ] **Step 3: Execute assign, replacement, unbind and batch binding via Desktop**

Expected: every successful row is read back from BitBrowser and reflected in `browser_profiles`; failed rows remain unbound/unchanged and display their reason.

- [ ] **Step 4: Run a real existing-account check bound to the fixture profile**

Expected: `proxy_ok` and `proxy_expired` are never `na` and match the formal relationship/readback fact.

- [ ] **Step 5: Record evidence and update the CHG checkpoint**

Mark only completed behavior as verified. If a real supplier proxy is unavailable, retain that as an explicit remaining acceptance item rather than treating unit tests as external-effect evidence.

- [ ] **Step 6: Commit workspace governance/evidence separately**

```bash
git -C wt-media-workspace add delivery/active/CHG-20260805-033 delivery/milestones/M2-account-runtime.md delivery/MASTER_IMPLEMENTATION_PLAN.md docs/superpowers/plans/2026-09-12-m2-c-proxy-closure.md
git -C wt-media-workspace commit -m "docs: record M2-C proxy closure verification"
```

## Self-Review

1. **Spec coverage:** Task 1 closes account-check items 3/4; Task 2 provides recommendation and one-proxy/multi-Profile reuse of the existing mutation path; Task 3 makes recommendation/manual adjustment/confirmation visible in Desktop; Task 4 covers external effect, readback and CHG evidence. M2-D is explicitly excluded.
2. **Placeholder scan:** No TBD/TODO implementation placeholders remain; every task declares exact target paths, API signatures, failing-test command, and verification command.
3. **Type consistency:** The profile proxy fact uses primitives shared by `mediaaccount` and `profilebinding`; batch Vue API names match the Cloud route contract (`recommend`, `assignBatch`, `profile_ids`).

