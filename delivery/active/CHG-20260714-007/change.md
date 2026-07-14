# CHG-20260714-007: M0 Comprehensive Acceptance

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`

## 2. Change Goal

Run final M0 acceptance across governance, engineering skeletons, health checks, CI definitions, Contract Map, and Release Matrix. If all M0 exit criteria pass, mark M0 as `DONE` in the master implementation plan.

## 3. Baseline References

- Master implementation plan: `delivery/MASTER_IMPLEMENTATION_PLAN.md#M0项目治理与工程基线`
- Contract governance: `docs/contracts/`
- Engineering baseline: `docs/engineering/`
- Execution Skill: `skills/workspace/executing-wt-media-change/SKILL.md`

## 4. Current Facts

- No active CHG existed before this CHG.
- CHG-006 completed and pushed M0 testing, CI, Contract Map, and Release Matrix.
- Four repositories are clean and synchronized with `origin/main`.
- M0 is still marked `IN_PROGRESS` pending comprehensive acceptance.

## 5. Scope

### Add

- M0 comprehensive acceptance evidence.
- Final M0 exit-criteria matrix.
- Optional GitHub Actions run evidence if available through `gh`.

### Modify

- `delivery/MASTER_IMPLEMENTATION_PLAN.md` M0 status, completion date, evidence, and commit references if M0 passes.
- Active CHG checkpoint and evidence.

### Delete

- Completed active CHG record after DONE evidence is committed.

### Explicitly Not Doing

- Do not modify Cloud, Agent, or Desktop runtime code.
- Do not implement M1 task execution, Agent registration, task leases, or cross-end task loop.
- Do not implement formal OpenAPI, Schema, DTO, or event definitions.
- Do not implement user/account/media account/Profile modules.
- Do not add platform adapters, publication, discovery, production, or interaction features.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | CHG-007 is the current Active CHG for M0 comprehensive acceptance. | CONFIRMED |
| D-02 | M0 can be marked `DONE` only if all M0 exit criteria pass with evidence. | CONFIRMED |
| D-03 | Remote CI status should be recorded if accessible, but local M0 verification remains the required acceptance command. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Create CHG-007 active record and refresh context. | IN_PROGRESS | `prepare_ai_workspace.py --change CHG-20260714-007` |
| T-02 | Run local M0 comprehensive verification. | TODO | `scripts/verify_m0_local.sh` and supporting checks |
| T-03 | Record CI/workflow status and repository sync facts. | TODO | Workflow inspection and optional `gh run list` |
| T-04 | Evaluate M0 exit criteria and update master plan. | TODO | Acceptance matrix all PASS |
| T-05 | Commit Workspace evidence and close CHG. | TODO | Git log and final status |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG record.
- [x] Update active ledger.
- [x] Set M0 Active CHG to CHG-007.
- [ ] Refresh root AI context.
- [ ] Run Workspace tests and skill checks.
- [ ] Run M0 config validation.
- [ ] Run cross-repo local M0 verification.
- [ ] Check repository sync and active governance state.
- [ ] Check CI workflow status when accessible.
- [ ] Mark M0 `DONE` if all exit criteria pass.
- [ ] Commit and clean active record.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one active CHG exists during implementation. | `find delivery/active -maxdepth 2 -name change.md` | TODO |
| AC-02 | CHG governance and context generation work. | `prepare_ai_workspace.py --change CHG-20260714-007` | TODO |
| AC-03 | Four repositories are clean and synchronized with origin. | `git status --short --branch` | TODO |
| AC-04 | Workspace tests, skill verification, and M0 config validation pass. | Workspace commands | TODO |
| AC-05 | Cloud, Agent, Desktop M0 health checks pass through unified local verification. | `scripts/verify_m0_local.sh` | TODO |
| AC-06 | CI workflows exist for all four repositories. | Workflow inspection | TODO |
| AC-07 | Contract Map and Release Matrix reflect M0 placeholder-only facts. | Config verification and file inspection | TODO |
| AC-08 | M0 master-plan exit criteria all pass. | Exit criteria matrix | TODO |
| AC-09 | No M1/M2/M3/M6/M7/M8 implementation is introduced. | `rg` scans and diff inspection | TODO |
| AC-10 | Workspace completion is committed and pushed. | Git log/status | TODO |

## 11. Evidence

Planned records:

- `evidence/task-01-context.md`
- `evidence/local-acceptance.md`
- `evidence/repository-and-ci-status.md`
- `evidence/m0-exit-criteria.md`
- `evidence/diff-and-scope-scan.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- Created CHG-007 active record.
- Updated `delivery/LEDGER.md`.
- Updated M0 Active CHG in `delivery/MASTER_IMPLEMENTATION_PLAN.md`.

Current:
- T-01 context refresh and start gate.

Next:
- Run `prepare_ai_workspace.py --change CHG-20260714-007`.
- Run local M0 comprehensive verification.

Blocked:
- None.

Recent verification:
- `git status --short --branch` in four repositories.
- `find delivery/active -maxdepth 2 -name change.md -print`.

## 13. DONE Gate

- [ ] Scope completed.
- [x] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated or command verification passed.
- [ ] Evidence recorded.
- [ ] Diff checked for out-of-scope changes.
- [ ] Affected repositories committed independently if changed.
- [ ] Completed active record removed after Git history records the CHG.
