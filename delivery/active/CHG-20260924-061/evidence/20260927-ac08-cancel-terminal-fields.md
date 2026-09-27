# CHG-20260924-061 AC-08 cancel arm — the terminal write a cancelled task never got

- Date: 2026-09-27
- Repo: `wt-media-cloud`, branch `codex/m4-a-cloud`
- Commit: `db29335` (defect fix)
- Scope: the cancel arm of AC-08, and a defect it exposed in
  `cancelTask`. No credentials, cookies, signed URLs, local usernames or
  absolute paths appear in this record. Throwaway harnesses (a probe binary and a
  real-database test file) live outside the commit and are deleted before the CHG
  closes.

## 1. How the defect surfaced

Driving AC-08's cancel arm through the real chain — bind a fresh node, click
download with the Agent sidecar deliberately stopped so the task can only be
`pending`, then cancel — the cancel answered `200 errcode=0` and the row read
`cancelled`. Three other columns did not agree with that answer:

| Column | Reading | What the statement above `cancelTask` says it should be |
|---|---|---|
| `finished_at` | `NULL` | written for the `pending` arm |
| `error_code` | `NULL` | `cancelled_by_user` |
| `error_message` | `NULL` | `cancelled by user` |
| `lease_expires_at` | unchanged | `NULL` |

The function's own comment says of the `pending` arm: *"there is nobody to ask:
the row becomes `cancelled` outright and the terminal fields are written here."*
And the other route into the same state, `ReconcileCancelledTasks`, writes
`finished_at` and `error_code = 'cancelled_by_user'`. Two routes to one terminal
state were producing different rows.

## 2. Root cause, measured before it was believed

`cancelTask` expressed both phases in one statement with a
`CASE WHEN status = 'pending'` per column, and assigned `status` **first**. MySQL
evaluates a `SET` list from left to right and a later assignment reads the value
an earlier one has just written, so by the time the following four `CASE`s were
evaluated, `status = 'pending'` was already false for a row that had just become
`cancelled` — every one of them fell through to its `ELSE` and kept the old value.

Controlled on MySQL 8.4.10 with two temporary tables holding a `pending` and a
`running` row, same statement body, only the position of the `status` assignment
differing:

| Arm | row | status | cancel_requested_at | finished_at | lease kept | error_code |
|---|---|---|---|---|---|---|
| `status` first (the shipped shape) | pending | cancelled | not set | **not set** | **yes** | **NULL** |
| `status` first | running | running | set | not set | yes | NULL |
| `status` last (control) | pending | cancelled | not set | **set** | **no** | **cancelled_by_user** |
| `status` last | running | running | set | not set | yes | NULL |

The two `running` rows are identical, so the broken half is exactly the
`pending` arm. A repository-wide scan for the same pattern found no second
occurrence: `reportProgress` and `completeTask` also use `CASE WHEN`, but on
`total_bytes`, which neither statement assigns before reading it.

## 3. Red, then green, against this repository's own function

Every test in this repository runs on `go-sqlmock`, which asserts **statement
text**; none of them can see what MySQL does with a statement. The measurement
therefore had to be a real database, and it had to call the repository's own
`cancelTask` rather than a transcription of its SQL.

A throwaway test file inside the package (untracked; deleted before the CHG
closes) opened a real MySQL, took the real definition with `SHOW CREATE TABLE`,
stripped the foreign keys a temporary table cannot carry, and re-created the
table as `TEMPORARY` so the name `file_transfer_tasks` shadows the real one in
that session and the production SQL runs unmodified. A guard asserted the shadow
was in effect by counting rows — the real table held 17 at the time, the scratch
one 5 — so a pool that opened a second connection could not silently point the
reads at real rows. Five rows: one `pending` with a stale lease, one `running`
with a live one, one of another team, one of another user, one already terminal.

| | Before the fix | After the fix |
|---|---|---|
| `pending` arm | **FAIL** — `finished_at` unset, `lease_expires_at` kept, `error_code`/`error_message` empty | PASS — `cancelled`, `finished_at` = the passed instant, lease `NULL`, `error_code=cancelled_by_user`, `error_message=cancelled by user`, `cancel_requested_at` still `NULL` |
| `running` arm | PASS | PASS — status stays `running`, `cancel_requested_at` set, no finish time, no error, lease kept |
| other team / other user / terminal | PASS — untouched | PASS — untouched |

