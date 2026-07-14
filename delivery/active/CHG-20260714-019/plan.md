# M2-C5 Profile concurrency and sensitive preflight plan

Execute under `executing-wt-media-change` and TDD.

1. Agent: failing tests then implement local Profile lock manager, guarded preflight/release context and client methods.
2. Cloud domain: failing tests then implement fixed sensitive operation enums, authorized task resolution, C4 node/session/presence validation, waiting/review outcomes and hashed permit credentials.
3. MySQL/routes: transactionally serialize the Profile row/lock, never auto-reuse an expired unreleased permit, add credentialed preflight/renew/release APIs.
4. Contracts/governance: publish provider revisions, advance maps only after providers pass, run full health/security/diff gates.
5. Close C5 and activate C6 without an approval pause.
