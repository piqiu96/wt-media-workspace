# Contract Map

This is a human-readable index for cross-repo contract ownership and consumers.
Machine-readable ownership and consumer facts live in `../../config/contract-map.yaml`.
Formal OpenAPI, schema, DTO, and event definitions live only in the provider repositories.

Current state is mixed. The machine-readable map is authoritative for exact revisions:

- Cloud API, Cloud-Agent API, business schemas, business enums and Cloud error codes are active formal definitions.
- Local Agent API, local event schemas, local status enums and local error codes are active formal definitions.
- `task_schemas` is active. Revision `2026.10.23.1` defines the universal task model, status state machine, task types, execution defaults and error codes.

Historical M0/M1 release entries remain valid evidence for their recorded scaffold/noop scope. They do not imply that the revised M0/M1 end-to-end milestone gates are complete.

## Cloud-Owned Contracts

- `../wt-media-cloud/contracts/cloud-api`
- `../wt-media-cloud/contracts/cloud-agent-api`
- `../wt-media-cloud/contracts/business-schemas`
- `../wt-media-cloud/contracts/task-schemas`
- `../wt-media-cloud/contracts/business-enums`
- `../wt-media-cloud/contracts/cloud-error-codes`

### Media-account game-set revision (M2-B)

Cloud owns the additive media-account API revision. `game_ids` is the
canonical request, response and query field for the full account game set;
`game_id` remains a single-value compatibility input/projection only. A request
containing both fields must use the same normalized singleton value or Cloud
rejects it. Cloud Web is the direct consumer; Agent has no media-account game
relation contract and Desktop consumes the Cloud Web build output only.

### Proxy ledger extraction and synchronous mutation revision (M2-C)

The Agent-owned Local Agent API revision `2026.09.05.1` provides compatible
`POST /api/v1/proxy-mutation` assign and `unbind` write/read-back operations;
credentials are write-only and never returned. Cloud owns the corresponding
compatible `POST /api/v1/proxies/{proxy_id}/assign`, `/unbind`, and
`/local-scan/{preview,confirm}` projections. The original revision records or
clears `browser_profiles.proxy_id` after an Agent response confirms the matching
proxy or `noproxy` read-back, or after a trusted Desktop Profile scan is
explicitly accepted. ADR-0027 updates the assignment and execution rule as described below.
Unknown scanned proxies become paused, unchecked records;
ambiguous tuple matches are surfaced as conflicts and are never guessed.
Cloud Web and Desktop consume the refreshed Web build output.

CHG-20261028-099 / ADR-0027 adds the Agent-owned `POST /api/v1/proxy-assignment`
capability (revision `2026.10.29.1`). Its explicit acknowledgement is not a
read-back or connectivity result. Cloud may confirm an assignment only after
the new capability acknowledges the requested Profile; an unavailable old
Agent cannot be assumed to support it. The prior `proxy-mutation` endpoint
retains its existing read-back contract for mixed-version compatibility and
the unbind flow. Unknown outcomes must not be retried automatically.

Revision `2026.09.06.1` adds a compatible Agent-owned `POST /api/v1/proxy-extract` operation. Cloud owns the compatible proxy-address parse, dynamic extraction preview, dynamic refresh, and bound-window detail projections. The Agent fetches a manually requested provider URL and returns only the first supported plain-text proxy address to Cloud; it never writes BitBrowser. Cloud stores the source URL as a secret, exposes only a configured/masked indication, clears stale check facts when the extracted connection changes, and leaves applying an updated proxy to the browser-window flow. That flow's current acknowledgement and pending rule is ADR-0027.

### Session-only auth and Agent Token revision (CHG-20261023-101)

