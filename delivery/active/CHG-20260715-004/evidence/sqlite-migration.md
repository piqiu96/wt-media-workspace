# M0-R3 SQLite Migration Evidence

- Change: CHG-20260715-004
- Date: 2026-07-15
- Agent commit: `2b65ac5`

## Test-First Evidence

Command:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.test_storage_migration -v
```

Expected result before implementation: fail because `wt_media_agent.storage.migration` does not exist.

Actual result before implementation:

```text
ImportError: cannot import name 'migration' from 'wt_media_agent.storage'
FAILED (errors=1)
```

Status: PASS for RED.

After implementation:

```text
test_applies_and_repeats_sqlite_migrations ... ok
Ran 1 test
OK
```

Status: PASS for GREEN.

## Isolated Directory Run

Command:

```text
scripts/migrate-storage.sh --data-dir /tmp/wt-media-agent-m0-r3-final
```

First run actual result:

```text
storage migration ok: 1 applied, 1 total
applied 0001_base base
```

Repeat run actual result:

```text
storage migration ok: 0 applied, 1 total
```

Status: PASS.

## Behavior Verified

- The migration command creates the selected data directory.
- SQLite database file is `local-agent.sqlite3` under the selected data directory unless `--db-path` is supplied.
- `schema_migrations` records applied versions.
- `agent_metadata` base table exists after migration.
- Repeat execution skips already applied migrations.
