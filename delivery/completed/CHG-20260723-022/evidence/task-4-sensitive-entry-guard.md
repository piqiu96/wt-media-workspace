# Task 4 Evidence: 本地敏感入口阻断

## 1. Implementation facts

- Cloud `runtimebinding.Service` added `CheckLocalTrust(userID, nodeID)`.
- MySQL trust check requires all of the following before a local sensitive entry can create work:
  - target Local Agent node belongs to the current Cloud user;
  - node is `local` and `online`;
  - node heartbeat is fresh;
  - bound Cloud session is still active;
  - user is enabled;
  - user has confirmed `bit_main_user_id`;
  - node reports `bitbrowser_status = normal`;
  - node `reported_main_user_id` matches the user's confirmed `bit_main_user_id`.
- Cloud Profile local sensitive entries now call the trust check before creating a task:
  - `POST /api/v1/browser-profiles`
  - `POST /api/v1/browser-profiles/:id/open`
  - `POST /api/v1/browser-profiles/:id/close`
  - `PATCH /api/v1/browser-profiles/:id`
- If trust fails, Cloud returns a visible business error and creates no task.
- `node_id` is used only for preflight trust checking and is removed from task payload before task creation.
- Local Agent status now projects non-secret `node_id`.
- Desktop/Tauri and Web local-agent state accept and project non-secret `node_id`.
- Web Profile operations can send `node_id`; if Desktop/Agent does not provide it, Cloud blocks the operation.

## 2. Automated verification

Command:

```text
gofmt -w internal/modules/profilebinding/routes.go internal/modules/runtimebinding/service.go \
internal/modules/runtimebinding/store_mysql.go internal/modules/runtimebinding/service_test.go \
internal/modules/profilebinding/routes_test.go internal/app/app.go &&
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

Note: Desktop cargo test passed with pre-existing unused-code warnings.

## 3. Real MySQL + Cloud API verification

Environment:

- MySQL database: `wt_media_m2_a2_task4_acceptance`
- Cloud: `127.0.0.1:18080`
- Initial admin: `m2a2_guard_admin`

### Case A: missing node_id is blocked

Request:

```text
POST /api/v1/browser-profiles
payload = {"name":"Should Block"}
```

Actual API result:

```text
errcode = 10001
message = 本地敏感操作请求缺少可信节点
```

Database actual result:

```text
tasks_after_missing_node = 0
```

### Case B: trusted node can create one task

Setup:

- Confirmed user's `bit_main_user_id = task4-main-user`.
- Inserted Local Agent node `node-task4-trusted`:
  - `status = online`
  - `mode = local`
  - bound to the current active session
  - `bitbrowser_status = normal`
  - `reported_main_user_id = task4-main-user`
  - fresh heartbeat

Request:

```text
POST /api/v1/browser-profiles
payload = {"name":"Trusted Create","node_id":"node-task4-trusted"}
```

Actual API result:

```text
errcode = 0
task_type = profile_create_task
status = pending
payload = {"name":"Trusted Create"}
```

Database actual result:

```text
tasks_after_trusted_node = 1
node_id_in_payload = NULL
```

### Case C: BitBrowser unavailable is blocked

Setup:

```text
local_agent_nodes.bitbrowser_status = unreachable
```

Request:

```text
POST /api/v1/browser-profiles
payload = {"name":"Should Block Again","node_id":"node-task4-trusted"}
```

Actual API result:

```text
errcode = 23003
message = 当前Desktop、Local Agent或BitBrowser身份不可信，已阻止本地敏感操作
```

Database actual result:

```text
tasks_after_untrusted_bitbrowser = 1
```

No new task was created after the trusted-node case.

## 4. Status

PASS.

Task 4 now satisfies the M2-A2 boundary:

```text
M2本地敏感入口统一检查当前Cloud用户、本机节点、会话、BitBrowser状态和main_user_id匹配；
不可信时用户可见阻断；
阻断时不创建任务、不产生外部副作用。
```
