# C6 automated four-repository matrix

Executed on 2026-07-14 from independent clean repositories:

| Repository | Gate | Result |
|---|---|---|
| Workspace | M0 config verifier, M2 static verifier, seven unit tests, eight governed skill files | PASS |
| Cloud | `go test ./... -count=1`, `go vet ./...`, parse 20 YAML contracts | PASS |
| Agent | 38 unit tests, parse six YAML contracts | PASS |
| Desktop | dependency-free lifecycle/binding verifier, diff check | PASS |

Additional facts:

- The M2 verifier checks releases C1-C5, migrations 001-005, Cloud/Agent revision `2026.07.14.6`, profile-guard event/status `2026.07.14.8`, Desktop locks, and secret-persistence markers.
- Desktop verification covers the JS invoke boundary and the Rust owned-ticket `BindingTransport` boundary. Cargo is absent, so Rust compilation is not claimed.
- A fresh M1 localhost integration rerun could not bind a loopback port in the current sandbox (`PermissionError: Operation not permitted`). Previously closed M1 evidence remains valid; this attempt is not called a fresh PASS.
- Real MySQL/BitBrowser rows are deliberately excluded from this automated PASS.
