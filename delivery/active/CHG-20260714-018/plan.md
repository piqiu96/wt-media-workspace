# M2-C4 Agent node and runtime attestation implementation plan

Execute under `executing-wt-media-change`, test-first, with independent Agent/Cloud/Workspace commits.

## Task 1: Agent report model and collector

- Add failing tests for normalized OS/architecture, Python/FFmpeg/disk/workdir statuses, BitBrowser reachability, and verified owner/Profile IDs.
- Implement an injectable collector that returns allow-listed values only and never raw paths, host/IP, command output, Cookie, or proxy facts.
- Run focused then full Python tests.

## Task 2: Cloud binding and runtime domain

- Add failing tests for active-session ticket issue/expiry/single-use, random node credential, session replacement rejection, and local-mode validation.
- Add failing tests for matching/mismatching user, owner and active Profile runtime reports.
- Implement domain interfaces without task authorization or locks.

## Task 3: MySQL and routes

- Add migration/tables for binding tickets, durable nodes, environment reports and Profile runtime presence; store token/credential hashes only.
- Add sqlmock tests for ticket consumption, credential lookup, active-session check and atomic report apply.
- Add authenticated ticket route and credentialed local register/report routes; preserve unauthenticated compatibility metadata and M1 no-DSN health behavior.

## Task 4: Agent client and contracts

- Extend Agent client tests before implementation for binding token registration and bearer node credential runtime reports.
- Publish Cloud Agent and Agent-owned report definitions/revisions with explicit status/error vocabularies.
- Run full Go/Python/YAML/security/health gates.

## Task 5: Governance and closure

- Advance Contract Map/release matrix only after provider verification.
- Record red/green evidence, security boundary, no-live-MySQL limitation and commits.
- Close C4 only with all ACs PASS, then activate C5 under continuous authorization.
