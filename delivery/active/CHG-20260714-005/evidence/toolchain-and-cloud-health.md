# Evidence: Toolchain And Cloud Health

- CHG: `CHG-20260714-005`
- Task: `T-02`
- Date: 2026-07-14
- Type: command
- Status: PASS

## Toolchain Facts

Command:

```text
go version
```

Result:

```text
go version go1.19.9 darwin/amd64
```

Command:

```text
/Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go version
```

Result:

```text
go version go1.26.5 darwin/arm64
```

Interpretation:

- Go 1.26.5 exists on disk.
- The current Codex shell still resolves bare `go` to `devenv/go19`.
- CHG-005 uses explicit `GO_BIN`/`GOROOT` for Cloud verification and leaves PATH normalization to a later M0 toolchain CHG.

## Cloud Test

Command:

```text
env GOROOT=/Users/aqiuye/Develop/workspace/devenv/go26/go GOPATH=/Users/aqiuye/Develop/workspace/devenv/go19/gopath GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build /Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go test ./...
```

Result:

```text
?   	github.com/wt-media/wt-media-cloud/cmd/server	[no test files]
?   	github.com/wt-media/wt-media-cloud/internal/app	[no test files]
?   	github.com/wt-media/wt-media-cloud/internal/common	[no test files]
ok  	github.com/wt-media/wt-media-cloud/internal/infra/config
?   	github.com/wt-media/wt-media-cloud/internal/infra/database	[no test files]
?   	github.com/wt-media/wt-media-cloud/internal/infra/logger	[no test files]
?   	github.com/wt-media/wt-media-cloud/internal/infra/objectstore	[no test files]
?   	github.com/wt-media/wt-media-cloud/internal/infra/scheduler	[no test files]
?   	github.com/wt-media/wt-media-cloud/internal/middleware	[no test files]
```

## Cloud Health Script

Added:

```text
wt-media-cloud/scripts/verify-health.sh
```

Command:

```text
env GOROOT=/Users/aqiuye/Develop/workspace/devenv/go26/go GOPATH=/Users/aqiuye/Develop/workspace/devenv/go19/gopath GO_BIN=/Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build WT_MEDIA_CLOUD_HTTP_ADDR=127.0.0.1:18080 scripts/verify-health.sh
```

Result:

```text
wt-media-cloud health ok
```

Manual endpoint checks before the script was added:

```text
curl --silent --show-error --fail http://127.0.0.1:18080/healthz
ok

curl --silent --show-error --fail http://127.0.0.1:18080/api/v1/health
{"data":{"status":"ok"}}
```

Sandbox note:

- Starting the local Cloud HTTP service without elevated execution failed with `bind: operation not permitted`.
- Elevated execution was required only for binding a local M0 health port.
