# M2-C4 Agent node and runtime attestation implementation plan

Execute under `executing-wt-media-change`, test-first, with independent Agent/Cloud/Workspace commits.

## Task 1: Agent report model and collector

- [x] Add failing tests for normalized OS/architecture, Python/FFmpeg/disk/workdir statuses, BitBrowser reachability, and verified owner/Profile IDs.
- [x] Implement an injectable collector that returns allow-listed values only and never raw paths, host/IP, command output, Cookie, or proxy facts.
- [x] Run focused then full Python tests.

## Task 2: Cloud binding and runtime domain

- [x] Add failing tests for active-session ticket issue/expiry/single-use, random node credential, session replacement rejection, and local-mode validation.
- [x] Add failing tests for matching/mismatching user, owner and active Profile runtime reports.
- [x] Implement domain interfaces without task authorization or locks.

## Task 3: MySQL and routes

- [x] Add migration/tables for binding tickets, durable nodes, environment reports and Profile runtime presence; store token/credential hashes only.
- [x] Add sqlmock tests for ticket consumption, Profile validation and atomic report apply; service/route tests cover credential lookup and active-session rejection.
- [x] Add authenticated ticket route and credentialed local register/report routes; preserve unauthenticated compatibility metadata and M1 no-DSN health behavior.

## Task 4: Agent client and contracts

- [x] Extend Agent client tests before implementation for binding token registration and bearer node credential runtime reports.
- [x] Publish Cloud Agent and Agent-owned report definitions/revisions with explicit status/error vocabularies.
- [x] Run full Go/Python/YAML/security gates; final health gates run during closure.

## Task 5: Governance and closure

- [x] Advance Contract Map/release matrix only after provider verification.
- [x] Record red/green evidence, security boundary, no-live-MySQL limitation and commits.
- Close C4 only with all ACs PASS, then activate C5 under continuous authorization.
