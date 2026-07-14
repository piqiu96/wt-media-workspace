# Compatibility Policy

Contracts use:

- API major version, such as `v1`;
- contract revision, such as `2026.07.14.1`.

Compatible changes may add optional fields, new enum values with safe defaults, or new endpoints.

Incompatible changes require:

- a decision record under `docs/decisions`;
- a migration plan;
- coordinated updates to provider and consumers;
- an updated release matrix entry.

Runtime components must not dynamically download contract files. They may check compatible versions at startup or before sensitive actions.
