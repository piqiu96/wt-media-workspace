# Evidence: Integration And Diff

- CHG: `CHG-20260714-008`
- Task: `T-05`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Purpose

Prove the M1-C1 Cloud-Agent compatibility slice works across affected repositories and does not introduce later M1/M2 behavior.

## Method

Commands:

```text
python3 -m unittest discover -s tests
python3 scripts/verify_skills.py
python3 scripts/verify_m0_config.py
go test ./...
PYTHONPATH=src python3 -m unittest discover -s tests
npm run verify
curl --silent --show-error --fail http://127.0.0.1:18080/api/v1/cloud-agent/compatibility
rg -n "registration|register|heartbeat|task polling|task lease|progress|result upload|account|profile|Desktop|SSE" ...
```

## Expected

- Workspace, Cloud, Agent, and Desktop verification pass.
- Cloud compatibility endpoint returns `v1@2026.07.14.1`.
- Diff scan shows no Agent registration, heartbeat, task execution, Desktop page, account, or Profile implementation.

## Actual

Verification results:

```text
Workspace: Ran 6 tests; OK
Workspace skills: verified 8 skill source files
Workspace config: Workspace config verification ok
Cloud: go test ./... passed
Agent: Ran 9 tests; OK
Desktop: wt-media-desktop health ok
```

Cloud endpoint response:

```json
{"data":{"api":"cloud-agent","major_version":"v1","contract_revision":"2026.07.14.1","minimum_agent_contract_revision":"2026.07.14.1","compatible_agent_major_versions":["v1"],"status":"compatible"}}
```

Diff scan interpretation:

```text
Cloud matches:
- internal/app/app.go registerHealthRoutes is existing health route naming.
- contracts/cloud-agent-api/README.md lists registration, progress, and result upload under Not Active Yet.

Agent matches:
- contracts/README.md mentions local SSE as an Agent-owned placeholder area.
```

No out-of-scope implementation was introduced.

## Follow-Up

- Commit final Workspace evidence snapshot.
- Push affected repositories.
- Remove completed active record after Git history preserves this evidence.
