# Manual Acceptance Account Window Actions

Date: 2026-07-25

## Trigger

Manual acceptance reported that media account row actions "打开窗口" and "关闭窗口" were unavailable.

## Finding

`AccountsPage.vue` had its own open/close implementation and still forced `refreshRuntimeWithCooldown()` before calling `profileOpen/profileClose`.

That status refresh triggers Local Agent runtime collection and BitBrowser profile scanning, so the media account action could stall before the real open/close request was sent. This differed from the corrected BrowserUsers page behavior.

## Change

- Media account "打开窗口" now calls Desktop `profileOpen` directly with the bound `bit_profile_id`.
- Media account "关闭窗口" now calls Desktop `profileClose` directly with the bound `bit_profile_id`.
- Added missing `bit_profile_id` guard.
- Added operation loading state and disabled concurrent open/close clicks.
- Added the same timeout/error message mapping used by BrowserUsers.
- Failure clears the running notice so the page shows a concrete red error.

## Verification

- `npm test` in `wt-media-cloud/web`: PASS, 9 files / 33 tests.
- `npm run build` in `wt-media-cloud/web`: PASS. Existing chunk warning remains.
- Desktop shell restarted with latest Web source:
  - execution session `81281`
  - `WT_MEDIA_DESKTOP_WEB_URL=http://127.0.0.1:5174`
  - `WT_MEDIA_DESKTOP_LOCAL_AGENT_URL=http://127.0.0.1:8765`
- Local Agent logging remains active in session `46283`.

## Status

Ready for manual retry on the media accounts page. Agent logs should show `local_api.profile_open.*` or `local_api.profile_close.*` for each click.
