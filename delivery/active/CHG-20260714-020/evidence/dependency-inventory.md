# C6 real dependency inventory

Observed on 2026-07-14:

- Docker CLI: present at `/usr/local/bin/docker`, client 20.10.12.
- Docker daemon: initially unavailable, then reachable after starting Docker Desktop with host permission.
- Docker images: only `app:6.0` is present; no MySQL 8-compatible local image is available. No image pull or container mutation was attempted.
- MySQL CLI/server: not found in PATH.
- `WT_MEDIA_MYSQL_DSN`: unset (value was not printed).
- BitBrowser application: installed at `/Applications/比特浏览器.app`.
- BitBrowser Local API: reachable at `127.0.0.1:54345`, but real `/browser/list` data is identity-unverifiable for C6 because 37 Profiles contain 2 distinct non-empty `userId` owners.
- `WT_MEDIA_BIT_API_URL`: unset (value was not printed).
- Rust Cargo: not installed, so native Rust compilation cannot be added as evidence; Desktop's dependency-free Node verifier passes.
- Host permission was required for Docker daemon access and BitBrowser localhost access from Python. No indirect workaround was attempted.

These facts keep AC-03 and AC-05 unavailable and make AC-04 fail the real owner-uniformity gate until BitBrowser Profile ownership is corrected. Fixture/sqlmock/unit results remain useful automated evidence but are not relabeled as real integration.
