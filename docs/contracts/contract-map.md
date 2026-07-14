# Contract Map

This is a human-readable index for cross-repo contract ownership and consumers.
Machine-readable ownership and consumer facts live in `../../config/contract-map.yaml`.
Formal OpenAPI, schema, DTO, and event definitions live only in the provider repositories.

Current state is mixed. The machine-readable map is authoritative for exact revisions:

- Cloud API, Cloud-Agent API, business schemas, business enums and Cloud error codes are active formal definitions.
- Local Agent API, local event schemas, local status enums and local error codes are active formal definitions.
- `task_schemas` remains `placeholder_only` and inactive. It must be published by `wt-media-cloud` before non-noop business executors treat task payloads and results as formal contracts.

Historical M0/M1 release entries remain valid evidence for their recorded scaffold/noop scope. They do not imply that the revised M0/M1 end-to-end milestone gates are complete.

## Cloud-Owned Contracts

- `../wt-media-cloud/contracts/cloud-api`
- `../wt-media-cloud/contracts/cloud-agent-api`
- `../wt-media-cloud/contracts/business-schemas`
- `../wt-media-cloud/contracts/task-schemas`
- `../wt-media-cloud/contracts/business-enums`
- `../wt-media-cloud/contracts/cloud-error-codes`

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
