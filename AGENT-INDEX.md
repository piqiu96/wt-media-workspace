# WT Media Agent Index

## Current Repository

`wt-media-workspace`

## Repository Role

- Governance control plane for WT Media.
- Owns product, engineering, contract, decision, delivery, and release governance.
- Does not own runtime code or runtime dependencies.

## Related Repositories

Paths are maintained in [`config/repository-map.yaml`](config/repository-map.yaml).

- `cloud`: `../wt-media-cloud`
- `agent`: `../wt-media-agent`
- `desktop`: `../wt-media-desktop`

## Current Context

`.ai/CURRENT_CONTEXT.md` in this repository is the **only** execution snapshot.

- It is generated, not authored: `python3 scripts/prepare_ai_workspace.py --change <CHG>`.
- Do not edit it by hand.
- Do not create or keep a copy at the outer execution root. `scripts/verify_agent_entry.py` fails if one reappears there.
- Keep it a snapshot, not a knowledge base: no history, no full decision library, no temporary verification notes.

## Context Loading Rules

### Layer 1 — Fixed Entry

Always read:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `AGENT-INDEX.md`
4. `.ai/CURRENT_CONTEXT.md`

### Layer 2 — Current Task

Read only the active CHG identified by `.ai/CURRENT_CONTEXT.md`:

- `delivery/active/<change-id>/change.md`
- Its current plan, spec, and checkpoint, when present

### Layer 3 — Target Repository

Before modifying code, enter the affected repository and read:

1. `AGENT-INDEX.md`
2. `AGENTS.md`
3. `CLAUDE.md`

Then read the relevant code and tests.

When the target repository has no `AGENT-INDEX.md` yet, do not invent one.
Fall back to this file plus that repository's `AGENTS.md`, and record the gap
in the active CHG. `scripts/verify_agent_entry.py` reports which repositories
are still missing the file.

## Default Exclusions

Do not load by default:

- `delivery/completed`
- old evidence
- historical decisions
- historical specs
- temporary experiment directories

Load them only when the current task explicitly requires them.

## Execution Boundary

- Workspace is the governance source of truth.
- Runtime code changes belong in the corresponding repository.
- Do not turn workspace into a runtime dependency.
- For parallel multi-repo work, use per-repository status files under the active CHG; do not concurrently edit `.ai/CURRENT_CONTEXT.md`.
