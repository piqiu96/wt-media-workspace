# Task 5 Evidence: M2-A2 真实综合验收

## 1. Scope

本 Evidence 收口 `CHG-20260723-022` 的 M2-A2 综合验收：

- 登录旧会话确认/替换；
- 主账号身份只确认 `main_user_id`，不应用 Profile Diff；
- 本地敏感入口在创建任务前检查可信 Desktop/Local Agent/BitBrowser 身份；
- 阻断时不创建 task、不产生外部副作用。

M2-A2 不实现 M2-B Profile 正式同步、M2-C 代理写入、M2-D Cookie 上号或 M2-E 本机执行抽屉。

## 2. Automated verification

Command:

```text
GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build \
go test ./internal/modules/runtimebinding ./internal/modules/profilebinding ./internal/modules/profileguard ./internal/modules/identity ./internal/app
```

Actual result:

```text
ok  	github.com/wt-media/wt-media-cloud/internal/modules/runtimebinding
ok  	github.com/wt-media/wt-media-cloud/internal/modules/profilebinding
ok  	github.com/wt-media/wt-media-cloud/internal/modules/profileguard
ok  	github.com/wt-media/wt-media-cloud/internal/modules/identity
ok  	github.com/wt-media/wt-media-cloud/internal/app
```

Command:

```text
npm run test
```

Actual result:

```text
Test Files  5 passed
Tests       15 passed
```

Command:

```text
PYTHONPATH=/Users/aqiuye/Develop/workspace/wt-media/wt-media-agent/src \
python3 -m unittest tests.test_app tests.test_runtime_environment tests.test_local_state
```

Actual result:

```text
Ran 10 tests
OK
```

Command:

```text
cargo test
```

Actual result:

```text
2 passed
```

Note:

Desktop cargo test passed with pre-existing unused-code warnings.

## 3. Real MySQL + Cloud API comprehensive verification

Environment:

- MySQL database: `wt_media_m2_a2_task5_acceptance`
- Cloud: `127.0.0.1:18080`
- Initial admin: `m2a2_task5_admin`

### Case A: old session replacement confirmation

Operations:

1. Login with `replace_existing=true` to create a known old session.
2. Login again without `replace_existing`.
3. Verify response is 409 / `errcode=20010`.
4. Verify old cookie still accesses `/api/v1/auth/me`.
5. Login again with `replace_existing=true`.
6. Verify old cookie is rejected and new cookie accesses `/api/v1/auth/me`.

Actual result:

```text
login_without_replace = [409, 20010, 当前账号已在其他位置登录，请确认是否替换旧会话]
old_session_before_confirm = [200, 0]
login_with_replace = [200, 0]
old_session_after_confirm = [401, 11001, 请先登录或凭证已过期]
new_session_after_confirm = [200, 0, m2a2_task5_admin]
```

Result: PASS.

### Case B: identity-only main account confirmation

Operations:

1. Submit Profile scan:

```text
main_user_id = task5-main-real
bit_profile_id = task5-bit-profile-do-not-apply
profile_user_id = task5-profile-user
```

2. Call:

```text
POST /api/v1/bit-browser/profile-scans/:scan_id/confirm-main-identity
```

Actual result:

```text
create_profile_scan = [201, 0]
confirm_main_identity = [200, 0, confirmed]
users.bit_main_user_id = task5-main-real
browser_profiles rows for task5-bit-profile-do-not-apply = 0
```

Result: PASS.

### Case C: local sensitive entry is blocked without node_id

Operation:

```text
POST /api/v1/browser-profiles
payload = {"name":"Task5 Missing Node"}
```

Actual result:

```text
profile_create_missing_node = [400, 10001, 本地敏感操作请求缺少可信节点]
tasks before = 0
tasks after missing node = 0
```

Result: PASS.

### Case D: trusted node can create one local task

Setup:

- Confirmed user's `bit_main_user_id = task5-main-real`.
- Inserted Local Agent node `node-task5-trusted` as a real MySQL runtime fact:
  - `mode = local`
  - `status = online`
  - bound to the active session
  - `bitbrowser_status = normal`
  - `reported_main_user_id = task5-main-real`
  - fresh heartbeat

Operation:

```text
POST /api/v1/browser-profiles
payload = {"name":"Task5 Trusted Create","node_id":"node-task5-trusted"}
```

Actual result:

```text
profile_create_trusted_node = [201, 0, profile_create_task, {"name":"Task5 Trusted Create"}]
tasks after trusted node = 1
```

