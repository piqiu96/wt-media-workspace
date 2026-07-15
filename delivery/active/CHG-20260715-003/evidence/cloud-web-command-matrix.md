# M0-R2 Cloud/Web Command Matrix

- Change: CHG-20260715-003
- Date: 2026-07-15
- Cloud commit: `db5b951`

## Scripts

| Script | Expected Result | Actual Result | Status |
|---|---|---|---|
| `scripts/bootstrap.sh` | Go modules and Web dependencies install. | `npm ci` added 71 packages; command exited 0. | PASS |
| `scripts/test.sh` | Cloud Go tests and Web Vitest tests pass. | Go packages passed; Web 3 files and 8 tests passed. | PASS |
| `scripts/build.sh` | Cloud server binary and Web assets build. | Command exited 0; Web Vite build succeeded. Go emitted a non-fatal stat-cache warning under the existing external GOPATH. | PASS with environment warning |
| `scripts/migrate.sh` | MySQL migrations run and repeat safely. | First run applied 5; repeat run applied 0. | PASS |
| `scripts/start.sh` | Cloud starts and waits for `/healthz`. | Started on 127.0.0.1:18082 and reported `wt-media-cloud started`. | PASS |
| `scripts/health.sh` | Probe health endpoints of an already running process. | Works when process is retained by a normal local shell. In Codex exec, background processes are cleaned after command return, so separate cross-command health is not reliable. | JUSTIFIED |
| `scripts/stop.sh` | Stop PID-file process or clean stale PID. | Reported `wt-media-cloud stopped`. | PASS |
| `scripts/verify-health.sh` | Run tests, start Cloud temporarily, probe health and stop. | Reported `wt-media-cloud health ok`. | PASS |

## Notes

- `WT_MEDIA_CLOUD_GOPATH` can force a project-local Go module cache. A forced cold local cache caused a long module download and was not kept as the default.
- Default scripts preserve an existing shell `GOPATH` for fast local reuse, and fall back to `.cache/go-path` when no GOPATH exists.
- The stat-cache warning in `scripts/build.sh` is non-fatal and comes from the current external Go module cache path. It does not block build output.
