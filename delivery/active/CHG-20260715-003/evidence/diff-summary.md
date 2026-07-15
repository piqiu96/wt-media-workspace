# M0-R2 Diff Summary

- Change: CHG-20260715-003
- Date: 2026-07-15

## Cloud Commit

Commit: `db5b951` (`feat: add cloud migration runner and m0 scripts`)

| Path | Reason |
|---|---|
| `cmd/migrate/main.go` | Adds executable migration command using `WT_MEDIA_MYSQL_DSN`. |
| `internal/modules/migration/runner.go` | Adds migration loader and repeat-safe runner. |
| `internal/modules/migration/runner_test.go` | Adds tests for ordered load and pending-only execution. |
| `scripts/bootstrap.sh` | Adds real dependency bootstrap. |
| `scripts/test.sh` | Adds real Go/Web test entry. |
| `scripts/build.sh` | Adds real Go/Web build entry. |
| `scripts/migrate.sh` | Adds migration script entry. |
| `scripts/start.sh` | Adds start script with health wait. |
| `scripts/health.sh` | Adds health probe script. |
| `scripts/stop.sh` | Adds PID-file stop script. |
| `scripts/verify-health.sh` | Adds GOPATH cache override support. |
| `README.md`, `scripts/README.md`, `migrations/README.md`, `web/README.md` | Documents M0-R2 command usage. |

## Workspace Changes

| Path | Reason |
|---|---|
| `delivery/LEDGER.md` | Active CHG switched from CHG-20260715-002 to CHG-20260715-003. |
| `delivery/MASTER_IMPLEMENTATION_PLAN.md` | M0 Active CHG updated to CHG-20260715-003. |
| `delivery/active/CHG-20260715-002/**` | Removed completed active R1 record from active directory. |
| `delivery/active/CHG-20260715-003/**` | Adds M0-R2 change, plan and evidence. |

## Scope Check

| Repository | Tracked Changes |
|---|---|
| `wt-media-cloud` | Committed as `db5b951`. |
| `wt-media-workspace` | Pending evidence/checkpoint commit. |
| `wt-media-agent` | None. |
| `wt-media-desktop` | None. |
