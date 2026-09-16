# Contract Map

This is a human-readable index for cross-repo contract ownership and consumers.
Machine-readable ownership and consumer facts live in `../../config/contract-map.yaml`.
Formal OpenAPI, schema, DTO, and event definitions live only in the provider repositories.

Current state is mixed. The machine-readable map is authoritative for exact revisions:

- Cloud API, Cloud-Agent API, business schemas, business enums and Cloud error codes are active formal definitions.
- Local Agent API, local event schemas, local status enums and local error codes are active formal definitions.
- `task_schemas` is active (M1-R1). Revision `2026.07.15.1` defines the universal task model, status state machine, task types, and error codes.

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
`/local-scan/{preview,confirm}` projections. Cloud records or clears
`browser_profiles.proxy_id` only after an Agent response confirms the matching
proxy or `noproxy` read-back, or after a trusted Desktop Profile scan is
explicitly accepted. Unknown scanned proxies become paused, unchecked records;
ambiguous tuple matches are surfaced as conflicts and are never guessed.
Cloud Web and Desktop consume the refreshed Web build output.

Revision `2026.09.06.1` adds a compatible Agent-owned `POST /api/v1/proxy-extract` operation. Cloud owns the compatible proxy-address parse, dynamic extraction preview, dynamic refresh, and bound-window detail projections. The Agent fetches a manually requested provider URL and returns only the first supported plain-text proxy address to Cloud; it never writes BitBrowser. Cloud stores the source URL as a secret, exposes only a configured/masked indication, clears stale check facts when the extracted connection changes, and requires browser-window-side write/read-back before any bound Profile changes.

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

ADR-0013 confirms content-pool-first ingestion, `discovery_strategy`, a controlled channel abstraction and four business `crawl_task` statuses. Cloud owns the future business API/enums, source/material relationship and task input/result/error contracts; Agent consumes execution contracts and implements channel adapters. Desktop reuses Cloud Web. Partial-failure mapping and content authorization require confirmed decisions before publication. This planning entry neither changes machine-readable revisions nor claims runtime compatibility, migrations or generated consumers have been updated.
