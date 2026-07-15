# M0-R3 Implementation Plan

> Required Skill: use `executing-wt-media-change`. Use TDD for the SQLite migration path because it changes Agent runtime behavior.

## Task 1: Start Gate

- [ ] Verify exactly one Active CHG.
- [ ] Read affected repository rules.
- [ ] Record Agent real file mapping.
- [ ] Record Git status for Workspace, Cloud, Agent and Desktop.

## Task 2: SQLite Migration TDD

- [ ] Write failing unittest for isolated SQLite migration and repeat behavior.
- [ ] Implement minimal storage migration module and command entry.
- [ ] Verify repeat behavior in a temp directory.

## Task 3: Stable Agent Scripts

- [ ] Add real bootstrap/test/build/start/stop/health/migrate scripts where missing.
- [ ] Ensure scripts use `.venv/bin/python` or `uv run` explicitly.
- [ ] Avoid storing secrets in scripts.

## Task 4: Dependency and Build

- [ ] Produce `uv.lock` or record why a different lock artifact is used.
- [ ] Run `uv build` with cache path.
- [ ] Verify package entry points.

## Task 5: Evidence and Completion

- [ ] Run Agent tests/build/health/migration repeat evidence.
- [ ] Record evidence and diff summary.
- [ ] Commit Agent and Workspace independently.
