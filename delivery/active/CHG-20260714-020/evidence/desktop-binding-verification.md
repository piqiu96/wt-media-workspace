# Desktop one-use binding verification

- Red: updated Desktop verifier failed on stale contract locks and missing `local_agent_bind_session`.
- Green: the Desktop service accepts a non-empty one-use ticket only as a Tauri invoke argument and normalizes the response to non-secret node facts.
- The Vue-facing response excludes node/permit credentials; source checks reject browser storage and ticket logging markers.
- Rust command boundary declares the fifth native command without adding direct Local Agent URLs to Vue.
- Contract locks: Cloud-Agent `2026.07.14.6`, Local Agent API `2026.07.14.6`, Profile guard event/status `2026.07.14.8`.
- `npm run verify` passes. Cargo is unavailable on the host and is recorded in the dependency inventory.
- Desktop commit: `6f5911c`.
