---
name: executing-wt-media-change
description: Use when implementing, resuming, reviewing, or completing an active WT Media CHG in delivery/active.
---

# Executing WT Media Change

Use this Skill for any WT Media M/L CHG implementation, resume, review, or completion. This Skill controls execution method only. It does not contain product requirements, architecture conclusions, contract definitions, or future feature scope.

## Authority Order

When facts conflict, resolve them in this order:

1. Root `AGENTS.md`.
2. Root `.ai/CURRENT_CONTEXT.md`.
3. Active `wt-media-workspace/delivery/active/<CHG>/change.md`.
4. Stable baselines referenced by the CHG:
   - `wt-media-workspace/docs/product`;
   - `wt-media-workspace/docs/engineering`;
   - `wt-media-workspace/docs/contracts`;
   - `wt-media-workspace/docs/decisions`.
5. Affected repository `AGENTS.md` files.
6. Current code and tests.

Do not treat chat history, generated summaries, or legacy root `docs/` files as stronger than the active CHG and stable Workspace baselines.

## Start Gate

Before coding, verify and report:

- active CHG ID and status;
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
- unexplained dirty worktree changes affect the planned files.

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

After completion, suggest the next CHG only from `delivery/MASTER_IMPLEMENTATION_PLAN.md` and current real code state. Do not automatically implement the next CHG.
