# M0-R1 Start Gate Evidence

- Change: CHG-20260715-002
- Date: 2026-07-15
- Scope: Workspace evidence-only audit; runtime repositories are read-only.

## Active CHG

Command:

```text
find wt-media-workspace/delivery/active -maxdepth 2 -name change.md -print
```

Expected result: exactly one active `change.md`.

Actual result:

```text
wt-media-workspace/delivery/active/CHG-20260715-002/change.md
```

Status: PASS.

## Current Facts

- M0 is `IN_PROGRESS`.
- M1 is `NOT_STARTED` and depends on M0 `DONE`.
- CHG-20260715-002 only writes Workspace delivery evidence.
- Cloud, Agent and Desktop are inspected and tested as read-only runtime repositories.

## Gap to This CHG

M0-R1 must convert revised M0 gates into concrete evidence:

- local toolchains;
- dependency entry points;
- bootstrap/test/build/start/stop/health commands;
- migration readiness;
- CI, Contract Map and Release Matrix consistency;
- follow-up ownership for M0-R2 through M0-R6.

## Real File Mapping

| Area | Files |
|---|---|
| Cloud backend | `wt-media-cloud/go.mod`, `wt-media-cloud/cmd/server/main.go`, `wt-media-cloud/scripts/verify-health.sh` |
| Cloud Web | `wt-media-cloud/web/package.json`, `wt-media-cloud/web/package-lock.json`, `wt-media-cloud/web/src/*.js`, `wt-media-cloud/web/src/*.vue` |
| Cloud migrations | `wt-media-cloud/migrations/20260714_*.sql`, `wt-media-cloud/internal/modules/migration/m2_migration_test.go` |
| Agent | `wt-media-agent/pyproject.toml`, `wt-media-agent/src/wt_media_agent`, `wt-media-agent/scripts/verify-health.sh`, `wt-media-agent/tests` |
| Desktop | `wt-media-desktop/package.json`, `wt-media-desktop/Cargo.toml`, `wt-media-desktop/src-tauri/Cargo.toml`, `wt-media-desktop/src-tauri/tauri.conf.json` |
| Governance | `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`, `wt-media-workspace/config/contract-map.yaml`, `wt-media-workspace/config/release-matrix.yaml` |

## Ordered Task List and Verification

| Task | Verification |
|---|---|
| T-01 Start Gate | Active scan, Git status, generated AI context. |
| T-02 Toolchain inventory | Version commands and command discovery. |
| T-03 Cloud/Web audit | Go test/build/health; Web test/build; migration readiness review. |
| T-04 Agent audit | unittest, Local health, `uv build`. |
| T-05 Desktop audit | npm health/test/build/dev/package/bootstrap/lint, Cargo check. |
| T-06 Governance audit | Workspace verifiers and release/contract review. |
| T-07 Gap register/manual skeleton | Every revised M0 gate mapped to status and follow-up. |
| T-08 Final verification | Workspace tests, diff check, repository status. |

## Risks and Blockers

- Rust/Cargo is not available, so Desktop/Tauri real build cannot pass M0 today.
- Desktop build/dev/package/bootstrap/lint scripts are echo placeholders.
- Cloud MySQL migration files exist, but no formal migration runner or mysql CLI was found.
- Agent build works after network access to PyPI, but dependency locking/offline reproducibility is not closed.
- No `.github` workflow files were found in the workspace scan.

## Proposed Commit Boundary

One Workspace-only commit:

```text
docs: activate m0 r1 environment audit
```

## Git Status at Start

| Repository | Status |
|---|---|
| `wt-media-workspace` | Expected CHG switch and CHG-20260715-002 evidence changes. |
| `wt-media-cloud` | Clean before audit; later generated ignored `.cache/`, `web/dist/`, and existing `web/node_modules/`. |
| `wt-media-agent` | Clean before audit; later generated ignored `.cache/`, `.venv/`, `dist/`, and `__pycache__/`. |
| `wt-media-desktop` | Clean. |

Status: PASS with recorded risks.
