# M2-A Permissions and Acceptance Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task with checkpoints.

**Goal:** Restore trustworthy M2 gates and complete permission/session/audit behavior so M2-A can pass its role, scope, and session-safety acceptance matrix.

**Architecture:** Keep authorization in Cloud identity and business services, keep Local Agent execution state in Agent, and keep Desktop out of Cloud business rules. Every M2-A change is tested at the service/route boundary and then verified through the existing Cloud-Agent contracts; no M2-B/C/D/E business object is added.

**Tech Stack:** Go 1.26 + Hertz + MySQL stores/tests; Vue 3/Vite/Vitest; Python 3.12 Agent; workspace Python governance scripts; Markdown evidence/checkpoints.

## Global Constraints

- Cloud owns formal users, game scopes, audit records, and Cloud contracts.
- Agent never connects to Cloud MySQL and must stop new claims after its bound Cloud session is invalidated.
- Do not persist or print real Cookie, SMS, proxy, node, binding-ticket, or Profile-permit credentials.
- Do not modify an existing BitBrowser Profile in M2-A; the disposable Profile is reserved for later M2-C/D/E acceptance.
- Do not create M3+ tables, endpoints, task types, or placeholder business objects.
- Every repository change ends with its own tests, diff check, evidence, checkpoint, and independent commit.

---

### Task 1: Establish the M2-A Active CHG and baseline evidence

**Files:**
- Create: `wt-media-workspace/delivery/active/CHG-20260721-M2A/change.md`
- Create: `wt-media-workspace/delivery/active/CHG-20260721-M2A/evidence/`
- Modify: `wt-media-workspace/delivery/LEDGER.md`
- Reference: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`

**Interfaces:**
- Produces the sole active change record consumed by all later M2-A tasks.
- Status starts `IN_PROGRESS`; `## 7. Pending Questions` must contain `None.`.

- [ ] **Step 1: Record the start gate**

Write the CHG with scope limited to Web test infrastructure, governance validators, Cloud authorization/audit, and Agent invalid-session behavior. Record current dirty files in all affected repositories and explicitly exclude unrelated generated artifacts.

- [ ] **Step 2: Run the baseline checks**

Run:

```bash
cd wt-media-cloud && /Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go test ./...
cd web && npm test -- --run
cd ../../wt-media-agent && PYTHONPATH=src python3 -m unittest discover -s tests
cd ../wt-media-workspace && python3 scripts/verify_m2_acceptance.py
```

Expected: Cloud and Agent pass; current Web and governance failures are captured as baseline evidence, not hidden.

- [ ] **Step 3: Update checkpoint and commit workspace governance**

Record completed baseline, current task, next task, blockers, and exact command results in `change.md`; commit only the new active CHG and ledger row in the workspace repository.

### Task 2: Repair Web API-client test base URL injection

**Files:**
- Modify: `wt-media-cloud/web/src/shared/api/http.js`
- Modify: `wt-media-cloud/web/src/session.test.js`
- Modify: `wt-media-cloud/web/src/profileBindings.test.js`
- Modify: `wt-media-cloud/web/src/mediaAccounts.test.js`
- Test: the three files above with Vitest

**Interfaces:**
- `createApiClient({ base, fetchImpl })` remains backward-compatible for browser callers.
- Tests provide an absolute base such as `http://test.local/api/v1` or a fetch mock that accepts relative paths.

- [ ] **Step 1: Add a failing regression assertion**

Add a test assertion that the client can invoke a mocked fetch with the configured absolute base and still sends `credentials: "include"`; run `npm test -- --run` and capture the current `ERR_INVALID_URL` failure.

- [ ] **Step 2: Implement the smallest test-safe URL resolution**

Resolve `base + path` through one helper in `http.js`. Keep production browser behavior unchanged for `/api/v1`; allow tests to pass an absolute `base` without reading process-global state.

- [ ] **Step 3: Run Web tests**

Run `npm test -- --run` from `wt-media-cloud/web`. Expected: all existing API-client tests pass, including HttpOnly-cookie behavior, sanitized Profile snapshots, encoded tag filters, and Cookie field exclusion.

- [ ] **Step 4: Commit Cloud Web test fix**

Run `git diff --check`, then commit only the Web client and test files with message `test(web): restore api client test base url`.

### Task 3: Make governance validators current and deterministic

