# M0-R4 Implementation Plan

> Required Skill: use `executing-wt-media-change`. Do not install system toolchains without explicit approval.

## Task 1: Start Gate

- [ ] Verify exactly one Active CHG.
- [ ] Read Desktop repository rules.
- [ ] Record Desktop file mapping and Git status.
- [ ] Record Rust/Cargo/Tauri availability.

## Task 2: Toolchain Resolution

- [ ] Use existing Rust/Cargo if available.
- [ ] If unavailable, request approval for installation.
- [ ] Record result in evidence.

## Task 3: Desktop Scripts and Build

- [ ] Replace echo scripts with real commands.
- [ ] Install/update Desktop dependencies and lockfiles.
- [ ] Run test/build/dev or record blocker.

## Task 4: Evidence and Completion

- [ ] Record command matrix and diff summary.
- [ ] Commit Desktop and Workspace independently.
