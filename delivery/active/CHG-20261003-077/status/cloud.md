# Cloud status

- Current component: `v0.1.0-rc.8` → `48d57d8d4d85ebaaa8eb89d1ad0bf474e5dd7962`; prior RC7 remains immutable.
- Implemented: self-contained release directory, template-state `config/`, `config-check`, pre/online variable rendering, atomic `current` activation, BaoTa Go project/process-manager guide, static Cloud Web with SPA fallback, and removal of shared/systemd/Nginx runtime layout.
- Verification: Cloud CI `37151385427` passed; full Go/Web tests passed (Web 487); deployment/package tests passed; local MySQL 8.4 empty database applied 50 migrations, rerun applied 0; Server Web/API/login and Scheduler/Worker passed; second-version switch and rollback passed.
- Local-only operator helper: `~/.wt-media/upload-config-variables.py` with `~/.wt-media/vars/cloud/{pre,online}.json`; dry-run only, no real variable upload.
- Consumed by product RC10; Cloud payload checks and Pre-release publication passed. Cloud tar SHA-256 is `5844a1e2da2bc95b40135d74e6fa58c400584959a4a5cc063ba64e7df1a4c0d1`.
- Variable reduction: fixed app/admin/server, Agent endpoint and Douyin endpoint are now plain TOML; variable count is 11 (primary DB 5, credentials 5, OSS prefix 1). Cloud CI `37175720841` passed and product RC11 Run `37175924935` passed.
- Remaining: real BaoTa installation and server acceptance.
