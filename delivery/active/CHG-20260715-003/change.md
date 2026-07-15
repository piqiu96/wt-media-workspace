# CHG-20260715-003: M0-R2 Cloud/Web 真实 bootstrap、build、test、MySQL Migration 和启动停止

## 1. Basic Information

- Level: M
- Status: VERIFYING
- Created: 2026-07-15
- Current repository: `wt-media-cloud`
- Affected repositories:
  - `wt-media-cloud`
  - `wt-media-workspace`

## 2. Change Goal

完成 revised M0 的 Cloud/Web 工程门禁：Cloud 和 Web 必须有真实可执行的 bootstrap、test、build、start/stop、health 检查和 MySQL migration 路径，能够在本机 MySQL 上从空库重复执行并留下证据。

本 CHG 只关闭 M0-R2，不关闭 M0，也不启动 M1。

## 3. Baseline References

- Engineering baseline: `wt-media-workspace/docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Master route: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`
- R1 audit evidence: commit `63f1b7f`
- Cloud repository rules: `wt-media-cloud/AGENTS.md`
- Cloud README and scripts: `wt-media-cloud/README.md`, `wt-media-cloud/scripts/README.md`
- Cloud migrations: `wt-media-cloud/migrations/20260714_*.sql`

## 4. Current Facts

- M0-R1 found Cloud Go tests, Cloud build, Cloud health, Web tests and Web build can pass.
- M0-R1 found MySQL TCP port 3306 reachable, but no mysql CLI and no formal Cloud migration runner.
- `wt-media-cloud/scripts/README.md` names stable command families, but only `scripts/verify-health.sh` currently exists.
- Web has `package-lock.json` and `node_modules/` present; `npm test` and `npm run build` pass.
- Cloud migration SQL files exist for current M2 tables; M0-R2 must provide a repeatable execution path without hand-editing tables.

## 5. Scope

### Add

- Cloud migration command or runner with tests.
- Stable Cloud scripts for bootstrap/test/build/start/stop/health/migration as needed by M0.
- Evidence for an empty local MySQL database migration run and repeat run.
- Evidence for Cloud/Web test/build/start/stop/health checks.

### Modify

- `wt-media-cloud` README/scripts documentation if command usage changes.
- `wt-media-workspace` active CHG evidence and checkpoint.
- `delivery/MASTER_IMPLEMENTATION_PLAN.md` only if M0-R2 findings require factual refinement.

### Delete

- Completed Active CHG-20260715-002 files from `delivery/active`; Git history retains the record.

### Explicitly Not Doing

- Implementing M1 persistent task/Agent registry behavior.
- Implementing new M2 business features.
- Changing Agent or Desktop runtime code.
- Marking M0 `DONE`; M0 still requires M0-R3 through M0-R6.
- Storing real secrets in committed scripts or evidence.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | M0-R2 closes only Cloud/Web and MySQL migration engineering readiness. | CONFIRMED |
| D-02 | MySQL migration must be executable from code or script and repeatable against a local empty database; SQL files alone do not pass the revised M0 gate. | CONFIRMED |
| D-03 | Web build/test can reuse existing Vite/Vitest setup, but bootstrap/start commands must be explicit enough for later M0-R6 acceptance. | CONFIRMED |

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
| T-01 | Start Gate for M0-R2. | DONE | `evidence/start-gate.md`. |
| T-02 | Add tests for Cloud migration execution behavior. | DONE | `evidence/migration-run.md`; RED failed on undefined runner API before implementation. |
| T-03 | Implement minimal repeatable MySQL migration runner/command. | DONE | Cloud commit `db5b951`; local MySQL first run applied 5, repeat run applied 0. |
| T-04 | Add or normalize stable Cloud scripts for bootstrap/test/build/start/stop/health/migration. | DONE | `evidence/cloud-web-command-matrix.md`. |
| T-05 | Add or normalize Web bootstrap/test/build/start evidence path. | DONE | `scripts/bootstrap.sh`, `scripts/test.sh`, `scripts/build.sh`; Web 8 tests and Vite build pass. |
| T-06 | Run full Cloud/Web verification matrix and record evidence. | DONE | `evidence/verification-summary.md`. |
| T-07 | Update Workspace evidence, checkpoint, acceptance matrix and commit affected repositories independently. | DONE | Cloud committed as `db5b951`; Workspace final verification runs before Workspace commit. |

## 9. Repository Checklist

### wt-media-cloud

- [x] Migration runner/command implemented and tested.
- [x] Stable scripts implemented or confirmed.
- [x] Cloud/Web verification evidence recorded.

### wt-media-workspace

- [x] Active CHG and Ledger point to CHG-20260715-003.
- [x] M0-R2 evidence recorded.
- [x] Checkpoint updated before handoff or completion.

### wt-media-agent

- [x] Not affected.

### wt-media-desktop

- [x] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one Active CHG exists and AI context points to CHG-20260715-003. | Active scan and `prepare_ai_workspace.py --no-write`. | PASS |
| AC-02 | Cloud migration can run against an empty local MySQL database and repeat safely. | Migration command evidence. | PASS |
| AC-03 | Cloud backend test/build/start/stop/health commands are real and pass. | Cloud command matrix. | PASS |
| AC-04 | Web dependency/test/build/start path is explicit and passes. | Web command matrix. | PASS |
| AC-05 | No Agent/Desktop runtime code is changed. | Git status and diff review. | PASS |
| AC-06 | M0-R3 through M0-R6 remaining dependencies are still explicit after this CHG. | Updated checkpoint/evidence. | PASS |

## 11. Evidence

Planned evidence:

- `evidence/start-gate.md`
- `evidence/migration-run.md`
- `evidence/cloud-web-command-matrix.md`
- `evidence/verification-summary.md`
- `evidence/diff-summary.md`

## 12. Current Checkpoint

Completed:
- CHG-20260715-002 M0-R1 was committed as `63f1b7f`.
- CHG-20260715-003 was activated for M0-R2.
- Cloud migration runner and CLI were implemented and committed as `db5b951`.
- Stable Cloud scripts were added for bootstrap, test, build, migrate, start, health and stop.
- Local MySQL migration verification passed: first run applied 5 migrations, repeat run applied 0.
- Cloud/Web verification passed: bootstrap, test, build, start internal health wait, stop and verify-health.

Current:
- Final Workspace verification and Workspace evidence commit.

Next:
- Close or hand off CHG-20260715-003, then continue M0-R3 Agent package/dependency/SQLite readiness.

Blocked:
- None.

Recent verification:
- M0-R1 post-commit status was clean across Workspace, Cloud, Agent and Desktop.
- Migration runner RED test failed before implementation on undefined `LoadDir`, `Apply` and `Migration`.
- `GOCACHE=... go test ./internal/modules/migration` passes after implementation.
- `scripts/bootstrap.sh` passes.
- `scripts/test.sh` passes Cloud Go tests and Cloud Web 8 tests.
- `scripts/build.sh` exits 0 and builds Cloud server plus Web assets; a non-fatal external Go stat-cache warning remains under the current shell GOPATH.
- `scripts/migrate.sh` against local MySQL verification DB repeats safely with `0 applied, 5 total`.
- `scripts/start.sh` starts Cloud and waits for `/healthz`; `scripts/stop.sh` cleans the PID file.
- `scripts/verify-health.sh` passes with `wt-media-cloud health ok`.

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
