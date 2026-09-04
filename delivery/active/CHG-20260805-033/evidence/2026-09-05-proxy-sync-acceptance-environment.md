# 2026-09-05 Proxy sync local acceptance environment

- Command: `scripts/m2b-local-acceptance.sh all --force-restart`.
  Expected: force-restart Cloud and Local Agent from current source, apply the fixed `wt_media_cloud` migrations, rebuild/mount the Desktop DMG, and leave the local acceptance stack ready.
  Actual: migration reported `0 applied, 27 total`; Desktop frontend and DMG rebuild completed. The harness session ended while emitting the final build log, so each required runtime gate was independently rechecked below.
- Cloud health: `GET http://127.0.0.1:18080/api/v1/health` returned `errcode: 0`.
- Local Agent: `/healthz` returned `ok`; `/api/v1/status` returned `bitbrowser_status: normal` and 40 BitBrowser Profile ids.
- Desktop: `WT Media_0.1.0_aarch64.dmg` is 4,940,924 bytes, built `2026-09-05 01:14:24`, and mounted at `/Volumes/WT Media`; generated `http-*.js` contains `127.0.0.1:18080/api/v1`.
- Desktop CORS: preflight for `/api/v1/proxies/local-scan/preview` from `http://tauri.localhost` returned `204`, matching origin and `Access-Control-Allow-Credentials: true`.
- Login smoke: `admin/admin123` with `replace_existing: true` returned `errcode: 0`.
- New route smoke: authenticated `POST /api/v1/proxies/local-scan/preview` with `scan_id=missing-scan` returned the Cloud-defined `errcode: 23001` (`扫描记录不存在`), proving the current Cloud process loaded the new route.
- Scope note: this establishes a current environment and verifies contracts. The real write/read-back acceptance must use an operator-selected writable proxy and BitBrowser Profile; it is not substituted by this record.
