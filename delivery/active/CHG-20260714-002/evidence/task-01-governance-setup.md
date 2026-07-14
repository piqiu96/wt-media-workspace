# Evidence: Task 01 Governance Setup

- CHG: `CHG-20260714-002`
- Task: `T-01`
- Date: 2026-07-14
- Type: command + diff
- Status: PASS

## Purpose

Verify that the CHG-002 governance files were missing before implementation and were then created as the current execution basis.

## Method

Initial failing checks:

```text
test -f wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md
test -f wt-media-workspace/templates/delivery/change.md
test -f wt-media-workspace/delivery/active/CHG-20260714-002/change.md
```

All three returned exit code `1`, confirming the required files did not yet exist.

## Expected

After implementation:

- `delivery/MASTER_IMPLEMENTATION_PLAN.md` exists and describes the corrected route.
- `templates/delivery/change.md` exists with Checkpoint, Q-xx, acceptance matrix, evidence, and DONE gate sections.
- `delivery/active/CHG-20260714-002/change.md` exists and is the only active CHG record.
- Completed CHG-001 is no longer retained as an active record.

## Actual

Implemented the files above and updated `delivery/LEDGER.md` to list `CHG-20260714-002` as the active change.

Post-implementation checks:

```text
find wt-media-workspace/delivery/active -maxdepth 2 -name change.md
```

Output:

```text
wt-media-workspace/delivery/active/CHG-20260714-002/change.md
```

`rg` confirmed Cloud user/account appears only as an explicit non-goal or as a conditional future milestone, not as the next committed CHG.

## Follow-Up

- Continue with T-02 Skill and rule references.
