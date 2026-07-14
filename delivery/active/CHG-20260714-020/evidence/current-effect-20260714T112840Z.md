# C6 current-effect execution

Executed: 2026-07-14T11:28:40Z

## Revisions

- Workspace: `4ea30ad docs: checkpoint chg-020 automated acceptance`
- Cloud: `2753715 feat: publish sensitive profile guard contract`
- Agent: `3d4081a feat: renew and report sensitive profile permits`
- Desktop: `84c9bbb feat: enforce native one-use binding boundary`

## Automated matrix

| Area | Command | Actual result | Status |
|---|---|---|---|
| Workspace config | `python3 scripts/verify_m0_config.py` | `Workspace config verification ok` | PASS |
| Workspace M2 static acceptance | `python3 scripts/verify_m2_acceptance.py` | `M2 static cross-repository acceptance matrix ok`; real MySQL/BitBrowser evidence remains separate | PASS |
| Workspace tests | `python3 -m unittest discover tests` | 7 tests passed | PASS |
| Cloud tests | `env GOCACHE=... go test ./... -count=1` | all packages passed | PASS |
| Cloud vet | `env GOCACHE=... go vet ./...` | exited 0 | PASS |
| Agent tests, system Python | `scripts/verify-health.sh` | system Python 3.9 cannot import `str | None` annotations used by the 3.12 project | ENV-BLOCKED |
| Agent tests, repo venv | `.venv/bin/python -m unittest discover -s tests` | 38 tests passed | PASS |
| Desktop verifier | `npm run verify` | `wt-media-desktop health ok` | PASS |

The Homebrew shellenv warning about `/bin/ps` sandbox access appeared in sandboxed commands but did not affect the PASS exits above.

## Real dependency probes

| Dependency | Command/action | Actual result | Status |
|---|---|---|---|
| Docker daemon | `open -a Docker`, then `docker info` with host permission | Docker Desktop daemon is reachable; 0 containers, 1 image | AVAILABLE |
| Local MySQL image | `docker images --format ...` | only `app:6.0` exists; no MySQL 8-compatible image is available locally | BLOCKED |
| MySQL CLI | `mysql --version` | command not found | BLOCKED |
| Cloud DSN | redacted env presence check | `WT_MEDIA_MYSQL_DSN=unset`; value was not printed | BLOCKED |
| BitBrowser app | `ls -d /Applications/比特浏览器.app` | installed | AVAILABLE |
| BitBrowser Local API | project adapter call to `http://127.0.0.1:54345/browser/list` with host permission | API reachable, but 37 Profiles contain 2 distinct non-empty `userId` owners | FAIL |

## Acceptance impact

- AC-01 remains PASS from fresh automated evidence.
- AC-02 remains PASS from fresh Desktop verifier plus prior Desktop boundary evidence.
- AC-03 remains BLOCKED: no MySQL CLI, no `WT_MEDIA_MYSQL_DSN`, and no local MySQL Docker image to run without dependency download.
- AC-04 is currently FAIL/BLOCKED by real BitBrowser data: the Local API is reachable, but Profile ownership is not uniform.
- AC-05 remains BLOCKED because it requires the real MySQL-backed runtime/profile/permit state.
- AC-06 remains BLOCKED until AC-03 through AC-05 have real PASS evidence.

No Cookies, binding tickets, node credentials, permit credentials, proxy secrets, or raw BitBrowser Profile payloads were printed or retained.
