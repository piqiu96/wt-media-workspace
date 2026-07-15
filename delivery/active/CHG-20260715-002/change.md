# CHG-20260715-002: M0-R1 真实工具链、依赖安装和脚手架差距核查

## 1. Basic Information

- Level: M
- Status: VERIFYING
- Created: 2026-07-15
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`

Read-only audited repositories:

- `wt-media-cloud`
- `wt-media-agent`
- `wt-media-desktop`

## 2. Change Goal

执行新 Master Plan 的 M0-R1：核清 Cloud、Web、Agent、Desktop 的真实工具链、依赖、构建、测试、启动停止、Migration、CI/Contract/Release 治理现状，形成可复验的证据矩阵和 M0-R2 至 M0-R6 的后续执行清单。

本 CHG 不把 M0 或 M1 标记为完成；它的目标是消除基础环境不确定性，让后续 M0 修复和最终人工端到端验收有明确闭环。

## 3. Baseline References

- Product baseline: `docs/product`
- Engineering baseline: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Contract governance: `docs/contracts/contract-map.md`, `config/contract-map.yaml`
- Release governance: `config/release-matrix.yaml`
- Master route: `delivery/MASTER_IMPLEMENTATION_PLAN.md`
- Alignment source: completed CHG-20260715-001 commits through `623789b`

## 4. Current Facts

- M0 is `IN_PROGRESS`; M1 is `NOT_STARTED` and depends on M0 `DONE`.
- Revised M0 requires real Cloud/Web/Agent/Desktop bootstrap, build, test, start/stop, health check, migration and CI gates.
- Revised M1 requires persistent MySQL task/Agent state, formal task schemas, real Desktop/Tauri/Local Agent control and restart recovery before M2 can be product-complete.
- Historical M0/M1 evidence remains useful but is insufficient because earlier gates accepted scaffold, mock-only, in-memory or noop paths.
- Runtime repositories may be inspected and commands may be run for evidence, but this CHG only writes Workspace delivery records.

## 5. Scope

### Add

- M0-R1 start-gate evidence.
- Toolchain and dependency inventory for Cloud, Web, Agent and Desktop.
- Repository command matrix covering bootstrap, test, build, start/stop, health check and migration paths where currently available.
- Gap register mapping every failed, missing or unverified M0 gate to M0-R2 through M0-R6.
- M0/M1 final manual acceptance checklist skeleton for the later end-to-end closure.

### Modify

- `delivery/MASTER_IMPLEMENTATION_PLAN.md` M0 Active CHG pointer and any factual checkpoint wording needed by this CHG.
- `delivery/LEDGER.md`.
- Generated AI context for the active CHG.

### Delete

- Completed Active CHG-20260715-001 files from `delivery/active`; Git history retains the record.

### Explicitly Not Doing

- Implementing Cloud, Web, Agent, Desktop, MySQL schema, SQLite schema, Tauri, task schema or Local Agent runtime changes.
- Marking M0 or M1 `DONE`.
- Starting M1 or M2 before M0 reaches the revised DONE gate.
- Treating scaffold-only, mock-only, echo or unavailable build commands as passing evidence.
- Fetching or changing dependencies silently; any dependency installation command must be recorded with expected and actual result.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Execute the revised milestone route in order: complete M0 before M1, and complete M1 before renewed M2 product execution. | CONFIRMED |
| D-02 | M0-R1 is an evidence and gap-closure CHG. It may prove commands pass or fail, but failed gates become explicit M0-R2 through M0-R6 work rather than hidden risk. | CONFIRMED |
| D-03 | Final M0/M1 closure must support user manual inspection of a real, mock-free base environment and end-to-end Cloud-Agent-Desktop-Web path. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

Each task follows:

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
| T-01 | Activate M0-R1 and complete the Start Gate. | DONE | `evidence/start-gate.md`. |
| T-02 | Inventory local toolchains and dependency entry points. | DONE | `evidence/toolchain-inventory.md`. |
| T-03 | Audit Cloud and Web bootstrap, test, build, start/stop, health and migration readiness. | DONE | `evidence/repository-command-matrix.md`. |
| T-04 | Audit Agent package, dependency, test, build, start/stop, health and SQLite migration readiness. | DONE | `evidence/repository-command-matrix.md`. |
| T-05 | Audit Desktop Vue/Tauri dependency, test, build, dev/start and mock-free entry readiness. | DONE | `evidence/repository-command-matrix.md`. |
| T-06 | Audit CI, Contract Map, Release Matrix and cross-repository gate consistency. | DONE | `evidence/m0-gap-register.md` and `evidence/verification-summary.md`. |
| T-07 | Produce the M0 gap register and M0/M1 manual acceptance checklist skeleton. | DONE | `evidence/m0-gap-register.md` and `evidence/m1-manual-acceptance-skeleton.md`. |
| T-08 | Run final Workspace verification, diff review and commit the M0-R1 evidence. | DONE | `evidence/verification-summary.md` and `evidence/diff-summary.md`; final commands run before commit. |

## 9. Repository Checklist

### wt-media-workspace

- [x] Active CHG, Ledger and generated context point to CHG-20260715-002.
- [x] M0-R1 evidence files are recorded under this CHG.
- [x] M0-R2 through M0-R6 follow-up scope is explicit.

### wt-media-cloud

- [x] Read-only audit completed; no code changes in this CHG.

### wt-media-agent

- [x] Read-only audit completed; no code changes in this CHG.

### wt-media-desktop

- [x] Read-only audit completed; no code changes in this CHG.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one Active CHG exists and AI context points to CHG-20260715-002. | Active directory and `prepare_ai_workspace.py --no-write`. | PASS |
| AC-02 | All relevant local toolchains and dependency entry points are inventoried. | Toolchain evidence. | PASS |
| AC-03 | Cloud/Web/Agent/Desktop command readiness is recorded with pass/fail/blocker evidence. | Repository command matrix. | PASS |
| AC-04 | Every revised M0 exit gate has an explicit current status and next CHG owner. | Gap register. | PASS |
| AC-05 | Later M1 end-to-end manual closure checklist is present and depends on M0 DONE. | Manual acceptance checklist evidence. | PASS |
| AC-06 | Runtime repositories remain unchanged by this audit CHG. | Git status and diff summary. | PASS |

## 11. Evidence

Planned evidence:

- `evidence/start-gate.md`
- `evidence/toolchain-inventory.md`
- `evidence/repository-command-matrix.md`
- `evidence/m0-gap-register.md`
- `evidence/m1-manual-acceptance-skeleton.md`
- `evidence/verification-summary.md`
- `evidence/diff-summary.md`

## 12. Current Checkpoint

Completed:
- CHG-20260715-001 passed fresh verification and was removed from Active scope.
- M0-R1 Active CHG was created.
- Start Gate, toolchain inventory, repository command matrix, M0 gap register and M1 manual acceptance skeleton were recorded.
- Governance verifier hardcoding was fixed so it validates the actual Active CHG instead of CHG-20260715-001 only.

Current:
- Final verification and Workspace commit.

Next:
- Close or hand off CHG-20260715-002, then start M0-R2 Cloud/Web bootstrap and MySQL migration execution.

Blocked:
- None.

Recent verification:
- `python3 scripts/verify_product_master_alignment.py` passed before activating this CHG.
- `python3 scripts/verify_m0_config.py` passed before activating this CHG.
- `python3 -m unittest discover -s tests` passed 12 tests before activating this CHG.
- `python3 scripts/prepare_ai_workspace.py --change CHG-20260715-001 --no-write` passed before activating this CHG.
- `git -C wt-media-workspace diff --check` passed before activating this CHG.
- `python3 scripts/verify_product_master_alignment.py` initially failed after CHG activation because the verifier hardcoded CHG-20260715-001; it now passes after the dynamic Active CHG fix.
- `python3 -m unittest discover -s tests` passes 12 Workspace tests after the verifier fix.
- Cloud `go test ./...`, Cloud build and authorized Cloud health check pass.
- Cloud Web `npm test` passes 8 tests and `npm run build` passes.
- Agent `.venv/bin/python -m unittest discover -s tests` passes 39 tests; authorized Agent health check passes; authorized `uv build` creates sdist and wheel.
- Desktop scaffold health passes, but real Desktop build/dev/package/bootstrap/lint and Cargo check fail the revised M0 gate.
- MySQL 3306 TCP probe passes after authorization, but mysql CLI and a formal migration runner are not available.

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
