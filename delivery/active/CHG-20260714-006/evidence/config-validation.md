# Evidence: Config Validation

- CHG: `CHG-20260714-006`
- Task: `T-02`
- Date: 2026-07-14
- Type: command
- Status: PASS

## Changes

- `config/contract-map.yaml` now marks all M0 contract areas as `placeholder_only`.
- `config/contract-map.yaml` now marks all formal definitions as `inactive`.
- `config/release-matrix.yaml` now records `0.1.0-m0-health`.
- `config/release-matrix.yaml` records `formal_contract_versions_active: false`.
- Formal `v1` contract claims were removed from the current M0 release matrix.
- `scripts/verify_m0_config.py` validates these invariants without external Python dependencies.
- `tests/test_verify_m0_config.py` covers contract map and release matrix validation.

## Commands

```text
python3 scripts/verify_m0_config.py
python3 scripts/verify_m0_config.py --allow-missing-repos
python3 -m unittest discover -s tests
```

## Results

```text
M0 config verification ok
M0 config verification ok
Ran 5 tests in 0.023s
OK
```

## Baseline Alignment

Updated `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` so its version matrix example no longer implies active M0 `v1` contracts.
