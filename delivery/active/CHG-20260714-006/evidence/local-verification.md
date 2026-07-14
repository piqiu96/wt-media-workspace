# Evidence: Local Verification

- CHG: `CHG-20260714-006`
- Task: `T-04`
- Date: 2026-07-14
- Type: command
- Status: PASS

## Toolchain Facts

```text
python3 --version
Python 3.9.6

python3.12 --version
zsh:1: command not found: python3.12

/Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go version
go version go1.26.5 darwin/arm64

node --version
v25.9.0

npm --version
11.12.1

cargo --version
zsh:1: command not found: cargo
```

Interpretation:

- CI is the formal Python 3.12 check for Agent/Workspace.
- Local Cloud verification uses the explicit Go 1.26.5 path.
- Desktop M0 verification does not require Cargo.

## Local Commands

```text
python3 scripts/verify_m0_config.py
python3 -m unittest discover -s tests
python3 scripts/verify_skills.py
env GOROOT=... GOPATH=... GO_BIN=... scripts/verify-health.sh
scripts/verify-health.sh
npm run verify
scripts/verify_m0_local.sh
```

## Results

```text
M0 config verification ok
Ran 5 tests in 0.023s
OK
verified 8 skill source files
wt-media-cloud health ok
wt-media-agent health ok
wt-media-desktop health ok
WT Media M0 local verification ok
```

## Sandbox Notes

- Cloud and Agent health scripts need local port binding.
- In this Codex sandbox, port binding required elevated execution.
- The first unified script run exposed an old ambient `GOROOT=.../go19/go`; scripts were updated so explicit Go 1.26 paths set the matching `GOROOT`.
