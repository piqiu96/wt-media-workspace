# M0-R6 Agent Checks

| Command | Result |
|---|---|
| initial `scripts/bootstrap.sh` | FAIL: uv default cache under `~/.cache/uv` was blocked by sandbox |
| after fix `scripts/bootstrap.sh` | PASS: uv uses repo-local `.cache/uv` |
| `scripts/test.sh` | PASS: 40 tests |
| `scripts/migrate-storage.sh --data-dir /tmp/wt-media-agent-m0-r6` | PASS: 1 applied, 1 total |
| repeat `scripts/migrate-storage.sh --data-dir /tmp/wt-media-agent-m0-r6` | PASS: 0 applied, 1 total |
| initial `scripts/build.sh` | FAIL in sandbox: DNS blocked for PyPI hatchling |
| escalated `scripts/build.sh` | PASS: sdist and wheel built |
| foreground local API diagnostic | PASS: `/healthz` returned `{"status":"ok","service":"wt-media-agent","mode":"m1"}` |
| initial `scripts/start-health.sh` + `scripts/health.sh` | FAIL: background process exited after start in current process manager |
| after detached start fix `PYTHON_BIN=.venv/bin/python scripts/start-health.sh` | PASS: health server started |
| `scripts/health.sh` | PASS: `wt-media-agent health ok` |
| `scripts/stop-health.sh` | PASS: health server stopped |

## Verification Script Fixes

- `scripts/bootstrap.sh`: default uv cache moved to repo-local `.cache/uv`.
- `scripts/start-health.sh`: background process now uses `subprocess.Popen(..., start_new_session=True)` for stable detached execution.

## Runtime Commit

- Agent: pending at evidence creation, then committed as `0e07b4e fix: stabilize agent m0 local scripts`.
