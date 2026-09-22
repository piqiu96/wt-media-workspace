---
name: executing-wt-media-change
description: Use when implementing, resuming, reviewing, or completing an active WT Media CHG in delivery/active.
---
<!-- GENERATED FILE - DO NOT EDIT DIRECTLY -->
<!-- Source: skills/workspace/executing-wt-media-change/SKILL.md -->


# Executing WT Media Change

Use this Skill for any WT Media M/L CHG implementation, resume, review, or completion. This Skill controls execution method only. It does not contain product requirements, architecture conclusions, contract definitions, or future feature scope.

## Authority Order

When facts conflict, resolve them in this order:

1. Root `AGENTS.md`.
2. `wt-media-workspace/.ai/CURRENT_CONTEXT.md` — the only execution snapshot; it never lives at the execution root.
3. Active `wt-media-workspace/delivery/active/<CHG>/change.md`.
4. The exact Milestone closure referenced by an M/L CHG, or the stable requirement referenced by a small Bug CHG.
5. Stable baselines referenced by the CHG:
   - `wt-media-workspace/docs/product`;
   - `wt-media-workspace/docs/engineering`;
   - `wt-media-workspace/docs/contracts`;
   - `wt-media-workspace/docs/decisions`.
6. Affected repository `AGENTS.md` files.
7. Current code and tests.

Do not treat chat history, generated summaries, or legacy root `docs/` files as stronger than the active CHG and stable Workspace baselines.

## Start Gate

Before coding, verify and report:

- active CHG ID and status;
- `wt-media-workspace/.ai/CURRENT_CONTEXT.md`, `delivery/LEDGER.md`, and `delivery/active` all identify the same single CHG;
- Milestone file and closure anchor for M/L work, or stable requirement reference for a planning-classified small Bug;
- the user-visible vertical result delivered by this CHG;
- required database change, external side effect, read-back, business projection, and page result inherited from the closure;
- current facts;
- gap to this CHG;
- real file mapping;
- ordered Task list;
- test and acceptance method for each Task;
- risks and blockers;
- proposed commit boundaries;
- current Git status for affected repositories.

Do not implement if:

- the CHG is `DISCUSSION`;
- a blocking `Q-xx` is open;
- the requested work changes "Explicitly Not Doing";
- contract ownership is unclear;
- product, engineering, contract, code, or tests conflict;
- the CHG spans multiple independent closures;
- the referenced closure requires a real effect or read-back that the CHG does not verify;
- unexplained dirty worktree changes affect the planned files.

If implementation reveals a missing business step, false-success acceptance, architecture conflict, or scope spanning multiple independent closures, stop and return to `planning-wt-media-delivery`. Do not infer the decision or hide the gap with a code patch.

## Task Protocol

Execute one Task at a time:

```text
failing verification or test
→ minimal implementation
→ test
→ diff check
→ evidence
→ checkpoint
→ independent commit
```

Keep edits within the active CHG scope. Do not start a later CHG or create future business objects to make the current Task easier.

## Evidence

Record evidence under:

```text
wt-media-workspace/delivery/active/<CHG>/evidence/
```

Evidence records must describe facts:

- command or manual action;
- expected result;
- actual result;
- pass/fail status;
- related commit or diff reference.

Do not duplicate product requirements in evidence files.

## Checkpoints

Update the active `change.md` checkpoint before pausing, committing, or finishing a Task.

Checkpoint text must include:

- completed work;
- current work;
- next step;
- blockers;
- recent verification.

If a new decision is required, stop, add a `Q-xx`, mark whether it blocks, and do not infer the answer.

## Completion Gate

Only mark a CHG `DONE` when all apply:

- scope completed;
- no blocking `Q-xx`;
- acceptance matrix all PASS;
- automated tests passed or exceptions are justified;
- required manual verification is recorded;
- diff checked for out-of-scope changes;
- affected runtime repositories are touched only when listed in scope;
- required baselines are updated;
- affected repositories are committed independently;
- completed active records are removed from `delivery/active` and `delivery/LEDGER.md` unless the user explicitly asks to keep an in-progress handoff.

Code presence, an HTTP success response, task creation, mock-only evidence, or a passing unit test cannot replace a required external side effect, read-back, business-state projection, and user-visible final result.

After completion, suggest the next CHG only from `delivery/MASTER_IMPLEMENTATION_PLAN.md` and current real code state. Do not automatically implement the next CHG.