**Files:**
- Modify: `wt-media-workspace/scripts/verify_m2_acceptance.py`
- Modify: `wt-media-workspace/scripts/verify_product_master_alignment.py`
- Modify: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md` only if a validator assertion reflects a confirmed current baseline
- Test: `wt-media-workspace/scripts/verify_m2_acceptance.py`
- Test: `wt-media-workspace/scripts/verify_product_master_alignment.py`

**Interfaces:**
- Validators report actionable `ERROR:` lines and exit 1; they never crash on a missing path.
- Desktop path checks use the current Tauri/Cloud unified frontend architecture.
- M0/M1/M2 assertions match the current Master Plan and the five-closure M2 plan.

- [ ] **Step 1: Add validator regression tests**

Add a lightweight Python test or fixture-driven test for: current Desktop path exists, missing path reports an error, and current milestone states are accepted. Run the focused test before changing validators.

- [ ] **Step 2: Update path and state assertions**

Replace the removed `wt-media-desktop/src/services/local-agent.js` requirement with checks for the current Rust bridge and unified frontend files. Change only assertions confirmed by the current plan; do not weaken contract or secret checks.

- [ ] **Step 3: Run both validators**

Run:

```bash
python3 scripts/verify_m2_acceptance.py
python3 scripts/verify_product_master_alignment.py
```

Expected: both produce deterministic, reviewable output. If a genuine governance mismatch remains, record it as a blocking question instead of masking it.

- [ ] **Step 4: Commit workspace validator changes**

Run `git diff --check`, update the active CHG checkpoint, and commit only validator/test changes with message `test(workspace): align M2 acceptance gates`.

### Task 4: Enforce game-scope authorization at every M2 business entry point

**Files:**
- Modify: `wt-media-cloud/internal/modules/mediaaccount/service.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/routes.go` only if service authorization cannot cover an entry point
- Modify: `wt-media-cloud/internal/modules/profilebinding/service.go`
- Modify: `wt-media-cloud/internal/modules/profilebinding/routes.go` only if needed for explicit game scope
- Modify: `wt-media-cloud/internal/modules/proxy/routes.go` and `service.go` where a user/game-scoped operation is exposed
- Test: `wt-media-cloud/internal/modules/mediaaccount/routes_test.go`
- Test: `wt-media-cloud/internal/modules/profilebinding/routes_test.go`
- Test: new focused proxy authorization test if proxy operations are user-owned rather than game-scoped

**Interfaces:**
- `identity.Service.CanAccessGame(userID, gameID) bool` is the only Cloud game-scope decision source.
- Unauthorized operations return the existing 403/error envelope and do not mutate stores or append success audits.

- [ ] **Step 1: Add negative route tests**

Create an operator scoped to `game-a`, issue a valid session, and assert requests against `game-b` return 403 for media-account create/list/update/identify and Profile-linked operations. Assert no store mutation occurs.

- [ ] **Step 2: Implement centralized service checks**

At the start of each mutating or reading service method that accepts a game-scoped record, load the record/game ID and call `CanAccessGame`. Return the module's existing forbidden error before any external side effect or store update.

- [ ] **Step 3: Run focused Cloud tests**

Run:

```bash
/Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go test ./internal/modules/identity ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/proxy
```

Expected: positive authorized operations continue to pass; cross-game reads and writes are rejected.

- [ ] **Step 4: Commit Cloud authorization changes**

Run `git diff --check`, record evidence and checkpoint, and commit with message `fix(cloud): enforce M2 game scope at business boundaries`.

### Task 5: Stop invalidated Local Agent sessions safely

**Files:**
- Modify: `wt-media-cloud/internal/modules/cloudagent/mysql_registry.go`
- Modify: `wt-media-cloud/internal/modules/cloudagent/routes.go`
- Modify: `wt-media-agent/src/wt_media_agent/cloud_agent_client.py`
- Modify: `wt-media-agent/src/wt_media_agent/runner.py`
- Test: `wt-media-cloud/internal/modules/cloudagent/registry_test.go`
- Test: `wt-media-agent/tests/test_cloud_agent_client.py`
- Test: `wt-media-agent/tests/test_noop_executor.py` or a new focused runner test

**Interfaces:**
- Cloud heartbeat returns the existing session-invalid error envelope and marks the local node draining/replaced.
- Agent treats session invalidation as a terminal control signal for new claims, drains active work, and reports uncertainty when an external effect may have occurred.

- [ ] **Step 1: Add failing invalidation tests**

Assert a local node with an invalidated session cannot heartbeat online or claim another task. Assert an Agent client maps the Cloud error to a session-invalid control result rather than retrying indefinitely.

- [ ] **Step 2: Implement Cloud drain behavior**

Keep the existing database session join, but make the state transition and response deterministic. Ensure a repeated heartbeat remains idempotent and never reactivates the node.

- [ ] **Step 3: Implement Agent drain behavior**

Stop the claim loop after the session-invalid signal, allow the current executor to reach a safe checkpoint, and mark a possibly externally effective action as uncertain instead of automatically retrying it.

- [ ] **Step 4: Run Cloud and Agent tests**

Run the focused tests, then the complete suites:

```bash
/Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go test ./...
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Expected: all pass and no retry loop remains after session invalidation.

