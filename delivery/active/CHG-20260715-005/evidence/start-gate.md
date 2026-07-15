# M0-R4 Start Gate Evidence

## Scope

- CHG: `CHG-20260715-005`
- Status at start: `IN_PROGRESS`
- Current repository: `wt-media-desktop`
- Affected repositories: `wt-media-desktop`, `wt-media-workspace`

## File Mapping

- Desktop app and npm scripts: `wt-media-desktop/package.json`, `index.html`, `src/App.vue`, `src/main.ts`, `vite.config.ts`, `tsconfig.json`
- Desktop wrapper scripts: `wt-media-desktop/scripts/*.sh`, `wt-media-desktop/scripts/*.mjs`
- Tauri/Rust shell: `wt-media-desktop/src-tauri/Cargo.toml`, `build.rs`, `tauri.conf.json`, `src-tauri/src/**`
- Tauri static asset: `wt-media-desktop/src-tauri/icons/icon.png`
- Workspace governance: this CHG, Ledger and Master Plan active CHG pointer

## Initial Gap

- Desktop npm scripts were echo placeholders for `bootstrap`, `dev`, `build`, `package` and `lint`.
- `start` and `stop` scripts were missing.
- Rust/Cargo were initially unavailable.
- Tauri config existed but no local Tauri build evidence existed under the revised M0 gate.

## Start Git Status

- `wt-media-desktop`: no tracked changes before R4 code work; `Cargo.lock` appeared after the first Rust test.
- `wt-media-workspace`: had governance changes from removing previous active CHG-004 and activating CHG-005.

## Result

PASS. M0-R4 was safe to execute after explicit approval for system toolchain installation.
