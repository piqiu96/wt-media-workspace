# M0-R1 Toolchain Inventory

- Change: CHG-20260715-002
- Date: 2026-07-15

## Local Toolchains

| Tool | Command | Actual Result | Status |
|---|---|---|---|
| Go | `go version` | `go version go1.26.5 darwin/arm64` | PASS |
| Go path | `type -a go` | `/Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go` | PASS |
| Node | `node --version` | `v25.9.0` | PASS |
| npm | `npm --version` | `11.12.1` | PASS |
| System Python | `python3 --version` | `Python 3.9.6` | FAIL for Agent requirement, because Agent requires `>=3.12`. |
| Agent venv Python | `wt-media-agent/.venv/bin/python --version` | `Python 3.14.4` | PASS |
| uv | `uv --version` | `uv 0.11.7` | PASS |
| Cargo | `cargo --version` | `zsh:1: command not found: cargo` | FAIL |
| rustc | `rustc --version` | `zsh:1: command not found: rustc` | FAIL |
| mysql CLI | `mysql --version` | `zsh:1: command not found: mysql` | FAIL |

## MySQL Port Probe

Command:

```text
nc -zv 127.0.0.1 3306
```

Expected result: local MySQL port is reachable.

Actual result after local-network authorization:

```text
Connection to 127.0.0.1 port 3306 [tcp/mysql] succeeded!
```

Status: PASS for TCP reachability. MySQL CLI remains unavailable, so migration verification needs an application runner or installed client.

## Dependency Entry Points

| Repository | Entry Points | Status |
|---|---|---|
| Cloud | `go.mod`, `go.sum`, `scripts/verify-health.sh` | PASS |
| Cloud Web | `web/package.json`, `web/package-lock.json`, `web/node_modules/` present | PASS |
| Agent | `pyproject.toml`, `.venv/`, `scripts/verify-health.sh` | PARTIAL: no `uv.lock`; `.venv` has no pip. |
| Desktop | `package.json`, `Cargo.toml`, `src-tauri/Cargo.toml`, `src-tauri/tauri.conf.json` | FAIL for real Tauri build: Rust/Cargo missing and npm scripts are scaffold echoes. |

Overall status: PASS for inventory completion; M0 gate status remains IN_PROGRESS because Desktop/Rust and MySQL migration readiness are not closed.