- [ ] **Step 5: Commit Cloud and Agent changes independently**

Commit Cloud first with `fix(cloud): drain invalidated local agent sessions`; commit Agent second with `fix(agent): stop claims after session invalidation`.

### Task 6: Add explicit BitBrowser binding/rebinding audit events

**Files:**
- Modify: `wt-media-cloud/internal/modules/profilebinding/service.go`
- Modify: `wt-media-cloud/internal/modules/profilebinding/store_mysql.go` only if the existing audit writer needs a typed summary
- Modify: `wt-media-cloud/internal/modules/profilebinding/service_test.go`
- Modify: `wt-media-cloud/internal/modules/profilebinding/store_mysql_test.go`
- Test: Profile binding route/service tests

**Interfaces:**
- Audit actions are stable strings: `bitbrowser.main_account.bind` for the first binding and `bitbrowser.main_account.rebind` for a deliberate replacement.
- Audit summaries contain only redacted identity facts and outcome; never Cookie, proxy password, node credentials, or raw BitBrowser payloads.

- [ ] **Step 1: Add failing audit assertions**

Assert first binding appends the bind action, a same-identity rescan is idempotent, and a changed identity cannot silently replace the bound main account. Assert audit JSON contains no secret field names or raw credential values.

- [ ] **Step 2: Implement explicit service audit actions**

Determine whether the operation is first bind, verified same identity, or rejected mismatch. Append the appropriate audit only after the formal Cloud update succeeds.

- [ ] **Step 3: Run Profile tests**

Run `/Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go test ./internal/modules/profilebinding ./internal/modules/identity` and expected all pass.

- [ ] **Step 4: Commit Cloud audit changes**

Run diff check, write evidence/checkpoint, and commit with message `feat(cloud): audit BitBrowser account binding changes`.

### Task 7: M2-A integrated verification and handoff

**Files:**
- Create: `wt-media-workspace/delivery/active/CHG-20260721-M2A/evidence/m2-a-automated-verification.md`
- Modify: `wt-media-workspace/delivery/active/CHG-20260721-M2A/change.md`
- Modify: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md` only after all M2-A exit conditions pass
- Modify: `wt-media-workspace/delivery/reports/M2-prd-chapter3-gap-matrix.md` with only verified M2-A row changes

**Interfaces:**
- Evidence lists command, expected result, actual result, status, repository commit, and any manual verification reference.
- M2-A remains `IN_PROGRESS` until automated and manual acceptance are complete; it may move to `VERIFYING` only after all evidence is present.

- [ ] **Step 1: Run all gates**

Run Cloud tests, Agent tests, Web tests, Desktop build/test, both workspace validators, `git diff --check`, and contract compatibility checks. Expected: all relevant gates pass.

- [ ] **Step 2: Perform role/session manual verification**

Use non-secret test users and game scopes to verify technician full access, operator allowed/denied games, disabled-user denial, 401 redirect, re-login invalidation, Agent draining, and audit visibility. Do not use the disposable Profile for M2-A external mutation.

- [ ] **Step 3: Record evidence and update checkpoint**

Record exact outputs and redacted identifiers. The checkpoint must list M2-A completed, M2-B as next, no blockers, and all recent verification results.

- [ ] **Step 4: Commit workspace evidence**

Commit only evidence, checkpoint, and confirmed baseline/matrix updates with message `docs: verify M2-A acceptance foundation`.

## Plan Self-Review

- Scope covers only M2-A; Profile mutation, proxy, Cookie, SMS, and Desktop Sidecar implementation remain in later CHGs.
- Every behavior has a concrete file mapping, focused test, full-suite command, and independent commit boundary.
- No task persists real credentials or treats fixture output as real-dependency evidence.
- The active CHG is not marked complete until manual role/session acceptance and all automated gates pass.
