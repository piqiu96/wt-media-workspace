# Cloud runtime binding verification

- Red: focused tests first failed on absent ticket/node/runtime types, MySQL store, migration, routes, and server-side session context.
- Ticket: current authenticated session ID is bound server-side; raw ticket is returned once, only SHA-256 hash is stored, expiry and one-use consumption are enforced transactionally.
- Node: raw credential is returned once, only its hash is stored, a newer registration replaces the old device node, and replaced/invalid-session credentials cannot report.
- Runtime: all statuses are allow-listed and Profile presence is accepted only when node user, confirmed user Bit owner, reported owner and every active confirmed Profile agree.
- Separation: `browser_profile_runtime_presence` has its own table and never mutates `browser_profiles.user_id`; no task eligibility or lock exists in C4.
- Full verification: all Go tests, Go vet, and eighteen Cloud provider YAML parses pass.
- Commits: Cloud `6ef0308`, `866364e`, and contract clarification `9770e1b`.

Live MySQL migration and a real Desktop-to-Agent binding-ticket transport were not available in C4; both are explicit M2-C6 integration gates.
