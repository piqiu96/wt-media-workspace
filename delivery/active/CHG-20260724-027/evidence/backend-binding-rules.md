# Task 2 后端绑定规则与 API 收敛

## Command / manual action

- Added `media_accounts.remark` migration.
- Updated media account service, store, routes, and frontend API client.
- Ran backend tests and local migration.

## Expected result

- Media account ledger supports remark and server-side filters.
- Profile binding validates authorized active Cloud Profile ownership.
- Same Profile + same platform is rejected.
- Bind / unbind / rebind resets login facts to `unknown`.
- Disabled accounts cannot start new binding changes.

## Actual result

- Added migration `20260724_015_media_account_binding_fields.sql`.
- `GET /api/v1/media-accounts` accepts:
  - `search`
  - `business_status`
  - `login_status`
  - `game_id`
  - `platform`
  - tag filters
- Added `DELETE /api/v1/media-accounts/:account_id/profile` for unbind.
- `PATCH /api/v1/media-accounts/:account_id/profile` resets `login_status` to `unknown` and clears `last_checked_at` when the Profile changes.
- Existing same-user active Profile and same-Profile same-platform tests pass.
- New unbind / disabled binding / filter tests pass.
- Local migration applied to stable database `wt_media_cloud`.

## Verification

- `go test ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/identity ./internal/modules/migration`: PASS
- `scripts/migrate.sh`: PASS, applied `20260724_015_media_account_binding_fields`
- Local API smoke:
  - `POST /api/v1/auth/login` as `operator01`: PASS
  - `GET /api/v1/browser-profiles`: PASS, returned empty authorized Profile list for the current local account

## Status

PASS
