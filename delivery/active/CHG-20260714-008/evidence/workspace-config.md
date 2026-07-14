# Evidence: Workspace Config

- CHG: `CHG-20260714-008`
- Task: `T-04`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Purpose

Prove that Workspace records Cloud-Agent `v1` compatibility as active machine-readable metadata without storing a duplicate formal API definition.

## Method

Files updated in `wt-media-workspace`:

```text
config/contract-map.yaml
config/release-matrix.yaml
scripts/verify_m0_config.py
tests/test_verify_m0_config.py
```

Commands:

```text
python3 -m unittest discover -s tests
python3 scripts/verify_skills.py
python3 scripts/verify_m0_config.py
```

## Expected

- `cloud_agent_api` is active at `v1@2026.07.14.1`.
- Other contract areas remain `m0-placeholder` or `placeholder_only`.
- Workspace does not store the provider-owned OpenAPI definition.

## Actual

```text
Ran 6 tests in 0.026s
OK
verified 8 skill source files
Workspace config verification ok
```

## Follow-Up

- Commit Workspace config slice.
- Run final integrated acceptance and diff scan.