The red run failed on precisely the four defects and nothing else, so the test
discriminates. Nothing in the tracked suite can regress it; see §6.

## 4. Fix

Two statements, one per phase, instead of one statement with a `CASE` per column.
Each phase writes every field of its own transition, so neither depends on the
order its assignments happen to be evaluated in. `RowsAffected` short-circuits:
the two predicates are mutually exclusive on `status`, so the result is still
either 0 or 1, and a terminal or unowned row matches neither — the same answer
the caller's own state check gives.

Re-ordering the assignments in the single statement was rejected even though its
control reading above is correct: with no test able to observe the semantics,
correctness should not rest on a rule nothing enforces.

## 5. Real chain, re-measured on the fixed build

Server restarted onto the rebuilt binary (`bin/control.sh restart`; the artefact's
mtime moved 12:28 → 13:07). Same arm, one coherent run: bind and click in **one**
session, sidecar stopped in between by the harness, then cancel.

| Step | Reading |
|---|---|
| click | `202`, task `pending`, `total_bytes=99242095`, `assigned_node_id=None` |
| row before | `pending, 99242095, transferred_bytes=0, finished_at=NULL, error_code=NULL, lease=NULL` |
| cancel | `200 errcode=0` |
| row after | `cancelled, transferred_bytes=0, finished_at=2026-09-27 13:11:10.086893, cancel_requested_at=NULL, error_code=cancelled_by_user, error_message=cancelled by user, lease_expires_at=NULL, attempt_count=0` |
| session API body | `status=cancelled`, `completed_bytes=0`, `error_code=cancelled_by_user`, `error_message='cancelled by user'`, `updated_at=2026-09-27T13:11:10.086893+08:00` |
| files on disk | unchanged at 2; neither belongs to a cancelled task |

A sidecar left running would have raced the cancel, so the harness stopped it and
verified the port was closed before clicking.

The download-centre listing then produced a before/after pair inside one
response, on the same material and the same route, without anything being
constructed for the purpose:

| Task | Lineage | `status` | `error_code` |
|---|---|---|---|
| `transfer_15104d96c61af59acf892c50` | cancelled after the fix | `cancelled` | `cancelled_by_user` |
| `transfer_a877be9c3cd46d605ad79bf3` | cancelled after the fix | `cancelled` | `cancelled_by_user` |
| `transfer_b3a61ac5e8539e8ffb3404d` | cancelled before the fix (12:02) | `cancelled` | `NULL` |

The row cancelled before the fix keeps its blank `error_code`; nothing was
retro-patched, and this record does not claim otherwise.

`dto.Task` is the session contract's fixed key set and carries no `finished_at`
and no `cancel_requested_at` — the visible half of this defect is `error_code`,
which the download centre does read. The absent `finished_at` is terminal-state
integrity in the table rather than an API-visible field.

## 6. Coverage, stated rather than implied

- Covered here: the `pending` arm's terminal write, the `running` arm's request
  write, the scope/state gating of both statements, the real chain from click to
  cancel, and the download-centre reading of the result.
- Automated: `go test ./...` in the Cloud worktree, green after the fix. The
  tracked test was rewritten to the two statements and now covers three arms —
  pending, running, and neither — but it asserts statement text, so it pins the
  chosen shape and cannot re-derive §2.
- **Not covered by any test in this repository**: whether MySQL's evaluation of a
  `SET` list leaves the row the code intends. There is no real-database harness
  in the Cloud repository; every existing test file uses `go-sqlmock`. Raised as
  `Q-03` in the checkpoint (non-blocking) with the recommendation to add an
  environment-gated real-database test, and deliberately not decided here.
- Not re-measured in this round: the `running` arm's end-to-end path through
  `ReconcileCancelledTasks`, which finishes a running task an executor never came
  back for. That path was measured in an earlier round and this fix does not touch
  it. What the fix does align is the terminal write itself: the `pending` statement
  now sets the same six columns to the same values `ReconcileCancelledTasks`
  already set for a running task — `status = 'cancelled'`, `finished_at = ?`,
  `lease_expires_at = NULL`, `error_code = 'cancelled_by_user'`,
  `error_message = 'cancelled by user'`, `updated_at = ?`. Only the `WHERE` differs,
  and it must: the reconcile statement keys off `cancel_requested_at IS NOT NULL`
  with no caller scope, this one off `status = 'pending'` plus the caller's team and
  user. Two routes into `cancelled` now produce the same row, which is what they did
  not do before.
