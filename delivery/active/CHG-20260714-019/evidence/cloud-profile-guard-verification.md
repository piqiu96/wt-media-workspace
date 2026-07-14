# Cloud Profile guard verification

- Red: domain/MySQL/route tests first failed on absent Profile guard types, store, migration and routes.
- Only an internal pre-authorized task can be preflighted; there is no public generic task-creation or arbitrary command endpoint.
- Preflight authenticates the C4 node/session and atomically validates assigned user/node/Profile/operation, active confirmed Profile, bound owner, normal BitBrowser state and runtime presence no older than 90 seconds.
- Profile row locking serializes permit decisions. Active conflict returns `waiting`; an expired unreleased permit and task move to `review_required` and are not reused.
- Permit credentials are returned once and only SHA-256 hashes persist. Renewals are capped at two minutes; finish is `completed` or `result_uncertain`.
- Full verification: all Go tests, Go vet and twenty Cloud YAML definitions pass.
- Process health: the same Cloud health script passed in C4. A C5 repeat was rejected by the Codex escalation quota; fresh app and route suites cover the changed wiring, and no workaround was attempted.
- Commits: Cloud `d1d0ddc`, `2753715`.

No live MySQL or real publication/interaction executor is used in C5. Real migration, multi-process contention and end-to-end failure recovery are C6 acceptance gates; actual platform executors remain explicitly outside C5.
