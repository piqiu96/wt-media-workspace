# M0-R3 Agent Command Matrix

- Change: CHG-20260715-004
- Date: 2026-07-15
- Agent commit: `2b65ac5`

| Command | Expected Result | Actual Result | Status |
|---|---|---|---|
| `uv lock --check --cache-dir .cache/uv` | Lock is current. | Resolved 1 package and exited 0. | PASS |
| `scripts/bootstrap.sh` | Sync local package and extras. | Built and installed `wt-media-agent==0.2.2`. | PASS |
| `scripts/test.sh` | Agent tests pass. | 40 tests passed. | PASS |
| `scripts/build.sh` | Source distribution and wheel build. | Built `dist/wt_media_agent-0.2.2.tar.gz` and wheel. | PASS |
| `scripts/migrate-storage.sh --data-dir ...` | SQLite migration runs. | First run applied 1; repeat run applied 0. | PASS |
| `PYTHON_BIN=.venv/bin/python scripts/verify-health.sh` | Tests, temporary Local Agent health start, probe and stop. | 40 tests passed and `wt-media-agent health ok`. | PASS |
| `scripts/start-health.sh` | Start Local Agent health and wait for `/healthz`. | Reported `wt-media-agent health started`. | PASS |
| `scripts/stop-health.sh` | Stop/clean health PID file. | Reported `wt-media-agent health stopped`. | PASS |

Status: PASS.
