# Task 2 Web API-client Evidence

Date: 2026-07-21

## Failing baseline

`npm test -- --run` failed all 8 API-client tests with `TypeError: Failed to parse URL from /api/v1/...` because the client factories ignored the test-provided fetch implementation and called Node's native fetch.

## Implementation

Commit: `daf423d test(web): restore api client test injection`

- Session, Profile Binding, and Media Account client factories now accept an optional `fetch` and `base` while preserving browser defaults.
- Media Account query filters normalize `allTags` to the Cloud `all_tags` contract.
- Media Account responses remove `original_cookie` and `active_cookie` before returning to Web callers.
- Test response fixtures now use the unified `{errcode: 0, data}` envelope.
- Assertions for GET requests verify required behavior without depending on incidental method/header fields.

## Verification

Command: `npm test -- --run` in `wt-media-cloud/web`

Actual: 3 test files passed, 8 tests passed, 0 failed.

Status: PASS
