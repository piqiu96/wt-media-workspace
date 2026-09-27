# CHG-20260924-061 Task 6 — cross-repository acceptance

- Date: 2026-09-27
- Repos: `wt-media-cloud` (`codex/m4-a-cloud`, HEAD `db29335`), `wt-media-agent`
  (`2d2dd48`), `wt-media-desktop` (`f6b8ace`)
- Scope: the twelve acceptance criteria of `change.md`, driven through the real
  HTTP chain and read back from MySQL, object storage and the operator machine's
  disk. No credentials, cookies, signed URLs, local usernames or absolute paths
  appear in this record.
- Environment: the Cloud server was restarted onto the binary rebuilt at
  `db29335` (13:07), the worker was rebuilt from the same commit
  (`go build ./cmd/discovery-worker`), and the Agent sidecar was started from the
  Agent worktree with its task-polling switch on. Every reading below was taken
  after `db29335` — the last content change to any of the three repositories —
  because that commit altered Cloud's terminal-state writes.

## 1. Acceptance matrix

| AC | Input (role / team / game) | Expected | Actual | |
|---|---|---|---|---|
| 061-AC-01 | material 151, converted, before any click, operator01 (team 1 / sjz) | no download is triggered by conversion | `dev/materials/151/` **0 objects**; `file_transfer_tasks` for 151 **0 rows**; `video_status = not_downloaded`; key / size / sha256 all NULL. Table-wide at that moment: 147 `not_downloaded`, 2 `ready` | PASS |
| 061-AC-02 | materials 151, 27, 29 read through `GET /api/v1/materials/{id}` and compared with MySQL | four video states are real, and API and MySQL agree | all four states observed live: `not_downloaded` (before each click) → `downloading` (151 at 13:16:54; 27 at 13:20:29–13:20:33) → `ready` (151 13:17:27 / 173,891,671; 27 13:21:12 / 241,823,150) and `failed` (29 at 13:22:19). API == MySQL on every field, including the failure reason: `last_error = 'douyin API rejected request'` is `materials.video_error`. UI leg deferred to user sign-off | PASS |
| 061-AC-03 | operator01; materials 27, 152, 153 | idempotent add, concurrent dedupe, removal, restore | two sequential adds → same usage id 11; **8 simultaneous adds → one distinct id 13**; remove → `204` and gone from my-materials (2 rows left); restore → `201`, same id 8, `active`, `removed_at` NULL. Table-wide after the run: 8 rows, **zero duplicate (user, material) pairs**. See §3 for what this round did not exercise | PASS |
| 061-AC-04 | material 27 preparation, cloud worker + real Garage bucket | prepared object lands in real storage and passes integrity | prepare task `success`, `integrity_sha256` = `integrity_bytes` = the material's digest and size. Provider read-back: `materials/27/a4822e88…5321.mp4 size=241823150 content_type=video/mp4`, `OBJECT COUNT=1`; same for 151 | PASS |
| 061-AC-05 | the same material downloaded to the operator machine by the Agent sidecar | real bytes on the operator's disk | file on disk **241,823,150 bytes**, sha256 `a4822e88…5321` = the task's declared digest. Agent log: `material download committed 241823150 bytes for transfer_acb6d0f9… as …-27.mp4` | PASS |
| 061-AC-06 | the download in flight, read every 2 s | progress, speed and terminal state come from the real task | `running` 13,107,200 → 85,196,800 → 144,179,200 → 207,093,760 → `success` 241,823,150; persisted `speed_bytes_per_sec = 25,023,908`, `eta_seconds = 0`, `attempt_count = 1`, `expected_sha256 = integrity_sha256`. UI leg deferred to user sign-off | PASS |
| 061-AC-07 | three clicks on one material; then a restart mid-download | no double execution, no unbounded tasks | three clicks returned **one task id**; the database grew by exactly **1** task row for that material (13 → 14). The restart created **no second task**: the same row went to `attempt_count = 2` and finished. A stale node credential is refused loudly (`Cloud refused this node's credential (HTTP 401); not claiming until it is replaced`) rather than silently spinning | PASS |
| 061-AC-08 | cancel, dead source, upload failure, no disk, wrong digest, concurrent dedupe, illegal state | no false success on any of them | per-arm labels in §2 — two arms measured this round, one measured here and previously, four backed by named automated tests | PASS |
| 061-AC-09 | admin / senior01 (team 1, `other`) / operator01 (team 1, `hy`+`sjz`) against materials 153, 1, 35 | scope isolation, no leak | every allow allowed and every deny denied with `403`; list row counts **149 / 26 / 11** with no out-of-scope row, and SQL reproduces the same three numbers independently (`materials ⋈ source_contents` by team and game, `user_game_scopes` as the scope source) | PASS |
| 061-AC-10 | the same three clicks, with nothing able to execute | the server starts no worker and does not wait synchronously | one server process (`.cache/wt-media-cloud-server`, no child processes, no worker process on the machine); clicks answered in **9 / 4 / 5 ms** while the worker was stopped and the Agent killed after binding; the task stayed `pending` with `transferred_bytes = 0`, `claimed_by_node_id` NULL, `heartbeat_at` NULL | PASS |
| 061-AC-11 | Cloud code, Cloud business tables, Cloud logs, Agent capability report | no local paths or long-lived signatures in Cloud; no synthesised Agent capability | Cloud code: **0** hits for `/Users/`, `/home/`, `/var/folders/`, `C:\Users`, `/tmp/` across **134** non-test `.go` files; Cloud data: **0** hits across **149** material rows and **26** task rows for `/Users/`, `/tmp/`, `X-Amz-Signature`, `Signature=`, `Expires=`; logs: **0** hits over **every** file under `logs/`. That directory holds **12** files: six live logs (line counts 1,412 / 0 / 0 / 11 / 11 / 6) and six `.wf` rotation targets, all **0 bytes** — and all six already existed at this reading (created 2026-09-26 17:05, before it). This cell first read "all six files", which named a subset while claiming the directory; the unnamed six are empty, so the zero does not change, but the set is stated here. Signature lifetime is `presign_ttl = '15m'` in both config trees and rejected if `<= 0`. Agent: every reported machine fact equals the independently measured one (disk 61,665 MB = `df -m`; ffmpeg 8.1.2 = `ffmpeg -version`; Python 3.14.6; arm64) | PASS |
| 061-AC-12 | the four suites, then the user's own walkthrough | M2/M3 regression green, UI flows pass | Cloud `go test -count=1 ./...` **exit=0, 67 ok / 0 FAIL** + `go vet` exit=0 + `gofmt -l` empty on this CHG's files; Agent `scripts/test.sh` exit=0; Desktop `scripts/test.sh` exit=0 (`release-versions: 20 passed, 0 failed`); Cloud Web `npm test` exit=0 (**34 files / 222 tests**). Desktop WebView and the real operator walkthrough are the user's sign-off step | PASS (suites); sign-off pending |

