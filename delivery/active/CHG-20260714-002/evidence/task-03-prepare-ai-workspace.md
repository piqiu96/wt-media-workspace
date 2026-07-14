# Evidence: Task 03 Prepare AI Workspace

- CHG: `CHG-20260714-002`
- Task: `T-03`
- Date: 2026-07-14
- Type: command + generated context
- Status: PASS

## Purpose

Verify that `prepare_ai_workspace.py --change` validates the active CHG and generates the root AI context plus the root `.agents` execution Skill copy.

## Method

Initial behavior check:

```text
python3 scripts/prepare_ai_workspace.py --change CHG-DOES-NOT-EXIST
```

Before implementation, the script ignored unknown arguments and returned the ordinary workspace summary. It also did not create `.ai/CURRENT_CONTEXT.md` or `.agents/skills/executing-wt-media-change/SKILL.md`.

## Expected

After implementation:

- Invalid CHG IDs or missing active CHGs fail.
- Valid active CHG generates `.ai/CURRENT_CONTEXT.md`.
- Valid active CHG generates `.agents/skills/executing-wt-media-change/SKILL.md` from the unique Workspace Skill source.
- Generated root context and Skill copies are ignored by Git.

## Actual

Invalid CHG check after implementation:

```text
python3 scripts/prepare_ai_workspace.py --change CHG-DOES-NOT-EXIST
```

Output:

```text
invalid change id: CHG-DOES-NOT-EXIST
```

Valid CHG generation:

```text
python3 scripts/prepare_ai_workspace.py --change CHG-20260714-002
```

Output included:

```text
"active_change": "CHG-20260714-002"
"active_change_status": "IMPLEMENTING"
"current_context": "/Users/aqiuye/Develop/workspace/wt-media/.ai/CURRENT_CONTEXT.md"
"generated_execution_skill": "/Users/aqiuye/Develop/workspace/wt-media/.agents/skills/executing-wt-media-change/SKILL.md"
```

Generated context inspection confirmed:

- active CHG is `CHG-20260714-002`;
- required Skill is `executing-wt-media-change`;
- stable baselines are `docs/product`, `docs/engineering`, `docs/contracts`, and `docs/decisions`;
- execution boundary says not to start the next CHG.

Generated Skill copy inspection confirmed it is marked generated and points back to:

```text
skills/workspace/executing-wt-media-change/SKILL.md
```

Sandbox note: the first non-escalated write to root `.agents/` failed with `Operation not permitted` because the execution sandbox marks that hidden directory read-only. The command was rerun with approval to create the user-required local AI context output.

## Follow-Up

- Run unit tests in T-04.
