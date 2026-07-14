# CHG-20260714-001: Workspace Document And Delivery Governance Migration

## 1. Basic Information

- Level: M
- Status: DONE
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - outer execution root rule files

## 2. Change Goal

Make `wt-media-workspace` the explicit governance source for current product facts, engineering facts, cross-repo contract governance, decision records, and active delivery records. Separate stable baseline documents from temporary code implementation process records.

## 3. Baseline References

- Product baseline: `docs/product/`
- Engineering baseline: `docs/engineering/`
- Contract governance: `docs/contracts/`
- Decision records: `docs/decisions/`
- Active delivery process: `delivery/active/`

## 4. Scope

### Add

- `docs/decisions`
- `delivery/active`
- `delivery/LEDGER.md`
- `delivery/active/CHG-20260714-001/change.md`
- `docs/engineering/specs`

### Modify

- Workspace README and rule files.
- Root execution README and rule files.
- Workspace scripts, skills, templates, and contract governance wording that refer to old paths.

### Delete

- `docs/adr`
- `docs/plans`
- empty `docs/release` and `docs/testing` placeholders
- `scripts/sync_root_docs.py`

### Explicitly Not Doing

- Do not change product requirement conclusions.
- Do not change engineering architecture conclusions beyond governance path terminology.
- Do not modify Cloud, Agent, or Desktop runtime business code.
- Do not create or implement the Cloud user/account module.
- Do not move actual OpenAPI, schema, DTO, or event definitions into Workspace.

## 5. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Use `docs/product` for current product facts. | CONFIRMED |
| D-02 | Use `docs/engineering` for current engineering facts. | CONFIRMED |
| D-03 | Use `docs/contracts` for human-readable cross-repo contract governance. | CONFIRMED |
| D-04 | Use `docs/decisions` instead of `docs/adr`. | CONFIRMED |
| D-05 | Use `delivery/active/<change-id>/change.md` for current implementation process records. | CONFIRMED |
| D-06 | Do not use `changes/active`. | CONFIRMED |
| D-07 | Do not create a top-level `contracts-map` directory. | CONFIRMED |
| D-08 | Actual formal contract definitions stay in the provider repositories. | CONFIRMED |

## 6. Pending Questions

None.

## 7. Implementation Order

1. Migrate `docs/adr` to `docs/decisions`.
2. Establish `delivery/active` and `delivery/LEDGER.md`.
3. Remove old implementation process directories under `docs/plans`.
4. Update README, AGENTS, CLAUDE, scripts, skills, and templates.
5. Scan for old path references.
6. Verify no runtime repository business code changed.
7. Commit the governance migration independently.

## 8. Repository Checklist

### wt-media-workspace

- [x] Create `docs/decisions`.
- [x] Create `delivery/active`.
- [x] Create `delivery/LEDGER.md`.
- [x] Create this `change.md`.
- [x] Update README and rule files.
- [x] Update scripts, skills, templates, and contract governance wording.
- [x] Remove old path references, except references inside this migration record and explicit legacy/trash guards.
- [x] Verify final tree.
- [x] Commit workspace governance migration.

### Outer execution root

- [x] Update root README and rule files to point at `wt-media-workspace/docs`.
- [x] Keep root `docs/` as legacy copies only until a separate cleanup decision.

### Runtime repositories

- [x] Confirm no Cloud, Agent, or Desktop runtime business code changed.

## 9. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | `docs/adr` no longer exists. | `find` scan | PASS |
| AC-02 | `docs/decisions` exists and contains the decision template. | `find` scan | PASS |
| AC-03 | `docs/plans` no longer exists. | `find` scan | PASS |
| AC-04 | `delivery/active` and `delivery/LEDGER.md` exist. | `find` scan | PASS |
| AC-05 | `docs/contracts` remains in place for human-readable governance. | `find` scan | PASS |
| AC-06 | Actual formal contract definitions remain in provider repositories. | `find` scan | PASS |
| AC-07 | No old `changes/active`, `docs/adr`, or `docs/plans` references remain outside this migration record. | `rg` scan | PASS |
| AC-08 | No Cloud, Agent, or Desktop runtime business code is modified by this change. | `git status` | PASS |

## 10. Current Checkpoint

Completed:
- Confirmed final governance directory model.
- Migrated `docs/adr` to `docs/decisions`.
- Created `delivery/active` and `delivery/LEDGER.md`.
- Removed old `docs/plans` process files and empty scaffold placeholders.
- Updated README, AGENTS, CLAUDE, scripts, skills, templates, and contract governance wording.
- Confirmed runtime repository business code was not modified by this change.

Current:
- Workspace governance migration is complete.

Next:
- Discuss `CHG-20260714-002: Cloud user and account management implementation` only after third-chapter requirements are confirmed.

Blocked:
- None.

Recent verification:
- `find wt-media-workspace -maxdepth 4 -type d`
- `find wt-media-workspace -maxdepth 5 -type f`
- `rg` scans for old path references
- `git status` for Cloud, Agent, and Desktop runtime repositories
- `python3 scripts/verify_skills.py`
- `python3 scripts/prepare_ai_workspace.py`
- `git diff --cached --check` for non-baseline files
