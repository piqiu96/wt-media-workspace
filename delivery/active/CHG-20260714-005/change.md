# CHG-20260714-005: M0-C3 Minimal Startup And Health Checks

## 1. Basic Information

- Level: M
- Status: DONE
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`
  - `wt-media-agent`
  - `wt-media-desktop`

## 2. Change Goal

Make the M0 Cloud, Agent, and Desktop skeletons independently startable or verifiable with minimal health checks, and record repeatable commands for future M0 validation.

## 3. Baseline References

- Master implementation plan: `delivery/MASTER_IMPLEMENTATION_PLAN.md#M0项目治理与工程基线`
- Engineering baseline: `docs/engineering/`
- Contract governance: `docs/contracts/`
- Execution Skill: `skills/workspace/executing-wt-media-change/SKILL.md`

## 4. Current Facts

- No active CHG existed before this CHG.
- CHG-004 was completed and pushed.
- Current Codex shell `PATH` still resolves `go` to `devenv/go19`.
- Go 1.26.5 exists at `devenv/go26/go/bin/go`.
- Cloud `go test ./...` passes when `GOROOT` is explicitly set to `devenv/go26/go`.
- Agent has a Python package shell and class-level local API health scaffold, but no real minimal local health server command.
- Desktop has Tauri/Vue placeholder files and npm scaffold scripts, but no minimal health verification script.

## 5. Scope

### Add

- Repeatable M0 health/start verification commands or scripts.
- Minimal local health surfaces needed for M0 validation.
- Evidence for Cloud, Agent, and Desktop health/start checks.
- Toolchain facts for Go 1.26.5 and current PATH mismatch.

### Modify

- Runtime scaffolds only where needed to expose M0 health/start checks.
- Repository README or script documentation when needed to make M0 commands discoverable.
- Active CHG checkpoint, evidence, ledger, and master plan.

### Delete

- None planned.

### Explicitly Not Doing

- Do not implement M1 task execution, Agent registration, task leases, or cross-end task loop.
- Do not implement M2 user/account/media account/Profile modules.
- Do not define formal Cloud-Agent or Local Agent contracts.
- Do not implement Desktop Local Agent lifecycle or SSE proxy.
- Do not add platform adapters, publication, discovery, production, or interaction features.
- Do not fetch dependencies unless an existing committed scaffold already requires them and the action is explicitly recorded.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | CHG-005 is the current Active CHG for M0-C3 minimal startup and health checks. | CONFIRMED |
| D-02 | Go 1.26.5 should be used explicitly for Cloud verification until PATH is normalized by a later toolchain CHG. | CONFIRMED |
| D-03 | Agent and Desktop health checks may be minimal M0-local commands; they must not imply M1 task loop behavior. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Create CHG-005 active record and refresh context. | DONE | `prepare_ai_workspace.py --change CHG-20260714-005` |
| T-02 | Record toolchain facts and Cloud health/start verification. | DONE | `evidence/toolchain-and-cloud-health.md` |
| T-03 | Add and verify Agent minimal local health command. | DONE | `evidence/agent-health.md` |
| T-04 | Add and verify Desktop minimal health verification command. | DONE | `evidence/desktop-health.md` |
| T-05 | Commit affected repositories and close CHG. | DONE | `evidence/commit-summary.md` |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG record.
- [x] Update active ledger.
- [x] Set M0 Active CHG to CHG-005.
- [x] Refresh root AI context.
- [x] Record startup and health evidence.
- [x] Close and clean active record.

### wt-media-cloud

- [x] Verify Go 1.26 toolchain.
- [x] Verify full `go test ./...`.
- [x] Verify Cloud process starts and exposes health.
- [x] Commit independently if runtime files change.

### wt-media-agent

- [x] Verify current Python test state.
- [x] Add minimal local health command if missing.
- [x] Verify local health command.
- [x] Commit independently if runtime files change.

### wt-media-desktop

- [x] Verify current npm script state.
- [x] Add minimal health verification command if missing.
- [x] Verify Desktop health command.
- [x] Commit independently if runtime files change.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one active CHG exists during implementation. | `find delivery/active -maxdepth 2 -name change.md` | PASS |
| AC-02 | Cloud full tests pass with Go 1.26.5. | Explicit Go 1.26 command | PASS |
| AC-03 | Cloud process starts and health endpoint returns OK. | Local process + curl | PASS |
| AC-04 | Agent exposes a minimal M0 health command without Cloud task behavior. | Python command/test | PASS |
| AC-05 | Desktop exposes a minimal M0 health verification command without Local Agent proxy behavior. | npm command | PASS |
| AC-06 | No M1/M2/M3/M6/M7/M8 implementation is introduced. | `rg` scans and diff inspection | PASS |
| AC-07 | Evidence records expected and actual results. | Evidence files | PASS |
| AC-08 | Affected repositories are committed independently when changed. | Git log checks | PASS |

## 11. Evidence

Planned records:

- `evidence/task-01-context.md`
- `evidence/toolchain-and-cloud-health.md`
- `evidence/agent-health.md`
- `evidence/desktop-health.md`
- `evidence/diff-and-scope-scan.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- Created CHG-005 active record.
- Updated `delivery/LEDGER.md`.
- Updated M0 Active CHG in `delivery/MASTER_IMPLEMENTATION_PLAN.md`.
- Refreshed root `.ai/CURRENT_CONTEXT.md`.
- Verified Cloud with explicit Go 1.26.5.
- Added and verified Cloud health script.
- Added and verified Agent local health server and script.
- Added and verified Desktop health script.
- Completed out-of-scope scans.
- Committed `wt-media-cloud`: `3bb6028 chore: add m0 cloud health verification`.
- Committed `wt-media-agent`: `2c2562f chore: add m0 agent health verification`.
- Committed `wt-media-desktop`: `54e6e70 chore: add m0 desktop health verification`.

Current:
- Final Workspace evidence commit and active-record cleanup.

Next:
- Commit Workspace CHG evidence, then remove completed active record.

Blocked:
- None.

Recent verification:
- `git status --short --branch` in four repositories.
- `devenv/go26/go/bin/go version`
- Cloud `go test ./...` with explicit Go 1.26.5 environment.
- `wt-media-cloud/scripts/verify-health.sh`
- `python3 -m unittest discover -s tests` in Agent
- `wt-media-agent/scripts/verify-health.sh`
- `npm run verify` in Desktop
- `npm test` in Desktop
- Workspace tests and skill verification
- M0 out-of-scope `rg` scans in Cloud, Agent, and Desktop

## 13. DONE Gate

- [x] Scope completed.
- [x] No blocking `Q-xx`.
- [x] Acceptance matrix all PASS.
- [x] Automated or command verification passed.
- [x] Evidence recorded.
- [x] Diff checked for out-of-scope changes.
- [x] Runtime repositories committed independently if changed.
- [x] Completed active record removal follows this DONE evidence commit.
