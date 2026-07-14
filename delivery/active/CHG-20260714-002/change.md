# CHG-20260714-002: Project CHG Execution Control System

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - outer execution root rule files

## 2. Change Goal

Build the project implementation governance and Codex execution-control capability needed to execute future WT Media CHGs safely, one active change at a time, without modifying Cloud, Agent, or Desktop business code.

## 3. Baseline References

- Product baseline: `docs/product/`
- Engineering baseline: `docs/engineering/`
- Contract governance: `docs/contracts/`
- Decisions: `docs/decisions/`
- Master implementation route: `delivery/MASTER_IMPLEMENTATION_PLAN.md`
- Standard change template: `templates/delivery/change.md`

## 4. Current Facts

- `CHG-20260714-001` exists and is `DONE`.
- `delivery/active` still contained the completed CHG-001 record before this change.
- `prepare_ai_workspace.py` only printed a JSON workspace summary and did not accept `--change`.
- Root `AGENTS.md` did not require using `executing-wt-media-change` for CHG work.
- The implementation master plan existed only as a legacy root `docs/` file.
- Cloud, Agent, and Desktop runtime repositories already contain unrelated scaffold work and are out of scope for this CHG.

## 5. Scope

### Add

- `executing-wt-media-change` Skill unique source.
- `delivery/MASTER_IMPLEMENTATION_PLAN.md`.
- Standard `change.md` template.
- Standard evidence record template and evidence directory convention.
- `prepare_ai_workspace.py --change CHG-xxxx`.
- Generated root `.ai/CURRENT_CONTEXT.md`.
- Script tests and verification evidence.

### Modify

- Root `AGENTS.md` to require the Skill for CHG implementation, resume, review, and completion.
- Workspace governance rules where needed to point to the Skill and DONE gate.
- `delivery/LEDGER.md` so it lists only current active CHGs.
- `prepare_ai_workspace.py`.

### Delete

- Completed CHG records from `delivery/active` after they are represented in stable baselines and Git history.

### Explicitly Not Doing

- Do not modify any business feature.
- Do not implement Cloud user or account modules.
- Do not implement Agent registration or task execution.
- Do not implement Desktop pages.
- Do not create future business objects or Contracts.
- Do not start the next CHG.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Use `CHG-20260714-002` because CHG-001 exists and is DONE. | CONFIRMED |
| D-02 | Build CHG execution control before more business coding. | CONFIRMED |
| D-03 | The next CHG after this one is not pre-committed to Cloud user/account work. | CONFIRMED |
| D-04 | `delivery/LEDGER.md` is an active index, not a historical archive. | CONFIRMED |
| D-05 | `docs/contracts` remains the human-readable cross-repo contract governance baseline. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Establish CHG-002 records, master plan, template, and evidence spec. | DONE | File checks, `rg`, diff inspection. |
| T-02 | Add `executing-wt-media-change` Skill and rule references. | TODO | `python3 scripts/verify_skills.py`, rule text inspection. |
| T-03 | Extend `prepare_ai_workspace.py --change` and generated context. | TODO | Script unit tests and manual command run. |
| T-04 | Record final verification evidence and close DONE gate. | TODO | Test summary, diff summary, runtime repo status check. |
| T-05 | Commit workspace and root changes independently. | TODO | Git status and commit log checks. |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create CHG-002 active change record.
- [x] Remove completed CHG-001 from active records.
- [x] Land `delivery/MASTER_IMPLEMENTATION_PLAN.md`.
- [x] Create standard change template.
- [x] Create evidence record template.
- [ ] Add `executing-wt-media-change` Skill.
- [ ] Extend `prepare_ai_workspace.py --change`.
- [ ] Add script tests.
- [ ] Record verification evidence.

### Outer execution root

- [ ] Update `AGENTS.md` CHG execution rule.
- [ ] Ignore generated `.ai/` and `.agents/` context outputs.
- [ ] Generate `.ai/CURRENT_CONTEXT.md` for this CHG.

### wt-media-cloud

- [ ] Confirm not modified by this CHG.

### wt-media-agent

- [ ] Confirm not modified by this CHG.

### wt-media-desktop

- [ ] Confirm not modified by this CHG.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Exactly one active CHG exists during implementation. | `find delivery/active -maxdepth 2 -name change.md` | TODO |
| AC-02 | `executing-wt-media-change` exists as the unique Skill source. | `python3 scripts/verify_skills.py` | TODO |
| AC-03 | Root `AGENTS.md` requires the Skill for CHG implementation, resume, review, and completion. | Text inspection | TODO |
| AC-04 | Master implementation plan is landed and does not lock next work to Cloud user/account. | Text inspection | PASS |
| AC-05 | Standard `change.md` template exists with Active CHG, Checkpoint, Q-xx, acceptance matrix, evidence, and DONE gate. | Text inspection | PASS |
| AC-06 | `prepare_ai_workspace.py --change CHG-xxxx` validates active CHG and generates root `.ai/CURRENT_CONTEXT.md`. | Unit tests and manual command | TODO |
| AC-07 | Evidence directory and record format are defined. | Template inspection | PASS |
| AC-08 | Script tests cover success and missing-change failure paths. | `python3 -m unittest discover -s tests` | TODO |
| AC-09 | Cloud, Agent, and Desktop business code is untouched by this CHG. | Git status comparison | TODO |
| AC-10 | DONE gate is satisfied before completion. | Final checklist | TODO |

## 11. Evidence

Evidence files live in `evidence/` and record verification facts for this CHG.

Planned records:

- `evidence/task-01-governance-setup.md`
- `evidence/task-02-skill-rules.md`
- `evidence/task-03-prepare-ai-workspace.md`
- `evidence/test-summary.md`
- `evidence/diff-summary.md`

## 12. Current Checkpoint

Completed:
- Confirmed CHG-001 exists and is DONE.
- Confirmed CHG-002 numbering.
- Confirmed runtime repositories have pre-existing out-of-scope scaffold changes.
- T-01 created CHG-002, the master implementation plan, the standard change template, and the evidence record template.
- T-01 removed completed CHG-001 from active records and updated the active ledger.

Current:
- T-02 Skill and rule references.

Next:
- Add execution Skill and rule references.

Blocked:
- None.

Recent verification:
- `test -f wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md` failed before implementation.
- `test -f wt-media-workspace/templates/delivery/change.md` failed before implementation.
- `test -f wt-media-workspace/delivery/active/CHG-20260714-002/change.md` failed before implementation.
- `find wt-media-workspace/delivery/active -maxdepth 2 -name change.md`
- `rg -n "Cloud user|Cloud 用户|用户账号|用户与账号|下一步" wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md wt-media-workspace/delivery/active/CHG-20260714-002/change.md wt-media-workspace/delivery/LEDGER.md`

## 13. DONE Gate

- [ ] Scope completed.
- [x] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed.
- [ ] Manual verification evidence recorded.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories untouched by this CHG.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.
- [ ] Completed active record handling is consistent with Git-history retention.
