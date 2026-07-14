# Cloud Profile binding verification

- Red: focused tests first failed on the absent Profile binding service/store/routes, media-account Profile resolver, and Web client module.
- Green domain: scan submission validates one normalized owner, preserves existing binding identity, persists staged candidates/Diff only, and has no formal user/Profile effect before confirmation.
- Green persistence: self-confirm applies the Bit user binding, Profile upserts, missing-state transitions, scan confirmation, and audit record in one transaction.
- Green API: authenticated users submit, review, and confirm only their own scans. Actor identity is taken from the C1 session, never from a request-body user ID.
- Green media accounts: only the same user's active Profile can be bound; one Profile/platform pair can belong to only one media account.
- Green Web/contracts: the Web client covers review/confirm and media-account binding; Cloud API/schema/enum/error provider revisions are `2026.07.14.3`.
- Verification: full Go tests and vet, eight Web tests and production build, and sixteen provider YAML parses passed.
- Commits: Cloud `bba30ef` and `727ad9e`.

No live MySQL instance was used in C3. SQL transaction behavior is verified with sqlmock and migration assertions; real migration/integration is reserved for C6.
