# CHG-20260715-007: M0-R6 三端独立构建、启动、健康检查和综合工程验收

## 1. Basic Information

- Level: M
- Status: VERIFYING
- Created: 2026-07-15
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-agent`
  - `wt-media-workspace`

## 2. Change Goal

完成 revised M0 的最终综合验收：基于 M0-R2/R3/R4/R5 的真实工程门禁，记录 Cloud/Web、Agent、Desktop 三端独立 bootstrap/test/build/start/health/stop 和迁移链路证据，确认 M0 可进入人工基础环境验收。

本 CHG 只关闭 M0-R6；如果全部通过，M0 才可由人工验收确认后进入 DONE/准备 M1。

## 3. Baseline References

- Master route: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`
- R2 Cloud/Web evidence: Cloud `db5b951`, Workspace `9c3971e`
- R3 Agent evidence: Agent `2b65ac5`, Workspace `67cc801`
- R4 Desktop evidence: Desktop `dd2ff80`, Workspace `a2978a9`
- R5 CI/config evidence: Cloud `0020854`, Agent `3d047fb`, Desktop `047d04c`, Workspace `51f63c5`

## 4. Current Facts

- MySQL is expected at `127.0.0.1:3306` with user `root`; local DSN is provided through `WT_MEDIA_MYSQL_DSN`.
- Cloud, Agent and Desktop already have real M0 scripts.
- R6 should not introduce new runtime behavior unless a verification-only blocker requires a small script fix.
- Agent `scripts/bootstrap.sh` used the default uv cache under the user home and failed under the managed workspace sandbox; this is a verification-only script fix, not Agent business behavior.

## 5. Scope

### Add

- Comprehensive R6 evidence files under this CHG.

### Modify

- Workspace delivery/checkpoint records.
- Agent bootstrap script only if needed to make the existing M0 gate reproducible in the workspace.
- M0 status in Master Plan only if the R6 evidence is sufficient.

### Delete

- Completed Active CHG-20260715-006 files from `delivery/active`; Git history retains the record.

### Explicitly Not Doing

- Implementing M1 task persistence or end-to-end task behavior.
- Changing Cloud, Agent or Desktop business runtime code.
- Claiming remote GitHub Actions execution.
- Masking failed local dependency, migration, start, health or stop checks.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | M0-R6 is evidence-heavy and should not add business features. | CONFIRMED |
| D-02 | Any failed start/health/stop check blocks M0 DONE until fixed or explicitly recorded. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Start Gate for M0-R6. | DONE | `evidence/start-gate.md`. |
| T-02 | Run Workspace governance checks. | DONE | `evidence/workspace-checks.md`. |
| T-03 | Run Cloud/Web bootstrap/test/migration/build/start/health/stop. | DONE | `evidence/cloud-checks.md`. |
| T-04 | Run Agent bootstrap/test/storage migration/build/start/health/stop. | DONE | `evidence/agent-checks.md`. |
| T-05 | Run Desktop bootstrap/lint/test/build/start/health/stop. | DONE | `evidence/desktop-checks.md`. |
| T-06 | Record summary, update M0 status if justified, diff check and commit Workspace. | VERIFYING | Evidence recorded; M0 set to VERIFYING; diff check passed; Workspace commit pending. |

## 9. Repository Checklist

### wt-media-workspace

- [x] Active CHG and Ledger point to CHG-20260715-007.
- [x] Comprehensive evidence recorded.
- [x] M0 Master Plan status updated to `VERIFYING`; not `DONE`.
- [ ] Workspace commit made.

### Runtime repositories

- [x] Agent bootstrap/start-health script fix committed: `0e07b4e`.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one Active CHG exists and AI context points to CHG-20260715-007. | `prepare_ai_workspace.py --no-write`. | PASS |
| AC-02 | Workspace governance/config/alignment checks pass. | Workspace command evidence. | PASS |
| AC-03 | Cloud/Web real bootstrap/test/migration/build/start/health/stop passes or blocker recorded. | Cloud command evidence. | PASS |
| AC-04 | Agent real bootstrap/test/storage migration/build/start/health/stop passes or blocker recorded. | Agent command evidence. | PASS |
| AC-05 | Desktop real bootstrap/lint/test/build/start/health/stop passes or blocker recorded. | Desktop command evidence. | PASS |
| AC-06 | No runtime code changes are introduced by R6. | Git status/diff review. | PASS |

## 11. Evidence

- `evidence/start-gate.md`
- `evidence/workspace-checks.md`
- `evidence/cloud-checks.md`
- `evidence/agent-checks.md`
- `evidence/desktop-checks.md`
- `evidence/verification-summary.md`
- `evidence/diff-summary.md`

## 12. Current Checkpoint

Completed:
- M0-R5 was committed: Cloud `0020854`, Agent `3d047fb`, Desktop `047d04c`, Workspace `51f63c5`.
- CHG-20260715-007 was activated for M0-R6.
- Workspace, Cloud/Web, Agent and Desktop command matrices passed.
- Agent verification script fixes were committed: `0e07b4e`.
- M0 was moved to `VERIFYING` pending final manual/user acceptance.

Current:
- Final Workspace verification, diff check and commit.

Next:
- Commit Workspace R6 evidence; user can perform manual M0 acceptance. If approved, proceed to M1-R1.

Blocked:
- None.

Recent verification:
- Workspace checks: PASS.
- Cloud/Web checks: PASS.
- Agent checks: PASS after script fixes.
- Desktop checks: PASS.
- Existing DB `wt-media-cloud` is not an empty migration target; isolated DB `wt_media_m0_r6_verify` passed migration.

## 13. DONE Gate

- [x] Scope completed.
- [x] No blocking `Q-xx`.
- [x] Acceptance matrix all PASS.
- [x] Automated tests passed or justified.
- [x] Manual verification evidence recorded where required.
- [x] Diff checked for out-of-scope changes.
- [x] Runtime repositories touched only if listed in scope.
- [x] Required baselines updated.
- [ ] Affected repositories committed independently.
