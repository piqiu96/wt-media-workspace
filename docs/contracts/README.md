<!-- governance: class=stable default_load=task -->

# Contract Governance

This directory holds human-readable governance for cross-repository contracts. The interface provider owns each formal definition; the OpenAPI, schema, DTO, and enum files live in the owning repository, not here.

## Index

- [Ownership](ownership.md): which repository owns each contract area.
- [Contract map](contract-map.md): current active contract revisions and their providers.
- [Compatibility policy](compatibility-policy.md): how compatible changes are reviewed.
- [Breaking-change policy](breaking-change-policy.md): what requires a new contract revision or migration.

## Boundary

- Do not copy an OpenAPI or schema file into this directory.
- When a revision changes, update the provider definition first, then this index and the consumer lock in the owning consumer repository.
- Contract revision evidence belongs in the CHG; this directory records only the stable governance rule.
