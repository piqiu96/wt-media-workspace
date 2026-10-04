# Workspace status

- Current: product `v0.1.0-rc.11` is published as a successful Pre-release after Run `37175924935`, with simplified Cloud `v0.1.0-rc.8`, Agent `v0.2.2-rc.2`, Desktop `v0.1.0-rc.3`, environment `online`.
- Release checks now validate pre/online environments and the new template-state Cloud package: `config/*.toml.tpl`, `bin/config-check`, renderer scripts, migrations, and no old systemd/Nginx/config-template layout.
- Verification: 11 Workspace release tests passed; RC11 all jobs, Cloud payload checks, Pre-release attachments and checksums passed.
- Remaining: user uploads the 11-variable `online.json` and performs BaoTa installation, recording `server-acceptance.md`.
