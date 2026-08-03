# Manual Acceptance Runtime - 2026-08-03

Date: 2026-08-03
Timezone: Asia/Shanghai

## Trigger

User requested a current-day M2-B packaged Desktop acceptance environment.

Confirmed user inputs:

- Real BitBrowser/Profile creation is allowed.
- Packaged Desktop is required.
- Acceptance account: `operator01`.
- No already logged-in Bilibili or Baijiahao window is available; acceptance must create or prepare one.

## Environment

- Cloud MySQL:
  - DSN: local `wt_media_cloud`.
  - Migration command: `scripts/migrate.sh`.
  - Actual: PASS, `migration ok: 0 applied, 16 total`.
- Cloud API:
  - Address: `http://127.0.0.1:18080`.
  - Health: PASS, `GET /api/v1/health`.
- Local Agent:
  - Address: `http://127.0.0.1:8765`.
  - Health: PASS, `GET /healthz`.
  - Status: PASS, `bitbrowser_status=normal`.
- BitBrowser:
  - App: `/Applications/比特浏览器.app`.
  - Local API port: `54345`.
  - Main user ID read by Agent: `2c9bc06191effa4e0191f9589996619f`.
- Cloud user:
  - `operator01` exists and is enabled.
  - `operator01` is bound to `bit_main_user_id=2c9bc06191effa4e0191f9589996619f`.
  - Local acceptance password was reset to `m2b-operator-20260803`.
  - Login API with `operator01` passed.

## Packaged Desktop

- Desktop frontend build:
  - Command: `bash ../wt-media-workspace/scripts/build-desktop.sh` through Tauri `beforeBuildCommand`.
  - Initial finding: FAIL, generated Desktop assets only included `index.desktop.html`; packaged Tauri runtime looked for `index.html` and showed `asset not found: index.html`.
  - Fix applied: `build-desktop.sh` now copies `index.desktop.html` to `index.html` and fails the build if `index.html` is absent or empty.
  - Retest: PASS, 30 frontend files copied to Desktop `.generated/frontend`; `index.html` is 410 bytes.
- Tauri config fix:
  - `beforeBuildCommand` changed from a brittle relative path to `bash ../wt-media-workspace/scripts/build-desktop.sh`.
- Packaged dmg:
  - Command: `cargo tauri build --bundles dmg --no-sign`.
  - Actual: PASS.
  - Output: `/Users/aqiuye/Develop/workspace/wt-media/wt-media-desktop/target/release/bundle/dmg/WT Media_0.1.0_aarch64.dmg`.
- DMG mount:
  - Command: `hdiutil attach target/release/bundle/dmg/WT Media_0.1.0_aarch64.dmg`.
  - Actual: PASS, mounted at `/Volumes/WT Media`.
  - Environment cleanup: duplicate old mounts `/Volumes/WT Media` and `/Volumes/WT Media 1` were detached before final launch.
- App launch:
  - Command: `open "/Volumes/WT Media/WT Media.app"`.
  - Actual: PASS, process source verified as `/Volumes/WT Media/WT Media.app/Contents/MacOS/wt-media-desktop-shell`.
  - Log check: PASS, `log show` narrow search found no `asset not found` or `index.html` errors after final launch.
- Packaged Desktop login regression:
  - Initial finding: FAIL, packaged Desktop login showed `服务器返回格式错误`.
  - Root cause: packaged Desktop used relative Cloud API base `/api/v1`; outside the Vite dev proxy this resolved against the Tauri asset protocol and returned non-JSON static-resource output.
  - Fix applied: Desktop packaged runtime resolves the default Cloud API base to `http://127.0.0.1:18080/api/v1`, while Desktop dev server `5174` keeps the relative `/api/v1` proxy path.
  - Cloud compatibility fix: local Desktop/dev CORS middleware now allows credentialed requests from `http://tauri.localhost`, `https://tauri.localhost`, `tauri://localhost`, and local Vite dev origins.
  - Retest: PASS, direct `POST /api/v1/auth/login` with Origin `http://tauri.localhost` returned unified JSON and `Set-Cookie`; newly launched packaged Desktop reached Cloud `/api/v1/auth/me` instead of Tauri static assets.

