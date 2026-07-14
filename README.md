# wt-media-workspace

Governance repository for the WT Media cross-repo project.

## Responsibility

This repository is the current governance source for:

- product facts;
- engineering facts;
- human-readable cross-repo contract governance;
- durable decision records;
- active delivery records;
- skill source files;
- release matrix and workspace preparation scripts.

Runtime code lives in `../wt-media-cloud`, `../wt-media-agent`, and `../wt-media-desktop`.

## Directories

- `docs/product`: current effective product baseline.
- `docs/engineering`: current effective engineering baseline.
- `docs/contracts`: human-readable Cloud, Agent, and Desktop contract governance.
- `docs/decisions`: durable decision records and reasons.
- `delivery/active`: current implementation process records.
- `delivery/LEDGER.md`: active delivery index, not a historical archive.
- `skills`: single source for Codex and Claude skills.
- `config`: skill distribution, contract map, and release matrix.
- `scripts`: workspace preparation and validation scripts.
- `templates`: generated root and repository rule templates.

## Rules

- Do not store Cloud, Agent, or Desktop runtime code here.
- Do not store production secrets here.
- Do not make runtime repositories depend on this repository at build or runtime.
- Do not edit generated `.codex/skills` or `.claude/skills` copies by hand.
- Do not use root `../docs` as the source of truth for new implementation decisions.
- Do not store OpenAPI, schema, DTO, or event definitions here when a provider repository owns them.
- Do not create `changes/active`; use `delivery/active/<change-id>/change.md`.
- Remove completed delivery records after final outcomes are reflected in stable baselines and Git.