Cloud owns revision `2026.10.23.1` across `cloud-api`, `cloud-agent-api`, `business-schemas`, `business-enums`, `task-schemas` and `cloud-error-codes`. `user_sessions` becomes the only authentication fact: Web allows multiple sessions, Desktop allows one valid session per user, and a second Desktop login returns `DESKTOP_LOGIN_CONFLICT` until the caller confirms with the current session id. Desktop exchanges a valid desktop session for a signed, stateless Agent Token at `POST /api/v1/local-agent/agent-token`; its `exp` equals the session `expires_at`, strict mode gates new work and report-safe mode closes already-claimed tasks. Device, node, presence and binding-ticket contracts are retired. Task claim/report requires the Agent Token plus `attempt_id`, and `task-recovery` settles silent `running` tasks as `EXECUTION_INTERRUPTED` or `RESULT_UNKNOWN` by external-side-effect flag.

The Agent-owned `local-agent-api` and `local-error-codes` revisions are `2026.10.23.1`: the local Agent stores the Agent Token in memory only, accepts BitBrowser binding from Agent-read facts, and declares the profile CRUD, cookie-read, sensitive preflight/finish and agent-token routes it implements. Desktop `contracts.lock.json` pins `cloud_agent_api`, `task_schemas` and `local_agent_api` at this revision.

### Platform identifier revision (CHG-20261015-098)

Cloud owns `2026.10.27.3` of `cloud-api` (media-accounts), `2026.10.27.2` of
`business-schemas` (media-account) and `2026.10.27.1` of `business-enums`
(media-account): the `platform` enum becomes `douyin | bilibili | baidu`, retiring
`baijiahao`. The Agent-owned `local-agent-api` revision `2026.10.27.1` changes
`AccountCheckRequest.platform` the same way, and Desktop `contracts.lock.json`
pins `local_agent_api v1@2026.10.27.1`. Display text is a client concern and
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
senior view). `GET /api/v1/games` is now declared with a `scope` parameter:
`all` is the widened dictionary (game as a filter, not an access boundary) and
`management` is the game-management page, available to senior operators and
admins with every game status but without `reference_summary` — the reference
detail those counts open is admin-only. Operators get 403 for `management`.
The game write endpoints are still implemented without contract declaration;
that pre-existing gap is not widened here.

### Account owner projection and local-operation gates (CHG-20261015-098 T-24)

Cloud owns `2026.10.27.6` of `cloud-api`. `MediaAccount` gains `user_name`, the
account owner's display name resolved by the read query (`users.nickname`,
falling back to `users.username`; empty when the user row is missing). It is a
read-only projection: no write path accepts it, and `user_id` remains the
identity fact. The revision also declares the three local-operation entry points
that were implemented but absent from the contract — `check`,
`cookies/read` and `cookies/read-sync` — with one shared role rule: operators
may act on the accounts they own, senior operators only the accounts they
created (`user_id` equals the caller), and admins cannot start local work at
all. Ownership is enforced server-side; the page's disabled buttons are a
courtesy, not the boundary.

### Proxy team scope and window-side write-back (CHG-20261028-099)

Cloud owns `2026.10.28.1` of `cloud-api`. Proxy resources now carry a required
`team_id`; operators and senior operators read and write their own team, admins
read every team and must name the target team when creating or importing.
`proxies.openapi.yaml` declares the full lifecycle that Web already calls
(list, detail, create, update, status, delete, quota, check, import preview and
import) plus `POST /api/v1/proxies/profile-unbind`, batch assignment and
release. Health checks run inside Cloud against the saved connection and return
`ok` / `conn_failed` / `auth_failed` / `timeout` / `invalid_params`; a result
arriving after the connection changed is discarded. Local-scan confirmation now
takes `selected_profile_ids` for unknown addresses and reports
`ownership_conflict` for windows registered to another operator, which the scan
never modifies.

`browser-profiles.openapi.yaml` records the role/team visibility of the window
list, the `adopt_bit_profile_ids` confirmation body, the Cloud-remark and
business-status update scope, the disabled-and-unreferenced delete rule, and the
window fields the page reads (`team_id`, `cloud_remark`, `business_status`,
`ownership_conflict`). BitBrowser writes remain Desktop/Agent-only; Cloud Web
declares the create/open/close stubs as Desktop-only refusals.

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
