# CHG-20260714-008: M1-C1 Cloud-Agent Contract And Version Compatibility

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

Activate the first M1 Cloud-Agent contract slice by defining a Cloud-owned `v1` compatibility contract, exposing a minimal Cloud runtime compatibility endpoint, and adding Agent-side version compatibility checks. This creates a real, testable handshake point for later Agent registration, heartbeat, and task execution CHGs.

## 3. Baseline References

- Master implementation plan: `delivery/MASTER_IMPLEMENTATION_PLAN.md#M1Cloud-Agent-Desktop最小任务闭环`
- Contract ownership: `docs/contracts/ownership.md`
- Compatibility policy: `docs/contracts/compatibility-policy.md`
- Breaking-change policy: `docs/contracts/breaking-change-policy.md`
- Contract map: `docs/contracts/contract-map.md`

## 4. Current Facts

- M0 is `DONE`.
- No active CHG existed before CHG-008.
- `cloud_agent_api` is owned by `wt-media-cloud`.
- `wt-media-agent` consumes the Cloud-Agent API.
- `wt-media-desktop` does not consume the Cloud-Agent API in M1-C1.
- `cloud_agent_api` is currently `placeholder_only` in Workspace config.
- Existing Cloud runtime exposes health endpoints only.
- Existing Agent runtime exposes Local Agent M0 health only.

## 5. Scope

### Add

- Cloud-owned Cloud-Agent `v1` compatibility contract artifact.
- Cloud runtime compatibility endpoint for the Cloud-Agent contract.
- Agent-side expected Cloud-Agent contract version and compatibility checker.
- Tests for Cloud compatibility data and Agent compatibility checks.
- Workspace config/release updates recording the M1 active Cloud-Agent contract.
- Evidence for verification, diff scope, and final commits.

### Modify

- `wt-media-cloud` Cloud-Agent contract placeholder status and route wiring.
- `wt-media-agent` consumer-side contract version support.
- `wt-media-workspace/config/contract-map.yaml`.
- `wt-media-workspace/config/release-matrix.yaml`.
- `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`.

### Delete

- None.

### Explicitly Not Doing

- Do not implement Agent registration.
- Do not implement heartbeat.
- Do not implement task creation, polling, lease, progress, result upload, or retry behavior.
- Do not implement Desktop pages or Desktop contract consumption.
- Do not implement user/account/media account/Profile modules.
- Do not introduce breaking contract changes.
- Do not make Workspace a runtime dependency.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | `wt-media-cloud` owns the formal Cloud-Agent contract. | CONFIRMED |
| D-02 | M1-C1 uses a minimal runtime compatibility endpoint, not a paper-only contract. | CONFIRMED |
| D-03 | `wt-media-agent` records expected Cloud-Agent major version and contract revision as consumer-side facts. | CONFIRMED |
| D-04 | `wt-media-desktop` is out of scope for M1-C1. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Create Active CHG, update M1 plan state, and refresh context. | DONE | `prepare_ai_workspace.py --change CHG-20260714-008` |
| T-02 | Add Cloud-owned Cloud-Agent `v1` compatibility contract and runtime endpoint. | DONE | `evidence/cloud-contract-and-endpoint.md` |
| T-03 | Add Agent consumer compatibility version checks. | DONE | `evidence/agent-compatibility.md` |
| T-04 | Update Workspace Contract Map, Release Matrix, verification script, and evidence. | DONE | `evidence/workspace-config.md` |
| T-05 | Run integrated acceptance, commit affected repos, push, and close CHG. | IN_PROGRESS | `evidence/integration-and-diff.md` |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG record.
- [x] Update active ledger.
- [x] Set M1 Active CHG to CHG-008.
- [x] Refresh root AI context.
- [x] Update Contract Map and Release Matrix.
- [x] Update verification script/tests for M1 Cloud-Agent contract state.
- [ ] Record evidence and cleanup completed active record.

### wt-media-cloud

- [x] Add provider-owned Cloud-Agent `v1` compatibility contract artifact.
- [x] Add runtime compatibility contract constants.
- [x] Add compatibility endpoint.
- [x] Add/extend tests.
- [ ] Commit independently.

### wt-media-agent

- [x] Add Cloud-Agent consumer compatibility module.
- [x] Add/extend tests.
- [ ] Commit independently.

### wt-media-desktop

- [x] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one active CHG exists during implementation. | `find delivery/active -maxdepth 2 -name change.md` | PASS |
| AC-02 | Cloud owns the formal Cloud-Agent `v1` compatibility contract. | File inspection and contract map | PASS |
| AC-03 | Cloud exposes a runtime compatibility endpoint. | Cloud tests and curl | PASS |
| AC-04 | Agent can determine whether Cloud-Agent contract metadata is compatible. | Agent unit tests | PASS |
| AC-05 | Workspace machine-readable config records active `cloud_agent_api` without duplicating full definitions. | `scripts/verify_m0_config.py` or successor validation | PASS |
| AC-06 | Release Matrix records a verified M1-C1 combination. | File inspection and config verification | PASS |
| AC-07 | No registration, heartbeat, task execution, Desktop page, or account/Profile behavior is introduced. | Diff scan | PASS |
| AC-08 | Affected repositories are committed independently and pushed. | Git log/status | TODO |

## 11. Evidence

Evidence files live in `evidence/` and must record facts, not repeat requirements.

Planned records:

- `evidence/task-01-context.md`
- `evidence/cloud-contract-and-endpoint.md`
- `evidence/agent-compatibility.md`
- `evidence/workspace-config.md`
- `evidence/integration-and-diff.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- Confirmed design approach with user.
- Confirmed M0 is `DONE`.
- Confirmed no Active CHG existed.
- Confirmed four repositories were clean and synchronized.
- Created CHG-008 active record.
- Updated `delivery/LEDGER.md`.
- Updated M1 Active CHG in `delivery/MASTER_IMPLEMENTATION_PLAN.md`.
- Refreshed root `.ai/CURRENT_CONTEXT.md`.
- Recorded T-01 evidence.
- Added Cloud-owned Cloud-Agent `v1` compatibility OpenAPI artifact.
- Added Cloud compatibility module and endpoint.
- Verified Cloud tests and endpoint response.
- Added Agent consumer compatibility checker.
- Verified Agent unit tests.
- Updated Workspace Contract Map and Release Matrix.
- Updated Workspace config verification tests.
- Verified Workspace tests, Skill source checks, and config validation.
- Ran integrated local acceptance across Workspace, Cloud, Agent, and Desktop.
- Verified Cloud compatibility endpoint response.
- Confirmed diff scan has no out-of-scope implementation.

Current:
- T-05 integrated acceptance, commit/push, and close CHG.

Next:
- Commit final evidence snapshot, push affected repositories, then remove completed active record.

Blocked:
- None.

Recent verification:
- `find wt-media-workspace/delivery/active -maxdepth 2 -name change.md -print`
- `git status --short --branch` in four repositories
- Contract governance and existing placeholder contract inspection
- `python3 scripts/prepare_ai_workspace.py --change CHG-20260714-008`
- `go test ./...` with Go 1.26 toolchain
- `curl http://127.0.0.1:18080/api/v1/cloud-agent/compatibility`
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
