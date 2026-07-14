# CHG-20260714-004: M0 Engineering Skeleton Audit And Dirty Worktree Closure

## 1. Basic Information

- Level: L
- Status: DONE
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`
  - `wt-media-agent`
  - `wt-media-desktop`

## 2. Change Goal

Audit the current dirty Cloud, Agent, and Desktop worktrees; keep only M0 engineering skeleton artifacts; remove or defer out-of-scope business and future-milestone artifacts; make each runtime repository independently reviewable and committed.

## 3. Baseline References

- Master implementation plan: `delivery/MASTER_IMPLEMENTATION_PLAN.md#M0项目治理与工程基线`
- Engineering baseline: `docs/engineering/`
- Contract governance: `docs/contracts/`
- Execution Skill: `skills/workspace/executing-wt-media-change/SKILL.md`

## 4. Current Facts

- `wt-media-workspace` was clean before this CHG.
- `delivery/active` was empty before this CHG.
- The outer `wt-media/.git` repository has been removed.
- `wt-media-cloud`, `wt-media-agent`, and `wt-media-desktop` contain pre-existing uncommitted scaffold work.
- Existing runtime code is implementation fact only; it does not prove M0 is complete until audited, tested, and committed.

## 5. Scope

### Add

- Dirty worktree audit evidence for Cloud, Agent, and Desktop.
- M0-compliant engineering skeleton commits for affected runtime repositories.
- Minimal tests or verification evidence required to make the skeleton reviewable.

### Modify

- Runtime repository scaffolds only where needed to align with M0:
  - repository rules;
  - minimal build/test entry points;
  - health check skeletons;
  - basic config/logging/error placeholders;
  - contract and release-matrix placeholders without formal business definitions.
- `delivery/MASTER_IMPLEMENTATION_PLAN.md` M0 Active CHG field.
- Active CHG checkpoint and evidence.

### Delete

- Out-of-scope scaffold artifacts that implement or imply later milestones before their CHG is active.
- Generated or stale files that should not be source-controlled.

### Explicitly Not Doing

- Do not implement M1 task execution, Agent registration, task leases, or cross-end task loop.
- Do not implement M2 user account, identity, role, media account, or Profile ownership modules.
- Do not implement M3 discovery, platform scraping, or material conversion.
- Do not implement M6/M7 publication adapters.
- Do not implement M8 interaction executors.
- Do not create M0-C3, M1, or later CHG files.
- Do not fetch dependencies during scaffold-only work.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | CHG-004 is the current Active CHG for M0 engineering skeleton audit and dirty worktree closure. | CONFIRMED |
| D-02 | Existing dirty runtime code must be audited before it can be kept or committed. | CONFIRMED |
| D-03 | M0 may keep skeleton directories and placeholders, but must not contain later business implementations. | CONFIRMED |
| D-04 | Runtime repositories must be committed independently. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Create CHG-004 active record and refresh context. | DONE | `prepare_ai_workspace.py --change CHG-20260714-004` |
| T-02 | Audit dirty runtime worktrees and classify files. | DONE | `evidence/dirty-worktree-audit.md` |
| T-03 | Apply M0 skeleton cleanup. | DONE | `evidence/cleanup-diff-summary.md` and out-of-scope `rg` scans |
| T-04 | Run repository tests/build checks. | DONE | `evidence/test-summary.md` |
| T-05 | Commit affected repositories and close CHG. | DONE | `evidence/commit-summary.md` |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG record.
- [x] Update active ledger.
- [x] Set M0 Active CHG to CHG-004.
- [x] Refresh root AI context.
- [x] Record audit and verification evidence.
- [x] Close and clean active record.

### wt-media-cloud

- [x] Audit dirty files.
- [x] Keep M0-compliant skeleton artifacts.
- [x] Remove/defer out-of-scope business artifacts.
- [x] Run verification.
- [x] Commit independently.

### wt-media-agent

- [x] Audit dirty files.
- [x] Keep M0-compliant skeleton artifacts.
- [x] Remove/defer out-of-scope platform/business artifacts.
- [x] Run verification.
- [x] Commit independently.

### wt-media-desktop

- [x] Audit dirty files.
- [x] Keep M0-compliant skeleton artifacts.
- [x] Remove/defer out-of-scope local-agent/task UI artifacts.
- [x] Run verification.
- [x] Commit independently.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one active CHG exists during implementation. | `find delivery/active -maxdepth 2 -name change.md` | PASS |
| AC-02 | Cloud dirty files are classified into keep/defer/delete decisions. | Audit evidence | PASS |
| AC-03 | Agent dirty files are classified into keep/defer/delete decisions. | Audit evidence | PASS |
| AC-04 | Desktop dirty files are classified into keep/defer/delete decisions. | Audit evidence | PASS |
| AC-05 | Runtime repositories contain only M0-compliant committed skeleton artifacts after cleanup. | Diff and status checks | PASS |
| AC-06 | No M1/M2/M3/M6/M7/M8 business implementation remains in M0 commits. | `rg` scans and diff inspection | PASS |
| AC-07 | Verification commands pass or failures are recorded as blockers with evidence. | Test evidence | PASS |
| AC-08 | Affected repositories are committed independently. | Git log checks | PASS |

## 11. Evidence

Planned records:

- `evidence/task-01-context.md`
- `evidence/dirty-worktree-audit.md`
- `evidence/cleanup-diff-summary.md`
- `evidence/test-summary.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- Created CHG-004 active record.
- Updated `delivery/LEDGER.md`.
- Updated M0 Active CHG in `delivery/MASTER_IMPLEMENTATION_PLAN.md`.
- Refreshed root `.ai/CURRENT_CONTEXT.md` for CHG-004.
- Audited Cloud, Agent, and Desktop dirty worktrees.
- Removed or neutralized out-of-scope M1/M2/M3/M6/M7/M8 implementation artifacts.
- Verified Skill sync and Workspace tests.
- Verified Agent unittest and Desktop npm scaffold test.
- Recorded Cloud Go >= 1.20 and Desktop Cargo environment limitations.
- Committed `wt-media-cloud`: `c28bd3d chore: establish m0 cloud skeleton`.
- Committed `wt-media-agent`: `4ef0dfe chore: establish m0 agent skeleton`.
- Committed `wt-media-desktop`: `0774635 chore: establish m0 desktop skeleton`.

Current:
- Final Workspace evidence commit and active-record cleanup.

Next:
- Commit Workspace CHG evidence, then remove completed active record.

Blocked:
- None.

Recent verification:
- `python3 scripts/sync_skills.py check --repo cloud`
- `python3 scripts/sync_skills.py check --repo agent`
- `python3 scripts/sync_skills.py check --repo desktop`
- `python3 scripts/verify_skills.py`
- `python3 -m unittest discover -s tests` in Workspace
- `env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/infra/config`
- `env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./...` (blocked by local Go 1.19.9 vs Hertz Go >= 1.20)
- `python3 -m unittest discover -s tests` in Agent
- `npm test` in Desktop
- `cargo test` in Desktop (blocked: `cargo` not installed)
- M0 out-of-scope `rg` scans in Cloud, Agent, and Desktop
- `git status --short --branch` in Cloud, Agent, and Desktop after commits

## 13. DONE Gate

- [x] Scope completed.
- [x] No blocking `Q-xx`.
- [x] Acceptance matrix all PASS.
- [x] Automated or command verification completed with environment exceptions recorded.
- [x] Evidence recorded.
- [x] Diff checked for out-of-scope changes.
- [x] Runtime repositories committed independently.
- [x] Completed active record removal follows this DONE evidence commit.
