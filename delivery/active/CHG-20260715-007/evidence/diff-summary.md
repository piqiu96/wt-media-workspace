# M0-R6 Diff Summary

## wt-media-agent

Expected verification script changes:

- `scripts/bootstrap.sh`: use repo-local uv cache by default.
- `scripts/start-health.sh`: use detached Python subprocess startup for stable background health server.

Commit:

- `0e07b4e fix: stabilize agent m0 local scripts`

Out-of-scope changes:

- No Agent business runtime behavior changed.

## wt-media-workspace

Expected governance changes:

- Active CHG moved from CHG-20260715-006 to CHG-20260715-007.
- M0 status moved to `VERIFYING` after automated/local engineering gates passed.
- R6 evidence added.
- Product/Master alignment script and test updated to accept M0 `VERIFYING`.

Out-of-scope changes:

- None identified.

## wt-media-cloud

- No code changes.

## wt-media-desktop

- No code changes.
