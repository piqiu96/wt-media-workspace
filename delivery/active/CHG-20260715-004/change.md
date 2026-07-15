# CHG-20260715-004: M0-R3 Agent 正式包入口、依赖锁、SQLite Migration、build 和启动停止

## 1. Basic Information

- Level: M
- Status: VERIFYING
- Created: 2026-07-15
- Current repository: `wt-media-agent`
- Affected repositories:
  - `wt-media-agent`
  - `wt-media-workspace`

## 2. Change Goal

完成 revised M0 的 Agent 工程门禁：Agent 必须有正式包入口、可重复依赖锁、SQLite migration 路径、真实 test/build/start/stop/health 脚本，并能在独立用户目录中完成本地存储初始化。

本 CHG 只关闭 M0-R3，不关闭 M0，也不启动 M1。

## 3. Baseline References

- Engineering baseline: `wt-media-workspace/docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Master route: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`
- R1 audit evidence: commit `63f1b7f`
- R2 Cloud evidence: Cloud commit `db5b951`, Workspace commit `9c3971e`
- Agent repository rules: `wt-media-agent/AGENTS.md`
- Agent package: `wt-media-agent/pyproject.toml`

## 4. Current Facts

- M0-R1 found Agent tests and Local health pass with `.venv/bin/python` 3.14.4.
- M0-R1 found Agent `uv build` passes only after network authorization to fetch build-system dependency `hatchling`.
- M0-R1 found no `uv.lock`.
- M0-R1 found `storage` is a placeholder and no SQLite migration command exists.
- Agent owns Local Agent runtime, local storage and external execution; Agent must not connect to Cloud MySQL.

## 5. Scope

### Add

- Agent dependency lock or equivalent repeatability artifact.
- Agent SQLite migration runner and command/script.
- Stable Agent scripts for bootstrap/test/build/start/stop/health/migrate as needed by M0.
- Evidence for isolated local SQLite migration, Agent tests/build and Local health.

### Modify

- `wt-media-agent` package/scripts/README documentation as needed.
- `wt-media-workspace` active CHG evidence and checkpoint.

### Delete

- Completed Active CHG-20260715-003 files from `delivery/active`; Git history retains the record.

### Explicitly Not Doing

- Implementing M1 durable task checkpoints or offline result replay beyond the base SQLite migration path.
- Connecting Agent to Cloud MySQL.
- Changing Cloud or Desktop runtime code.
- Marking M0 `DONE`; M0 still requires M0-R4 through M0-R6.
- Storing secrets in committed scripts or evidence.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | M0-R3 closes Agent engineering readiness only; M1 checkpoint/offline-result semantics remain later work. | CONFIRMED |
| D-02 | Agent SQLite migration must run in a caller-selected local data directory and be repeatable. | CONFIRMED |
| D-03 | Agent build/test/start scripts must use the project package entry points rather than system Python assumptions. | CONFIRMED |

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
| T-01 | Start Gate for M0-R3. | DONE | `evidence/start-gate.md`. |
| T-02 | Add tests for SQLite migration repeat behavior. | DONE | `evidence/sqlite-migration.md`; RED failed on missing `storage.migration`. |
| T-03 | Implement minimal repeatable SQLite migration runner/command. | DONE | Agent commit `2b65ac5`; first migration applied 1, repeat applied 0. |
| T-04 | Add or normalize stable Agent scripts for bootstrap/test/build/start/stop/health/migrate. | DONE | `evidence/agent-command-matrix.md`. |
| T-05 | Produce dependency-lock/build evidence. | DONE | `uv.lock` and `scripts/build.sh` evidence. |
| T-06 | Run full Agent verification matrix and record evidence. | DONE | `evidence/verification-summary.md`. |
| T-07 | Update Workspace evidence, checkpoint, acceptance matrix and commit affected repositories independently. | DONE | Agent committed as `2b65ac5`; Workspace final verification runs before Workspace commit. |

## 9. Repository Checklist

### wt-media-agent

- [x] SQLite migration runner/command implemented and tested.
- [x] Stable scripts implemented or confirmed.
- [x] Dependency/build repeatability evidence recorded.
- [x] Agent verification evidence recorded.

### wt-media-workspace

- [x] Active CHG and Ledger point to CHG-20260715-004.
- [x] M0-R3 evidence recorded.
- [x] Checkpoint updated before handoff or completion.

### wt-media-cloud

- [x] Not affected.

### wt-media-desktop

- [x] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one Active CHG exists and AI context points to CHG-20260715-004. | Active scan and `prepare_ai_workspace.py --no-write`. | PASS |
| AC-02 | Agent SQLite migration can run in an isolated directory and repeat safely. | SQLite migration evidence. | PASS |
| AC-03 | Agent tests/build/start/stop/health commands are real and pass. | Agent command matrix. | PASS |
| AC-04 | Agent dependency repeatability is locked or explicitly evidenced. | Lock/build evidence. | PASS |
| AC-05 | No Cloud/Desktop runtime code is changed. | Git status and diff review. | PASS |
| AC-06 | M0-R4 through M0-R6 remaining dependencies are still explicit after this CHG. | Updated checkpoint/evidence. | PASS |

## 11. Evidence

Planned evidence:

- `evidence/start-gate.md`
- `evidence/sqlite-migration.md`
- `evidence/agent-command-matrix.md`
- `evidence/verification-summary.md`
- `evidence/diff-summary.md`

## 12. Current Checkpoint

Completed:
- CHG-20260715-003 M0-R2 was committed: Cloud `db5b951`, Workspace `9c3971e`.
- CHG-20260715-004 was activated for M0-R3.
- Agent SQLite migration runner, package entry and scripts were implemented and committed as `2b65ac5`.
- `uv.lock` was generated.
- Agent verification passed: lock check, bootstrap, 40 tests, build, SQLite first/repeat migration, verify-health and start/stop health scripts.

Current:
- Final Workspace verification and Workspace evidence commit.

Next:
- Close or hand off CHG-20260715-004, then continue M0-R4 Desktop Vue/Tauri Rust dependency/build/dev/start readiness.

Blocked:
- None.

Recent verification:
- M0-R2 post-commit status was clean across Workspace, Cloud, Agent and Desktop.
- SQLite migration RED test failed before implementation on missing `wt_media_agent.storage.migration`.
- `PYTHONPATH=src .venv/bin/python -m unittest tests.test_storage_migration -v` passes after implementation.
- `uv lock --check --cache-dir .cache/uv` passes.
- `scripts/bootstrap.sh` passes.
- `scripts/test.sh` passes 40 tests.
- `scripts/build.sh` passes and builds sdist/wheel.
- `scripts/migrate-storage.sh --data-dir /tmp/wt-media-agent-m0-r3-final` applies 1 migration then repeats with 0 applied.
- `PYTHON_BIN=.venv/bin/python scripts/verify-health.sh` passes.
- `scripts/start-health.sh` and `scripts/stop-health.sh` pass.

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
