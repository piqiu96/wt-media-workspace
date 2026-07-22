# Task 3 Evidence: BitBrowser主账号身份扫描

## 1. Decision

User confirmed Q-01:

```text
新增一个 A2-only 的主账号确认 API，只绑定/验证 main_user_id；
现有 Profile Diff 应用保留到 M2-B。
```

## 2. Implementation facts

- Cloud added an identity-only confirmation path:
  - `POST /api/v1/bit-browser/profile-scans/:scan_id/confirm-main-identity`
  - `profilebinding.Service.ConfirmMainIdentity`
  - `profilebinding.Store.ConfirmMainIdentity`
- The existing `ConfirmScan` path is preserved for M2-B Profile Diff application.
- The new identity-only confirmation updates only:
  - `users.bit_main_user_id`
  - `users.bit_account_status`
  - `users.bit_account_bound_at`
  - `users.bit_account_last_verified_at`
  - `profile_sync_scans.status`
  - `profile_sync_scans.confirmed_at`
  - identity audit log
- It does not create, update, or mark missing formal `browser_profiles`.
- Web Profile scan drawer now exposes two separate actions:
  - `仅确认主账号`
  - `确认同步窗口`

## 3. Automated verification

Command:

```text
gofmt -w internal/modules/profilebinding/store_mysql_test.go &&
GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build \
go test ./internal/modules/profilebinding ./internal/modules/identity
```

Actual result:

```text
ok  	github.com/wt-media/wt-media-cloud/internal/modules/profilebinding	1.834s
ok  	github.com/wt-media/wt-media-cloud/internal/modules/identity	(cached)
```

Command:

```text
npm run test
```

Actual result:

```text
Test Files  5 passed
Tests       14 passed
```

## 4. Real MySQL + Cloud API verification

Environment:

- MySQL database: `wt_media_m2_a2_acceptance`
- Cloud: `127.0.0.1:18080`
- Initial admin: `m2a2_admin`

Steps:

1. Applied Cloud migrations to the dedicated acceptance database.
2. Started Cloud against the real MySQL database.
3. Logged in as `m2a2_admin`.
4. Submitted a Profile scan with:
   - `main_user_id = m2a2-main-real`
   - `bit_profile_id = m2a2-profile-should-not-apply`
5. Called:

```text
POST /api/v1/bit-browser/profile-scans/profile_scan_a21cce01cc0d800d0fc7d721/confirm-main-identity
```

API actual result:

```text
errcode = 0
scan.status = confirmed
confirmed_at is present
```

Database actual result:

```text
users.bit_main_user_id = m2a2-main-real
users.bit_account_status = bound
profile_sync_scans.status = confirmed
browser_profiles rows for bit_profile_id m2a2-profile-should-not-apply = 0
```

## 5. Status

PASS.

Task 3 now satisfies the M2-A2 boundary:

```text
用户通过真实扫描确认 main_user_id；
Cloud 只绑定/验证主账号身份；
Profile Diff 正式应用留到 M2-B；
本步骤不创建、不更新正式 browser_profile。
```
