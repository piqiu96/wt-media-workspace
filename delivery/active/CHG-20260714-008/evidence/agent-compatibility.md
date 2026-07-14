# Evidence: Agent Compatibility

- CHG: `CHG-20260714-008`
- Task: `T-03`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Purpose

Prove that Agent can evaluate Cloud-Agent compatibility metadata without copying the provider-owned OpenAPI definition.

## Method

Files added or updated in `wt-media-agent`:

```text
src/wt_media_agent/cloud_agent_contract.py
tests/test_cloud_agent_contract.py
contracts/README.md
```

Command:

```text
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Expected

- Agent accepts current Cloud-Agent metadata for `v1` revision `2026.07.14.1`.
- Agent rejects incompatible major versions, older revisions, missing compatible agent major version, and malformed Cloud envelopes.

## Actual

```text
Ran 9 tests in 0.000s
OK
```

## Follow-Up

- Commit Agent consumer slice.
- Update Workspace Contract Map and Release Matrix.
