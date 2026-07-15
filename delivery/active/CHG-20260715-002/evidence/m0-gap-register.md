# M0-R1 Gap Register

- Change: CHG-20260715-002
- Date: 2026-07-15

## Gate Classification

| Revised M0 Gate | Current Status | Evidence | Follow-up |
|---|---|---|---|
| Skill, Active CHG, Checkpoint, Q-xx, Evidence and DONE gate usable | PASS | CHG-20260715-002 active, generated AI context valid, Workspace tests pass. | Continue using current CHG process. |
| Outer `wt-media/` workspace recognizes four repos | PASS | Root AGENTS and `prepare_ai_workspace.py` identify Workspace, Cloud, Agent, Desktop. | None. |
| Cloud real bootstrap/test/build/start/health/stop | PARTIAL | Go tests/build pass; health script passes after local port authorization. No stable `bootstrap` command beyond Go module state. | M0-R2 |
| Web real dependency/test/build | PASS | `web/node_modules/` present; `npm test` and `npm run build` pass. | M0-R2 should formalize bootstrap/start evidence. |
| Cloud empty MySQL migration repeatability | FAIL | Migration SQL files and tests exist; no migration runner found; mysql CLI unavailable. | M0-R2 |
| Agent formal package entry, dependency lock, build, start/health/stop | PARTIAL | Tests and health pass; `uv build` passes after network authorization; no `uv.lock`; `.venv` lacks pip. | M0-R3 |
| Agent SQLite migration in isolated user dir | FAIL | `storage` package exists as placeholder; no SQLite migration command found. | M0-R3 |
| Desktop Vue/Tauri Rust dependency/bootstrap/test/build/dev/start/stop | FAIL | Desktop health scaffold passes; build/dev/package/bootstrap/lint are echo commands; Cargo/Rust missing. | M0-R4 |
| Desktop mock-free local page / Tauri entry | FAIL | `src-tauri` config exists, but no real Tauri dependency/build/dev path. | M0-R4 |
| CI covers Go, Web, Python, Rust/Tauri, Migration and Contract | FAIL | No `.github` workflow files found by workspace scan. Release matrix records historical commands only. | M0-R5 |
| Workspace not runtime dependency | PASS | Runtime commands ran from runtime repos; Workspace only stores governance/evidence. | Continue verifying in M0-R6. |
| `contract-map.yaml` and `release-matrix.yaml` match current verified state | PASS | Workspace config verifier passes; release matrix explicitly says historical evidence does not close revised M0/M1. | Continue maintaining in M0-R5/R6. |
| M0-R6 three-runtime integrated engineering acceptance | NOT_STARTED | R1 found prerequisites not yet closed. | M0-R6 |

## Follow-up CHG Shape

| Candidate | Required Outcome |
|---|---|
| M0-R2 | Cloud/Web real bootstrap/start/stop scripts, repeatable MySQL migration runner against empty DB, Web dev/start evidence and Cloud/Web integrated health evidence. |
| M0-R3 | Agent dependency lock, offline/reproducible build, SQLite migration path, package entry validation, start/stop health evidence without relying on ad hoc environment. |
| M0-R4 | Install/declare Rust/Cargo/Tauri toolchain, replace Desktop echo scripts with real bootstrap/dev/build/test/package, validate mock-free Tauri shell/local page. |
| M0-R5 | Add or document CI gates for Go, Web, Python, Rust/Tauri, migration and contract/release governance. |
| M0-R6 | Run the final three-runtime engineering acceptance with clean statuses and human startup evidence. |

## Technical Risk Summary

- Highest risk: Desktop/Tauri is still scaffold-only and local Rust toolchain is missing.
- Medium risk: Cloud migration execution is not yet operational despite migration files existing.
- Medium risk: Agent build depends on live PyPI access; dependency lock/offline repeatability is not closed.
- Low/medium risk: Go build writes a stat-cache warning to an external GOPATH path under sandbox; build still exits 0.

Status: PASS for gap register completeness.
