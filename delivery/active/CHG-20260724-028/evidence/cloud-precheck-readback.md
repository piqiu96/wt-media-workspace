# Cloud Precheck / Readback Evidence

## Command / Action

Implemented and tested:

- `POST /api/v1/media-accounts/:account_id/check`
- `POST /api/v1/media-accounts/:account_id/check/result`
- `mediaaccount.Service.StartLocalAccountCheck`
- `mediaaccount.Service.ApplyLocalAccountCheckResult`

## Expected

- Cloud performs permission, account, profile, business-status, and local-node precheck only.
- Cloud creates a `profileguard` sensitive operation authorization for `authenticated_account_check`.
- Cloud does not call Local Agent or BitBrowser.
- Result writeback updates platform UID, name, avatar, login status, and last checked time.
- Account mismatch / duplicate is a business result, not a technical API failure.

## Actual

- Cloud check start requires ordinary operator ownership, enabled media account, bound active profile, and a non-empty local node id.
- Cloud creates `profileguard.SensitiveTask` with operation `authenticated_account_check`.
- Cloud returns `task_id`, `browser_profile_id`, `bit_profile_id`, platform, and expected platform account id for Desktop execution.
- Result writeback updates account facts.
- Duplicate identity is saved as `identification_status=duplicate` and `login_status=account_mismatch` without returning an API error.

## Verification

```text
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build GOPATH=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-path go test ./internal/app ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/profileguard ./internal/modules/runtimebinding
```

Result:

```text
ok github.com/wt-media/wt-media-cloud/internal/app
ok github.com/wt-media/wt-media-cloud/internal/modules/mediaaccount
ok github.com/wt-media/wt-media-cloud/internal/modules/profilebinding
ok github.com/wt-media/wt-media-cloud/internal/modules/profileguard
ok github.com/wt-media/wt-media-cloud/internal/modules/runtimebinding
```

## Result

PASS.
