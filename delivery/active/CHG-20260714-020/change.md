# CHG-20260714-020: M2-C6 用户账号运行环境综合验收

## 1. Basic Information

- Level: M
- Status: DONE
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`
  - `wt-media-agent`
  - `wt-media-desktop`

## 2. Change Goal

完成 M2 用户、媒体账号、BitBrowser Profile、Agent 节点、运行环境和敏感任务锁的真实跨端验收；补齐 Desktop 一次性绑定票据传递边界和可重复的验收工具。真实依赖缺失时明确阻塞，不用 mock 冒充真实证据。

## 3. Baselines

- M2 C1-C5 stable code/contracts and CHG evidence reflected in Workspace baselines.
- Product: user/account core acceptance in `第三章_用户与账号管理.md` 3.7.4.
- Product: local environment checks and Agent security in `第二章_系统架构.md` 2.6.4, 2.10.4-2.10.5.
- Engineering: real cross-end verification and concurrency rules in architecture 2.7-2.8.

## 4. Scope

### Add/Verify

- Desktop-owned bridge method that accepts a one-use Cloud binding ticket and passes it to the Local Agent without exposing the HttpOnly session Cookie or persisting the ticket.
- Cross-repo contract locks and deterministic C6 verifier for Cloud/Agent/Desktop revisions.
- Real MySQL migration/bootstrap/login/media account/Profile scan confirmation/node binding/runtime presence/sensitive permit flow.
- Real BitBrowser full Profile scan and owner consistency when the installed local dependency is available.
- Concurrent preflight waiting and expired-lock review behavior against real MySQL.
- Full regression, health, security and dirty-tree gates across four repositories.

### Explicitly Not Doing

- Fabricating real MySQL/BitBrowser evidence with mocks.
- Platform publication/interaction executors, proxy/CK mutation, packaging, or deployment.
- Persisting the binding ticket, node credential, permit credential, Cookie, proxy secret, or local path in Desktop state/logs.

## 5. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Automated/unit/sqlmock evidence and real dependency evidence are recorded separately; only the latter satisfies the real integration gate. | CONFIRMED |
| D-02 | Desktop transports a one-use binding ticket through its native command boundary and immediately forgets it; Vue never receives the HttpOnly Cloud session Cookie. | CONFIRMED |
| D-03 | Docker may be used for isolated MySQL only if the local daemon is available and the environment permits it; no dependency download is silently substituted. | CONFIRMED |
| D-04 | Missing BitBrowser installation/login/Profile data is a genuine external blocker for that acceptance row, not a reason to weaken identity checks. | CONFIRMED |
| D-05 | User authorization permits all safe in-scope C6 work without stepwise approval, but cannot override tool quota or absent external dependencies. | CONFIRMED |
| D-06 | BitBrowser `mainUserId` is the root/main account identity; BitBrowser `userId` is Profile/sub-account identity. Multiple Profile `userId` values are valid when all Profiles share one non-empty `mainUserId`. | CONFIRMED |

## 6. Tasks

| Task | Goal | Status |
|---|---|---|
| T-01 | Activate C6, inventory real dependencies and current repo state. | DONE |
| T-02 | Implement/test Desktop one-use binding bridge and contract locks. | DONE |
| T-03 | Add deterministic cross-repo C6 verifier and execute full automated matrix. | DONE |
| T-04 | Execute real MySQL and BitBrowser integration matrix where dependencies exist. | DONE |
| T-05 | Resolve findings, record evidence, close the C1-C6 foundation acceptance only if all mandatory real gates pass. | DONE |

## 7. Acceptance Matrix

| AC | Requirement | Status |
|---|---|---|
| AC-01 | C1-C5 automated/full contract/security gates pass from clean independent repositories. | PASS |
| AC-02 | Desktop passes one-use binding ticket through native boundary without session/secret persistence. | PASS |
| AC-03 | Real MySQL migrations and end-to-end Cloud state transitions pass. | PASS |
| AC-04 | Real BitBrowser scan proves full-list uniform main account and secret-free payload. | PASS |
| AC-05 | Real concurrency shows one grant/one waiting and expired uncertain permit becomes review-required. | PASS |
| AC-06 | Final M2 baselines/contracts/releases agree and no blocking limitation remains. | PASS |

## 8. Current Checkpoint

Completed:
- C1-C5 implemented and closed.
- Docker CLI exists; Docker Desktop daemon can be reached with host permission, but no MySQL 8-compatible local image exists and no image pull was attempted.
- Local MySQL at `127.0.0.1:3306` is reachable through the Cloud Go MySQL driver. Database `wt-media-cloud` was created/reset, all five M2 migrations applied, and 14 tables exist.
- Real MySQL initially exposed a migration incompatibility; Cloud commit `7147b37 fix: align m2 mysql migration constraints` aligned M2 string FK collations and Profile FK length.
- Cloud API real run against `wt-media-cloud` passed health, single-active-session, three-role boundaries, media account, Profile confirm/bind, one-use node binding, runtime report, concurrent sensitive permit, renewal/finish, and expired-permit review checks.
- BitBrowser real data showed 37 Profiles under one `mainUserId` and 2 distinct Profile/sub-account `userId` values. User confirmed this reflects the main/sub-account permission tree, so `mainUserId` is now the authoritative BitBrowser root identity while `userId` is retained as `profile_user_id` audit metadata.
- `users.bit_main_user_id` is indexed but not unique, so multiple Cloud users/operators may share one BitBrowser main account tree while Cloud Profile assignment continues to isolate operations.
- Agent, Cloud, contracts, product docs, ADR-0002, release matrix, and Desktop contract lock were updated to use `main_user_id` plus `profile_user_id`; old `owner_user_id` remains only as historical ADR context.
- Desktop contract locks and ephemeral `local_agent_bind_session` boundary pass `npm run verify`; node/permit credentials are excluded from Vue response/state.
- Rust native boundary moves the ticket once into `BindingTransport`; its return type contains only non-secret node facts.
- Fresh 2026-07-14T12:53:18Z execution: Workspace M2 static verifier, seven Workspace tests, Cloud Go/vet, Agent 38 tests with repo `.venv`, and Desktop verification pass.
- Fresh 2026-07-14 local regression after identity remap:
  - `wt-media-cloud`: `GOCACHE=$PWD/.cache/go-build go test ./...` PASS.
  - `wt-media-cloud`: `GOCACHE=$PWD/.cache/go-build go vet ./...` PASS.
  - `wt-media-agent`: `.venv/bin/python -m unittest discover -s tests` PASS, 39 tests.
  - `wt-media-cloud/web`: `npm test -- --run` PASS, 8 tests.
  - `wt-media-workspace`: `python3 scripts/verify_m0_config.py`, `python3 -m unittest discover -s tests`, and `python3 scripts/verify_m2_acceptance.py` PASS.
  - `wt-media-desktop`: `npm run verify` PASS.
- Fresh 2026-07-14T23:11+08:00 effect run:
  - Cloud/Agent/Web/Desktop/Workspace automated checks still PASS.
  - Local MySQL `wt-media-cloud` is reachable and has 14 tables, but its current schema still contains old `owner_user_id`, `bit_owner_user_id`, and `reported_owner_user_id` columns plus `uq_users_bit_owner_user_id`; it has not yet been reset/re-migrated to the new `main_user_id`/`profile_user_id` schema.
  - Cloud API starts against local MySQL and `/api/v1/health` returns `{"status":"ok"}`; `/api/v1/cloud-agent/compatibility` returns contract revision `2026.07.14.7`.
  - Runtime environment collection reports macOS/arm64, writable workdir, normal disk, FFmpeg not installed, and `bitbrowser_status=unreachable`.
  - Real BitBrowser AC-04 rerun remains blocked because `127.0.0.1:8899` returns connection refused.
- Fresh 2026-07-14T15:22:15Z real remap rerun:
  - Local MySQL `wt-media-cloud` was reset and all five M2 migrations were re-applied; 14 tables exist.
  - Schema now exposes `bit_main_user_id`, `main_user_id`, `profile_user_id`, and `reported_main_user_id`; `users.idx_users_bit_main_user_id` is non-unique, while `browser_profiles.uq_browser_profiles_bit_profile` remains unique.
  - Real Cloud/MySQL C6 verifier PASS: health, single-active session, three roles, role boundaries, media account, Profile confirm/bind, one-use node binding, runtime report, concurrent permit, and expired-permit review.
  - BitBrowser Local API port confirmed as project default `127.0.0.1:54345`; `127.0.0.1:8899` is not the active/default BitBrowser port.
  - Real BitBrowser scan PASS: 37 Profiles, one `mainUserId`, two `profile_user_id` values allowed under the same main account, and secret-free payload keys only.
  - Runtime environment collection now reports `bitbrowser_status=normal` with the confirmed `main_user_id` and 37 Profile IDs.
- Fresh 2026-07-14T15:27:27Z manual acceptance services:
  - Cloud API is running on `127.0.0.1:18080` with local MySQL `wt-media-cloud`; `/api/v1/health` and `/api/v1/cloud-agent/compatibility` pass.
  - Local Agent API is running on `127.0.0.1:8765` with `WT_MEDIA_BITBROWSER_API_URL=http://127.0.0.1:54345`; `/healthz` passes and real BitBrowser Profile scan returns the new `main_user_id` / `profile_user_id` payload.
  - Web dev server is running on `127.0.0.1:5173`.
  - Current Web dev config has no Vite `/api` proxy, so page-origin API calls from `5173` will not reach Cloud `18080` unless a dev proxy is added or acceptance uses direct Cloud API calls.
