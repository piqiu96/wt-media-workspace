# CHG107 Verification

Date: 2026-10-29

## Cloud automated verification

- `go test ./...` — PASS.
- `npm --prefix web test -- --reporter=dot` — PASS, 88 files / 801 tests.
- `npm --prefix web run build:cloud` — PASS.
- `npm --prefix web run build:desktop` — PASS.
- `python3 scripts/docs/check.py` in Workspace — PASS, 15 indexes.
- OpenAPI and business-schema YAML parse — PASS for identity, media-account, content-production and file-transfer definitions.

## Database migration

- Backup before applying migration: `/tmp/wt_media_cloud_pre_chg107_20261029.sql` (18,766,230 bytes).
- Cloned `wt_media_cloud` to `wt_media_cloud_chg107_scratch`, applied `20261029_078_category_model.sql`, then applied the same migration to the stable local database.
- Existing categories: 4, all migrated with `type=game`.
- Migrated relation counts: `user_category_scopes=4`, `media_account_categories=3`.
- Source contents retaining an intentionally empty category: 11.
- Media accounts intentionally without a category relation: 5.
- Legacy dependent columns remaining: 0.
- Foreign keys pointing to `categories`: 7.

## API and page readback

- Temporary fresh database applied all 79 migrations through `20261029_078_category_model.sql`.
- Admin login succeeded.
- `POST /api/v1/categories` created `AI.代充` with server-assigned numeric ID; `GET /api/v1/categories?scope=management&type=ai&enabled=true` read it back.
- `POST /api/v1/media-accounts` accepted an account with no categories and returned a non-nil empty `category_ids` array.
- A media account selecting both `AI.代充` and `游戏.三角洲` was rejected with HTTP 400.
- Browser page `/categories` rendered 一级类型 / 类目名称 / 启用状态. Creating `二次元.原神` through the page produced server-assigned ID 4 and read it back in the table.

## Known environment limitation

- `python3 scripts/wt.py chg verify CHG-20261029-107` passes the Workspace unit suite and Cloud module suite, then stops in the unrelated M1 integration verifier because it imports the retired `wt_media_agent.cloud_agent_client` module. No CHG107 assertion failed before that point.
