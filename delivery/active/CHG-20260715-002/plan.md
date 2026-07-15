# M0-R1 Implementation Plan

> Required Skill: use `executing-wt-media-change` for execution, evidence, checkpoint and completion.

**Goal:** turn the revised M0 from a high-level gate into a concrete, reproducible engineering checklist by auditing the real local state of Cloud, Web, Agent and Desktop.

**Scope:** evidence-only audit in `wt-media-workspace`; runtime repositories are read-only for this CHG.

## Task 1: Start Gate

- [ ] Verify exactly one Active CHG.
- [ ] Record current facts and gap to CHG.
- [ ] Record real file mapping.
- [ ] Record ordered task list and verification method.
- [ ] Record risks, blockers and commit boundary.
- [ ] Record Git status for `wt-media-workspace`, `wt-media-cloud`, `wt-media-agent` and `wt-media-desktop`.

## Task 2: Toolchain Inventory

- [ ] Record Go toolchain and Cloud command entry points.
- [ ] Record Node/npm toolchain and Web/Desktop command entry points.
- [ ] Record Python/uv toolchain and Agent command entry points.
- [ ] Record Rust/Cargo/Tauri toolchain and Desktop command entry points.
- [ ] Record MySQL availability relevant to M0 migration checks.

## Task 3: Cloud and Web Audit

- [ ] Identify bootstrap, test, build, start/stop, health and migration commands.
- [ ] Run safe local commands or record why they are blocked.
- [ ] Classify each revised M0 gate as PASS, FAIL, BLOCKED or NOT_PRESENT.

## Task 4: Agent Audit

- [ ] Identify package, dependency, test, build, start/stop, health and SQLite migration commands.
- [ ] Run safe local commands or record why they are blocked.
- [ ] Classify each revised M0 gate as PASS, FAIL, BLOCKED or NOT_PRESENT.

## Task 5: Desktop Audit

- [ ] Identify Vue/Tauri dependency, test, build, dev/start and mock-free entry commands.
- [ ] Run safe local commands or record why they are blocked.
- [ ] Classify each revised M0 gate as PASS, FAIL, BLOCKED or NOT_PRESENT.

## Task 6: Governance Audit

- [ ] Run Workspace verifiers.
- [ ] Review `contract-map.yaml`, `release-matrix.yaml` and Master Plan consistency.
- [ ] Confirm M0-R2 through M0-R6 candidate ownership is actionable.

## Task 7: Evidence and Completion

- [ ] Write repository command matrix.
- [ ] Write M0 gap register.
- [ ] Write M1 manual acceptance checklist skeleton.
- [ ] Update `change.md` tasks, acceptance matrix, checkpoint and DONE gate.
- [ ] Run final verification and diff review.
- [ ] Commit only `wt-media-workspace` changes.
