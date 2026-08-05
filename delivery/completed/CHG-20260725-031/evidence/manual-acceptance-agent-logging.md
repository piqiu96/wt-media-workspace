# Manual Acceptance Agent Logging

Date: 2026-07-25

## Trigger

Manual acceptance still showed `正在打开BitBrowser窗口` without a clear failure reason. User requested environment confirmation and Agent-side error logs.

## Environment Confirmation

- Local Agent was restarted from the current `wt-media-agent` source with:
  - `WT_MEDIA_AGENT_LOG_LEVEL=INFO`
  - `127.0.0.1:8765`
  - execution session `46283`
- Desktop shell was restarted from the current debug binary with:
  - `WT_MEDIA_DESKTOP_WEB_URL=http://127.0.0.1:5174`
  - `WT_MEDIA_DESKTOP_LOCAL_AGENT_URL=http://127.0.0.1:8765`
  - execution session `58261`
- Vite Desktop Web source is reachable at `http://127.0.0.1:5174/` and returns `/src/apps/desktop/main.ts`.

## Findings

Direct Local Agent call for screenshot row `百家号_百变小灵`:

- Profile ID: `0ab85cc0373f42eb9e804c3db20be30a`
- Command: `POST /api/v1/bit-browser/profile-open`
- First actual result: 502 with `BitBrowser Local API request failed: timed out`
- Agent log:
  - `local_api.profile_open.start profile_id=0ab85cc0373f42eb9e804c3db20be30a`
  - `local_api.profile_open.failure profile_id=0ab85cc0373f42eb9e804c3db20be30a duration_ms=5018 error=BitBrowser Local API request failed: timed out`
- Subsequent retry result: success in 5ms.

This confirms the environment is calling the real Local Agent and real BitBrowser Local API. The visible issue was not a mock or stale route; it was a BitBrowser Local API timeout that the UI did not expose clearly.

## Change

- Cloud Web open/close no longer performs a forced runtime status refresh before calling `profileOpen/profileClose`.
- Cloud Web clears the running notice on open/close failure.
- Cloud Web maps timeout errors to a concrete red error message that points to Agent logs.
- Local Agent logs status/open/close start, success, failure, profile ID, duration, and failure reason.

## Verification

- `npm test` in `wt-media-cloud/web`: PASS, 9 files / 33 tests.
- `npm run build` in `wt-media-cloud/web`: PASS. Existing chunk warning remains.
- `.venv/bin/python -m unittest tests.test_local_profile_operations` in `wt-media-agent`: PASS, 4 tests.
- Agent log output verified manually in session `46283`.

## Status

Ready for manual retry. If BitBrowser times out again, the page should show a red timeout error and the Agent terminal should contain the exact `profile_id`, duration, and error message.
