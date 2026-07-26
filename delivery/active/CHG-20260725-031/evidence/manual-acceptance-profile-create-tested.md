# Manual Acceptance Profile Create Tested

Date: 2026-07-26

## Trigger

Manual acceptance reported that BrowserUsers profile creation still failed and asked that fixes be tested before acceptance.

## Findings

Real BitBrowser Local API and Local Agent tests showed three separate facts:

- `/browser/create` is not available in the current BitBrowser Local API.
- `/browser/update` is the active create/update endpoint.
- Creating through `/browser/update` requires:
  - `browserFingerPrint`;
  - an explicit proxy mode.
- A 5 second create timeout can produce false failure: BitBrowser may create the profile after Local Agent already returned timeout.

## Changes

- Local Agent profile create uses `/browser/update`.
- Local Agent profile create defaults no-proxy profiles to:
  - `proxyMethod: 2`;
  - `proxyType: "noproxy"`;
  - `browserFingerPrint: {}`.
- Local Agent uses a dedicated profile-create timeout:
  - default `30s`;
  - override via `WT_MEDIA_BITBROWSER_CREATE_TIMEOUT_SECONDS`.
- Local Agent logs profile create start/success/failure with profile name, group ID, created profile ID, duration, and error.
- Cloud profile archive route now has route-level test coverage for the actual project convention: HTTP 200 with `data:null`.

## Verification

### Automated

- Agent:
  - `.venv/bin/python -m unittest tests.test_bitbrowser_runtime tests.test_local_profile_operations`
  - PASS, 14 tests.
- Cloud:
  - `go test ./internal/modules/profilebinding`
  - PASS.
- Web:
  - `npm test`
  - PASS, 10 files / 34 tests.
  - `npm run build`
  - PASS. Existing chunk warning remains.

### Real BitBrowser / Local Agent

- Local Agent with latest code is running:
  - PID `39991`.
- Service health:
  - `GET http://127.0.0.1:8765/healthz`
  - Actual: PASS, returned `{"status":"ok","service":"wt-media-agent","mode":"m1"}`.
- Real create via Local Agent:
  - `POST http://127.0.0.1:8765/api/v1/bit-browser/profile-create`
  - Payload: `{"name":"wt-media-acceptance-20260726-1220","groupId":"402880a99f4a13aa019f527f92df42d4","groupName":"测试组"}`
  - Actual: PASS, returned `{"data":{"id":"e25a849033e242d4ae4a9685d6b036c1"}}`.
- Agent log:
  - `local_api.profile_create.start name=wt-media-acceptance-20260726-1220 group_id=402880a99f4a13aa019f527f92df42d4`
  - `local_api.profile_create.success profile_id=e25a849033e242d4ae4a9685d6b036c1 duration_ms=4182`
- Read-back via Local Agent profile scan:
  - Actual: PASS, returned profile `e25a849033e242d4ae4a9685d6b036c1`.
  - Name: `wt-media-acceptance-20260726-1220`.
  - Group: `测试组`.
  - Seq: `54`.
  - Proxy: `noproxy`.

## Status

Ready for BrowserUsers manual retry. Profile creation has now been verified with the real Local Agent and real BitBrowser Local API before handoff.
