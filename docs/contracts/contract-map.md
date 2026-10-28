# Contract Map

This is a human-readable index for cross-repo contract ownership and consumers.
Machine-readable ownership and consumer facts live in `../../config/contract-map.yaml`.
Formal OpenAPI, schema, DTO, and event definitions live only in the provider repositories.

Current state is mixed. The machine-readable map is authoritative for exact revisions:

- Cloud API, Cloud-Agent API, business schemas, business enums and Cloud error codes are active formal definitions.
- Local Agent API, local event schemas, local status enums and local error codes are active formal definitions.
- `task_schemas` retired together with the generic Cloud task table and `/cloud-agent/tasks/*` endpoints. File transfer keeps its own contract.

Historical M0/M1 release entries remain valid evidence for their recorded scaffold/noop scope. They do not imply that the revised M0/M1 end-to-end milestone gates are complete.

## Cloud-Owned Contracts

- `../wt-media-cloud/contracts/cloud-api`
- `../wt-media-cloud/contracts/cloud-agent-api`
- `../wt-media-cloud/contracts/business-schemas`
- `../wt-media-cloud/contracts/business-enums`
- `../wt-media-cloud/contracts/cloud-error-codes`

### Media-account category-set revision (M2-B, superseded by ADR-0028)

Cloud owns the media-account category API revision. `category_ids` is the
canonical request, response and query field for the complete account category
set; empty means intentionally unclassified. No single-category compatibility
field remains. Cloud Web is the direct consumer; Agent has no media-account
category relation contract and Desktop consumes the Cloud Web build output only.

### Operating-resource proxy execution revision (ADR-0027)

The Agent-owned Local Agent API revision `2026.10.29.2` exposes synchronous
`POST /api/v1/proxy-extract` and `POST /api/v1/proxy-mutation`; mutation returns
secret-free read-back for assign/unbind. `proxy-check` is retired because proxy
health is checked by Cloud against the saved connection. Agent credentials remain
write-only and never appear in responses.

### Session-only auth and Agent Token revision (CHG-20261023-101)

Cloud owns the current revisions across `cloud-api`, `cloud-agent-api`, `business-schemas`, `business-enums` and `cloud-error-codes`. `user_sessions` becomes the only authentication fact: Web allows multiple sessions, Desktop allows one valid session per user, and a second Desktop login returns `DESKTOP_LOGIN_CONFLICT` until the caller confirms with the current session id. Desktop exchanges a valid desktop session for a signed, stateless Agent Token at `POST /api/v1/local-agent/agent-token`; its `exp` equals the session `expires_at`, strict mode gates new work and report-safe mode closes already-claimed tasks. Device, node, presence and binding-ticket contracts are retired. Generic task claim/report and recovery are retired; the surviving Cloud-Agent surface is compatibility, Agent Token, and dedicated file-transfer routes.

The Agent-owned `local-agent-api` and `local-error-codes` are active formal definitions. The local Agent stores the Agent Token in memory only and accepts BitBrowser binding from Agent-read facts. Generic sensitive preflight/permit and task claim/report interfaces are retired. Desktop `contracts.lock.json` pins the surviving Cloud-Agent and Local Agent contracts.

### Platform identifier revision (CHG-20261015-098)

Cloud owns `2026.10.27.3` of `cloud-api` (media-accounts), `2026.10.27.2` of
`business-schemas` (media-account) and `2026.10.27.1` of `business-enums`
(media-account): the `platform` enum becomes `douyin | bilibili | baidu`, retiring
`baijiahao`. The Agent-owned `local-agent-api` revision `2026.10.27.1` changes
`AccountCheckRequest.platform` the same way, and Desktop `contracts.lock.json`
pins the current `local_agent_api` revision. Display text is a client concern and
lives in `web/src/shared/utils/platforms.js`, so no contract carries Chinese
platform names. The enum change is breaking in both directions: Cloud and Agent
must ship together, and rollback needs a reverse data migration first. See
ADR-0024 and the `platform-identifier-rename-20261027` release entry.

