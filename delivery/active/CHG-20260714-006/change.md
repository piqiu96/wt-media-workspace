# CHG-20260714-006: M0-C4 Tests CI Contract Map And Release Matrix

## 1. Basic Information

- Level: M
- Status: DONE
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`
  - `wt-media-agent`
  - `wt-media-desktop`

## 2. Change Goal

Formally solidify M0 testing, CI, contract ownership map, release matrix, and toolchain paths so M0 validation is repeatable locally and in CI.

## 3. Baseline References

- Master implementation plan: `delivery/MASTER_IMPLEMENTATION_PLAN.md#M0项目治理与工程基线`
- Contract governance: `docs/contracts/`
- Execution Skill: `skills/workspace/executing-wt-media-change/SKILL.md`

## 4. Current Facts

- No active CHG existed before this CHG.
- CHG-005 completed and pushed M0 health verification scripts.
- Current bare `go` in Codex still resolves to `devenv/go19`.
- Go 1.26.5 exists at `devenv/go26/go/bin/go`.
- No `.github/workflows` directories exist in the four repositories.
- `config/contract-map.yaml` lists ownership paths but does not explicitly mark M0 contract areas as placeholder-only.
- `config/release-matrix.yaml` currently lists contract versions as `v1`, which overstates M0 because formal API/schema definitions are not active yet.

## 5. Scope

### Add

- CI workflows for Workspace, Cloud, Agent, and Desktop.
- Local verification scripts for M0 config and cross-repo M0 checks.
- Evidence for toolchain, CI definitions, contract map, release matrix, and tests.

### Modify

- `config/contract-map.yaml` to mark M0 contract areas as placeholder-only ownership records.
- `config/release-matrix.yaml` to record the currently verified M0 combination without claiming formal contract versions.
- Runtime repository scripts or docs only where needed to make CI/test commands stable.

### Delete

- None planned.

### Explicitly Not Doing

- Do not implement M1 task execution, Agent registration, task leases, or cross-end task loop.
- Do not implement formal OpenAPI, Schema, DTO, or event definitions.
- Do not implement user/account/media account/Profile modules.
- Do not introduce runtime dependency from Cloud, Agent, or Desktop to Workspace.
- Do not add platform adapters, publication, discovery, production, or interaction features.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | CHG-006 is the current Active CHG for M0-C4 testing, CI, contract map, and release matrix. | CONFIRMED |
| D-02 | M0 contract map records ownership and consumer relationships only; formal interface definitions remain inactive placeholders. | CONFIRMED |
| D-03 | Release matrix must describe verified M0 scaffold and health checks without claiming business contract compatibility. | CONFIRMED |
| D-04 | CI should run repository-local checks; Workspace may validate cross-repo governance but must not become runtime dependency. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Create CHG-006 active record and refresh context. | DONE | `prepare_ai_workspace.py --change CHG-20260714-006` |
| T-02 | Solidify Workspace config validation for contract map and release matrix. | DONE | `evidence/config-validation.md` |
| T-03 | Add CI workflows and repository-local verification entrypoints. | DONE | `evidence/ci-workflows.md` |
| T-04 | Run M0 verification matrix locally. | DONE | `evidence/local-verification.md` and `evidence/diff-and-scope-scan.md` |
| T-05 | Commit affected repositories and close CHG. | DONE | `evidence/commit-summary.md` |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG record.
- [x] Update active ledger.
- [x] Set M0 Active CHG to CHG-006.
- [x] Refresh root AI context.
- [x] Update `contract-map.yaml`.
- [x] Update `release-matrix.yaml`.
- [x] Add config verification script/tests.
- [x] Add Workspace CI.
- [x] Record evidence.
- [x] Close and clean active record.

### wt-media-cloud

- [x] Add Cloud CI workflow.
- [x] Ensure M0 health verification is CI-ready.
- [x] Run verification.
- [x] Commit independently if changed.

### wt-media-agent

- [x] Add Agent CI workflow.
- [x] Ensure M0 health verification is CI-ready.
- [x] Run verification.
- [x] Commit independently if changed.

### wt-media-desktop

- [x] Add Desktop CI workflow.
- [x] Ensure M0 health verification is CI-ready.
- [x] Run verification.
- [x] Commit independently if changed.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one active CHG exists during implementation. | `find delivery/active -maxdepth 2 -name change.md` | PASS |
| AC-02 | Contract map records M0 placeholder ownership and valid provider paths. | Config verification | PASS |
| AC-03 | Release matrix records verified M0 health/test state without claiming formal contract versions. | Config verification | PASS |
| AC-04 | Cloud CI exists and runs M0 health verification. | Workflow inspection + local script | PASS |
| AC-05 | Agent CI exists and runs M0 health verification. | Workflow inspection + local script | PASS |
| AC-06 | Desktop CI exists and runs M0 verification. | Workflow inspection + npm scripts | PASS |
| AC-07 | Workspace CI exists and validates governance scripts/config. | Workflow inspection + Workspace tests | PASS |
| AC-08 | No M1/M2/M3/M6/M7/M8 implementation is introduced. | `rg` scans and diff inspection | PASS |
| AC-09 | Affected repositories are committed independently when changed. | Git log checks | PASS |

## 11. Evidence

Planned records:

- `evidence/task-01-context.md`
- `evidence/config-validation.md`
- `evidence/ci-workflows.md`
- `evidence/local-verification.md`
- `evidence/diff-and-scope-scan.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- Created CHG-006 active record.
- Updated `delivery/LEDGER.md`.
- Updated M0 Active CHG in `delivery/MASTER_IMPLEMENTATION_PLAN.md`.
- Refreshed root `.ai/CURRENT_CONTEXT.md`.
- Updated contract map and release matrix to M0 placeholder-only facts.
- Added config validation script and tests.
- Added M0 CI workflows for Workspace, Cloud, Agent, and Desktop.
- Added Workspace unified local M0 verification script.
- Verified M0 local matrix.
- Completed out-of-scope scans.
- Committed `wt-media-cloud`: `f00ae41 ci: add m0 cloud verification`.
- Committed `wt-media-agent`: `1351f5f ci: add m0 agent verification`.
- Committed `wt-media-desktop`: `54d7b6f ci: add m0 desktop verification`.

Current:
- Final Workspace evidence commit and active-record cleanup.

Next:
- Commit Workspace CHG evidence, then remove completed active record.

Blocked:
- None.

Recent verification:
- `git status --short --branch` in four repositories.
- `find delivery/active -maxdepth 2 -name change.md -print`.
- `python3 scripts/verify_m0_config.py`
- `python3 -m unittest discover -s tests`
- `python3 scripts/verify_skills.py`
- `scripts/verify_m0_local.sh`
- `npm run verify`
- Cloud and Agent `scripts/verify-health.sh`
- CI workflow inspection
- M0 out-of-scope `rg` scans

## 13. DONE Gate

- [x] Scope completed.
- [x] No blocking `Q-xx`.
- [x] Acceptance matrix all PASS.
- [x] Automated or command verification passed.
- [x] Evidence recorded.
- [x] Diff checked for out-of-scope changes.
- [x] Runtime repositories committed independently if changed.
- [x] Completed active record removal follows this DONE evidence commit.
