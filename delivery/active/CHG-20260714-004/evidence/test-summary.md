# Evidence: Test Summary

- CHG: `CHG-20260714-004`
- Task: `T-04`
- Date: 2026-07-14
- Type: command
- Status: PASS_WITH_ENVIRONMENT_LIMITATIONS

## Cloud

Command:

```text
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./...
```

Result:

```text
github.com/cloudwego/netpoll@v0.7.3 ... undefined: unsafe.String
github.com/cloudwego/netpoll@v0.7.3 ... undefined: unsafe.SliceData
github.com/cloudwego/netpoll@v0.7.3 ... undefined: unsafe.StringData
note: module requires Go 1.20
ok github.com/wt-media/wt-media-cloud/internal/infra/config (cached)
```

Command:

```text
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/infra/config
```

Result:

```text
ok github.com/wt-media/wt-media-cloud/internal/infra/config (cached)
```

Rejected command variant:

```text
env GOCACHE=... GOMODCACHE=... go test ./...
```

Result:

```text
go: downloading github.com/cloudwego/hertz v0.10.5
lookup goproxy.cn: no such host
```

Interpretation:

- This CHG explicitly does not fetch dependencies, so no network escalation was requested.
- The valid local verification uses existing module cache with repository-local `GOCACHE`.

Interpretation:

- Cloud skeleton config tests pass.
- Full Cloud test is blocked by local Go `1.19.9`; the architecture baseline requires Go + Hertz, and Hertz currently requires Go >= 1.20.
- This CHG keeps the architecture target and records the toolchain requirement instead of replacing Hertz with stdlib HTTP.

## Agent

Command:

```text
python3 -m unittest discover -s tests
```

Result:

```text
Ran 2 tests in 0.000s
OK
```

## Desktop

Command:

```text
npm test
```

Result:

```text
No desktop tests yet
```

Command:

```text
cargo test
```

Result:

```text
zsh:1: command not found: cargo
```

Interpretation:

- Desktop npm scaffold script runs.
- Rust verification requires Rust/Cargo to be installed in the local environment; no dependency fetch or toolchain install was performed in this scaffold-only CHG.

## Workspace

Command:

```text
python3 -m unittest discover -s tests
```

Result:

```text
Ran 3 tests in 0.028s
OK
```

Command:

```text
python3 scripts/verify_skills.py
```

Result:

```text
verified 8 skill source files
```

Command:

```text
python3 scripts/sync_skills.py check --repo cloud
python3 scripts/sync_skills.py check --repo agent
python3 scripts/sync_skills.py check --repo desktop
```

Result:

```text
skill outputs are up to date
```

## Scope Scan

Commands:

```text
rg -n "identity|account|agent.register|task.claim|publication|Bilibili|Baijiahao|Douyin|Profile|LocalAgent|localAgent" README.md AGENTS.md cmd internal contracts migrations web
rg -n "Bilibili|Baijiahao|Douyin|publication|interaction|discovery|TaskRunner|cloud_client|task polling|result upload|Platform adapters" README.md AGENTS.md src contracts tests
rg -n "localAgent|LocalAgent|AgentController|HTTP/SSE proxy|task progress|Agent status|publication|interaction" README.md AGENTS.md src src-tauri contracts.lock.json
```

Result:

```text
Only explanatory future-scope exclusions were found.
```

## Follow-Up

- M0-C3 or M0-C4 must run Cloud tests with Go >= 1.20 and Desktop Rust tests with Cargo available.