## 2. AC-08, arm by arm

"Measured this round" means a real injection against the rebuilt binaries on
2026-09-27 after `db29335`; "automated" means a named test in the tracked suite
that this round did not re-run.

| Arm | Source | Reading |
|---|---|---|
| cancel (cloud, `pending`) | **measured this round** and previously | `200 errcode=0`; row `cancelled` with `finished_at`, cleared lease, `error_code = cancelled_by_user`, `error_message = 'cancelled by user'`, `cancel_requested_at` NULL; the refreshed body agrees. Detail in `20260927-ac08-cancel-terminal-fields.md` |
| cancel (local_agent task already assigned to a node) | **measured this round** | `200 errcode=0`; `status = cancelled`, `error_code = cancelled_by_user`, `completed_bytes = 0` |
| dead source | **measured this round** | material 29's source re-pointed at an id the provider does not know: prepare task `failed`, `attempt 1/3`, `error_code = source_detail_failed`, `error_message = 'douyin API rejected request'`; the dependent local download task **also failed** rather than sitting open; `video_status = failed`; **0 objects** under the material's prefix, so a failure leaves no half-object. The source row was restored afterwards |
| restart mid-download, then resume | **measured this round** | part file killed at 24,641,536 bytes; after the Agent came back the part **did not reset to zero** (32,505,856 bytes held for ~70 s while the lease lapsed, then 48.5 → 113 → 163 → 213 MB) and the run finished with `integrity_sha256 = expected_sha256`, no `.part` left |
| upload failure | automated, **not re-run this round** | `TestPrepareFailureMatrix` carries five arms: *the staged object could not be written*, *…did not read back as uploaded*, *…could not be read back at all*, *the copy to the formal key failed*, *the formal object did not read back as uploaded* |
| no disk | automated, **not re-run this round** | `ERROR_DISK_INSUFFICIENT = "download_disk_insufficient"` (`executors/material_download.py`) with `test_no_room_is_refused_before_a_byte_is_fetched` |
| wrong digest | automated, **not re-run this round** | `test_a_body_with_the_wrong_digest_never_becomes_the_file`, `test_a_body_with_the_wrong_digest_is_retried_from_zero`, `test_a_source_shorter_than_the_task_declared_fails_the_size_check` |
| concurrent dedupe | **measured this round** + automated | 8 simultaneous adds → one id (AC-03); `TestCreateTaskDeduplicatesTheBusinessCommand`, `TestClaimTaskAnswersNullWhenTheClaimLosesItsRace` |
| illegal state rollback | automated, **not re-run this round** | `TestMarkVideoPreparingOnlyLeavesTheStatesAPreparationMayStartFrom`, `TestMarkVideoFailedWillNotTakeBackAReadyMaterial`, `TestCancelTaskRefusesATaskThatIsAlreadyTerminal`, `TestRetryTaskRequiresAFailedTaskWithinItsBound` |

The source-failure arm also produced a reading this round did **not** act on: a
piece of work that fails on the source stops at `attempt 1/3`, i.e. a source
failure never spends the retry budget. Whether a transient source error should be
retried is a product decision, so it is registered as `Q-04` in the checkpoint
rather than changed here.

