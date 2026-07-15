# M0-R4 Diff Summary

## wt-media-desktop

Expected changes:

- `package.json` and `package-lock.json`: real npm scripts and Vue/Vite/Tauri dependencies.
- `Cargo.lock`, `.cargo/config.toml`, `src-tauri/Cargo.toml`, `src-tauri/build.rs`: real Rust/Tauri dependency and build setup.
- `index.html`, `src/App.vue`, `src/vite-env.d.ts`, `tsconfig.json`, `vite.config.ts`: runnable Vue/Vite app.
- `scripts/*.sh`, `scripts/*.mjs`, `scripts/README.md`: executable bootstrap/test/build/start/health/stop loop and script gate.
- `src-tauri/src/main.rs`, `src-tauri/src/local_agent/mod.rs`, `src-tauri/tauri.conf.json`: minimal Tauri shell wiring.
- `src-tauri/icons/icon.png`, `src-tauri/gen/schemas/*.json`: Tauri build assets/schemas.
- `README.md`: current Desktop bootstrap and verification instructions.

Out-of-scope changes:

- None identified in `wt-media-desktop`.

Commit:

- `dd2ff80 feat: add desktop m0 tauri readiness`

## wt-media-workspace

Expected changes:

- Remove previous active CHG-20260715-004 records from `delivery/active`.
- Keep `delivery/LEDGER.md` and `delivery/MASTER_IMPLEMENTATION_PLAN.md` pointed at CHG-20260715-005.
- Add CHG-20260715-005 evidence and checkpoint updates.

Out-of-scope changes:

- None identified in `wt-media-workspace`.

## Other Repositories

- `wt-media-cloud`: no runtime code changes for this CHG.
- `wt-media-agent`: no runtime code changes for this CHG.
