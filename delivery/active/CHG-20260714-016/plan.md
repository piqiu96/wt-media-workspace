# M2-C2 Media Account Model and Assignment Implementation Plan

> **For agentic workers:** Execute inline under `executing-wt-media-change`; every task uses red-green TDD, records evidence, updates the checkpoint, and commits the affected repository independently.

**Goal:** Deliver a Cloud-owned media-account model and authenticated management flow with direct user/game ownership, safe identification, user-scoped deduplication, and simple tags.

**Architecture:** A focused `internal/modules/mediaaccount` package owns domain rules and a Store interface. `MySQLStore` persists accounts/tags, Hertz routes authenticate through the existing identity service, and the Vue client communicates only with `/api/v1/media-accounts` using the HttpOnly session cookie.

**Tech Stack:** Go 1.24+/CloudWeGo Hertz/MySQL 8/sqlmock; Vue 3/Vite/Vitest; YAML provider contracts.

## Global Constraints

- Cloud MySQL is the formal source for users and `media_account`.
- Ordinary and senior operators remain restricted to their own `user_id` and configured `game_id` scopes.
- Technicians have global Cloud authorization but cannot bypass future local Profile/Cookie boundaries.
- Never return Cookie values in account JSON, logs, audits, or list filters.
- Do not implement C3-C5 Profile, BitBrowser, Agent-runtime, or concurrency behavior.

---

### Task 1: Domain lifecycle and authorization

**Files:**
- Create: `wt-media-cloud/internal/modules/mediaaccount/service.go`
- Create: `wt-media-cloud/internal/modules/mediaaccount/service_test.go`

**Interfaces:**
- Consume `identity.PublicUser`, role constants, and opaque game IDs.
- Produce `Service.CreateAccount`, `GetAccount`, `ListAccounts`, `UpdateAccount`, and `IdentifyAccount` plus public `Account` values with no Cookie fields.

- [ ] Write table-driven tests for own/global access, game scope, one-game validation, pending creation, independent status validation, safe identification, and user-scoped duplicate handling.
- [ ] Run `go test ./internal/modules/mediaaccount -run 'TestService' -count=1` and observe compile/test failure because the service does not exist.
- [ ] Implement only the domain types, Store interface, authorization helpers, lifecycle, and duplicate behavior required by those tests.
- [ ] Re-run the focused command and require PASS.
- [ ] Review the diff for Cookie exposure or C3 behavior and record the red/green output in evidence.

### Task 2: Tags and filtering

**Files:**
- Modify: `wt-media-cloud/internal/modules/mediaaccount/service.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/service_test.go`

**Interfaces:**
- Produce `Service.AddTags(actor, accountIDs, tags)`, `RemoveTags(...)`, and `AccountFilter{AnyTags, AllTags, ExcludeTags}`.

- [ ] Add failing tests for tag normalization/uniqueness, ownership enforcement, bulk add/remove, and any/all/exclude semantics.
- [ ] Run the focused tests and confirm the new cases fail for missing behavior.
- [ ] Implement minimal tag rules and Store calls without a global tag model.
- [ ] Re-run focused tests and require PASS.

### Task 3: MySQL persistence and schema

**Files:**
- Create: `wt-media-cloud/internal/modules/mediaaccount/store_mysql.go`
- Create: `wt-media-cloud/internal/modules/mediaaccount/store_mysql_test.go`
- Create: `wt-media-cloud/migrations/20260714_002_media_accounts.sql`
- Modify: `wt-media-cloud/migrations/README.md`

**Interfaces:**
- `MySQLStore` implements the Task 1/2 Store interface.
- Migration creates `media_accounts` and `media_account_tags`, preserves secret columns, and enforces account/tag uniqueness without introducing a Profile foreign key before C3.

- [ ] Write sqlmock tests for insert, lookup/list filters, update/identify conflict, and tag transactions.
- [ ] Run `go test ./internal/modules/mediaaccount -run 'TestMySQLStore' -count=1` and observe failure because `NewMySQLStore` is absent.
- [ ] Implement SQL persistence and migration with deterministic ordering.
- [ ] Re-run focused and package tests and require PASS.

### Task 4: Authenticated API and app wiring

**Files:**
- Create: `wt-media-cloud/internal/modules/mediaaccount/routes.go`
- Create: `wt-media-cloud/internal/modules/mediaaccount/routes_test.go`
- Modify: `wt-media-cloud/internal/modules/identity/routes.go`
- Modify: `wt-media-cloud/internal/app/app.go`
- Modify: `wt-media-cloud/internal/app/identity_test.go`

**Interfaces:**
- Expose `POST/GET /api/v1/media-accounts`, `GET/PATCH /api/v1/media-accounts/:id`, `POST /:id/identify`, `POST /tags/add`, and `POST /tags/remove`.
- Reuse identity Cookie authentication through an exported authenticator; do not accept actor IDs from request bodies.

- [ ] Write failing route tests for authentication, ownership/game scope, status update, duplicate conflict, tag filters, and secret-free responses.
- [ ] Run focused route tests and confirm missing route/wiring failure.
- [ ] Implement handlers, error mapping, and server wiring.
- [ ] Re-run route tests and the full Go suite; require PASS.

### Task 5: Cloud Web flow and provider contracts

**Files:**
- Create: `wt-media-cloud/web/src/mediaAccounts.js`
- Create: `wt-media-cloud/web/src/mediaAccounts.test.js`
- Modify: `wt-media-cloud/web/src/App.vue`
- Create: `wt-media-cloud/contracts/cloud-api/v1/media-accounts.openapi.yaml`
- Create: `wt-media-cloud/contracts/business-schemas/v1/media-account.yaml`
- Create: `wt-media-cloud/contracts/business-enums/v1/media-account.yaml`
- Create: `wt-media-cloud/contracts/cloud-error-codes/v1/media-account.yaml`
- Modify provider README files.

**Interfaces:**
- Web methods always use `credentials: include`, render no Cookie values, and support list/create/tag actions.
- Contracts match route names, enum values, response envelopes, authorization and conflict errors.

- [ ] Write failing Vitest cases for request credentials, filters, create payloads, and absence of browser storage/Cookie response parsing.
- [ ] Run `npm test -- --run` and observe the missing module failure.
- [ ] Implement client and minimal authenticated UI; publish YAML definitions.
- [ ] Run Web tests/build, YAML parsing, Go tests, health verification, and npm audit.

### Task 6: Governance, evidence, and closure

**Files:**
- Modify: `wt-media-workspace/config/contract-map.yaml`
- Modify: `wt-media-workspace/config/release-matrix.yaml`
- Modify: `wt-media-workspace/scripts/verify_m0_config.py`
- Modify: `wt-media-workspace/delivery/active/CHG-20260714-016/change.md`
- Add evidence files under `delivery/active/CHG-20260714-016/evidence/`.

- [ ] First update contract/release data and observe the old config verifier fail on the new expected state.
- [ ] Update the verifier and run all Workspace gates.
- [ ] Record red/green, test/build/audit, diff, limitations, and independent commit facts.
- [ ] Mark every AC PASS only from fresh evidence; commit Cloud and Workspace independently.
- [ ] Remove completed CHG-016 from active/ledger and activate C3 under the user's continuous-execution authorization.