## 3. Not covered this round, and why

- **The Desktop GUI walkthrough** (binding and clicking in the real client) and
  **the UI legs of AC-02, AC-06 and AC-12**. By the user's ruling of 2026-09-27
  the Desktop GUI binding and click are the user's sign-off step; this record
  states plainly that the page-level three-way reconciliation was not performed
  here, not that it passed.
- **AC-03's create-from-nothing branch.** All three arms this round landed on
  rows that already existed (`usage_id` 11 / 13 / 8, created at 12:58 by the
  earlier run), so this round's readings cover the idempotent path and the
  removal/restore path — the `201` creation branch was covered by the 12:58 run,
  not by this one.
- **The four AC-08 arms listed as "automated" above.** Re-injecting them for real
  means breaking tracked configuration (a wrong bucket) or an unachievable
  environment (filling the disk); neither would add confidence about the real
  chain beyond what the named tests already assert, and the arms that only a real
  chain can expose — cancel, dead source, restart-and-resume — were injected.
- **The bucket-level cross-check against the provider's own UI.** Task 3's
  segment compared the probe's listing with the Garage admin UI at the 7-object
  state. This round's total (11 objects / 730,165,767 bytes) was checked only
  arithmetically against the service's own listing: it moved by exactly the three
  objects this round prepared (+52,089,181 +173,891,671 +241,823,150 =
  +467,804,002 bytes), which is the reading recorded, not a second UI comparison.
- **`scripts/verify_m3_acceptance.py` was not run to completion**, and
  `scripts/verify_m1_integration.py` cannot pass on this tree at all. Both are
  named in `AGENT-INDEX.md` §12 as needing a live instance and being **outside**
  the gate table, so neither is a gate. The m3 script is the more interesting
  one: it seeds an isolated team and dozens of fixtures into the dev database,
  which would move the very denominators §1 cites (149 material rows, 28 task
  rows) an hour after they were recorded — so it was left alone, with the reason
  stated rather than the run quietly performed. Its login precondition, which a
  side effect of this round had broken, was restored and verified instead (see
  the checkpoint). The m1 script's failure is fully accounted for by the
  repository's own `README.md:71`: the variable it sets to move the server does
  not move the listen address, so the health probe it waits on can never reach
  the server it started. Detail and both measurements are in the checkpoint.
- **AC-11's positive controls.** Every zero above was taken with the matcher
  proved able to match: each pattern was matched against its own text (1 hit
  each) and the searches were shown to find real strings in the same file set or
  table (e.g. `Presign` in 6 files; the SQL matcher matched a literal). One
  caveat is recorded rather than smoothed over: `bitbrowser_status` starts at
  `"normal"` and is only downgraded by a caught `BitBrowserError`; what keeps a
  single `normal` from qualifying a node on its own is that the same report
  carries `main_user_id`, which is empty when the identity could not be read.

## 4. Closing re-measure

Every reading in §1 is stamped with when it was taken, and three of them move as
the round continues. Re-measured after the last change, so that nobody has to
guess which number is stale:

| Surface | In §1 | Closing |
|---|---|---|
| `logs/` | 6 live files, `access.log` 1,412 lines | **12** files; the live `access.log` alone read 2,204 lines, and the directory read 2,236 and then 2,238 one second later — it is a live file, appended to by the Agent sidecar bound to this Cloud, which polls `/claim` about every 5 s. The count is a reading of a moving file; the **zero** is not. 0 hits for all five shapes; positive control inside the same file set: `material` matches 127 lines |
| `materials` / `file_transfer_tasks` | 149 / 26 rows | 149 / **28** rows |
| non-test `.go` files | 134 | 134 — unchanged, the worktree is clean |

Controls were re-run rather than carried over, because a zero is only worth what
its matcher is worth. Code: `Presign` is visible in 12 files under the same
retrieval, and the `/Users/` literal **is** found — 6 tracked non-`.go` files,
namely a placeholder in `LocalSettingsPage.vue:143` (`/Users/你的用户名/Movies/WTMedia`)
and fictional fixture paths in the `.js` tests. So the code-side zero is a zero
of the **Go surface**, not of the whole repository, which is how §1 words it.
The Windows-path pattern's matcher was pinned with a control built without a
literal backslash (`printf 'C:%cUsers' 92`). Data: the five `LOCATE(...) > 0`
controls each returned 1, and the columns searched were enumerated from
`information_schema.COLUMNS` — 5 text columns in `materials`, 16 in
`file_transfer_tasks` — not guessed.

The two extra task rows appeared after the §1 scan; this round's own click arms
and the restart-resume arm are the writes that account for them, and the
material count did not move.

## Result

PASS — all twelve criteria have a reading taken after the last content change.
The real chain was driven end to end on the rebuilt binaries: a source video was
re-resolved, prepared into real object storage, queued, downloaded to the
operator machine, interrupted in flight, resumed from the bytes already on disk
and committed with the declared digest, with object, disk, task and material all
agreeing. The one criterion this record does not close is the user's own
walkthrough of the Desktop client and the three pages, which the user's ruling
placed at sign-off.
