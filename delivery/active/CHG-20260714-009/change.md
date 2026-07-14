# CHG-20260714-009: M1-C2 Agent Registration And Heartbeat

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

Implement the M1 Agent node registration and heartbeat slice so Agent can identify itself to Cloud and Cloud can track node liveness through Cloud-owned Cloud-Agent API endpoints.

## 3. Baseline References

- Master implementation plan: `delivery/MASTER_IMPLEMENTATION_PLAN.md#M1Cloud-Agent-Desktop最小任务闭环`
- Engineering architecture: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Contract ownership: `docs/contracts/ownership.md`
- Compatibility policy: `docs/contracts/compatibility-policy.md`
- Cloud-Agent contract from CHG-008: `wt-media-cloud/contracts/cloud-agent-api/v1/compatibility.openapi.yaml`

## 4. Current Facts

- M1 is `IN_PROGRESS`.
- M1-C1 completed Cloud-Agent `v1@2026.07.14.1` compatibility.
- No active CHG existed before CHG-009.
- Cloud owns Cloud-Agent API definitions.
- Agent consumes Cloud-Agent API definitions.
- Desktop is not affected by M1-C2.

## 5. Scope

### Add

- Cloud-owned Agent registration and heartbeat contract artifact.
- Cloud runtime endpoints for Agent registration and heartbeat.
- Cloud in-memory M1 Agent registry for node liveness.
- Agent Cloud client methods for registration and heartbeat.
- Unit tests and evidence.

### Modify

- Cloud-Agent contract README.
- Cloud route wiring.
- Agent configuration/client surface as needed.
- Workspace delivery records and evidence.

### Delete

- None.

### Explicitly Not Doing

- Do not implement task creation, task polling, lease, progress, or result upload.
- Do not implement noop executor.
- Do not implement Local Agent SSE.
- Do not implement Desktop pages or process control.
- Do not implement user/account/media account/Profile modules.
- Do not connect Agent directly to Cloud MySQL.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Cloud owns Agent registration and heartbeat contracts. | CONFIRMED |
| D-02 | M1-C2 may use in-memory Cloud state; database persistence is outside this CHG. | CONFIRMED |
| D-03 | Agent registration must include Cloud-Agent contract version facts. | CONFIRMED |
| D-04 | Desktop is out of scope for M1-C2. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Create Active CHG and refresh context. | DONE | `prepare_ai_workspace.py --change CHG-20260714-009` |
| T-02 | Add Cloud registration/heartbeat contract and runtime endpoints. | TODO | Cloud tests |
| T-03 | Add Agent registration/heartbeat client. | TODO | Agent tests |
| T-04 | Run integrated verification and record evidence. | TODO | Workspace, Cloud, Agent, Desktop checks |
| T-05 | Commit, push, cleanup active record. | TODO | Git/CI status |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG record.
- [x] Update active ledger.
- [x] Set M1 Active CHG to CHG-009.
- [x] Refresh root AI context.
- [ ] Record evidence and cleanup completed active record.

### wt-media-cloud

- [ ] Add Cloud-owned registration/heartbeat contract artifact.
- [ ] Add in-memory Agent registry.
- [ ] Add registration and heartbeat endpoints.
- [ ] Add tests.
- [ ] Commit independently.

### wt-media-agent

- [ ] Add Cloud client registration and heartbeat methods.
- [ ] Add tests.
- [ ] Commit independently.

### wt-media-desktop

- [x] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one active CHG exists during implementation. | `find delivery/active -maxdepth 2 -name change.md` | PASS |
| AC-02 | Cloud owns formal registration/heartbeat contract artifact. | File inspection | TODO |
| AC-03 | Cloud can register an Agent and update heartbeat state. | Cloud tests | TODO |
| AC-04 | Agent can build and send registration/heartbeat requests. | Agent tests | TODO |
| AC-05 | No task creation, polling, lease, executor, SSE, Desktop, or account/Profile behavior is introduced. | Diff scan | TODO |
| AC-06 | Affected repositories are committed independently and pushed. | Git log/status | TODO |

## 11. Evidence

- `evidence/task-01-context.md`
- `evidence/cloud-registration-heartbeat.md`
- `evidence/agent-client.md`
- `evidence/integration-and-diff.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- Confirmed request to continue through M1.
- Confirmed M1-C1 completed and M1 is `IN_PROGRESS`.
- Confirmed no Active CHG existed.
- Confirmed four repositories were clean and synchronized.
- Created CHG-009 active record.
- Updated `delivery/LEDGER.md`.
- Updated M1 Active CHG in `delivery/MASTER_IMPLEMENTATION_PLAN.md`.
- Refreshed root `.ai/CURRENT_CONTEXT.md`.
- Recorded T-01 evidence.

Current:
- T-02 Cloud registration/heartbeat contract and endpoints.

Next:
- Commit Workspace start record, then implement Cloud provider slice.

Blocked:
- None.

Recent verification:
- `find wt-media-workspace/delivery/active -maxdepth 2 -name change.md -print`
- `git status --short --branch` in four repositories
- `python3 scripts/prepare_ai_workspace.py --change CHG-20260714-009`

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
