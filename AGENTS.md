# WT Media Workspace Governance

## Responsibility

This repository owns product, engineering, contract, decision, delivery, skill, release-matrix, and workspace preparation governance.

## Boundaries

- Runtime code lives in `../wt-media-cloud`, `../wt-media-agent`, and `../wt-media-desktop`.
- Current product facts live in `docs/product`.
- Current engineering facts live in `docs/engineering`.
- Human-readable cross-repo contract governance lives in `docs/contracts`.
- Durable decision records live in `docs/decisions`.
- Current implementation process records live in `delivery/active`.
- Root `../docs` is legacy and not the source of truth for new implementation work.
- Generated skill copies in runtime repositories are outputs, not sources.

## Change Governance

- No M/L feature implementation without an active `delivery/active/<change-id>/change.md`.
- CHG implementation, resume, review, and completion must use the `executing-wt-media-change` Skill.
- Discussion, review comments, and questions do not become requirements until recorded as confirmed decisions.
- Only confirmed decisions may drive code changes.
- Do not implement anything listed under "Explicitly Not Doing" in the active change record.
- New architecture or contract branches must be recorded under pending questions and resolved before implementation continues.
- Update the active change checkpoint before ending a coding session.

## Required Checks

- Validate skill source names before distribution.
- Check contract ownership before cross-repo changes.
- Keep release matrix updated when validated component combinations change.
