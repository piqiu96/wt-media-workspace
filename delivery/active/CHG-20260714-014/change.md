# CHG-20260714-014: M1-C7 Three-End Integration Verification

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`
  - `wt-media-agent`
  - `wt-media-desktop`

## 2. Change Goal

Prove the M1 Cloud-Agent-Desktop technical spine with a repeatable integration verification: Cloud runs, Agent registers and executes a noop task through real HTTP, Local Agent status/SSE is reachable, Desktop verification passes, and Workspace records the M1 release evidence.

## 3. Baseline References

- Engineering baseline: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Contract governance: `docs/contracts/ownership.md`
- Contract governance: `docs/contracts/contract-map.md`
- Contract compatibility: `docs/contracts/compatibility-policy.md`
- Master plan: `delivery/MASTER_IMPLEMENTATION_PLAN.md#M1Cloud-Agent-Desktop-最小任务闭环`

## 4. Current Facts

- M1-C1 through M1-C6 are complete and pushed.
- Cloud provides compatibility, registration, heartbeat, noop task creation/claim/report, and task lookup.
- Agent provides `CloudAgentClient`, `NoopExecutor`, and Local Agent status/SSE HTTP endpoints.
- Desktop provides dependency-free Local Agent control/status verification via `npm run verify`.

## 5. Scope

### Add

- Workspace M1 integration verification script.
- Evidence for Cloud-Agent real HTTP noop execution.
- Evidence for Local Agent status/SSE and Desktop verification.
- M1 final release-matrix entry.

### Modify

- Workspace M1 plan status and release-matrix verification coverage.

### Delete

- None.

### Explicitly Not Doing

- Do not implement M2 user/account/profile code.
- Do not modify Cloud, Agent, or Desktop business code unless an integration defect blocks M1.
- Do not create new formal contract definitions.
- Do not start M2 after closing M1.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | M1-C7 verification starts real Cloud and Local Agent HTTP processes and drives Cloud-Agent task flow over HTTP. | CONFIRMED |
| D-02 | Desktop is included through its M1 `npm run verify` control/status verification. | CONFIRMED |

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
| T-01 | Create Active CHG and refresh AI context. | DONE | `prepare_ai_workspace.py --change CHG-20260714-014` |
| T-02 | Add repeatable M1 integration verification script. | TODO | Script initially absent, then passes. |
| T-03 | Run full M1 integration verification and record evidence. | TODO | `python3 scripts/verify_m1_integration.py` |
| T-04 | Mark M1 DONE and update release matrix. | TODO | Workspace config verification. |
| T-05 | Complete CHG and remove active record. | TODO | Active ledger empty after completion. |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG.
- [ ] Add integration script.
- [ ] Record integration evidence.
- [ ] Mark M1 DONE.
- [ ] Remove active record when complete.

### wt-media-cloud

- [ ] Verified via real HTTP server.

### wt-media-agent

- [ ] Verified via real CloudAgentClient and NoopExecutor.
- [ ] Verified via Local Agent status/SSE server.

### wt-media-desktop

- [ ] Verified via `npm run verify`.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Cloud compatibility and health endpoints are reachable in a real process. | `python3 scripts/verify_m1_integration.py` | TODO |
| AC-02 | Agent registers, claims a noop task, and reports succeeded over Cloud HTTP. | `python3 scripts/verify_m1_integration.py` | TODO |
| AC-03 | Cloud stores final task status `succeeded` with progress `100`. | `python3 scripts/verify_m1_integration.py` | TODO |
| AC-04 | Local Agent status and SSE endpoints return M1 status event data. | `python3 scripts/verify_m1_integration.py` | TODO |
| AC-05 | Desktop M1 control/status verification passes. | `python3 scripts/verify_m1_integration.py` | TODO |

## 11. Evidence

Evidence files live in `evidence/` and must record facts, not repeat requirements.

- `evidence/task-01-context.md`
- `evidence/integration-run.md`
- `evidence/m1-final-summary.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- Created CHG-014 active record.

Current:
- M1 integration verification script.

Next:
- Add failing verification for missing script, then implement script.

Blocked:
- None.

Recent verification:
- CHG-013 workspace and Desktop verification passed before CHG-014 creation.

## 13. DONE Gate

- [ ] Scope completed.
- [ ] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Manual verification evidence recorded where required.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories touched only if listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.
