# C6 real dependency inventory

Observed on 2026-07-14:

- Docker CLI: present at `/usr/local/bin/docker`, client 20.10.12.
- Docker daemon: unavailable (`Cannot connect to the Docker daemon at unix:///var/run/docker.sock`). No image pull or container mutation was attempted.
- MySQL CLI/server: not found in PATH.
- `WT_MEDIA_MYSQL_DSN`: unset (value was not printed).
- BitBrowser application: installed at `/Applications/比特浏览器.app`.
- BitBrowser Local API: connection to `127.0.0.1:54345` refused.
- `WT_MEDIA_BIT_API_URL`: unset (value was not printed).
- Rust Cargo: not installed, so native Rust compilation cannot be added as evidence; Desktop's dependency-free Node verifier passes.
- Codex escalation quota rejected fresh GUI/local-process launches. No indirect workaround was attempted.

These facts make AC-03 through AC-05 real integration rows currently unavailable. Fixture/sqlmock/unit results remain useful automated evidence but are not relabeled as real integration.
