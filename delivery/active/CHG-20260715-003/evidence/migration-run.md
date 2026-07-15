# M0-R2 Migration Run Evidence

- Change: CHG-20260715-003
- Date: 2026-07-15
- Cloud commit: `db5b951`

## Test-First Evidence

Command:

```text
GOCACHE=... go test ./internal/modules/migration
```

Expected result before implementation: fail because `LoadDir`, `Apply` and `Migration` do not exist.

Actual result before implementation:

```text
undefined: LoadDir
undefined: Apply
undefined: Migration
FAIL github.com/wt-media/wt-media-cloud/internal/modules/migration [build failed]
```

Status: PASS for RED.

After implementation, the same targeted package test passed:

```text
ok github.com/wt-media/wt-media-cloud/internal/modules/migration
```

Status: PASS for GREEN.

## Local MySQL Empty/Repeat Run

Database used for verification: `wt_media_m0_r2_verify`.

Command shape:

```text
WT_MEDIA_MYSQL_DSN='<local root DSN>/wt_media_m0_r2_verify?parseTime=true&loc=UTC' scripts/migrate.sh
```

First run actual result:

```text
migration ok: 5 applied, 5 total
applied 20260714_001_identity identity
applied 20260714_002_media_accounts media_accounts
applied 20260714_003_browser_profiles browser_profiles
applied 20260714_004_agent_runtime agent_runtime
applied 20260714_005_sensitive_profile_locks sensitive_profile_locks
```

Status: PASS.

Repeat run actual result:

```text
migration ok: 0 applied, 5 total
```

Status: PASS.

## Behavior Verified

- The migration command creates the DSN database when missing.
- Migrations are loaded from `migrations/*.sql` in lexical order.
- `schema_migrations` records applied versions.
- Repeat execution skips already applied versions.
- Real secrets are not committed in scripts or evidence.
