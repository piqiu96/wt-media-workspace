# CHG-YYYYMMDD-NNN: Title

## 1. Basic Information

- Level: M
- Status: DISCUSSION
- Created: YYYY-MM-DD
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`

## 2. Change Goal

Describe the single concrete outcome of this CHG.

## 3. Baseline References

- Product baseline: `docs/product/...`
- Engineering baseline: `docs/engineering/...`
- Contract governance: `docs/contracts/...`
- Decisions: `docs/decisions/...`

## 4. Current Facts

- Fact 1.
- Fact 2.

## 5. Scope

### Add

- Item.

### Modify

- Item.

### Delete

- Item or `None`.

### Explicitly Not Doing

- Item.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Decision text. | CONFIRMED |

## 7. Pending Questions

| ID | Question | Blocking |
|---|---|---|
| Q-01 | Question text. | YES |

Use `None.` when there are no pending questions.

## 8. Implementation Tasks

Each task must follow:

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
| T-01 | Goal. | TODO | Command or manual evidence. |

## 9. Repository Checklist

### wt-media-workspace

- [ ] Item.

### wt-media-cloud

- [ ] Not affected.

### wt-media-agent

- [ ] Not affected.

### wt-media-desktop

- [ ] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Requirement. | Verification. | TODO |

## 11. Evidence

Evidence files live in `evidence/` and must record facts, not repeat requirements.

Recommended files:

- `evidence/task-xx-<topic>.md`
- `evidence/test-summary.md`
- `evidence/diff-summary.md`
- `evidence/manual-verification.md`

Each evidence record should include:

- command or manual action;
- expected result;
- actual result;
- pass/fail status;
- relevant commit or diff reference.

## 12. Current Checkpoint

Progress lives in `checkpoint.md`, beside this file — it is **not** inlined here.
`scripts/verify_delivery_governance.py` requires the pair: an active CHG with no
`checkpoint.md` is an active change nobody can resume.

See `checkpoint.md` for completed work, current work, next step, blockers, and
recent verification.

## 13. DONE Gate

- [ ] Scope completed.
- [ ] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Manual verification evidence recorded where required.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories touched only if listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.

