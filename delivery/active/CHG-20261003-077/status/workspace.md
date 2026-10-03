# Workspace status

- Current: product `v0.1.0-rc.10` Manifest prepared with Cloud `v0.1.0-rc.7`, Agent `v0.2.2-rc.2`, Desktop `v0.1.0-rc.3`, environment `online`. RC9 component builds passed but its Workspace payload test still expected the removed systemd/Nginx layout; RC10 carries the corrected check.
- Release checks now validate pre/online environments and the new template-state Cloud package: `config/*.toml.tpl`, `bin/config-check`, renderer scripts, migrations, and no old systemd/Nginx/config-template layout.
- Verification: 11 Workspace release tests passed; RC10 Manifest validation and Delivery governance passed.
- Remaining: commit/push RC10 product Tag, observe the complete GitHub Run, verify downloaded Cloud Artifact and Pre-release attachments, then collect actual BaoTa deployment evidence in `server-acceptance.md`.
