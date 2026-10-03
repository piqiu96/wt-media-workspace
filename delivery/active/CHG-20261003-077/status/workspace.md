# Workspace status

- Current: product `v0.1.0-rc.9` Manifest prepared with Cloud `v0.1.0-rc.7`, Agent `v0.2.2-rc.2`, Desktop `v0.1.0-rc.3`, environment `online`.
- Release checks now validate pre/online environments and the new template-state Cloud package: `config/*.toml.tpl`, `bin/config-check`, renderer scripts, migrations, and no old systemd/Nginx/config-template layout.
- Verification: 9 Workspace release tests passed; RC9 Manifest validation and Delivery governance passed.
- Remaining: commit/push RC9 product Tag, observe the complete GitHub Run, verify downloaded Cloud Artifact and Pre-release attachments, then collect actual BaoTa deployment evidence in `server-acceptance.md`.
