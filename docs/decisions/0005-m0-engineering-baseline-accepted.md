# Decision 0005: M0 Engineering Baseline Accepted

## Status

Accepted

## Context

M0 (Project Governance & Engineering Baseline) reached VERIFYING status on 2026-07-15 after M0-R6 automated gates passed across all three platforms. The final manual acceptance was completed by user review on 2026-07-15.

Key findings during acceptance:

1. **Cloud/Web**: Go 1.26.5 bootstrap, test, build, MySQL migration (empty DB), start, health, stop all PASS.
2. **Agent**: Python 3.9.6 local (CI 3.12), 40 tests, SQLite migration, build, start-health, stop all PASS after two script fixes (uv cache path, detached health server).
3. **Desktop**: Vue/Vite/Tauri Rust bootstrap, lint, test, build, start, health, stop all PASS. Fixed `main.ts` missing `createApp(App).mount('#app')` blank-page bug. Bundling enabled (`bundle.active = true`), `.dmg` produced.
4. **Workspace**: Governance checks, config alignment, 13 Python tests all PASS.

One risk carried forward: the existing local database `wt-media-cloud` has tables but lacks `schema_migrations`. The decision on migrate/recreate/preserve is deferred to M1 planning.

## Decision

- M0 engineering baseline and manual acceptance are complete. M0 is marked `DONE`.
- The `main.ts` `createApp(App).mount('#app')` fix is part of M0 closure, not a separate CHG.
- Desktop bundling (`bundle.active = true`) is enabled for user preview; production-grade packaging (code signing, notarization, updater) remains in M10.
- The existing `wt-media-cloud` database state is acknowledged as a local legacy condition; M1-R1 will address the migration path.

## Consequences

- Positive: All four repositories have verified real toolchain, build, test, migration, start/stop/health for their respective platforms.
- Negative: None. M0 explicitly excludes business models, user auth, task execution, FFmpeg, platform automation, and installers.
- Follow-up: M1 begins with `task_schemas` formalization and task model persistence.
