# Test Evidence

## Cloud

```text
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build GOPATH=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-path go test ./internal/app ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/profileguard ./internal/modules/runtimebinding
```

Result: PASS.

## Agent

```text
PYTHONPATH=src python3 -m unittest discover -s tests
```

Result: PASS. 53 tests.

Note: `uv run pytest ...` could not run because `pytest` is not installed in the current Agent environment, so the existing `unittest` runner was used.

## Desktop

```text
cargo test
```

Result: PASS. 5 tests.

## Web

```text
npm --prefix web test -- --run mediaAccounts localAgentService
npm --prefix web run build:cloud
npm --prefix web run build:desktop
```

Result: PASS.

## Manual Verification Required

User still needs to validate with real Desktop + Local Agent + BitBrowser:

1. Login as ordinary operator in Desktop.
2. Confirm trusted local node is bound.
3. Open a media account already bound to an authorized browser window.
4. Click `检查账号`.
5. Confirm Cloud account detail/list show the returned platform UID, login status, and last checked time.
6. Confirm Cloud Web does not show the local check entry.
