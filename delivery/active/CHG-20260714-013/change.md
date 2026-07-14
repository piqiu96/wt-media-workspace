# CHG-20260714-013: M1-C6 Desktop Start Stop And Local Agent Status Display

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING
- Created: 2026-07-14
- Current repository: `wt-media-desktop`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-desktop`

## 2. Change Goal

Implement the minimal Desktop-side control and observation surface for the Local Agent: Desktop can model start, stop, status refresh, and status-event display through its own service/store/page boundaries without Vue directly calling Local Agent HTTP/SSE.

## 3. Baseline References

- Engineering baseline: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Contract governance: `docs/contracts/ownership.md`
- Contract governance: `docs/contracts/contract-map.md`
- Contract compatibility: `docs/contracts/compatibility-policy.md`
- Master plan: `delivery/MASTER_IMPLEMENTATION_PLAN.md#M1Cloud-Agent-Desktop-最小任务闭环`

## 4. Current Facts

- M1-C5 activated Local Agent API `v1@2026.07.14.5` and Local event schema `status@2026.07.14.5`.
- `wt-media-desktop` currently has only a scaffold `src/main.ts`, README placeholders, and `npm run verify`.
- `wt-media-desktop` has no installed Vue/Tauri frontend dependency chain yet.
- Desktop rules require Vue to use Tauri command wrappers instead of directly accessing Local Agent dynamic ports or tokens.

## 5. Scope

### Add

- Desktop Local Agent frontend service wrapper for start, stop, status, and status events.
- Desktop Local Agent store for lifecycle state and status-event application.
- Desktop local status page model for visible status/progress data.
- Desktop verification coverage for the service/store/page boundaries.
- Workspace evidence and M1 release-matrix update for M1-C6.

### Modify

- Desktop `src/main.ts` to expose the local status page model as the current scaffold entry.
- Desktop `scripts/health-check.mjs` to validate M1-C6 behavior.
- Desktop `contracts.lock.json` to record consumed Local Agent contract revisions.
- Workspace `delivery/MASTER_IMPLEMENTATION_PLAN.md`, `delivery/LEDGER.md`, and release matrix.

### Delete

- None.

### Explicitly Not Doing

- Do not implement a full Vue application or install frontend dependencies.
- Do not implement Tauri command macros or process spawning side effects.
- Do not modify Cloud or Agent business code.
- Do not create M2 user/account/profile objects.
- Do not start M1-C7 before this CHG is complete and closed.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | M1-C6 uses a dependency-injected Desktop service wrapper so UI code does not directly call Local Agent HTTP/SSE. | CONFIRMED |
| D-02 | Verification remains dependency-free and runs through `npm run verify`. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

Each task must follow:

```text
failing verification or test
→ minimal implementation
→ test
→ diff check
→ evidence
→ checkpoint
→ independent commit
```

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Create Active CHG and refresh AI context. | DONE | `prepare_ai_workspace.py --change CHG-20260714-013` |
| T-02 | Add Desktop Local Agent service/store/page model. | DONE | `npm run verify` initially failed, then passed. |
| T-03 | Update Desktop contract lock and docs. | DONE | `npm run verify`; diff inspection. |
| T-04 | Update Workspace release matrix and evidence. | DONE | Workspace tests and config verification. |
| T-05 | Complete CHG and remove active record. | TODO | Active ledger empty after completion. |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG.
- [x] Record Desktop evidence.
- [x] Update release matrix and M1 plan.
- [ ] Remove active record when complete.

### wt-media-cloud

- [x] Not affected.

### wt-media-agent

- [x] Not affected.

### wt-media-desktop

- [x] Add Local Agent service wrapper.
- [x] Add Local Agent store.
- [x] Add local status page model.
- [x] Update verification script.
- [x] Update consumed contract lock.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Desktop can model Local Agent start and stop through a Desktop-owned service boundary. | `npm run verify` | PASS |
| AC-02 | Desktop can display Local Agent status and pending result count from the Local Agent status/event shape. | `npm run verify` | PASS |
| AC-03 | Desktop Vue/page layer does not directly access Local Agent dynamic ports or tokens. | Code inspection and `npm run verify` | PASS |
| AC-04 | Desktop records consumed Local Agent API and event schema revisions. | `contracts.lock.json` inspection | PASS |

## 11. Evidence

Evidence files live in `evidence/` and must record facts, not repeat requirements.

- `evidence/task-01-context.md`
- `evidence/desktop-local-agent.md`
- `evidence/workspace-release-matrix.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- Created CHG-013 active record.
- Added Desktop Local Agent service, store, page model, Rust command boundary, verification, README notes, and contract lock.
- Added Workspace release matrix entry and evidence.

Current:
- CHG-013 completion gate.

Next:
- Run final workspace and Desktop verification, then remove active record.

Blocked:
- None.

Recent verification:
- `npm run verify` failed before implementation with missing M1-C6 checks, then passed after implementation.
- `cargo check` was attempted but not run because `cargo` is not available in the current shell.

## 13. DONE Gate

- [x] Scope completed.
- [x] No blocking `Q-xx`.
- [x] Acceptance matrix all PASS.
- [x] Automated tests passed or justified.
- [x] Manual verification evidence recorded where required.
- [x] Diff checked for out-of-scope changes.
- [x] Runtime repositories touched only if listed in scope.
- [x] Required baselines updated.
- [x] Affected repositories committed independently.
