# M0-R6 Implementation Plan

> Required Skill: use `executing-wt-media-change`. R6 is an evidence and acceptance CHG.

## Task 1: Start Gate

- [ ] Verify exactly one active CHG.
- [ ] Record clean runtime repository status.
- [ ] Confirm MySQL DSN and temp Agent data dir.

## Task 2: Run Checks

- [ ] Workspace governance/config/alignment checks.
- [ ] Cloud/Web bootstrap, tests, MySQL migration repeat, build, start, health, stop.
- [ ] Agent bootstrap, tests, SQLite migration repeat, build, start-health, health, stop-health.
- [ ] Desktop bootstrap, lint, tests, build, start, health, stop.

## Task 3: Evidence and Closure

- [ ] Record evidence.
- [ ] Update Master Plan M0 status if all gates pass.
- [ ] Diff check.
- [ ] Commit Workspace.
