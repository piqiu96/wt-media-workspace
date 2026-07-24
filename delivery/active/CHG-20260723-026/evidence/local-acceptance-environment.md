# Local acceptance environment

## Command / manual action

- Fixed Cloud local scripts to use one stable acceptance database and port:
  - database: `wt_media_cloud`
  - HTTP address: `127.0.0.1:18080`
  - session cookie secure flag disabled for local HTTP
- Changed Cloud local start script to build and run `.cache/wt-media-cloud-server` instead of relying on `go run` as the long-running process.
- Started Cloud API in a foreground Codex session for manual acceptance because background child processes can be cleaned up when the command session exits.
- Verified Cloud API health and local acceptance logins.

## Expected result

- Cloud API is reachable on `127.0.0.1:18080`.
- Local acceptance data uses `wt_media_cloud`.
- The known local acceptance accounts can log in:
  - `admin`
  - `senior01`
  - `operator01`

## Actual result

- `GET /healthz` returned `ok`.
- API login returned success payloads for all three local acceptance accounts.

## Status

PASS

## Notes

- This evidence records local acceptance environment stabilization only.
- It does not change the M2-B product closure or browser window synchronization requirements.
