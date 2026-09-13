# Task 6 Local proxy scan and create-sync

- Cloud contract revision `2026.09.05.1` adds `POST /api/v1/proxies/local-scan/preview` and `/confirm`. Preview is zero-side-effect. Confirm requires the current trusted Desktop `node_id` and only reconciles unambiguous Profile—proxy relations.
- Scan handling: an observed existing tuple switches the formal relation; observed `noproxy` clears it; an unknown tuple creates a paused, unchecked record marked `本机扫描发现，待补充并检测`; multiple matching records are reported as `conflict` and are not guessed. A confirmed scan can be retried to finish a previously interrupted formal reconciliation.
- Desktop ProxyPage: the new-proxy dialog optionally selects an unbound active Profile and calls the synchronous assign/read-back API; `扫描本机代理` reuses the Tauri Local Agent Profile scan, previews Cloud Diff, accepts the trusted scan, or restores Cloud configuration one Profile at a time through the existing write/read-back API.
- Commands: `go test ./internal/modules/proxy ./internal/modules/profilebinding -count=1`; `npm test -- --run`; `npm run build:cloud`; `npm run build:desktop`.
  Expected: lifecycle and local scan route tests, all Web tests, and both Web builds pass.
  Actual: Cloud proxy and profilebinding packages passed; 42 Web tests passed; both builds completed. Vite issued the pre-existing chunk-size warning only.
- External-effect limitation: tests use controlled fixtures. The user must perform the real BitBrowser actions with a writable real proxy before this can be counted as M2-C end-to-end acceptance.