### Material creator revision (CHG-20261015-098 T-21)

Cloud owns `2026.10.27.4` of `cloud-api` and `2026.10.27.3` of
`business-schemas` (content-production): `Material` gains `created_by` (required,
the library column that already exists) and `created_by_name` (resolved from the
user directory at read time; absent when that user is gone). The creator is a
fact about the material, so every role reads it, unlike the `usage.operators`
names that stay with senior operators and administrators.

### System management revision (CHG-20261015-098 T-23)

Cloud owns `2026.10.27.5` of `cloud-api` and `2026.10.27.4` of
`business-schemas` (identity). `OperationTeam` gains `user_count`, read from the
users table in the same statement as the row, so a team's headcount does not
need the user list (that endpoint is admin-only and would 403 for the read-only
senior view). The former games endpoint is replaced by `/api/v1/categories` with a `scope` parameter:
`all` is the widened dictionary (category as a filter, not an access boundary) and
`management` is the category-management page, available to senior operators and
admins with every category status but without `reference_summary` — the reference
detail those counts open is admin-only. Operators get 403 for `management`.
The category write endpoints are still implemented without contract declaration;
that pre-existing gap is not widened here.

### Account owner projection and local-operation gates (CHG-20261015-098 T-24)

Cloud owns `2026.10.27.6` of `cloud-api`. `MediaAccount` gains `user_name`, the
account owner's display name resolved by the read query (`users.nickname`,
falling back to `users.username`; empty when the user row is missing). It is a
read-only projection: no write path accepts it, and `user_id` remains the
identity fact. The revision also declares the three local-operation entry points
that were implemented but absent from the contract — `check`,
`cookies/read-sync` and its result callback — with one shared role rule: operators
may act on the accounts they own, senior operators only the accounts they
created (`user_id` equals the caller), and admins cannot start local work at
all. Ownership is enforced server-side; the page's disabled buttons are a
courtesy, not the boundary.

### Operating-resource contract (CHG-20261028-099)

Cloud owns revision `2026.10.29.2` of the affected API schemas. `proxies` is the
team-scoped proxy ledger with boolean `enabled`, `max_profiles`, Cloud-side health
checks, and current formal/reserved occupancy. `browser-profiles` records the
single user snapshot, `bit_` mirror fields, boolean enablement, Cloud remark, and
two proxy-operation endpoints: start reservation and settle the Desktop result.
`apply` and `unbind` require the result call; `release` only clears the formal
Cloud relation. Uncertain Desktop results are reported as failures and clear the
reservation for direct retry. Legacy assign/batch/unbind/release/local-scan Cloud
endpoints and Cloud Web create/open/close stubs are retired.

## Agent-Owned Contracts

- `../wt-media-agent/contracts/local-agent-api`
- `../wt-media-agent/contracts/local-event-schemas`
- `../wt-media-agent/contracts/local-status-enums`
- `../wt-media-agent/contracts/local-error-codes`

## Consumers

- `wt-media-cloud/web` consumes Cloud API contracts.
- `wt-media-agent` consumes Cloud-Agent API and task schemas.
- `wt-media-desktop` consumes Cloud API and Local Agent contracts.

## Readiness Rule

Contract existence and milestone completion are separate facts. A consumer may use an active contract revision only after its own real build/integration gate passes. Placeholder contracts cannot satisfy a production or end-to-end acceptance row.

## M3 V2 planned contract scope (not a published revision)

ADR-0013 confirms content-pool-first ingestion, `discovery_strategy`, a controlled channel abstraction and five business `crawl_task` statuses (`pending`, `running`, `success`, `partial_success`, `failed`). Cloud owns the future business API/enums, source/material relationship and task input/result/error contracts; Agent consumes execution contracts and implements channel adapters. Desktop reuses Cloud Web. Partial-failure mapping is confirmed as of 2026-09-23 (`partial_success` is a real business state, not a pending decision); content authorization still requires confirmed decisions before publication. This planning entry neither changes machine-readable revisions nor claims runtime compatibility, migrations or generated consumers have been updated.
