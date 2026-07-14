# Evidence: Cloud Registration Heartbeat

- CHG: `CHG-20260714-009`
- Task: `T-02`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Purpose

Prove that Cloud owns and serves the M1-C2 Agent registration and heartbeat contract.

## Method

Files added or updated in `wt-media-cloud`:

```text
contracts/cloud-agent-api/v1/registration-heartbeat.openapi.yaml
contracts/cloud-agent-api/README.md
internal/modules/cloudagent/registry.go
internal/modules/cloudagent/registry_test.go
internal/modules/cloudagent/routes.go
internal/app/app.go
```

Commands:

```text
go test ./...
curl -X POST /api/v1/cloud-agent/agents/register
curl -X POST /api/v1/cloud-agent/agents/agent-local-1/heartbeat
curl /api/v1/cloud-agent/agents/agent-local-1
```

## Expected

- Cloud tests pass.
- Register returns an online Agent node.
- Heartbeat updates Agent liveness and status.
- Get returns the current Agent node.

## Actual

```text
ok github.com/wt-media/wt-media-cloud/internal/modules/cloudagent
```

Register response:

```json
{"data":{"agent_id":"agent-local-1","mode":"local","version":"0.1.0","contract_major_version":"v1","contract_revision":"2026.07.14.2","status":"online","capabilities":["noop"]}}
```

Heartbeat/get response:

```json
{"data":{"agent_id":"agent-local-1","mode":"local","version":"0.1.0","contract_major_version":"v1","contract_revision":"2026.07.14.2","status":"draining","capabilities":["noop"]}}
```

## Follow-Up

- Commit Cloud provider slice.
- Implement Agent registration/heartbeat client.