## Real BitBrowser Profile Verification

- Group read:
  - Endpoint: Local Agent `POST /api/v1/bit-browser/profile-groups`.
  - Actual: PASS, returned real group `测试组` with ID `402880a99f4a13aa019f527f92df42d4`.
- Profile create:
  - Endpoint: Local Agent `POST /api/v1/bit-browser/profile-create`.
  - Payload name: `m2b-acceptance-20260803-2257`.
  - Actual: PASS, returned BitBrowser profile ID `9e6c697c69fc467fa5e0829ca4fbebee`.
- Profile read-back:
  - Endpoint: Local Agent `POST /api/v1/bit-browser/profile-scans`.
  - Actual: PASS.
  - Read-back facts:
    - `bit_profile_id`: `9e6c697c69fc467fa5e0829ca4fbebee`.
    - `name`: `m2b-acceptance-20260803-2257`.
    - `seq`: `55`.
    - `group_name`: `测试组`.
    - `proxy_type`: `noproxy`.
- Profile open:
  - Initial Agent result: FAIL, 5 second timeout.
  - Direct BitBrowser `/browser/open` with longer timeout: PASS, returned DevTools endpoint and browser process PID.
  - Fix applied: Agent profile mutation timeout now defaults to 30 seconds and is configurable through `WT_MEDIA_BITBROWSER_MUTATION_TIMEOUT_SECONDS`.
  - Retest through Local Agent: PASS, returned `{"data":{"status":"opened"}}`.
- Profile close:
  - Retest through Local Agent: PASS, returned `{"data":{"status":"closed"}}`.

## Automated Verification

- Agent:
  - Command: `.venv/bin/python -m unittest tests.test_bitbrowser_runtime tests.test_local_profile_operations`.
  - Actual: PASS, 16 tests.
- Desktop package:
  - Command: `cargo tauri build --bundles dmg --no-sign`.
  - Actual: PASS.
  - Note: existing Rust dead-code warnings remain.
- Cloud:
  - Health endpoint: PASS.
- Web/Desktop frontend:
  - `build:desktop` executed by Tauri `beforeBuildCommand`.
  - Actual: PASS.
  - Note: existing chunk size warning remains.
- Web tests:
  - Command: `npm test`.
  - Actual: PASS, 10 files / 36 tests.
- Cloud app tests:
  - Command: `go test ./internal/app`.
  - Actual: PASS.
- Local environment script:
  - Script: `wt-media-workspace/scripts/m2b-local-acceptance.sh`.
  - Verification command: `m2b-local-acceptance.sh verify`.
  - Actual: PASS, verified Cloud, Agent, BitBrowser through Agent, Desktop generated assets, and DMG.

## Manual Acceptance Still Required

The environment is ready for the user to click through the packaged Desktop UI.

Required manual checks:

- Login packaged Desktop with `operator01 / m2b-operator-20260803`.
- Confirm environment page shows Agent and BitBrowser available.
- BrowserUsers page:
  - scan windows;
  - confirm the new window `m2b-acceptance-20260803-2257` appears;
  - verify open window and close window buttons perform real effects;
  - verify stop/archive button updates Cloud state and does not delete the BitBrowser profile.
- Media accounts page:
  - create a test media account;
  - bind it to the new profile;
  - run single check before login and confirm explicit failure/not logged-in result;
  - manually log into Bilibili or Baijiahao inside the BitBrowser window;
  - run sync/check again and confirm platform UID/name/avatar/login status read back.
- Batch check:
  - select multiple accounts;
  - confirm skipped items show reasons;
  - confirm successful items do not roll back when another item fails;
  - confirm failed-item retry only reruns failed items.

## Status

Current-day M2-B runtime environment is usable after the packaged Desktop entrypoint and login API base fixes. Automated real BitBrowser window create/read/open/close passed after the Agent timeout fix. The final launched app process is from the newly mounted DMG, not an old build. A stable local acceptance script now exists for repeatable startup/build/launch/verify flows. Full M2-B closure still requires the user to complete packaged Desktop UI and platform-login manual checks.
