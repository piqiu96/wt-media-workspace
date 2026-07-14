# C6 real MySQL and Cloud API execution

Executed: 2026-07-14T12:53:18Z

## Scope

This run used the user-provided local MySQL service at `127.0.0.1:3306` and the user-requested database name `wt-media-cloud`.

Credentials, session Cookies, binding tokens, node credentials, Profile permit credentials, and raw BitBrowser Profile payloads were not printed or retained.

## Cloud migration finding and fix

Initial real migration execution against MySQL 8-compatible local MySQL failed on `20260714_002_media_accounts.sql`:

- MySQL error: `Error 3780 (HY000)`, foreign key column incompatibility for `fk_media_accounts_user`.
- Root cause: M2 migrations mixed `utf8mb4_0900_ai_ci` and `utf8mb4_unicode_ci` collations across string foreign keys; `media_accounts.browser_profile_id VARCHAR(255)` also did not match `browser_profiles.id VARCHAR(64)`.
- Fix commit: Cloud `7147b37 fix: align m2 mysql migration constraints`.

## Real database result

Command action:

- Created/reset database `wt-media-cloud`.
- Applied Cloud migrations `20260714_001_identity.sql` through `20260714_005_sensitive_profile_locks.sql`.

Observed result:

```text
database=wt-media-cloud
migrations_applied=5
table_count=14
```

Status: PASS

## Real Cloud API result

Cloud was started against `wt-media-cloud` on `127.0.0.1:18080` with local HTTP secure-cookie mode disabled for acceptance.

Observed redacted acceptance summary:

```text
status=pass
database=wt-media-cloud
steps=health,single_active_session,three_roles,role_boundaries,media_accounts,profile_confirm_and_account_bind,one_use_binding,runtime_report,concurrent_permit,expired_permit_review
users=3 profiles=1 nodes=1 tasks=4 permits=2
secrets_printed=false
```

Covered facts:

- Bootstrap technician login worked.
- Re-login invalidated the prior active session.
- Technician, operator, and senior operator roles existed; operator was blocked from technician-only user creation and from an out-of-scope game.
- Media account create/identify/bind flow returned no cookie secret material.
- Browser Profile scan/confirm populated one active Cloud Profile and bound it to the media account.
- One-use local Agent binding ticket was accepted once and rejected on reuse.
- Runtime report validated bound owner/Profile/node presence.
- Concurrent sensitive preflight returned exactly one `granted` and one `waiting`.
- Granted permit renewed and finished normally.
- Expired active permit forced the next preflight into `review_required`.
- Database stored hash-length credential facts, not raw binding/node/permit credentials.

Status: PASS for AC-03 and AC-05.

## Real BitBrowser result

Fresh redacted Local API probe:

```text
{'status': 'identity_unverifiable', 'profile_count': 37, 'distinct_owner_count': 2, 'missing_owner_count': 0, 'raw_profile_fields_printed': False}
```

Status: FAIL for AC-04 until the real BitBrowser Profile set used for acceptance has one non-empty owner `userId`.

## Verification after changes

Commands run after the Cloud migration fix:

| Area | Command | Result |
|---|---|---|
| Cloud | `go test ./... -count=1` | PASS |
| Cloud | `go vet ./...` | PASS |
| Workspace | `python3 scripts/verify_m2_acceptance.py` | PASS |
| Workspace | `python3 -m unittest discover tests` | PASS, 7 tests |
| Agent | `.venv/bin/python -m unittest discover -s tests` | PASS, 38 tests |
| Desktop | `npm run verify` | PASS |

CHG-020 remains active because AC-04 and therefore AC-06 are not complete.
