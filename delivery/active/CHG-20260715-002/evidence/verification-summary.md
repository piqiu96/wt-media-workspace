# M0-R1 Verification Summary

- Change: CHG-20260715-002
- Date: 2026-07-15

## Commands

| Command | Expected Result | Actual Result | Status |
|---|---|---|---|
| `python3 scripts/verify_product_master_alignment.py` | Alignment verifier passes with current active CHG. | Initially failed on hardcoded CHG-20260715-001; after verifier fix, passed. | PASS |
| `python3 scripts/verify_m0_config.py` | Workspace config verifier passes. | `Workspace config verification ok`. | PASS |
| `python3 -m unittest discover -s tests` | Workspace tests pass. | 12 tests passed. | PASS |
| `python3 scripts/prepare_ai_workspace.py --change CHG-20260715-002 --no-write` | AI workspace validation reports CHG-20260715-002. | Exited 0 and reported active CHG `CHG-20260715-002`. | PASS |
| Cloud `go test ./...` | Cloud tests pass. | All packages passed or had no test files. | PASS |
| Cloud `go build -o /tmp/wt-media-cloud-server ./cmd/server` | Cloud server builds. | Exit 0; stat-cache warning recorded. | PASS |
| Cloud `scripts/verify-health.sh` | Cloud health passes. | Authorized run reported `wt-media-cloud health ok`. | PASS |
| Cloud Web `npm test` | Web tests pass. | 8 tests passed. | PASS |
| Cloud Web `npm run build` | Web build passes. | Vite build succeeded. | PASS |
| Agent `.venv/bin/python -m unittest discover -s tests` | Agent tests pass. | 39 tests passed. | PASS |
| Agent `scripts/verify-health.sh` | Local Agent health passes. | Authorized run reported `wt-media-agent health ok`. | PASS |
| Agent `uv build --cache-dir .cache/uv` | Agent sdist/wheel build. | Authorized run built sdist and wheel. | PASS |
| Desktop `npm test` / `npm run health` | Desktop scaffold health passes. | Health check passed. | PASS for scaffold health only |
| Desktop `npm run build`, `npm run dev`, `npm run package`, `npm run bootstrap`, `npm run lint` | Real commands exist and run. | Commands are echo placeholders. | FAIL for revised M0 gate |
| Desktop `cargo check` | Rust workspace checks. | `cargo` not found. | FAIL |
| `nc -zv 127.0.0.1 3306` | MySQL TCP reachable. | Authorized run connected to 3306. | PASS |

## Summary

M0-R1 audit is complete. Cloud/Web and Agent have runnable foundations with specific reproducibility gaps. Desktop/Tauri and migration/CI gates remain the primary blockers to M0 DONE.
