# Desktop → Rust → Local Agent Account Check Evidence

## Command / Action

Implemented:

- Local Agent synchronous endpoint `POST /api/v1/account-check`.
- Desktop Tauri command `local_agent_account_check`.
- Web Desktop local-agent service wrapper `accountCheck`.
- Local Agent OpenAPI contract entry for account check.

## Expected

- Vue does not call Local Agent dynamic port directly.
- Rust uses the stored local node credential to run Cloud sensitive preflight.
- Rust calls Local Agent only after a granted permit.
- Rust finishes the permit after the local operation.
- Local Agent returns safe identity facts only, never Cookie values.

## Actual

- Desktop Vue invokes `local_agent_account_check` through Tauri.
- Rust preflights `/api/v1/local-agent/sensitive-tasks/:task_id/preflight`.
- Rust calls Local Agent `/api/v1/account-check`.
- Rust finishes `/api/v1/local-agent/sensitive-permits/:permit_id/finish`.
- Local Agent reads cookies locally and returns only `platform_account_id`, `name`, `avatar_url`, `login_status`, and `message`.
- Bilibili UID extraction uses `DedeUserID`; cookie values such as `SESSDATA` do not leave Agent.
- Unsupported/unrecognized platform identity returns `environment_error` instead of fake success.

## Verification

```text
PYTHONPATH=src python3 -m unittest discover -s tests
```

Result:

```text
Ran 53 tests
OK
```

```text
cargo test
```

Result:

```text
running 5 tests
test result: ok. 5 passed
```

## Result

PASS.

真实 BitBrowser 账号身份读取仍需要用户在本机环境用真实窗口验收。
