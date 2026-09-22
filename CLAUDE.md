# WT Media Workspace Claude Entry

## Repository Role

This repository is the WT Media governance control plane. It owns product, engineering, contract, decision, delivery, and release governance.

It does not own runtime code and must not become a runtime dependency.

## Agent Entry

Read, in order:

1. `AGENT-INDEX.md`
2. `.ai/CURRENT_CONTEXT.md`
3. The active CHG identified by the current context

`AGENTS.md` is the Codex entry. This file is the Claude Code entry. They are parallel entry points, not aliases.

## Working Rules

- Use progressive context loading.
- Do not load completed delivery records, old evidence, or historical decisions unless the current task requires them.
- Make runtime code changes in the corresponding repository, not here.
- Keep `.ai/CURRENT_CONTEXT.md` as the only dynamic execution snapshot.
