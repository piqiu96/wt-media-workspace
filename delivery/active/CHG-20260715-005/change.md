# CHG-20260715-005: M0-R4 Desktop Vue/Tauri Rust 正式依赖、build、dev、启动停止和本地页面

## 1. Basic Information

- Level: M
- Status: VERIFYING
- Created: 2026-07-15
- Current repository: `wt-media-desktop`
- Affected repositories:
  - `wt-media-desktop`
  - `wt-media-workspace`

## 2. Change Goal

完成 revised M0 的 Desktop 工程门禁：Desktop 必须有真实 Vue/Tauri/Rust 依赖、可执行 bootstrap/test/build/dev/start/stop/health 路径、本地页面和 Tauri shell 构建证据；echo-only 脚本不能通过。

本 CHG 只关闭 M0-R4，不关闭 M0，也不启动 M1。

## 3. Baseline References

- Engineering baseline: `wt-media-workspace/docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Master route: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`
- R1 audit evidence: commit `63f1b7f`
- R2 Cloud evidence: Cloud `db5b951`, Workspace `9c3971e`
- R3 Agent evidence: Agent `2b65ac5`, Workspace `67cc801`
- Desktop repository rules: `wt-media-desktop/AGENTS.md`

## 4. Current Facts

- M0-R1 found `cargo` and `rustc` were not available.
- `rustup` is not installed; Homebrew is available.
- Rust/Cargo was installed through Homebrew with explicit approval after disk space was recovered.
- Desktop now has real Vue/Vite/Tauri dependencies, npm/Cargo lockfiles, wrapper scripts, local page, Tauri icon and Tauri build config.
- Desktop `npm test`, `scripts/test.sh`, `scripts/build.sh`, `scripts/start.sh`, `scripts/health.sh`, `scripts/stop.sh`, `npm run lint` and `npm run build` have passed.

## 5. Scope

### Add

- Real Desktop dependency declarations and lockfile updates.
- Real Desktop bootstrap/test/build/dev/start/stop/health scripts.
- Evidence for Tauri/Rust check/build and local page health.
- Blocker evidence if system toolchain installation is not approved or unavailable.

### Modify

- `wt-media-desktop` package/scripts/docs/Tauri config only as needed for M0 build/dev readiness.
- `wt-media-workspace` active CHG evidence and checkpoint.

### Delete

- Completed Active CHG-20260715-004 files from `delivery/active`; Git history retains the record.

### Explicitly Not Doing

- Implementing M1 Desktop sidecar lifecycle, token security or Cloud task UI beyond M0 readiness.
- Changing Cloud or Agent runtime code.
- Marking M0 `DONE`; M0 still requires M0-R5 and M0-R6 after R4.
- Installing system toolchains without explicit approval.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | M0-R4 requires real Rust/Cargo/Tauri build evidence; echo scripts are failing evidence. | CONFIRMED |
| D-02 | System-level Rust/Cargo installation requires explicit approval before execution. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Start Gate for M0-R4. | DONE | `evidence/start-gate.md`. |
| T-02 | Resolve Rust/Cargo toolchain availability. | DONE | `evidence/toolchain.md`, `cargo --version`, `rustc --version`. |
| T-03 | Replace Desktop echo scripts with real bootstrap/test/build/dev/health paths. | DONE | `node scripts/verify-real-scripts.mjs`, `scripts/README.md`, `package.json`. |
| T-04 | Verify local page/Tauri build readiness. | DONE | `npm test`, `scripts/test.sh`, `npm run build`, `scripts/build.sh`, `scripts/start.sh`, `scripts/health.sh`, `scripts/stop.sh`. |
| T-05 | Record evidence and commit Desktop/Workspace independently. | VERIFYING | Diff check passed; independent commits pending. |

## 9. Repository Checklist

### wt-media-desktop

- [x] Rust/Cargo availability resolved with evidence.
- [x] Echo scripts replaced.
- [x] Desktop verification evidence recorded.

### wt-media-workspace

- [x] Active CHG and Ledger point to CHG-20260715-005.
- [x] M0-R4 evidence recorded.
- [x] Checkpoint updated before handoff or completion.

### wt-media-cloud

- [x] Not affected.

### wt-media-agent

- [x] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one Active CHG exists and AI context points to CHG-20260715-005. | Active scan and `prepare_ai_workspace.py --no-write`. | PASS |
| AC-02 | Rust/Cargo/Tauri toolchain is available or explicitly blocked. | Toolchain evidence. | PASS |
| AC-03 | Desktop scripts are real and pass, or blocker is recorded before any false PASS. | Command matrix. | PASS |
| AC-04 | No Cloud/Agent runtime code is changed. | Git status and diff review. | PASS |

## 11. Evidence

- `evidence/start-gate.md`
- `evidence/toolchain.md`
- `evidence/desktop-command-matrix.md`
- `evidence/verification-summary.md`
- `evidence/diff-summary.md`

## 12. Current Checkpoint

Completed:
- CHG-20260715-004 M0-R3 was committed: Agent `2b65ac5`, Workspace `67cc801`.
- CHG-20260715-005 was activated for M0-R4.
- Rust/Cargo were installed through Homebrew after explicit approval.
- Homebrew Node was reinstalled after `brew linkage node` exposed a broken `llhttp` dependency.
- Desktop echo scripts were replaced with real npm/Vite/Tauri/Cargo scripts and shell wrappers.
- Desktop Vue/Vite app, Tauri invoke handlers, Tauri icon, Cargo sparse/slow-network config, npm lockfile and Cargo lockfile were added.
- `scripts/start.sh` → `scripts/health.sh` → `scripts/stop.sh` passed with a local Vite dev server on `127.0.0.1:5174`.
- Desktop runtime repository committed: `dd2ff80`.

Current:
- Diff check and independent commit preparation.

Next:
- Commit `wt-media-workspace`; next CHG should be M0-R5.

Blocked:
- None.

Recent verification:
- `cargo --version`: `cargo 1.97.0`.
- `rustc --version`: `rustc 1.97.0`.
- `node --version`: `v26.5.0`.
- `scripts/bootstrap.sh`: PASS.
- `npm run lint`: PASS.
- `scripts/test.sh`: PASS.
- `scripts/build.sh`: PASS.
- `scripts/start.sh`: PASS.
- `scripts/health.sh`: PASS.
- `scripts/stop.sh`: PASS.
- `git -C wt-media-desktop commit`: `dd2ff80 feat: add desktop m0 tauri readiness`.

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
