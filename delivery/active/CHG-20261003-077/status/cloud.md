# Cloud status

- Current component: `v0.1.0-rc.7` → `99eaf30cdf08fdaa87c6799dce5cc8ca56b336cd`.
- Implemented: self-contained release directory, template-state `config/`, `config-check`, pre/online variable rendering, atomic `current` activation, BaoTa Go project/process-manager guide, static Cloud Web with SPA fallback, and removal of shared/systemd/Nginx runtime layout.
- Verification: Cloud CI `37151385427` passed; full Go/Web tests passed (Web 487); deployment/package tests passed; local MySQL 8.4 empty database applied 50 migrations, rerun applied 0; Server Web/API/login and Scheduler/Worker passed; second-version switch and rollback passed.
- Local-only operator helper: `~/.wt-media/upload-config-variables.py` with `~/.wt-media/vars/cloud/{pre,online}.json`; dry-run only, no real variable upload.
- Consumed by product RC10; Cloud payload checks and Pre-release publication passed. Cloud tar SHA-256 is `5844a1e2da2bc95b40135d74e6fa58c400584959a4a5cc063ba64e7df1a4c0d1`.
- Remaining: real BaoTa installation and server acceptance.
