# M0-R3 Diff Summary

- Change: CHG-20260715-004
- Date: 2026-07-15

## Agent Commit

Commit: `2b65ac5` (`feat: add agent storage migration and m0 scripts`)

| Path | Reason |
|---|---|
| `pyproject.toml` | Adds `wt-media-agent-storage-migrate` package entry. |
| `uv.lock` | Adds dependency lock for repeatability. |
| `src/wt_media_agent/storage/migration.py` | Adds repeat-safe SQLite storage migration runner. |
| `tests/test_storage_migration.py` | Adds migration repeat test. |
| `scripts/bootstrap.sh` | Adds real Agent bootstrap script. |
| `scripts/test.sh` | Adds real Agent test script. |
| `scripts/build.sh` | Adds real Agent build script. |
| `scripts/migrate-storage.sh` | Adds SQLite migration script. |
| `scripts/start-health.sh`, `scripts/health.sh`, `scripts/stop-health.sh` | Adds Local Agent health process scripts. |
| `README.md`, `scripts/README.md` | Documents M0-R3 command usage. |

## Workspace Changes

| Path | Reason |
|---|---|
| `delivery/LEDGER.md` | Active CHG switched from CHG-20260715-003 to CHG-20260715-004. |
| `delivery/MASTER_IMPLEMENTATION_PLAN.md` | M0 Active CHG updated to CHG-20260715-004. |
| `delivery/active/CHG-20260715-003/**` | Removed completed active R2 record from active directory. |
| `delivery/active/CHG-20260715-004/**` | Adds M0-R3 change, plan and evidence. |

## Scope Check

| Repository | Tracked Changes |
|---|---|
| `wt-media-agent` | Committed as `2b65ac5`. |
| `wt-media-workspace` | Pending evidence/checkpoint commit. |
| `wt-media-cloud` | None. |
| `wt-media-desktop` | None. |
