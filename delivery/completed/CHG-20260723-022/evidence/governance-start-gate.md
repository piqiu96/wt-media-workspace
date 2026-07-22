# CHG-20260723-022 Start Gate Evidence

## 1. Governance alignment

- Active CHG: `CHG-20260723-022`
- CHG status: `IN_PROGRESS`
- Current context: `.ai/CURRENT_CONTEXT.md` points to `CHG-20260723-022`
- Ledger: `delivery/LEDGER.md` points to `CHG-20260723-022`
- Milestone: `delivery/milestones/M2-account-runtime.md#m2-a-用户权限会话与运行环境可信闭环`
- Implementation plan: `docs/superpowers/plans/2026-07-23-m2-account-runtime-detailed-implementation-plan.md#chg-m2-a2确认式会话与desktop环境可信`

Result: PASS.

## 2. User-visible result required by this CHG

M2-A2 must make the local execution environment trustworthy before later M2 local operations:

- login replacement is explicit and confirmable;
- Desktop/Local Agent/BitBrowser trust status is visible;
- `main_user_id` binding comes from real BitBrowser identity scan;
- sensitive local operations are blocked when trust checks fail.

## 3. Current facts before implementation

- M2-A1 is completed and archived under `delivery/completed/CHG-20260722-021`.
- Cloud already has user/session, Local Agent binding ticket, Agent node, profile identity scan, and profile guard foundations.
- Agent already validates BitBrowser profile scans for single `main_user_id` and complete `profile_user_id`.
- Existing Cloud login behavior invalidated old sessions automatically on a fresh login.
- Existing Web login page did not ask the user to confirm replacing an old session.

## 4. Gap to CHG

- Task 1: missing explicit old-session replacement confirmation.
- Task 2: Desktop environment status projection still needs dedicated implementation.
- Task 3: `main_user_id` scan confirmation flow still needs dedicated implementation.
- Task 4: sensitive local entry guard still needs dedicated implementation.
- Task 5: real Cloud/Desktop/Agent/BitBrowser acceptance still remains for A2 as a whole.

## 5. File mapping

Task 1 session replacement:

- Cloud service: `wt-media-cloud/internal/modules/identity/service.go`
- Cloud route: `wt-media-cloud/internal/modules/identity/routes.go`
- MySQL store: `wt-media-cloud/internal/modules/identity/store_mysql.go`
- Cloud tests: `wt-media-cloud/internal/modules/identity/*_test.go`
- Web API client: `wt-media-cloud/web/src/shared/api/session.js`
- Web login page: `wt-media-cloud/web/src/modules/auth/pages/LoginPage.vue`

Later A2 tasks:

- Runtime binding: `wt-media-cloud/internal/modules/runtimebinding`
- Profile binding: `wt-media-cloud/internal/modules/profilebinding`
- Profile guard: `wt-media-cloud/internal/modules/profileguard`
- Agent BitBrowser adapter/API: `wt-media-agent/src/wt_media_agent`
- Desktop shell/status pages: `wt-media-desktop`

## 6. Dirty worktree note

The workspace was already dirty before Task 1 implementation, including unrelated Cloud proxy and generated dist changes. Task 1 only intentionally modified identity and login source/test files listed above plus this CHG evidence/checkpoint.

## 7. Test and acceptance approach

- Automated Cloud identity tests for confirmation semantics.
- Automated Web tests for front-end regressions.
- Real MySQL + Cloud API verification for cookie/session behavior.
- Browser page verification for the user-facing confirmation prompt.

