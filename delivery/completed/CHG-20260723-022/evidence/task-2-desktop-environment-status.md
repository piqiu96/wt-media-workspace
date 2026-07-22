# Task 2 Evidence: Desktop环境状态投影

## 1. Scope

Task 2 implements the minimal Desktop environment projection required before later local sensitive operations:

- Local Agent `/api/v1/status` includes allow-listed runtime environment facts;
- Desktop Tauri status command can deserialize and return those facts;
- Desktop Agent status page displays Cloud login, Local Agent, BitBrowser, `main_user_id`, runtime facts, and a user-facing executable/trust conclusion.

It does not bind `main_user_id`, apply Profile scan results, or block sensitive entries. Those remain Task 3 and Task 4.

## 2. Implementation facts

Changed files:

- `wt-media-agent/src/wt_media_agent/local_api/server.py`
- `wt-media-agent/tests/test_app.py`
- `wt-media-desktop/src-tauri/src/main.rs`
- `wt-media-cloud/web/src/apps/desktop/features/local-agent/service.js`
- `wt-media-cloud/web/src/apps/desktop/features/local-agent/store.js`
- `wt-media-cloud/web/src/apps/desktop/features/local-agent/init.js`
- `wt-media-cloud/web/src/apps/desktop/features/local-agent/local-agent-status.js`
- `wt-media-cloud/web/src/apps/desktop/features/local-agent/AgentStatusPage.vue`

Behavior:

- Agent status merges `RuntimeEnvironmentCollector` output, including `bitbrowser_status` and, when safely available, `main_user_id`.
- Desktop status can display:
  - Cloud登录；
  - Local Agent运行状态；
  - BitBrowser状态；
  - 主账号ID；
  - OS/CPU/Agent版本；
  - 可执行结论和恢复原因。

## 3. Automated verification

Command:

```text
PYTHONPATH=/Users/aqiuye/Develop/workspace/wt-media/wt-media-agent/src python3 -m unittest tests.test_app tests.test_runtime_environment tests.test_local_state
```

Result:

```text
Ran 9 tests in 0.338s
OK
```

Command:

```text
npm run test
```

Result:

```text
Test Files  5 passed (5)
Tests       14 passed (14)
```

Command:

```text
cargo test
```

Result:

```text
running 2 tests
test local_agent::tests::binding_ticket_is_moved_once_and_only_facts_return ... ok
test local_agent::tests::empty_binding_ticket_is_rejected_before_transport ... ok
test result: ok. 2 passed
```

Note:

Desktop Rust tests pass with pre-existing warning noise in the Tauri shell scaffold.

## 4. Real environment verification status

Task 2 does not replace the A2 final real environment acceptance. A real Desktop + Local Agent + BitBrowser verification is still required in `task-5-m2-a2-acceptance.md`.

Result: PASS for implementation and automated verification; real BitBrowser display remains pending for A2 final acceptance.

