# M0-R2 Implementation Plan

> Required Skill: use `executing-wt-media-change`. Use TDD for the migration runner because it changes Cloud runtime behavior.

## Task 1: Start Gate

- [ ] Verify exactly one Active CHG.
- [ ] Read affected repository rules.
- [ ] Record Cloud/Web real file mapping.
- [ ] Record Git status for Workspace, Cloud, Agent and Desktop.
- [ ] Record command and acceptance method for each task.

## Task 2: Migration Runner TDD

- [ ] Write a failing Go test for repeatable migration execution using a SQL mock or isolated test database abstraction.
- [ ] Implement the minimal runner.
- [ ] Add a CLI command or script path that can execute migrations from `WT_MEDIA_MYSQL_DSN`.
- [ ] Verify repeat behavior.

## Task 3: Stable Cloud Scripts

- [ ] Add real bootstrap/test/build/start/stop/health/migrate scripts where missing.
- [ ] Ensure scripts use local cache paths where needed.
- [ ] Avoid storing secrets in scripts.

## Task 4: Web Path

- [ ] Confirm Web dependency bootstrap command.
- [ ] Run Web tests/build.
- [ ] Add start/static preview evidence if needed by M0.

## Task 5: Evidence and Completion

- [ ] Run Cloud Go tests/build/health.
- [ ] Run local MySQL migration empty/repeat evidence.
- [ ] Run Web tests/build/start evidence.
- [ ] Record evidence and diff summary.
- [ ] Commit Cloud and Workspace independently.
