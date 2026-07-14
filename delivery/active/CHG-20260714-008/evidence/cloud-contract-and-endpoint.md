# Evidence: Cloud Contract And Endpoint

- CHG: `CHG-20260714-008`
- Task: `T-02`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Purpose

Prove that Cloud owns an active Cloud-Agent `v1` compatibility contract and exposes the matching runtime compatibility endpoint.

## Method

Files added or updated in `wt-media-cloud`:

```text
contracts/cloud-agent-api/v1/compatibility.openapi.yaml
contracts/cloud-agent-api/README.md
contracts/README.md
internal/modules/cloudagent/compatibility.go
internal/modules/cloudagent/compatibility_test.go
internal/app/app.go
```

Commands:

```text
env GOROOT=/Users/aqiuye/Develop/workspace/devenv/go26/go \
  GOPATH=/Users/aqiuye/Develop/workspace/devenv/go19/gopath \
  GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build \
  /Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go test ./...

curl --silent --show-error --fail \
  http://127.0.0.1:18080/api/v1/cloud-agent/compatibility
```

## Expected

- Cloud tests pass.
- Compatibility endpoint returns `cloud-agent`, `v1`, revision `2026.07.14.1`, and status `compatible`.

## Actual

```text
ok github.com/wt-media/wt-media-cloud/internal/modules/cloudagent
```

Endpoint response:

```json
{"data":{"api":"cloud-agent","major_version":"v1","contract_revision":"2026.07.14.1","minimum_agent_contract_revision":"2026.07.14.1","compatible_agent_major_versions":["v1"],"status":"compatible"}}
```

## Follow-Up

- Commit Cloud provider slice.
- Implement Agent consumer compatibility checks.
