# Cloud status

- Current component: `v0.1.0-rc.7` → `99eaf30cdf08fdaa87c6799dce5cc8ca56b336cd`.
- Implemented: self-contained release directory, template-state `config/`, `config-check`, pre/online variable rendering, atomic `current` activation, BaoTa Go project/process-manager guide, static Cloud Web with SPA fallback, and removal of shared/systemd/Nginx runtime layout.
- Verification: Cloud CI `37151385427` passed; full Go/Web tests passed (Web 487); deployment/package tests passed; local MySQL 8.4 empty database applied 50 migrations, rerun applied 0; Server Web/API/login and Scheduler/Worker passed; second-version switch and rollback passed.
- Local-only operator helper: `~/.wt-media/upload-config-variables.py` with `~/.wt-media/vars/cloud/{pre,online}.json`; dry-run only, no real variable upload.
- Remaining: consume Cloud `rc.7` in product RC9, verify the GitHub Cloud Artifact, then collect real BaoTa server evidence.
