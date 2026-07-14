# Contract Map

This is a human-readable index for cross-repo contract ownership and consumers.
Machine-readable ownership and consumer facts live in `../../config/contract-map.yaml`.
Formal OpenAPI, schema, DTO, and event definitions live only in the provider repositories.

M0 status: all listed contract areas are `placeholder_only`. They record ownership and
expected consumers, but no formal `v1` OpenAPI, schema, DTO, or event definition is active yet.

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