Result: PASS.

### Case E: BitBrowser unavailable blocks the same sensitive entry

Setup:

```text
local_agent_nodes.bitbrowser_status = unreachable
```

Operation:

```text
POST /api/v1/browser-profiles
payload = {"name":"Task5 Untrusted BitBrowser","node_id":"node-task5-trusted"}
```

Actual result:

```text
profile_create_untrusted_bitbrowser = [409, 23003, 当前Desktop、Local Agent或BitBrowser身份不可信，已阻止本地敏感操作]
tasks after untrusted BitBrowser = 1
```

No new task was created after the trusted-node case.

Result: PASS.

## 4. Real Desktop + BitBrowser visual verification

Task 2 already verified the Desktop projection implementation and automated Desktop tests.

This run did not operate the user's visible BitBrowser UI through the Desktop shell. The real external identity effects required by A2 were verified through real MySQL + Cloud API facts:

- identity confirmation persisted to `users.bit_main_user_id`;
- no formal `browser_profiles` were created by the A2-only confirmation path;
- trusted/untrusted Local Agent node facts changed Cloud sensitive-entry behavior;
- blocked sensitive operations created no tasks.

## 5. User management smoke review correction

User feedback:

```text
用户管理功能我看是空白页，你确定你成功验收功能了？
```

Root cause found:

- `用户与权限` is a Cloud management page and exists only in Cloud router `/users`;
- Desktop router intentionally does not include `/users`;
- shared `AppLayout.vue` still exposed `用户与权限` in Desktop menu, so clicking it from Desktop could navigate to a non-existent route and render a blank page;
- the local dev environment also previously had Cloud Web proxy logs pointing to `127.0.0.1:18080` while Cloud API was not yet running there, which made the current user-visible environment fail the original acceptance expectation.

Fix:

- `web/src/layout/AppLayout.vue` now filters Cloud-only `/users` from Desktop menu;
- Cloud menu keeps `用户与权限`;
- user management should be verified from Cloud Web, not Desktop Web.

Verification:

```text
Command: npm run test
Result:
  Test Files  5 passed
  Tests       15 passed

Command: curl --verbose --max-time 3 http://127.0.0.1:5173/
Result: HTTP/1.1 200 OK, Cloud Web entry served.

Command: curl --verbose --max-time 3 http://127.0.0.1:5174/
Result: HTTP/1.1 200 OK, Desktop Web entry served.

Command: login to Cloud API, then GET /api/v1/users
Result:
  login = errcode 0, user m2a2_task5_admin
  users = errcode 0, one admin user returned
```

Result: PASS for backend/API and route-scope correction. Manual UI acceptance should open Cloud Web `http://127.0.0.1:5173/users`.

During user smoke review, the Desktop environment status page exposed `当前任务` and `待回传结果`. These fields belong to later business execution / M2-E local execution projection, not to M2-A2 environment trust. They were removed from the M2-A2 status page:

```text
wt-media-cloud/web/src/apps/desktop/features/local-agent/local-agent-status.js
wt-media-cloud/web/src/apps/desktop/features/local-agent/AgentStatusPage.vue
```

Verification after the UI correction:

```text
npm run test

Test Files  5 passed
Tests       15 passed
```

During user smoke review, the topbar `退出` button was found to only navigate to `/login` without invalidating the Cloud session. Logout is part of the M2-A2 trusted session boundary, so the button was changed to call `POST /api/v1/auth/logout` through `sessionClient.logout()` before routing to `/login`.

Changed file:

```text
wt-media-cloud/web/src/layout/AppLayout.vue
```

Verification:

```text
npm run test

Test Files  5 passed
Tests       15 passed
```

Real Cloud API verification:

```text
POST /api/v1/auth/login
→ errcode = 0

POST /api/v1/auth/logout
→ errcode = 0

GET /api/v1/auth/me with the same cookie
→ HTTP 401
→ errcode = 11001
→ message = 请先登录或凭证已过期
```

Result: PASS.

Remaining visible UI smoke check before final CHG closure:

```text
Open Desktop
→ 环境状态
→ verify Cloud / Local Agent / BitBrowser / main_user_id / 可执行结论 are visible
→ Profile 创建/open/close with untrusted environment shows Chinese blocked message
```

This check requires the user's local Desktop + BitBrowser interactive environment.

## 5. Status

PASS for automated verification and real MySQL + Cloud API acceptance.

Manual Desktop + visible BitBrowser smoke check remains recommended before marking the CHG `DONE`.
