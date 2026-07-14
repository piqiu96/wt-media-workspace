# C6 real integration resume gate

Do not close CHG-020 until every row below has fresh evidence from real dependencies.

## Prerequisites

1. A reachable MySQL 8-compatible server and an ephemeral C6 database.
2. Either `WT_MEDIA_MYSQL_DSN` or an equivalent Cloud runtime DSN configured without committing or printing credentials.
3. The installed BitBrowser application logged in, with its Local API listening on the configured URL and at least one Profile owned by the intended BitBrowser user.
4. Cloud, Local Agent and Desktop processes permitted to bind loopback ports.

## Required execution order

1. Apply Cloud migrations `20260714_001` through `20260714_005` to the empty C6 database and retain migration output with secrets redacted.
2. Start Cloud against that database; bootstrap the first admin, verify duplicate bootstrap rejection, create operator/viewer users, verify single-active-session invalidation and all three role boundaries.
3. Create and assign media accounts; verify unassigned, assigned and enabled/disabled visibility and mutation rules.
4. Use the real BitBrowser Local API to fetch the complete Profile list. Confirm all rows share one non-empty owner user ID and that no cookie, proxy password or local path reaches Cloud.
5. Issue a one-use Cloud binding ticket, pass it through Desktop to Local Agent, consume it once, reject reuse, and verify only the credential hash is stored by Cloud.
6. Report the real node/Profile/runtime environment and verify owner, assignment, node and freshness checks.
7. Submit two sensitive preflights for the same Profile. Verify exactly one grant and one waiting response; renew the grant within the bounded window and finish it normally.
8. Create a second granted permit, let it expire without a finish report, then verify the next preflight returns `review_required` and no automatic replay occurs.
9. Rerun the complete automated matrix and confirm all four repositories are clean.

## Evidence to retain

- Exact revisions and commit IDs, timestamps, redacted request/response summaries, database assertions, BitBrowser owner/count summary, and pass/fail per AC-03 through AC-05.
- Never retain Cookies, binding tickets, node/permit credentials, proxy secrets, or local filesystem paths.
