# Manual Acceptance Open Hang Fix

Date: 2026-07-25

## Trigger

Manual acceptance screenshot showed the page stuck at `正在打开BitBrowser窗口：心怀星火`.

## Finding

The Desktop command executed the BitBrowser open/close call and then immediately performed a full profile scan before returning to Vue.

For open/close, that scan is not required to prove the external side effect. If BitBrowser is still starting the browser window or profile listing is temporarily slow, the UI remains on the running notice even after the open request succeeds.

## Change

- `local_agent_profile_open` now returns after Local Agent `/profile-open` succeeds.
- `local_agent_profile_close` now returns after Local Agent `/profile-close` succeeds.
- `ProfileOperationResult.snapshot` is optional and omitted for open/close.
- Create/restore still keep their required read-back behavior.

## Verification

- Direct Local Agent open for screenshot profile:
  - `POST http://127.0.0.1:8765/api/v1/bit-browser/profile-open`
  - Payload: `{"id":"0b2ed362e88141f38894ba221483030d"}`
  - Actual: PASS, returned `{"data":{"status":"opened"}}`.
- `cargo test` in `wt-media-desktop/src-tauri`
  - Actual: PASS, 10 tests.
- `cargo build` in `wt-media-desktop/src-tauri`
  - Actual: PASS.
- Restarted latest Desktop shell from rebuilt debug binary.
  - New execution session: `3117`.

## Status

Ready for manual retry. The page should now leave the `正在打开/关闭` state as soon as the Local Agent open/close call succeeds.
