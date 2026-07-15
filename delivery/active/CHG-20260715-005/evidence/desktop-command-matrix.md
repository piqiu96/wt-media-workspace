# M0-R4 Desktop Command Matrix

| Command | Expected | Actual | Status |
|---|---|---|---|
| `node scripts/verify-real-scripts.mjs` before implementation | Fail on echo/missing scripts | Failed on placeholder `bootstrap`, `dev`, `lint`, `build`, `package`, missing `start`/`stop` | PASS |
| `npm install` | Generate lockfile and install Vue/Vite/Tauri CLI dependencies | Added 47 packages, 0 vulnerabilities | PASS |
| `node scripts/verify-real-scripts.mjs` after implementation | Real scripts only | `desktop real script verification ok` | PASS |
| `npm run typecheck` | Vue/TS typecheck passes | PASS | PASS |
| `npm run web:build` | Vite web build passes | PASS, `dist/index.html` and JS asset generated | PASS |
| `cargo test --workspace` | Rust/Tauri tests pass | PASS, 2 tests passed | PASS |
| `npm test` | Full Desktop verify passes | PASS: script gate, health-check, typecheck, cargo test | PASS |
| `npm run lint` | Typecheck and cargo fmt check pass | PASS | PASS |
| `scripts/bootstrap.sh` | `npm ci` completes from lockfile | PASS; npm warned about pending install script approvals but Vite build later passed | PASS |
| `scripts/test.sh` | Wrapper test passes | PASS | PASS |
| `npm run build` | Vite build and Tauri build pass | PASS, built `target/release/wt-media-desktop-shell` | PASS |
| `scripts/build.sh` | Wrapper build passes | PASS | PASS |
| `scripts/start.sh` | Starts local dev page | PASS with escalation; started Vite on `http://127.0.0.1:5174/` | PASS |
| `scripts/health.sh` | Static and dev-page health pass | PASS with escalation; `wt-media-desktop dev health ok` | PASS |
| `scripts/stop.sh` | Stops dev server | PASS; process stopped | PASS |

## Notes

- Non-escalated local listen failed with `listen EPERM` under Codex sandbox. Escalated start/health/stop is required for local port verification in this environment.
- Tauri first build exposed a missing default icon; adding `src-tauri/icons/icon.png` resolved the build panic.
- Rust warnings for unused placeholder modules are acceptable in M0 because full Desktop sidecar/system bridge behavior is explicitly deferred.
