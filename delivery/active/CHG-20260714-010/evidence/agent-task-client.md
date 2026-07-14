# Evidence: Agent Task Client

- CHG: `CHG-20260714-010`
- Task: `T-03`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Purpose

Prove that Agent can build a Cloud-Agent task claim request with Agent identity and lease duration.

## Method

Files updated in `wt-media-agent`:

```text
src/wt_media_agent/cloud_agent_client.py
src/wt_media_agent/cloud_agent_contract.py
tests/test_cloud_agent_client.py
tests/test_cloud_agent_contract.py
```

Command:

```text
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Expected

- Agent consumes Cloud-Agent `v1@2026.07.14.3`.
- `claim_task` sends `agent_id` and `lease_seconds` to `/api/v1/cloud-agent/tasks/claim`.

## Actual

```text
Ran 13 tests in 0.000s
OK
```

## Follow-Up

- Commit Agent task client slice.
- Update Workspace Contract Map and Release Matrix.
