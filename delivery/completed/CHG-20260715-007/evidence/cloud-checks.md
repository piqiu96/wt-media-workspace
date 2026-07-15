# M0-R6 Cloud/Web Checks

| Command | Result |
|---|---|
| `go version` | PASS: `go1.26.5 darwin/arm64` |
| `scripts/bootstrap.sh` | PASS: npm dependencies installed; npm emitted allow-scripts advisory for esbuild/fsevents |
| `scripts/test.sh` | PASS: Go packages passed; Web Vitest 8 tests passed |
| `WT_MEDIA_MYSQL_DSN=.../wt-media-cloud scripts/migrate.sh` | EXPECTED FAIL: existing user DB has tables but no `schema_migrations`; failed on `Table 'users' already exists` |
| `WT_MEDIA_MYSQL_DSN=.../wt_media_m0_r6_verify scripts/migrate.sh` | PASS: 5 applied, 5 total |
| repeat `WT_MEDIA_MYSQL_DSN=.../wt_media_m0_r6_verify scripts/migrate.sh` | PASS: 0 applied, 5 total |
| `scripts/build.sh` | PASS: Web Vite build passed; Go emitted nonfatal stat-cache warning for external GOPATH |
| `WT_MEDIA_CLOUD_HTTP_ADDR=127.0.0.1:18080 ... scripts/start.sh` | PASS: Cloud started |
| `WT_MEDIA_CLOUD_HTTP_ADDR=127.0.0.1:18080 scripts/health.sh` | PASS: `wt-media-cloud health ok` |
| `scripts/stop.sh` | PASS: Cloud stopped |

## Notes

- R6 did not mutate or repair the existing `wt-media-cloud` database because it is not an empty migration target.
- Empty-database migration acceptance used isolated DB `wt_media_m0_r6_verify`.
