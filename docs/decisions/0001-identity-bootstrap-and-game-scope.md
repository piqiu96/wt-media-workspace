# Decision 0001: Identity Bootstrap and Game-Scope Keys

## Status

Accepted

## Context

M2-C1 requires username/password authentication, technical-user provisioning, a single active session, and game-scoped authorization. The product baseline requires that users are created by technical users and that ordinary and senior operators are assigned to games, but it does not define how an empty deployment gets its first technical user or a separate game-catalog module.

## Decision

- On an empty Cloud MySQL database, the deployment may create one initial `technician` user only when both `WT_MEDIA_INITIAL_TECHNICIAN_USERNAME` and `WT_MEDIA_INITIAL_TECHNICIAN_PASSWORD` are explicitly configured.
- The bootstrap password is hashed before persistence, is never logged, and is not reset on later process starts. The application has no built-in default user or password.
- C1 represents assignments using opaque stable `game_id` strings. It does not create a game catalog, game CRUD API, or organization hierarchy. Later business modules must use the same identifiers when applying game scopes.
- Browser authentication uses a server-side opaque session and an HttpOnly, SameSite=Lax cookie. The session token and password material are not returned in JSON, audit logs, or normal logs.

## Consequences

- Positive: an empty deployment can become operable without a hidden default credential; C1 stays within the fixed-role and no-organization scope.
- Negative: deployment automation must securely supply two bootstrap environment variables once; technicians must use stable game IDs until a separately approved game-master-data change exists.
- Follow-up: M2-C4 binds Local Agent work to the active Cloud session, and later business modules apply `game_id` scope checks to their own resources.
