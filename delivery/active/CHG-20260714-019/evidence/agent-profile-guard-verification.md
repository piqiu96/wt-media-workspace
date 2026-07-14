# Agent Profile guard verification

- Red: tests first failed because the local Profile lock/guard and Cloud client methods did not exist.
- Green: `ProfileLockManager` is process-local and exclusive by Profile; it is acquired before Cloud preflight and always released locally.
- Cloud `waiting` prevents execution without failing the task. `review_required` also prevents execution.
- Normal completion explicitly finishes the permit; an executor exception reports `result_uncertain`, preserving the no-blind-retry rule.
- Preflight, renew and finish use the node bearer credential; renew/finish additionally require the one-time Profile permit credential.
- Full verification: 38 Python tests and six Agent YAML definitions pass.
- Process health: the same Python 3.12 health script passed in C4. A C5 repeat was rejected by the Codex escalation quota; C5 does not modify the Local API server entrypoint, and no workaround was attempted.
- Commits: Agent `5cd9212`, `3d4081a`.
