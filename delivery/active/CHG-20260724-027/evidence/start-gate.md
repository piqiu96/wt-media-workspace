# Task 1 Start Gate 与现状审计

## Command / manual action

- Read active context, `delivery/LEDGER.md`, `delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`, and `CHG-20260724-027/change.md`.
- Audited media account, browser profile, user/game/team, Cloud Web, and Desktop Web code paths.

## Expected result

- Confirm one active CHG and one M2-B3 scope.
- Identify the earliest unproven B3 closure before changing runtime code.
- Confirm CHG-027 does not include account check, Cookie, proxy, or BitBrowser operations.

## Actual result

- Active CHG is `CHG-20260724-027`.
- Current B3 scope is media account ledger and Cloud Profile binding only.
- Existing reusable backend:
  - `internal/modules/mediaaccount/service.go`
  - `internal/modules/mediaaccount/routes.go`
  - `internal/modules/mediaaccount/store_mysql.go`
  - `internal/modules/profilebinding/store_mysql.go`
  - `web/src/shared/api/mediaAccounts.js`
  - `web/src/modules/accounts/pages/AccountsPage.vue`
- Existing backend already supports basic account creation, list, tags, status update, manual identify, cookie export, account check task creation, cookie read task creation, and bind profile.
- Gaps against CHG-027:
  - no explicit unbind or换绑语义;
  - bind does not reset login status to `unknown`;
  - disabled/retired account binding restrictions are incomplete;
  - list filters do not cover search, business status, or login status;
  - API does not expose account remark;
  - Cloud/Desktop account page has no Profile binding UI;
  - page still exposes check/Cookie/identify-style operations that belong to later B4/D flows;
  - frontend sends `businessStatus` but backend expects `business_status`, so business status filter is ineffective.

## Status

PASS

## Next

Proceed to Task 2: backend binding rules and API convergence.
