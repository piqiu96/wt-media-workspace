# CHG-20260721-020: M2-A 权限与可信验收基础

## 1. Basic Information

- Level: L
- Status: IN_PROGRESS
- Created: 2026-07-21
- Affected repositories: `wt-media-cloud`, `wt-media-agent`, `wt-media-workspace`
- Current repository: `wt-media-workspace`
- Design: `docs/superpowers/specs/2026-07-21-m2-completion-design.md`
- Plan: `docs/superpowers/plans/2026-07-21-m2-a-implementation-plan.md`

## 2. Change Goal

Restore trustworthy M2 acceptance gates and complete the remaining M2-B～M2-E closures before one final human acceptance. The user explicitly approved postponing manual acceptance until the full M2 implementation is ready. External effects remain subject to staged task creation, read-back, audit, and redaction rules.

## 3. Start Gate

### Current facts

- M2 is `IN_PROGRESS`; the reviewed working estimate is 35/64 complete, with 16 partial and 13 not implemented.
- Cloud Go tests and Agent tests pass on the baseline.
- Web API-client tests currently fail because Node has no absolute base URL for relative fetch paths.
- `verify_m2_acceptance.py` references a removed Desktop path and crashes.
- `verify_product_master_alignment.py` contains obsolete milestone assertions.
- The BitBrowser API is available, but this CHG performs no Profile mutation.

### Gap to this CHG

- Web API-client test gate is red.
- Workspace M2/product-plan validators are not current or deterministic.
- Game-scope authorization is not proven at every M2 business entry point.
- Local Agent session invalidation drains Cloud registry state but requires end-to-end safe-stop verification.
- BitBrowser binding/rebinding does not have an explicit audit action for every outcome.

### File mapping

- Web: `wt-media-cloud/web/src/shared/api/http.js` and API-client tests.
- Governance: `wt-media-workspace/scripts/verify_m2_acceptance.py`, `scripts/verify_product_master_alignment.py`.
- Cloud authorization: `wt-media-cloud/internal/modules/identity`, `mediaaccount`, `profilebinding`, and applicable proxy boundaries.
- Agent session control: `wt-media-cloud/internal/modules/cloudagent`, `wt-media-agent/src/wt_media_agent/cloud_agent_client.py`, `runner.py`.
- Audit: `wt-media-cloud/internal/modules/profilebinding` and identity audit contracts.

### Ordered tasks

1. Establish baseline evidence and this Active CHG.
2. Repair Web API-client test base URL injection.
3. Make governance validators current and deterministic.
4. Enforce game-scope authorization at M2 business entry points.
5. Stop invalidated Local Agent sessions safely.
6. Add explicit BitBrowser binding/rebinding audit events.
7. Run integrated M2-A verification and handoff.

### Verification and acceptance

- Cloud: Go unit, route, store, and integration tests.
- Agent: Python unit tests for Cloud client, runner, checkpoints, and uncertain-result handling.
- Web: Vitest API-client tests and Cloud/Desktop production builds.
- Workspace: both governance validators, diff checks, contract compatibility, redacted evidence.
- Manual: non-secret test users and game scopes; no external Profile mutation in M2-A.

### Risks and blockers

- Existing Cloud working-tree proxy and generated Web `dist-*` changes are unrelated and must not be staged by this CHG.
- Existing workspace report, plan, and `.DS_Store` changes are unrelated and must be preserved.
- Any product/contract conflict discovered during implementation becomes a blocking `Q-xx`; no behavior is inferred.
- Real credentials are available for later M2 acceptance but are prohibited from this CHG's files, logs, tests, and evidence.

### Proposed commit boundaries

- Workspace Active CHG start gate.
- Cloud Web test fix.
- Workspace validator fix.
- Cloud authorization fix.
- Cloud session-drain fix.
- Agent session-drain fix.
- Cloud BitBrowser audit fix.
- Workspace M2-A evidence/checkpoint and confirmed matrix updates.

## 4. Explicitly Not Doing

- No M2-B Profile create/open/close/update implementation.
- No M2-C proxy write/read-back or real proxy executor.
- No M2-D Cookie/SMS/manual account-opening implementation.
- No M2-E Desktop Sidecar completion or final M2 status change.
- No M3+ business models, tasks, or placeholder endpoints.

## 5. Checkpoint

- Completed: Tasks 1–6; Web/gov gates are green, authorization is covered, invalidated sessions drain Cloud/Agent safely, and binding/rebinding emits explicit secret-safe audit actions. Evidence is in `evidence/start-gate.md`, `evidence/task-2-web.md`, `evidence/task-3-governance.md`, `evidence/task-4-authorization.md`, `evidence/task-5-session-invalidation.md`, and `evidence/task-6-binding-audit.md`.
- Current: M2-B foundation is implemented: Profile mutation routes create typed tasks with payloads, Agent has Profile mutation executors, and the acceptance schema includes task payloads and Profile proxy fields.
- Next: complete Profile-specific uncertain-result review, then finish proxy protocol/read-back, Profile assignment, Cookie write/read, and account-opening paths.
- Blockers: None for implementation; final human acceptance is intentionally deferred until M2-B～M2-E are complete.
- Recent verification: Cloud all tests passed; Agent 46/46 passed; Web 8/8 and both workspace validators remain green.

## 6. Evidence Index

- `evidence/start-gate.md` — baseline commands, dirty-tree facts, and start-gate decision.
- `evidence/task-6-binding-audit.md` — binding/rebinding audit behavior and verification.
- `evidence/m2-a-automated-verification.md` — integrated automated verification and manual handoff boundary.

## 7. Pending Questions

None.
