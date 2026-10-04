# Cloud status

- Current component: `v0.1.0-rc.9` → `1d6457f97006742d5e4d743a01a06767de66b2c6`; prior tags (`v0.1.0-rc.8` and earlier) remain immutable.
- Implemented: single self-contained Go binary `bin/wtmctl` that pulls remote TOML variables, validates Schema/values, verifies the artifact, renders the private `config/`, runs migrations, verifies the database, installs the release, atomically switches `current`, performs read-only acceptance, and rolls back. All Python/shell deployment entry points were removed; the package no longer contains `deploy/*.py` or `deploy/*.sh`. BaoTa remains the only process manager; `wtmctl` never starts or stops Cloud processes.
- Variables: JSON replaced by TOML (`online.toml`, `pre.toml`); variable Schema (`deploy/config-variable-schema.toml`) matches the 11 template variables; the local helper and `~/.wt-media/vars/cloud/{online,pre}.toml` were migrated and uploaded to `wt-media/vars/cloud/{online,pre}.toml` with a verified read-back.
- Verification: Cloud CI `37182796598` passed (`go test ./...`, Web tests, migrations, Linux build, packaging tests); `wtmctl vars check/pull/config render` and a full `config_online` render passed locally; `git diff --check` clean.
- Server output layout: `/home/www/wt-media-cloud/output` with `online.toml`/`online.url`/`online-deploy.toml`; runtime port `127.0.0.1:8188`; `admin/admin123` remains the initial admin.
- Consumed by product RC12: cloud artifact `wt-media-cloud_v0.1.0-rc.12_linux-amd64.tar.gz` with SHA-256 `90026317ef333c6609a7bedd5d51aadfbdedc056a3365c1be00bb1dfab956fb6`; workspace `package` job ran `verify_cloud` (requires `bin/wtmctl`, schema/examples, rejects `deploy/*.py|*.sh`) and passed.
- Remaining: real BaoTa installation and server acceptance.
