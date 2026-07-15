# M0-R5 Workflow Matrix

| Repository | Workflow | Revised M0 Gate |
|---|---|---|
| `wt-media-cloud` | `.github/workflows/m0-cloud.yml` | Go 1.26.5, Node 26, MySQL 8.4 service, `scripts/bootstrap.sh`, `scripts/test.sh`, two `scripts/migrate.sh` runs, `scripts/build.sh` |
| `wt-media-agent` | `.github/workflows/m0-agent.yml` | Python 3.12, `astral-sh/setup-uv@v5`, `scripts/bootstrap.sh`, `scripts/test.sh`, two SQLite `scripts/migrate-storage.sh` runs, `scripts/build.sh` |
| `wt-media-desktop` | `.github/workflows/m0-desktop.yml` | `macos-latest`, Node 26, Rust stable, `scripts/bootstrap.sh`, `npm run lint`, `scripts/test.sh`, `scripts/build.sh` |
| `wt-media-workspace` | `.github/workflows/m0-workspace.yml` | Python 3.12, unit tests, `verify_skills.py`, `verify_m0_config.py --allow-missing-repos`, `verify_product_master_alignment.py`, dynamic active CHG context validation |

## Notes

- Desktop CI uses macOS because the M0-R4 proof is a macOS Tauri build and local shell path.
- Workspace active context validation dynamically discovers the single active CHG instead of hardcoding `CHG-20260715-006`.
- Remote GitHub CI was not run in this CHG; workflow coverage is verified statically by `verify_m0_config.py`.
