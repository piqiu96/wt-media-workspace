---
name: cross-repo-contract-change
description: Manage provider-owned contract changes and generated consumer updates.
---

# Cross-Repo Contract Change

Use this skill for any Cloud API, Cloud-Agent API, or Local Agent API contract change.

## Sequence

1. Confirm contract owner from `docs/contracts/ownership.md`.
2. Update provider contract files.
3. Decide whether the change is compatible.
4. Regenerate consumer code if generators exist.
5. Update `config/contract-map.yaml` or compatibility docs if ownership changes.
6. Update release matrix after validation.

## Blocking Conditions

- Breaking change without a decision record under `docs/decisions`.
- Consumer update without provider contract update.
- Runtime code copying contract definitions by hand.
