# M2-C1 Identity Foundation Implementation Plan

> **For agentic workers:** Execute tasks sequentially with test-first verification and an independent commit after each completed deliverable.

**Goal:** Add Cloud-owned identity persistence, fixed-role authorization, one active browser session per user, and the public Cloud API contract needed by M2-C1.

**Architecture:** The `identity` Cloud module owns users, opaque server-side sessions, game-scope assignments, and audit summaries. It depends on a small repository interface whose MySQL implementation is used by runtime assembly; tests use a deterministic in-memory implementation. Hertz routes authenticate through the session cookie and delegate every authorization decision to the module.

**Tech Stack:** Go 1.20 module compiled with the configured Go 1.26.5 toolchain; Hertz; MySQL; bcrypt; OpenAPI v3; Vue 3/Vite for the Cloud Web login surface.

## Global Constraints

- Cloud MySQL is the formal source of users, sessions, roles, game scopes, and audit summaries.
- Roles are exactly `operator`, `senior_operator`, and `technician`; there is no custom RBAC or organization tree.
- A replacement login invalidates the preceding session; multiple tabs sharing the same cookie remain valid.
- Passwords and session tokens never enter API JSON, audit summaries, or logs.
- `game_id` is an opaque stable key in C1; no game catalog is added.
- Browser Profile, Cookie, proxy, Agent, and sensitive-task code remain outside C1.

## File Mapping

| File | Responsibility |
|---|---|
| `wt-media-cloud/migrations/20260714_001_identity.sql` | MySQL tables and uniqueness constraints for users, sessions, scopes, and audit records. |
| `wt-media-cloud/internal/infra/database/mysql.go` | Open/ping MySQL and expose a transactional execution boundary. |
| `wt-media-cloud/internal/modules/identity/*.go` | Identity domain types, repository interface, service, MySQL store, routes, and focused tests. |
| `wt-media-cloud/internal/middleware/auth.go` | Resolve the opaque session cookie and attach the authenticated actor to protected requests. |
| `wt-media-cloud/internal/app/app.go` | Wire the configured database and identity routes without altering Cloud-Agent routes. |
| `wt-media-cloud/contracts/cloud-api/v1/identity.openapi.yaml` | Cloud-owned C1 public API definition. |
| `wt-media-cloud/contracts/business-enums/v1/identity.yaml` | Fixed role and user-status enums. |
| `wt-media-cloud/contracts/business-schemas/v1/identity.yaml` | Public user/session-safe DTO definitions. |
| `wt-media-cloud/contracts/cloud-error-codes/v1/identity.yaml` | Stable authentication and authorization error codes. |
| `wt-media-cloud/web/*` | Login, current-user bootstrap, and an authenticated minimal shell; it does not duplicate authorization policy. |
| `wt-media-workspace/config/{contract-map.yaml,release-matrix.yaml}` | Mark the C1 Cloud contracts active only after verification. |

## Ordered Tasks

### Task 1: Persistence and domain service

1. Add failing tests for password verification, disabled-user rejection, replacement-session invalidation, and technician-only user administration.
2. Verify the tests fail because the `identity` module is absent.
3. Add the migration, repository interface, in-memory test store, bcrypt password service, fixed-role checks, scope assignments, and audit-summary redaction.
4. Run focused identity tests, then the full Cloud Go suite.
5. Commit the Cloud domain/persistence deliverable independently.

### Task 2: HTTP API and contract

1. Add failing route tests for login, logout, `me`, old-session rejection, technician user creation, password reset, and scope updates.
2. Add the public Cloud API, schema, enum, and error-code definitions before exposing routes.
3. Implement cookie parsing/issuance, authentication middleware, and identity routes; preserve existing Cloud-Agent endpoints unchanged.
4. Run focused route tests, the full Cloud Go suite, and the Cloud health verification.
5. Commit the Cloud contract/API deliverable independently.

### Task 3: Cloud Web and release evidence

1. Add failing Web tests for unauthenticated redirection and current-user rendering; keep credentials out of persisted browser state.
2. Implement the minimal Vue/Vite login and authenticated shell against the Cloud API; authorization stays server-side.
3. Run Web tests/build and the Cloud suite; update the owned-contract map and release matrix only with fresh successful evidence.
4. Record exact command output, diffs, and acceptance results under the active CHG.
5. Commit Workspace and Cloud Web changes independently, then close C1 only if all C1 acceptance criteria are PASS.

## Acceptance-to-Verification Mapping

| Acceptance criterion | Primary test |
|---|---|
| AC-01 password, status, no secret leakage | `go test ./internal/modules/identity -run 'Test.*(Password|Disabled|Audit)'` |
| AC-02 one active session | `go test ./internal/modules/identity -run TestSessionReplacementInvalidatesPriorSession` |
| AC-03 roles and game scopes | `go test ./internal/modules/identity -run 'Test.*(Role|GameScope)'` |
| AC-04 Cloud-enforced authorization | focused identity route tests plus Web unauthenticated-route tests |
| AC-05 owned contracts and regressions | contract-file validation, `go test ./...`, Cloud health verification, and Web build |
