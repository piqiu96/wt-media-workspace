# Evidence: Agent Client

- CHG: `CHG-20260714-009`
- Task: `T-03`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Purpose

Prove that Agent can build Cloud-Agent registration and heartbeat requests with contract version facts.

## Method

Files added in `wt-media-agent`:

```text
src/wt_media_agent/cloud_agent_client.py
tests/test_cloud_agent_client.py
```

Command:

```text
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Expected

- Register request includes `agent_id`, `mode`, version, capabilities, Cloud-Agent major version, and contract revision.
- Heartbeat request sends status to the Agent heartbeat endpoint.
- Invalid Cloud response envelopes are rejected.

## Actual

```text
Ran 12 tests in 0.003s
OK
```

## Follow-Up

- Commit Agent client slice.
- Run integrated verification and diff scan.
