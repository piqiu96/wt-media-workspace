# CHG-20260714-012: M1-C5 Local Agent HTTP SSE Offline Queue

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-agent`

## 2. Change Goal

Add Local Agent loopback HTTP status, a minimal SSE event stream, and an offline pending result queue so Desktop can observe Agent state in the next CHG.

## 3. Baseline References

- Master implementation plan: `delivery/MASTER_IMPLEMENTATION_PLAN.md#M1Cloud-Agent-Desktop最小任务闭环`
- Engineering architecture: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Contract ownership: `docs/contracts/ownership.md`

## 4. Current Facts

- Agent can register, heartbeat, claim a task, execute noop, and report status.
- Local Agent currently exposes `/healthz` only.
- Local Agent API and local SSE contracts are owned by `wt-media-agent`.

## 5. Scope

### Add

- Local Agent `/api/v1/status`.
- Local Agent `/api/v1/events` SSE snapshot stream.
- In-memory offline pending result queue.
- Agent-owned Local Agent contract docs.
- Tests and evidence.

### Explicitly Not Doing

- Do not add Desktop UI/process control.
- Do not add Cloud persistence.
- Do not add business executors.
- Do not add user/account/Profile modules.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Local Agent API and SSE are owned by `wt-media-agent`. | CONFIRMED |
| D-02 | M1-C5 uses an in-memory pending result queue. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Create Active CHG and refresh context. | DONE | `prepare_ai_workspace.py --change CHG-20260714-012` |
| T-02 | Add Local Agent status/SSE/offline queue. | TODO | Agent tests |
| T-03 | Update Workspace evidence and release matrix. | TODO | Workspace/Agent/Desktop checks |
| T-04 | Commit, push, cleanup active record. | TODO | Git/CI status |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG record.
- [x] Update active ledger.
- [x] Set M1 Active CHG to CHG-012.
- [x] Refresh root AI context.

### wt-media-agent

- [ ] Add Local Agent status endpoint.
- [ ] Add SSE endpoint.
- [ ] Add pending result queue.
- [ ] Add tests.

### wt-media-cloud

- [x] Not affected.

### wt-media-desktop

- [x] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one active CHG exists during implementation. | `find delivery/active -maxdepth 2 -name change.md` | PASS |
| AC-02 | Local Agent exposes status. | Agent tests/curl | TODO |
| AC-03 | Local Agent exposes SSE event snapshot. | Agent tests | TODO |
| AC-04 | Offline pending result queue stores and drains results. | Agent tests | TODO |
| AC-05 | No Desktop UI/process control or Cloud persistence is introduced. | Diff scan | TODO |
| AC-06 | Affected repositories are committed independently and pushed. | Git log/status | TODO |

## 11. Evidence

- `evidence/task-01-context.md`
- `evidence/agent-local-api.md`
- `evidence/integration-and-diff.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- Created CHG-012 active record.
- Updated `delivery/LEDGER.md`.
- Updated M1 Active CHG.
- Refreshed root `.ai/CURRENT_CONTEXT.md`.
- Recorded T-01 evidence.

Current:
- T-02 Local Agent status/SSE/offline queue.

Next:
- Run `prepare_ai_workspace.py --change CHG-20260714-012`.
- Commit Workspace start record.

Blocked:
- None.

Recent verification:
- `git status --short --branch` in four repositories.
- `python3 scripts/prepare_ai_workspace.py --change CHG-20260714-012`

## 13. DONE Gate

- [ ] Scope completed.
- [x] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Diff checked for out-of-scope changes.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.
- [ ] Completed active record removed after Git history records the CHG.
