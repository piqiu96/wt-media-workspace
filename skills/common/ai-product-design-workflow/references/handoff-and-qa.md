# ChatGPT / Codex handoff and QA

## Manual handoff

ChatGPT and Codex are separate environments unless the product explicitly provides a connected handoff. Never claim to switch modes, start a local process or edit a local working tree when unavailable.

The design handoff points to repository files and includes only:
- task and exact scope;
- active design brief and confirmed decisions;
- formal PRD/standard references;
- common patterns to reuse;
- files/entry points to inspect;
- prohibited scope changes;
- browser scenarios/evidence required;
- unresolved D1 items that must not be guessed.

Do not paste the whole PRD or repeat common rules in every prompt.

## Implementation agent

1. Read repository instructions.
2. Read referenced design brief and formal sources.
3. Inspect actual common components and existing page code.
4. Implement confirmed scope and authorized D2/D3 choices only.
5. Ask only for unresolved D1 decisions.
6. Reuse before adding shared components.
7. Preserve unrelated behavior.
8. Run relevant tests and browser checks; distinguish pass/fail/not-run.
9. Return changed files, screenshots, commands/results, regressions and unresolved issues.
10. Update implementation maturity; never mark ACCEPTED for the human.

## Acceptance

Compare implementation against confirmed design decisions and actual scenarios. A screenshot alone cannot prove interaction. A passing test suite cannot prove product usability. Record acceptance explicitly and then promote stable facts to their existing owners.
