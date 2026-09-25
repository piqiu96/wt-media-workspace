# Checkpoint: CHG-YYYYMMDD-NNN

- CHG: `CHG-YYYYMMDD-NNN`（short title）
- Level: S | M | L
- Updated: YYYY-MM-DD

## 状态

`IMPLEMENTING`（activation date, or the note explaining the current state）

State words come from §3 of `delivery/MASTER_IMPLEMENTATION_PLAN.md`. A record in
`delivery/active/` may only be `IMPLEMENTING` or `VERIFYING`.

## Completed

One bullet per finished Task: what changed, the measured readings that prove it,
and the commit. Keep the numbers — a checkpoint without readings is a claim.

- **T-01 <goal>**: what was changed; the reading that proves it
  (`<gate> exit=0`, `Ran NN tests`, …); commit `<sha>`.

## Current

Which Task was last completed and which one is next.

## Next

1. **T-XX**: goal, landing points, and the verification this Task owes.
2. …

## Blocked

- None.

## Recent verification

| 判据 | 读数 |
|---|---|
| `<gate>` | `exit=0`, … |

Take the readings **after the last content change** of the Task — an earlier
reading is not a closing value. Note the time the readings were taken and where
the raw output lives (`evidence/artifacts/…`).
