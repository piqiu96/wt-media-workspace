# Evidence: Cloud Task Store

- CHG: `CHG-20260714-010`
- Task: `T-02`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Purpose

Prove that Cloud can create `noop_task` records idempotently and allow only one Agent to hold a valid task lease.

## Method

Files added or updated in `wt-media-cloud`:

```text
contracts/cloud-agent-api/v1/task-lease.openapi.yaml
contracts/cloud-agent-api/README.md
contracts/cloud-agent-api/v1/compatibility.openapi.yaml
internal/modules/cloudagent/task_store.go
internal/modules/cloudagent/task_store_test.go
internal/modules/cloudagent/routes.go
internal/app/app.go
```

Commands:

```text
go test ./...
curl -X POST /api/v1/tasks/noop
curl -X POST /api/v1/cloud-agent/tasks/claim
```

## Expected

- Idempotent create returns the same task for the same idempotency key.
- First Agent can claim a pending task.
- Same Agent can retry claim while lease is valid.
- Different Agent cannot claim the same valid lease.

## Actual

```text
ok github.com/wt-media/wt-media-cloud/internal/modules/cloudagent
```

HTTP results:

```text
POST /api/v1/tasks/noop -> 200 pending noop_task
POST /api/v1/cloud-agent/tasks/claim agent-local-1 -> 200 leased
POST /api/v1/cloud-agent/tasks/claim agent-local-2 -> 409 no_pending_task
```

## Follow-Up

- Commit Cloud task slice.
- Add Agent task claim client method.
