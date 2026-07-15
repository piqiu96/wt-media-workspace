# M1 Manual Acceptance Skeleton

- Change: CHG-20260715-002
- Date: 2026-07-15
- Purpose: record the later human inspection path required after M0 and M1 are implemented.

This is not a completed M1 manual verification record. M1 cannot start until M0 is `DONE`.

## Required Manual Demonstration

| Step | Expected Human-Visible Result |
|---|---|
| 1. Start MySQL with a clean or known test database. | Cloud can apply migrations and connect without manual table editing. |
| 2. Start Cloud backend and Cloud Web. | Browser can open Cloud Web and login using a real account. |
| 3. Start Desktop Tauri shell. | Desktop opens a real shell, not a mock-only local page. |
| 4. Desktop starts or controls Local Agent through Rust sidecar/process management. | Local Agent health is visible through Desktop-managed control path. |
| 5. Create a `noop_task` from Cloud Web. | Task is persisted in MySQL with idempotency and lease fields. |
| 6. Agent registers and claims the task. | Cloud shows Agent node and task ownership; no duplicate Agent can claim the same task. |
| 7. Agent writes local checkpoint and reports progress. | Desktop/Web show started/progress/succeeded state through real HTTP/SSE. |
| 8. Restart Cloud. | Task and Agent registry state survive restart. |
| 9. Restart Agent. | Agent resumes from SQLite checkpoint or safely releases lease. |
| 10. Disconnect Cloud temporarily while Agent finishes. | Result remains in local durable storage and is replayed idempotently when Cloud returns. |
| 11. Restart Desktop. | Desktop reconnects to Local Agent without exposing Local Token to Vue/localStorage. |
| 12. Review logs and diagnostics. | No secret leakage; recovery events are visible enough for troubleshooting. |

## Required Evidence in Later M1-R8

- Commands used to start/stop Cloud, Web, Desktop and Agent.
- Browser/Desktop screenshots or written manual observations for login, task creation, progress and success.
- Database evidence for persistent task, lease, idempotency and Agent registry rows.
- SQLite evidence for checkpoint/offline result storage.
- Restart matrix result for Cloud, Agent and Desktop.
- Diff and repository status proving no out-of-scope changes.

Status: PASS as a skeleton; actual M1 manual verification remains NOT_STARTED.
