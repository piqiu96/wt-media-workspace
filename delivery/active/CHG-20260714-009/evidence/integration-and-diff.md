# Evidence: Integration And Diff

- CHG: `CHG-20260714-009`
- Task: `T-04`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Purpose

Prove the Agent registration and heartbeat slice works without introducing later M1 task execution or Desktop behavior.

## Method

Commands:

```text
python3 -m unittest discover -s tests
python3 scripts/verify_m0_config.py
go test ./...
PYTHONPATH=src python3 -m unittest discover -s tests
npm run verify
curl POST /api/v1/cloud-agent/agents/register
curl POST /api/v1/cloud-agent/agents/agent-local-1/heartbeat
curl GET /api/v1/cloud-agent/agents/agent-local-1
```

## Expected

- Workspace, Cloud, Agent, and Desktop verification pass.
- Cloud registers an Agent node and updates heartbeat status.
- Agent can build registration and heartbeat client requests.
- No task polling, lease, executor, SSE, Desktop page, or account/Profile behavior is introduced.

## Actual

```text
Workspace: Ran 6 tests; OK
Workspace config: Workspace config verification ok
Cloud: go test ./... passed
Agent: Ran 12 tests; OK
Desktop: wt-media-desktop health ok
```

Cloud-Agent latest contract revision:

```text
v1@2026.07.14.2
```

Diff interpretation:

```text
Cloud changes are limited to Cloud-Agent registration/heartbeat contract, registry, and routes.
Agent changes are limited to Cloud-Agent registration/heartbeat client and tests.
Workspace changes are limited to CHG evidence plus Contract Map and Release Matrix metadata.
Desktop has no source changes.
```

## Follow-Up

- Commit Workspace evidence and config.
- Push affected repositories.
- Remove completed active record.
