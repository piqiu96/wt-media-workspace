# M2 synchronous Agent fast path

## Boundary

- Short Agent/BitBrowser API operations remain synchronous: profile scans, direct profile mutations, and proxy connectivity checks.
- Browser launch, page-element interaction, Cookie operations, and account checks remain taskized because they can block, retry, or require checkpointing.
- A failed synchronous proxy check does not silently create a task. The proxy page exposes an explicit background retry and links the resulting task to the execution-task view.

## Implementation

- Agent exposes `POST /api/v1/proxy-check`, validates host/port, and returns only `connectivity` (plus an optional proxy id; credentials are never returned).
- Cloud `POST /api/v1/proxies/:id/check` calls the Agent directly and records `last_check_result`.
- The previous task path is preserved at `POST /api/v1/proxies/:id/check/background` for an operator-requested retry.
- The task page accepts `?task_id=` and polls the task detail endpoint while it is active.

## Verification

- Agent: `PYTHONPATH=src python3 -m unittest discover -s tests -q` — 48 tests passed.
- Cloud: `GOCACHE=/private/tmp/wt-media-go-cache go test ./internal/modules/proxy ./internal/app` — passed.
- Web: `npm test -- --run` — 8 tests passed.
