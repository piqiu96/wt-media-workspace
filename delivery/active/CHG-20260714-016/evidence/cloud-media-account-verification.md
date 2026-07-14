# Evidence: Cloud Media Account Verification

- CHG: `CHG-20260714-016`
- Task: `T-02` through `T-05`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Purpose

Prove C2 domain, persistence, API, Web, contracts, and secret boundaries behave as accepted.

## Method

Red evidence was observed before each implementation layer:

- domain: Go failed with undefined `Service`, `Store`, `AccountFilter`, and related types;
- MySQL: Go failed with undefined `MySQLStore` and `NewMySQLStore`;
- routes: Go failed with undefined `RegisterRoutes`;
- Web: Vitest failed because `mediaAccounts.js` did not exist;
- governance: the old verifier rejected `m2_media_accounts` and contract revision `2026.07.14.2`.

Fresh green commands after commits `18f687a` and `8eb70ba`:

```text
GOCACHE="$PWD/.cache/go-build" ../../devenv/go26/go/bin/go test ./... -count=1
GOCACHE="$PWD/.cache/go-build" ../../devenv/go26/go/bin/go vet ./...
cd web && npm test -- --run
cd web && npm run build
cd web && npm audit --audit-level=high
ruby YAML parse for contracts/**/*.yaml
GO_BIN=../../devenv/go26/go/bin/go scripts/verify-health.sh
```

## Expected

All automated checks pass, public responses omit Cookie values, and the runtime health process starts successfully.

## Actual

- Every Go package passed; media-account domain/store/route tests are green and `go vet` reported no issues.
- Vitest passed 5/5 tests and Vite produced the production bundle.
- npm audit reported 0 vulnerabilities.
- All 12 contract YAML files parsed successfully.
- Real-process verification printed `wt-media-cloud health ok`.
- Secret tests prove public Account JSON and audit summaries contain neither Cookie values nor Cookie fields.

## Follow-Up

- No local MySQL daemon was available. SQL behavior is covered with deterministic sqlmock expectations and migration invariant tests; C6 must execute the migration and end-to-end flow against real MySQL.
