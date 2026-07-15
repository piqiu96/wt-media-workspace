# M0-R1 Repository Command Matrix

- Change: CHG-20260715-002
- Date: 2026-07-15

## Cloud Backend

| Command | Expected Result | Actual Result | Status |
|---|---|---|---|
| `GOCACHE=... go test ./...` | Go packages test successfully. | All packages passed or had no test files. | PASS |
| `GOCACHE=... go build -o /tmp/wt-media-cloud-server ./cmd/server` | Server binary builds outside repo. | Exit 0 and binary built; Go emitted a stat-cache warning for external GOPATH write denied by sandbox. | PASS with environment warning |
| `GOCACHE=... WT_MEDIA_CLOUD_HTTP_ADDR=127.0.0.1:18080 scripts/verify-health.sh` | Server starts, health endpoints respond, script exits 0. | Sandbox run failed on port bind; authorized run exited 0 with `wt-media-cloud health ok`. | PASS |

## Cloud Web

| Command | Expected Result | Actual Result | Status |
|---|---|---|---|
| `npm test` | Vitest passes. | 3 files passed, 8 tests passed. | PASS |
| `npm run build` | Vite production build succeeds. | Build succeeded and emitted `dist/` assets. | PASS |

## Cloud Migration Readiness

| Check | Expected Result | Actual Result | Status |
|---|---|---|---|
| Migration SQL files | Current migration files are present. | `20260714_001_identity.sql` through `20260714_005_sensitive_profile_locks.sql` exist. | PASS |
| Migration tests | Schema expectations are tested. | Go migration/module tests passed through `go test ./...`. | PASS |
| Empty MySQL execution path | Repeatable migration runner or documented executable command exists. | No formal migration runner found; mysql CLI unavailable. | FAIL |

## Agent

| Command | Expected Result | Actual Result | Status |
|---|---|---|---|
| `.venv/bin/python -m unittest discover -s tests` | Agent tests pass with Python >=3.12. | 39 tests passed; app reports `mode=local`. | PASS |
| `PYTHON_BIN=.venv/bin/python scripts/verify-health.sh` | Local Agent health server starts and responds. | Sandbox run failed on port bind; authorized run exited 0 with `wt-media-agent health ok`. | PASS |
| `uv build --cache-dir .cache/uv` | Source distribution and wheel build. | Sandbox run failed on network; authorized run built `dist/wt_media_agent-0.2.2.tar.gz` and wheel. | PASS with dependency-source risk |
| `.venv/bin/python -m pip show hatchling` | Build dependency can be inspected in venv. | `.venv` has no pip. | FAIL for pip-based inspection; uv build remains usable. |

## Desktop

| Command | Expected Result | Actual Result | Status |
|---|---|---|---|
| `npm test` | Real Desktop tests pass. | Runs `node scripts/health-check.mjs` and prints `wt-media-desktop health ok`. | PARTIAL |
| `npm run health` | Health check passes. | `wt-media-desktop health ok`. | PASS for scaffold health |
| `npm run build` | Real Desktop build runs. | Echo: `Desktop build is not wired in scaffold phase`. | FAIL |
| `npm run dev` | Real Desktop dev server/Tauri dev path runs. | Echo: `Desktop dev server is not wired in scaffold phase`. | FAIL |
| `npm run package` | Real package command runs. | Echo: `Desktop packaging is not wired in scaffold phase`. | FAIL |
| `npm run bootstrap` | Real dependency bootstrap runs. | Echo: `Install dependencies after scaffold approval`. | FAIL |
| `npm run lint` | Real lint runs. | Echo: `No desktop lint configured yet`. | FAIL |
| `cargo check` | Rust workspace checks. | `zsh:1: command not found: cargo`. | FAIL |

## Workspace Governance

| Command | Expected Result | Actual Result | Status |
|---|---|---|---|
| `python3 scripts/verify_product_master_alignment.py` | Product/Master/governance alignment passes for the current active CHG. | Initially failed because active CHG was hardcoded to CHG-20260715-001; fixed to read the actual active CHG dynamically, then passed. | PASS after fix |
| `python3 scripts/verify_m0_config.py` | Workspace config passes. | `Workspace config verification ok`. | PASS |
| `python3 -m unittest discover -s tests` | Workspace tests pass. | 12 tests passed after verifier fix. | PASS |
| `python3 scripts/prepare_ai_workspace.py --change CHG-20260715-002 --no-write` | AI context validation points to CHG-20260715-002. | Exited 0 and reported active CHG `CHG-20260715-002`. | PASS |

Overall status: PASS for audit completion; revised M0 remains IN_PROGRESS because several real gates fail.
