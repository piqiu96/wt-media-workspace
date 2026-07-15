# Decision 0006: M1 Interruption, Recovery, and Idempotency Matrix

## Status

Accepted

## Context

M1 (Cloud-Agent-Desktop Minimum Task Loop) requires that tasks survive process restarts
and network interruptions. Each component has different persistence and resilience properties.

## Recovery Matrix

| Scenario | Cloud | Agent | Desktop | Recovery Mechanism |
|---|---|---|---|---|
| Cloud restart during task execution | MySQL persists tasks + registry; noop tasks survive | Agent detects claim loss; re-claims on heartbeat interval | Desktop reconnects via HTTP | MySQL task store + Agent poll loop |
| Agent restart during task execution | Task remains `leased` until lease expires | SQLite checkpoints track incomplete tasks; `_recover_incomplete_tasks()` on startup | Desktop detects agent offline via health endpoint | SQLite checkpoint + lease expiry + re-claim |
| Desktop restart | No impact (Desktop is a viewer) | No impact | Tauri shell restarts; Vue mounts and calls `local_agent_status` | Stateless Vue + Tauri HTTP bridge retries |
| Network partition (Agent → Cloud) | Tasks remain in MySQL; leasing agents timeout | OfflineResults queue in SQLite; `_flush_offline_queue()` on reconnect | Desktop local page still shows agent status | SQLite offline queue + flush on recovery |
| Desktop → Agent connection lost | No impact | No impact | `local_agent_status` returns error; UI shows Stopped | `reqwest::get()` timeout → error state in Vue |
| Duplicate task creation | `idempotency_key UNIQUE` in MySQL | N/A | N/A | MySQL unique constraint + `ON DUPLICATE KEY` |
| Duplicate task claim | `Claim` checks `status='pending'` before update | `_recover_incomplete_tasks` skips completed tasks | N/A | MySQL `WHERE status='pending'` guard |
| Duplicate task report | `WHERE status NOT IN terminal` guard | N/A | N/A | MySQL `ErrTaskAlreadyTerminal` on terminal tasks |
| Concurrent agent claims | `FOR UPDATE` row lock on claim query | N/A | N/A | MySQL row-level locking |
| Task cancel during execution | `Cancel` sets `cancelled`; terminal guard prevents double-cancel | Runner checks status before re-claiming | UI shows cancelled status | Status machine + terminal guard |
| Browser refresh during task creation | Noop task is idempotent via idempotency_key | N/A | N/A | Idempotency key dedup in MySQL |

## Design Properties

1. **Cloud is the source of truth** for task state. Agent SQLite is a checkpoint cache, not authoritative.
2. **At-most-once execution** for terminal tasks. Once `succeeded`/`failed`/`cancelled`, no more reports accepted.
3. **Lease expiration** prevents abandoned tasks from blocking the queue. Expired leases can be re-claimed.
4. **Offline queue** in Agent SQLite ensures results are not lost during network partitions.
5. **Last-write-wins** for progress updates during normal operation (idempotent by task_id + agent_id).

## Consequences

- Positive: all interruption and recovery scenarios are addressed with existing M1 infrastructure.
- Negative: no formal chaos-monkey testing yet; scenarios validated through code review and unit tests.
- Follow-up: M10 will add formal chaos engineering, backup/restore, and disaster recovery drills.
