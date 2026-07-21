# Task 5 Session Invalidation Evidence

Date: 2026-07-21

## Cloud

Commit: `985644f test(cloud): verify invalid session drains local agent`

Added sqlmock coverage for an invalidated local session. The MySQL registry marks `agent_nodes` as `draining`, marks `local_agent_nodes` as `replaced`, and returns `ErrSessionInvalid` before the node can become online again.

## Agent

Commit: `1e3e96f fix(agent): stop claims after session invalidation`

- Added `SessionInvalidError` for the unified Cloud `errcode=11001` response, including HTTP 409 response bodies.
- The claim loop stops after session invalidation.
- An in-flight task receiving the same signal is checkpointed as failed with `session_invalidated_result_uncertain` and the runner drains instead of retrying blindly.

## Verification

| Command | Actual | Status |
|---|---|---|
| `/Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go test ./...` with workspace `GOCACHE` | All Cloud packages passed | PASS |
| `PYTHONPATH=src python3 -m unittest discover -s tests -v` | 46 tests passed | PASS |
| `git diff --check` in Cloud and Agent | No whitespace errors | PASS |

No real credential or external Profile was used in this task.
