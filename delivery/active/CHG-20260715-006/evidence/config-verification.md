# M0-R5 Config Verification Evidence

## Release Matrix Updates

Updated Desktop toolchain facts:

```yaml
ci_node_version: "26"
local_observed_node: "26.5.0"
local_observed_npm: "11.17.0"
ci_rust_toolchain: stable
local_observed_rustc: "1.97.0"
local_observed_cargo: "1.97.0"
```

Updated Desktop Rust status to record that M0-R4 verified the real Vue/Vite/Tauri Rust loop.

## Verification Script Updates

`scripts/verify_m0_config.py` now verifies:

- current contract map ownership and placeholder task schema state;
- current release matrix historical release markers;
- current revised M0 Desktop Node/Rust/Cargo facts;
- CI workflow gates for Cloud, Agent, Desktop and Workspace.

`scripts/verify_product_master_alignment.py` now verifies the updated M0-R4 Tauri readiness statement.

`scripts/verify_m0_local.sh` now runs the real revised M0 local command matrix instead of old scaffold health checks. Cloud MySQL migration is run when `WT_MEDIA_MYSQL_DSN` is set; otherwise it prints an explicit skip for local convenience. CI uses a MySQL service and always runs migrations.

## Local Verification

```text
python3 scripts/verify_m0_config.py
Workspace config verification ok

python3 scripts/verify_product_master_alignment.py
Product and Master Plan alignment verification ok

python3 -m unittest discover -s tests
Ran 13 tests
OK

sh -n scripts/verify_m0_local.sh
PASS
```

## Status

PASS.
