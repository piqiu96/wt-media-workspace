# CHG-20260715-006: M0-R5 CI、Contract Map、Release Matrix 和跨平台工程门禁

## 1. Basic Information

- Level: M
- Status: VERIFYING
- Created: 2026-07-15
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-cloud`
  - `wt-media-agent`
  - `wt-media-desktop`
  - `wt-media-workspace`

## 2. Change Goal

完成 revised M0 的 R5 工程门禁：CI、Contract Map、Release Matrix 必须反映 M0-R2/R3/R4 已经验证过的真实 bootstrap/test/build/migration/Tauri 路径，历史 echo-only 或 scaffold-only 门禁不能继续代表 M0。

本 CHG 只关闭 M0-R5，不关闭 M0，也不启动 M1。

## 3. Baseline References

- Master route: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`
- R1 audit evidence: Workspace `63f1b7f`
- R2 Cloud/Web evidence: Cloud `db5b951`, Workspace `9c3971e`
- R3 Agent evidence: Agent `2b65ac5`, Workspace `67cc801`
- R4 Desktop evidence: Desktop `dd2ff80`, Workspace `a2978a9`
- Contract map: `wt-media-workspace/config/contract-map.yaml`
- Release matrix: `wt-media-workspace/config/release-matrix.yaml`

## 4. Current Facts

- Four workflow files already exist:
  - `wt-media-cloud/.github/workflows/m0-cloud.yml`
  - `wt-media-agent/.github/workflows/m0-agent.yml`
  - `wt-media-desktop/.github/workflows/m0-desktop.yml`
  - `wt-media-workspace/.github/workflows/m0-workspace.yml`
- Existing workflows mostly run historical health checks and do not fully cover the revised M0 real bootstrap/build/migration/Tauri gates.
- `release-matrix.yaml` still records historical Desktop Node 25 and no Rust/Cargo success fact.
- `contract-map.yaml` already records active provider/consumer ownership, but R5 must verify it still matches the current repository files and known placeholder task schema status.

## 5. Scope

### Add

- CI checks that run the real M0 scripts introduced by R2/R3/R4.
- Workspace verification coverage for release matrix and contract map consistency.
- Evidence for workflow/config diffs and local verification.

### Modify

- Existing M0 workflow YAML in Cloud, Agent, Desktop and Workspace.
- Workspace config verification scripts only as needed to enforce current R5 facts.
- `config/release-matrix.yaml` and related docs/evidence to reflect the current verified M0 toolchain.

### Delete

- Completed Active CHG-20260715-005 files from `delivery/active`; Git history retains the record.

### Explicitly Not Doing

- Running GitHub-hosted CI remotely.
- Adding production deployment or packaging release jobs beyond M0 engineering gates.
- Implementing M0-R6 full three-runtime integrated local acceptance.
- Implementing M1 task closure, auth, business UI or runtime features.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | R5 CI must represent real M0 bootstrap/test/build/migration gates, not scaffold-only health checks. | CONFIRMED |
| D-02 | Release Matrix should distinguish historical verified releases from the current revised M0 readiness snapshot. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Start Gate for M0-R5. | DONE | `evidence/start-gate.md`. |
| T-02 | Update Cloud/Agent/Desktop/Workspace CI gates to real M0 commands. | DONE | `evidence/workflow-matrix.md`. |
| T-03 | Update Release Matrix and config verification for revised M0 toolchain facts. | DONE | `evidence/config-verification.md`. |
| T-04 | Run local verification matrix and record evidence. | DONE | `evidence/verification-summary.md`. |
| T-05 | Diff check and independent commits. | VERIFYING | Diff check passed; commits pending. |

## 9. Repository Checklist

### wt-media-cloud

- [x] Workflow uses real bootstrap/test/migration/build gates.

### wt-media-agent

- [x] Workflow uses real uv/bootstrap/test/storage migration/build gates.

### wt-media-desktop

- [x] Workflow uses real npm/Vite/Tauri/Cargo gates.

### wt-media-workspace

- [x] Workflow verifies governance, contract map and release matrix.
- [x] Release Matrix reflects current revised M0 readiness facts.
- [x] Evidence and checkpoint updated.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one Active CHG exists and AI context points to CHG-20260715-006. | `prepare_ai_workspace.py --no-write`. | PASS |
| AC-02 | CI definitions cover Cloud/Web, Agent, Desktop/Tauri and Workspace governance real M0 gates. | Workflow diff and evidence. | PASS |
| AC-03 | Contract Map and Release Matrix are verified by Workspace scripts/tests. | `verify_m0_config.py`, unit tests. | PASS |
| AC-04 | No business runtime behavior is changed. | Diff review. | PASS |

## 11. Evidence

- `evidence/start-gate.md`
- `evidence/workflow-matrix.md`
- `evidence/config-verification.md`
- `evidence/verification-summary.md`
- `evidence/diff-summary.md`

## 12. Current Checkpoint

Completed:
- M0-R4 was committed: Desktop `dd2ff80`, Workspace `a2978a9`.
- CHG-20260715-006 was activated for M0-R5.
- Cloud/Agent/Desktop/Workspace M0 workflows were updated to real revised M0 gates.
- Release Matrix and Workspace verification scripts were updated to current Desktop Node/Rust/Cargo facts.
- `verify_m0_local.sh` was updated to the real revised M0 command matrix.
- Runtime workflow commits completed: Cloud `0020854`, Agent `3d047fb`, Desktop `047d04c`.

Current:
- Diff check and independent commits.

Next:
- Commit Workspace workflow/config/evidence changes; next CHG should be M0-R6.

Blocked:
- None.

Recent verification:
- `python3 scripts/verify_m0_config.py`: PASS.
- `python3 scripts/verify_product_master_alignment.py`: PASS.
- `python3 -m unittest discover -s tests`: PASS, 13 tests.
- `python3 scripts/prepare_ai_workspace.py --change CHG-20260715-006 --no-write`: PASS.
- `sh -n scripts/verify_m0_local.sh`: PASS.
- `git commit` runtime workflow commits: Cloud `0020854`, Agent `3d047fb`, Desktop `047d04c`.

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
