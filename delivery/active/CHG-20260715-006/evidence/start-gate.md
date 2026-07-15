# M0-R5 Start Gate Evidence

## Scope

- CHG: `CHG-20260715-006`
- Status at start: `IN_PROGRESS`
- Current repository: `wt-media-workspace`
- Affected repositories: `wt-media-cloud`, `wt-media-agent`, `wt-media-desktop`, `wt-media-workspace`

## Inventory

Existing workflow files:

- `wt-media-cloud/.github/workflows/m0-cloud.yml`
- `wt-media-agent/.github/workflows/m0-agent.yml`
- `wt-media-desktop/.github/workflows/m0-desktop.yml`
- `wt-media-workspace/.github/workflows/m0-workspace.yml`

Existing config files:

- `wt-media-workspace/config/contract-map.yaml`
- `wt-media-workspace/config/release-matrix.yaml`
- `wt-media-workspace/scripts/verify_m0_config.py`
- `wt-media-workspace/scripts/verify_m0_local.sh`

## Initial Gap

- Cloud workflow only ran `scripts/verify-health.sh`; it did not run bootstrap, tests, MySQL migration and build.
- Agent workflow only ran `scripts/verify-health.sh`; it did not run uv bootstrap, tests, SQLite storage migration and build.
- Desktop workflow used Node 25 on Ubuntu and only ran `npm run verify`; it did not run the new real Tauri build gate.
- Workspace workflow did not run product/Master alignment or active CHG context validation.
- Release matrix still recorded Desktop Node 25 and historical Rust status rather than M0-R4 verified Rust/Tauri facts.
- `verify_m0_local.sh` still used old health checks rather than the revised M0 real command matrix.

## Result

PASS. R5 changes were safe to execute and remained limited to CI/config/governance gates.
