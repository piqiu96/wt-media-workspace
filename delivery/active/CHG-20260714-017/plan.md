# M2-C3 BitBrowser User and Profile Binding Implementation Plan

> **For agentic workers:** Execute inline with `executing-wt-media-change`; each layer starts with a failing focused test and ends with evidence/checkpoint/independent repository commits.

**Goal:** Produce a safe staged binding flow from an Agent-owned, secret-free BitBrowser Profile scan to confirmed Cloud user/Profile facts and same-owner media-account binding.

**Architecture:** Agent owns `/browser/list` integration and normalizes only allow-listed Profile facts. Cloud owns staged scan/Diff persistence and formal Profile mirrors; authenticated users explicitly confirm only their own ready scans. C4/C5 later add node attestation and sensitive-task runtime enforcement.

**Tech Stack:** Python 3.12 stdlib HTTP/unittest; Go/Hertz/MySQL/sqlmock; Vue/Vitest; YAML contracts.

## Global Constraints

- Normalize BitBrowser `userId`, not `operUserId`, to `owner_user_id`.
- Never transport/store Profile Cookie, password, proxy username, proxy password, or raw response blobs.
- Scan has no formal effect before confirmation.
- No automatic rebind or local Profile delete.
- No sensitive task authorization claim before C4/C5.

### Task 1: Agent BitBrowser adapter

**Files:** create `src/wt_media_agent/runtimes/bitbrowser.py`; create `tests/test_bitbrowser_runtime.py`; modify Agent config.

- [ ] Write failing tests for zero-based 100-item paging, error/timeout JSON handling, field allow-listing, and uniform `userId` validation.
- [ ] Run `uv run pytest tests/test_bitbrowser_runtime.py -q` and confirm missing module failure.
- [ ] Implement injectable HTTP transport, typed snapshot/Profile values, and explicit errors.
- [ ] Re-run focused tests and require PASS.

### Task 2: Agent Local API and provider contracts

**Files:** modify `local_api/server.py`; add `contracts/local-agent-api/v1/local-agent.openapi.yaml`, event/status/error v1 files; modify tests/readmes.

- [ ] Add failing Local API tests for Profile scan success and unavailable/mismatch errors.
- [ ] Implement `POST /api/v1/bit-browser/profile-scans` without exposing the configured Bit API URL or raw response.
- [ ] Publish actual M1 health/status/events plus C3 scan definitions at revision `2026.07.14.6`.
- [ ] Run Agent full tests, Ruff, contract YAML parse, and real local health verification.

### Task 3: Cloud staged binding domain and persistence

**Files:** create `internal/modules/profilebinding/{service,store_mysql}.go` plus tests; add migration `20260714_003_browser_profiles.sql`; extend identity/media-account persistence only through explicit interfaces.

- [ ] Write failing service tests for ready/mixed/empty/mismatch scans, no pre-confirm writes, self-confirm, Diff apply, and no rebind.
- [ ] Implement domain service and safe public values.
- [ ] Write failing sqlmock/migration tests, then implement transactionally confirmed binding/Profile upsert/missing-state apply.
- [ ] Require focused and full Go tests PASS.

### Task 4: Cloud API, media-account binding, Web, and provider contracts

**Files:** add profile routes/tests/contracts and Web client/tests; extend media-account service/store/routes and migration constraints.

- [ ] Add failing authenticated route tests for submit/review/confirm and same-user Profile binding.
- [ ] Implement routes using C1 session identity; do not accept an actor ID body field.
- [ ] Add failing Vitest client tests for scan review/confirm and secret stripping; implement minimal review UI.
- [ ] Publish Cloud revision `2026.07.14.3` and run Go/Web/YAML/security gates.

### Task 5: Governance and closure

**Files:** update Contract Map/release matrix/verifier, CHG evidence/checkpoint, then active delivery.

- [ ] Change governance data first and observe the old verifier reject the new revisions.
- [ ] Update verifier and run all Workspace tests.
- [ ] Record provider conflict repair, red/green evidence, no-live-BitBrowser limitation, and commits.
- [ ] Close only with all ACs PASS and activate C4 under the user's continuous-execution authorization.
