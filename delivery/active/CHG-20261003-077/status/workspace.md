# Workspace status

- Current: product `v0.1.0-rc.11` Manifest is prepared with simplified Cloud `v0.1.0-rc.8`, Agent `v0.2.2-rc.2`, Desktop `v0.1.0-rc.3`, environment `online`.
- Release checks now validate pre/online environments and the new template-state Cloud package: `config/*.toml.tpl`, `bin/config-check`, renderer scripts, migrations, and no old systemd/Nginx/config-template layout.
- Verification: 11 Workspace release tests passed after reducing the payload to 11 template variables; RC11 Manifest and governance passed.
- Remaining: RC11 product Run/Artifact readback, then user uploads the 11-variable `online.json` and performs BaoTa installation, recording `server-acceptance.md`.
