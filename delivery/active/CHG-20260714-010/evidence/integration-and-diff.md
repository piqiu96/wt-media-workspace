# Evidence: Integration And Diff

- CHG: `CHG-20260714-010`
- Task: `T-04`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Purpose

Prove the M1-C3 task creation/claim/lease slice works without introducing execution, progress, Local Agent SSE, Desktop, or account/Profile behavior.

## Method

Commands:

```text
python3 -m unittest discover -s tests
python3 scripts/verify_skills.py
python3 scripts/verify_m0_config.py
go test ./...
PYTHONPATH=src python3 -m unittest discover -s tests
npm run verify
curl POST /api/v1/tasks/noop
curl POST /api/v1/cloud-agent/tasks/claim
rg -n "executor|progress|succeeded|failed|SSE|Desktop|account|profile|SQLite|result upload" ...
```

## Expected

- Workspace, Cloud, Agent, and Desktop verification pass.
- Cloud-Agent latest contract revision is `v1@2026.07.14.3`.
- Diff scan shows no executor, progress, result upload, SSE, Desktop, account, or Profile implementation.

## Actual

```text
Workspace: Ran 6 tests; OK
Workspace skills: verified 8 skill source files
Workspace config: Workspace config verification ok
Cloud: go test ./... passed
Agent: Ran 13 tests; OK
Desktop: wt-media-desktop health ok
```

Diff interpretation:

```text
Cloud matches are limited to generic error names and Not Active Yet documentation.
Agent has no out-of-scope matches.
```

## Follow-Up

- Commit Workspace evidence/config snapshot.
- Push affected repositories.
- Remove completed active record.
