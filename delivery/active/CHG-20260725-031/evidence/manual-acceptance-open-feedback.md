# Manual Acceptance Open Feedback Fix

Date: 2026-07-25

## Trigger

Manual acceptance reported that clicking "打开" still had no visible reaction.

## Change

- Cloud Web `ProfilesPage.vue` now shows an immediate "正在打开/关闭BitBrowser窗口" notice.
- Cloud Web blocks missing `bit_profile_id` before invoking Desktop and shows a user-visible error.
- Cloud Web disables other open/close actions while one window operation is running and shows button loading.
- Desktop `ProfileOperationArgs` now accepts both `bit_profile_id` and Tauri-style `bitProfileId` payloads.

## Verification

### Automated

- `npm test` in `wt-media-cloud/web`
  - Expected: existing Web tests pass.
  - Actual: PASS, 9 files / 33 tests.
- `npm run build` in `wt-media-cloud/web`
  - Expected: production Web build succeeds.
  - Actual: PASS. Existing large chunk warning remains.
- `cargo test` in `wt-media-desktop/src-tauri`
  - Expected: Desktop Rust tests pass, including payload compatibility.
  - Actual: PASS, 9 tests.
- `cargo build` in `wt-media-desktop/src-tauri`
  - Expected: latest Desktop debug binary is rebuilt.
  - Actual: PASS.
- `.venv/bin/python -m unittest tests.test_local_profile_operations` in `wt-media-agent`
  - Expected: Local Agent profile operation tests pass.
  - Actual: PASS, 4 tests in the active environment.

### Runtime

- Restarted latest Desktop shell from:
  - `/Users/aqiuye/Develop/workspace/wt-media/wt-media-desktop/target/debug/wt-media-desktop-shell`
  - New execution session: `1584`.
- Confirmed Desktop shell Web source:
  - `curl http://127.0.0.1:5174/`
  - Actual: PASS, Vite HTML returned `/src/apps/desktop/main.ts`.
- Confirmed Local Agent health:
  - `curl http://127.0.0.1:8765/api/v1/health`
  - Actual: PASS, status `ok`.
- Confirmed BitBrowser group read-back:
  - `POST http://127.0.0.1:8765/api/v1/bit-browser/profile-groups`
  - Actual: PASS, returned group `402880a99f4a13aa019f527f92df42d4` / `测试组`.
- Confirmed BitBrowser open operation:
  - `POST http://127.0.0.1:8765/api/v1/bit-browser/profile-open`
  - Payload: `{"id":"08c39d31efe44e598027468a2edfae34"}`
  - Actual: PASS, returned `{"data":{"status":"opened"}}`.

## Status

Ready for user to retry in the freshly restarted Desktop shell. If the UI still does not open the window, the page should now show either a loading state, a success notice, or the concrete Desktop/Agent error.
