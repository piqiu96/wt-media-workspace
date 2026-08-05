# Manual Acceptance Profile Create And Archive Fix

Date: 2026-07-25

## Trigger

Manual acceptance reported on the BrowserUsers page:

- Creating a BitBrowser window failed with `HTTP Error 404: Not Found`.
- Stopping/archiving a Cloud browser window appeared unavailable.
- New profile proxy binding and proxy replacement were expected during creation/list management.

## Findings

### Create failure

Direct BitBrowser Local API probes:

- `POST http://127.0.0.1:54345/browser/create` with `{}` returned `Not Found`.
- `POST http://127.0.0.1:54345/browser/update` with a non-existent probe ID returned structured BitBrowser business error `{"success":false,"msg":"ID不合法"}`.

This confirms the 404 came from using a non-existent BitBrowser endpoint. The active API path for create/update semantics is `/browser/update`.

### Archive failure

Cloud `DELETE /api/v1/browser-profiles/:id` returns NoContent/204. The Web API client tried to parse every response as JSON, so the archive action could fail client-side even when the Cloud route was correct.

### Proxy binding scope

M2-B requires proxy summary display and proxy changes in scan Diff. Full proxy import/detect/recommend/write/read-back/replacement belongs to M2-C (`M2-C 代理资源与窗口真实绑定闭环`). It is not implemented inside this M2-B fix.

## Change

- Local Agent BitBrowser runtime now creates profiles through `/browser/update`.
- Local Agent accepts created profile IDs from `id`, `browserId`, or `profileId`.
- Web HTTP client accepts empty 204 responses.
- BrowserUsers stop/archive button now shows a running notice, loading state, and concrete error on failure.

## Verification

- Agent tests:
  - `.venv/bin/python -m unittest tests.test_bitbrowser_runtime tests.test_local_profile_operations`
  - PASS, 12 tests.
- Web tests:
  - `npm test`
  - PASS, 10 files / 34 tests.
- Web build:
  - `npm run build`
  - PASS. Existing chunk warning remains.
- Runtime restarted:
  - Local Agent session `17057`.
  - Desktop shell session `69344`.

## Status

Ready for manual retry:

- BrowserUsers new window creation should no longer fail with `/browser/create` 404.
- BrowserUsers stop/archive should no longer fail on an empty 204 response.
- Proxy binding/replacement should be validated under M2-C, not counted as M2-B done.
