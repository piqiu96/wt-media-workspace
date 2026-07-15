# M0-R5 Implementation Plan

> Required Skill: use `executing-wt-media-change`. Keep R5 limited to CI/config engineering gates.

## Task 1: Start Gate

- [ ] Verify exactly one active CHG.
- [ ] Inventory workflow files and current release/contract config.
- [ ] Record git status for all affected repositories.

## Task 2: CI Gates

- [ ] Update Cloud CI to run bootstrap, tests, MySQL migration and build.
- [ ] Update Agent CI to run bootstrap, tests, SQLite migration and build.
- [ ] Update Desktop CI to run bootstrap, lint, test and build.
- [ ] Update Workspace CI to run governance/config/alignment checks.

## Task 3: Config Verification

- [ ] Update Release Matrix toolchain facts.
- [ ] Extend config verification where current facts must be enforced.
- [ ] Run Workspace tests.

## Task 4: Evidence and Commits

- [ ] Record workflow/config/verification evidence.
- [ ] Run diff checks.
- [ ] Commit affected repositories independently.
