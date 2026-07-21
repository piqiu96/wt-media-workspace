# M2-E Desktop Local Agent lifecycle

Desktop now owns the Local Agent child handle in application state. Both the
packaged `wt-media-agent` sidecar and the development Python fallback are
spawned without blocking the command, repeated starts return
`already_running`, and `local_agent_stop` kills and clears the owned child.

Verification:

- `cargo fmt`
- `cargo test` — 2 tests passed.

The remaining acceptance step is an integrated packaged-app smoke run; unit
coverage confirms deterministic process ownership and stop behavior.
