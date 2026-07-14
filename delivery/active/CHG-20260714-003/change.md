# CHG-20260714-003: M0-M10 Master Implementation Plan Hardening

## 1. Basic Information

- Level: M
- Status: DONE
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`

## 2. Change Goal

Make `delivery/MASTER_IMPLEMENTATION_PLAN.md` the durable execution baseline for M0-M10, including milestone status, dependencies, candidate CHGs, Active CHG field, exit conditions, evidence index, completion date, and commit/tag fields.

## 3. Baseline References

- Product baseline: `docs/product/`
- Engineering baseline: `docs/engineering/`
- Contract governance: `docs/contracts/`
- Current master route: `delivery/MASTER_IMPLEMENTATION_PLAN.md`
- Execution Skill: `skills/workspace/executing-wt-media-change/SKILL.md`

## 4. Current Facts

- CHG-002 is complete and no active CHG existed before this change.
- Root `.ai/CURRENT_CONTEXT.md` still referenced completed CHG-002 before regeneration.
- `MASTER_IMPLEMENTATION_PLAN.md` already has the high-level route and execution protocol.
- `MASTER_IMPLEMENTATION_PLAN.md` does not yet contain the formal M0-M10 status table and detailed candidate CHG breakdown.
- Cloud, Agent, and Desktop repositories currently have unrelated dirty scaffold work and are out of scope.
- The outer `wt-media/.git` repository has been removed; the four sub-repository Git histories remain.

## 5. Scope

### Add

- Formal milestone status specification.
- M0-M10 milestone fields:
  - status;
  - goal;
  - dependencies;
  - candidate CHGs;
  - Active CHG;
  - exit conditions;
  - evidence;
  - completion date;
  - commit/tag.
- Detailed candidate CHG lists for M0-M10.
- Explicit next-step rule after CHG-003.
- Evidence for master plan diff and verification.

### Modify

- `delivery/MASTER_IMPLEMENTATION_PLAN.md`.
- `delivery/LEDGER.md`.
- Root generated `.ai/CURRENT_CONTEXT.md` via `prepare_ai_workspace.py --change CHG-20260714-003`.

### Delete

- None during implementation.
- Completed active record is removed after DONE is committed.

### Explicitly Not Doing

- Do not create M0-C2 or any later CHG.
- Do not modify Cloud, Agent, or Desktop business code.
- Do not clean runtime repository dirty worktrees.
- Do not implement engineering skeleton changes.
- Do not mark any milestone DONE merely because directories or code already exist.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | M0-M10 is the formal project implementation sequence. | CONFIRMED |
| D-02 | Current CHG corresponds to plan hardening only, not business coding. | CONFIRMED |
| D-03 | M0 is `IN_PROGRESS`; M1-M10 are `NOT_STARTED` until verified. | CONFIRMED |
| D-04 | Existing code is current implementation fact, not automatic milestone completion. | CONFIRMED |
| D-05 | Do not create future CHG files while planning candidate CHGs. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Create CHG-003 active record and regenerate execution context. | DONE | `prepare_ai_workspace.py --change CHG-20260714-003` |
| T-02 | Update `MASTER_IMPLEMENTATION_PLAN.md` with M0-M10 formal milestone model. | DONE | Diff inspection and milestone scans. |
| T-03 | Verify no runtime repository changes and record evidence. | DONE | Git status and tests. |
| T-04 | Close CHG-003, commit, then remove completed active record. | DONE | Git log and active ledger checks. |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create CHG-003 active record.
- [x] Update active ledger.
- [x] Regenerate root AI context for CHG-003.
- [x] Update master implementation plan.
- [x] Record evidence.
- [x] Run verification.
- [x] Commit.
- [ ] Remove completed active record after DONE commit.

### wt-media-cloud

- [ ] Confirm not modified by this CHG.

### wt-media-agent

- [ ] Confirm not modified by this CHG.

### wt-media-desktop

- [ ] Confirm not modified by this CHG.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one active CHG exists during implementation. | `find delivery/active -maxdepth 2 -name change.md` | PASS |
| AC-02 | Master plan contains M0-M10 formal milestone sections. | `rg` and text inspection | PASS |
| AC-03 | Each milestone has status, goal, dependencies, candidate CHGs, Active CHG, exit conditions, evidence, completion date, and commit/tag. | Text inspection | PASS |
| AC-04 | M0 is `IN_PROGRESS`; M1-M10 are `NOT_STARTED`. | `rg` and text inspection | PASS |
| AC-05 | CHG-003 does not create M0-C2 or later CHG files. | `find delivery/active` | PASS |
| AC-06 | Cloud, Agent, and Desktop business code is untouched by this CHG. | Git status comparison | PASS |
| AC-07 | Verification evidence is recorded. | Evidence file inspection | PASS |

## 11. Evidence

Planned records:

- `evidence/task-01-context.md`
- `evidence/master-plan-diff.md`
- `evidence/verification-summary.md`

## 12. Current Checkpoint

Completed:
- Confirmed `delivery/active` was empty before CHG-003.
- Confirmed Workspace working tree was clean before CHG-003.
- Confirmed runtime repositories have pre-existing dirty scaffold work.
- Created this CHG-003 active record.
- Regenerated root `.ai/CURRENT_CONTEXT.md` for CHG-003.
- Updated `delivery/MASTER_IMPLEMENTATION_PLAN.md` with formal M0-M10 milestone fields, candidate CHGs, dependencies, and exit conditions.
- Ran final verification and recorded evidence.

Current:
- CHG-003 complete.

Next:
- Remove completed CHG-003 files from `delivery/active` and clear `delivery/LEDGER.md`; Git keeps the full record.

Blocked:
- None.

Recent verification:
- `git status --short --branch`
- `find delivery/active -maxdepth 3 -type f -print`
- `sed -n '1,260p' delivery/MASTER_IMPLEMENTATION_PLAN.md`
- `python3 scripts/prepare_ai_workspace.py --change CHG-20260714-003`
- `sed -n '1,120p' ../.ai/CURRENT_CONTEXT.md`
- `rg -n '^### M(10|[0-9])：' delivery/MASTER_IMPLEMENTATION_PLAN.md`
- `rg -n 'M0-C|M1-C|M2-C|M3-C|M4-C|M5-C|M6-C|M7-C|M8-C|M9-C|M10-C' delivery/MASTER_IMPLEMENTATION_PLAN.md`
- `git diff --check`
- `python3 -m unittest discover -s tests`
- `python3 scripts/verify_skills.py`
- `python3 scripts/prepare_ai_workspace.py --no-write --change CHG-20260714-003`
- `git status --short --branch` in `wt-media-cloud`, `wt-media-agent`, and `wt-media-desktop`
- Workspace close commit pending for this completed record.

## 13. DONE Gate

- [x] Scope completed.
- [x] No blocking `Q-xx`.
- [x] Acceptance matrix all PASS.
- [x] Automated or command verification passed.
- [x] Evidence recorded.
- [x] Diff checked for out-of-scope changes.
- [x] Runtime repositories untouched by this CHG.
- [x] Affected repository committed independently.
- [x] Completed active record removed after Git history records the CHG.