- Fresh 2026-07-14T15:33:36Z manual UI proxy:
  - Web Vite dev server now proxies `/api` to `http://127.0.0.1:18080`.
  - `POST http://127.0.0.1:5173/api/v1/auth/login` with the local acceptance technician account returns HTTP 200 without printing Cookie/header/body material.
  - `wt-media-cloud/web`: `npm test -- --run` PASS, 8 tests.
- Fresh 2026-07-14T15:44:40Z repeated-login hardening:
  - Cloud login endpoint is idempotent when a request already has a valid session for the same username; it returns the current user without creating a replacement session.
  - Missing-cookie or different-user login still follows the existing single-active-session rule.
  - `wt-media-cloud`: `go test ./internal/modules/identity ./internal/app` PASS.
  - `wt-media-cloud`: `go test ./...` PASS.
  - Manual status-code check through Web proxy: `first_login=200 repeat_login=200 me_after_repeat=200`.
- Fresh 2026-07-15 final closure verification:
  - Workspace config verification, 7 unit tests, and M2 static cross-repository acceptance matrix PASS.
  - Cloud full `go test ./...` and `go vet ./...` PASS; Web Vitest 8/8 PASS.
  - Agent unittest 39/39 PASS; Desktop `npm run verify` PASS.
  - Final diff checks PASS with no whitespace errors or files outside the C6 identity/runtime/manual-acceptance scope.
  - Independent runtime commits: Cloud `dd40878`, `0abe85e`, `be819a8`; Agent `f3aa990`; Desktop `5af392e`.

Current:
- CHG-020 original C6 scope is complete. It proves the M2 C1-C6 foundation but does not claim that the full user/account product domain is complete.

Next:
- Remove this completed record from the Active Ledger when the independently approved product/Master Plan alignment CHG is activated.

Blocked:
- None.

## 9. DONE Gate

- [x] All acceptance rows PASS with real evidence where required.
- [x] Full four-repository regression passes.
- [x] No secret persistence/logging.
- [x] Stable baselines and release matrix finalized.
- [x] Repositories committed independently.
