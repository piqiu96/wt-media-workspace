# M0-R5 Diff Summary

## wt-media-cloud

Expected changes:

- `.github/workflows/m0-cloud.yml` now runs real bootstrap/test/MySQL migration/build gates.

Out-of-scope changes:

- None. No Cloud runtime code was changed.

Commit:

- `0020854 ci: run real m0 cloud gates`

## wt-media-agent

Expected changes:

- `.github/workflows/m0-agent.yml` now runs uv bootstrap/test/SQLite migration/build gates.

Out-of-scope changes:

- None. No Agent runtime code was changed.

Commit:

- `3d047fb ci: run real m0 agent gates`

## wt-media-desktop

Expected changes:

- `.github/workflows/m0-desktop.yml` now runs macOS Node/Rust bootstrap/lint/test/Tauri build gates.

Out-of-scope changes:

- None. No Desktop runtime code was changed.

Commit:

- `047d04c ci: run real m0 desktop gates`

## wt-media-workspace

Expected changes:

- Active CHG moved from CHG-20260715-005 to CHG-20260715-006.
- `release-matrix.yaml` reflects current Desktop Node/Rust/Cargo M0-R4 facts.
- `verify_m0_config.py`, its tests and product/Master alignment verification enforce the new R5 facts.
- `verify_m0_local.sh` uses the revised real M0 command matrix.
- Workspace workflow runs config/alignment/context checks.

Out-of-scope changes:

- None identified.
