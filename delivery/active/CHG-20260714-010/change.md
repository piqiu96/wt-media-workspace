# CHG-20260714-010: M1-C3 Task Creation Claim Lease Idempotency

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`
  - `wt-media-agent`

## 2. Change Goal

Implement the M1 task backbone slice for creating a `noop_task`, claiming it by one Agent, and enforcing lease/idempotency rules in Cloud.

## 3. Baseline References

- Master implementation plan: `delivery/MASTER_IMPLEMENTATION_PLAN.md#M1Cloud-Agent-Desktop最小任务闭环`
- Engineering architecture: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Contract ownership: `docs/contracts/ownership.md`
- Cloud-Agent API current revision: `v1@2026.07.14.2`

## 4. Current Facts

- M1-C1 and M1-C2 are complete.
- Cloud can track registered Agent heartbeat.
- Agent can register and heartbeat via Cloud client.
- No active CHG existed before CHG-010.

## 5. Scope

### Add

- Cloud-owned task creation/claim/lease contract artifact.
- Cloud in-memory M1 task store for `noop_task`.
- Cloud task creation endpoint with idempotency key.
- Cloud-Agent task claim endpoint with lease.
- Agent client method for task claim.
- Tests and evidence.

### Modify

- Cloud-Agent API contract README and revision metadata.
- Workspace Contract Map and Release Matrix.
- Agent Cloud client.

### Delete

- None.

### Explicitly Not Doing

- Do not execute noop task.
- Do not report started/progress/succeeded/failed.
- Do not add Local Agent SSE or offline result queue.
- Do not add Desktop UI/process control.
- Do not persist tasks to MySQL in this CHG.
- Do not implement user/account/Profile modules.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Cloud is the task state authority. | CONFIRMED |
| D-02 | M1-C3 may use in-memory Cloud task state; persistence is later work. | CONFIRMED |
| D-03 | Only one Agent may hold a valid lease for a task. | CONFIRMED |
| D-04 | Idempotent create uses caller-provided idempotency key. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Create Active CHG and refresh context. | DONE | `prepare_ai_workspace.py --change CHG-20260714-010` |
| T-02 | Add Cloud task contract/store/endpoints. | DONE | `evidence/cloud-task-store.md` |
| T-03 | Add Agent task claim client. | DONE | `evidence/agent-task-client.md` |
| T-04 | Update Workspace config/evidence and run integrated verification. | DONE | `evidence/integration-and-diff.md` |
| T-05 | Commit, push, cleanup active record. | IN_PROGRESS | Git/CI status |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG record.
- [x] Update active ledger.
- [x] Set M1 Active CHG to CHG-010.
- [x] Refresh root AI context.
- [ ] Update Contract Map and Release Matrix.
- [ ] Record evidence and cleanup completed active record.

### wt-media-cloud

- [x] Add task contract artifact.
- [x] Add in-memory task store.
- [x] Add create and claim endpoints.
- [x] Add tests.
- [ ] Commit independently.

### wt-media-agent

- [x] Add task claim client method.
- [x] Add tests.
- [ ] Commit independently.

### wt-media-desktop

- [x] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one active CHG exists during implementation. | `find delivery/active -maxdepth 2 -name change.md` | PASS |
| AC-02 | Cloud can create `noop_task` idempotently. | Cloud tests/curl | PASS |
| AC-03 | Only one Agent can claim a valid task lease. | Cloud tests | PASS |
| AC-04 | Same Agent can retry claim idempotently while lease is valid. | Cloud tests | PASS |
| AC-05 | Agent can build claim request. | Agent tests | PASS |
| AC-06 | No executor/progress/SSE/Desktop/account behavior is introduced. | Diff scan | PASS |
| AC-07 | Affected repositories are committed independently and pushed. | Git log/status | TODO |

## 11. Evidence

- `evidence/task-01-context.md`
- `evidence/cloud-task-store.md`
- `evidence/agent-task-client.md`
- `evidence/integration-and-diff.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- Confirmed CHG-009 completed and active records were cleared.
- Confirmed four repositories were clean and synchronized.
- Created CHG-010 active record.
- Updated `delivery/LEDGER.md`.
- Updated M1 Active CHG in `delivery/MASTER_IMPLEMENTATION_PLAN.md`.
- Refreshed root `.ai/CURRENT_CONTEXT.md`.
- Recorded T-01 evidence.
- Added Cloud-owned task lease contract artifact.
- Added Cloud in-memory task store and create/claim/get endpoints.
- Updated Cloud-Agent contract revision to `2026.07.14.3`.
- Verified Cloud tests and HTTP create/claim behavior.
- Updated Agent consumed contract revision to `2026.07.14.3`.
- Added Agent task claim client method.
- Verified Agent tests.
- Updated Workspace Contract Map and Release Matrix for M1-C3.
- Ran integrated verification across Workspace, Cloud, Agent, and Desktop.
- Confirmed diff scan has no out-of-scope implementation.

Current:
- T-05 commit, push, and active-record cleanup.

Next:
- Run `prepare_ai_workspace.py --change CHG-20260714-010`.
- Commit Workspace evidence/config snapshot, push affected repositories, then remove completed active record.

Blocked:
- None.

Recent verification:
- `git status --short --branch` in four repositories
- `python3 scripts/prepare_ai_workspace.py --change CHG-20260714-010`
- `go test ./...` with Go 1.26 toolchain
- `curl` create noop task and claim task requests
- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `python3 -m unittest discover -s tests`
- `python3 scripts/verify_skills.py`
- `python3 scripts/verify_m0_config.py`
- `npm run verify`
- out-of-scope `rg` scans over changed runtime files

## 13. DONE Gate

- [ ] Scope completed.
- [x] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Manual verification evidence recorded where required.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories touched only if listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.
- [ ] Completed active record removed after Git history records the CHG.
