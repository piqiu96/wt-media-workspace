# M0-R6 Desktop Checks

| Command | Result |
|---|---|
| `scripts/bootstrap.sh` | PASS: npm dependencies installed; npm emitted allow-scripts advisory for esbuild/fsevents |
| `npm run lint` | PASS: Vue typecheck and `cargo fmt --check` |
| `scripts/test.sh` | PASS: script gate, health-check, typecheck, Rust tests |
| `scripts/build.sh` | PASS: Vite build and Tauri release build; output `target/release/wt-media-desktop-shell` |
| `scripts/start.sh` | PASS with local-port escalation: Vite dev server started on `127.0.0.1:5174` |
| `scripts/health.sh` | PASS with local-port escalation: static and dev health OK |
| `scripts/stop.sh` | PASS: dev server stopped |

## Notes

- Rust warnings are limited to placeholder bridge modules and are acceptable for M0; M1 owns the mock-free Desktop/Local Agent integration.
