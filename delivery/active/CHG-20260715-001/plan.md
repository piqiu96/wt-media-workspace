# Product and Master Plan Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-wt-media-change` and `superpowers:executing-plans` to execute this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce one internally consistent product and implementation baseline in which M0/M1 deliver a real end-to-end environment, M2 is replanned for the complete account domain, and M3-M10 use canonical objects and correct dependency gates.

**Architecture:** Treat consolidated PRD and responsible detailed chapters as product truth, then align engineering/contract governance and finally regenerate the Master Plan from a capability crosswalk. Historical code and releases remain evidence, but revised milestone exit gates decide current status.

**Tech Stack:** Markdown product/engineering/delivery documents, YAML governance maps, Python static verification, Git repository evidence.

## Global Constraints

- Only `wt-media-workspace` may be modified.
- No runtime feature implementation or provider-owned formal contract activation is allowed.
- Historical commits and completed CHG evidence remain in Git history.
- Current operational design must not depend on `content_lead`, independent `crawl_result`, `interaction_batch`, `interaction_item`, or `production_signal`.
- Exactly one Active CHG is allowed.
- Every task ends with verification, diff review, evidence, checkpoint and an independent Workspace commit.

---

### Task 1: Normalize Product Facts

**Files:**
- Modify: `docs/product/prd/社媒运营平台_产品需求说明书_V1.md`
- Modify: `docs/product/prd/详细文档/第二章_系统架构.md`
- Modify: `docs/product/prd/详细文档/第三章_用户与账号管理.md`
- Modify: `docs/product/prd/详细文档/第四章_内容发现.md`
- Modify: `docs/product/prd/详细文档/第五章_素材生产.md`
- Modify: `docs/product/prd/详细文档/第六章_发布管理.md`
- Modify: `docs/product/prd/详细文档/第七章_互动管理.md`
- Modify: `docs/product/prd/详细文档/第八章_数据统计.md`
- Create: `delivery/active/CHG-20260715-001/evidence/product-milestone-crosswalk.md`

**Interfaces:**
- Consumes: D-04 through D-09 in `change.md`.
- Produces: canonical object/status/ownership facts consumed by Tasks 2-4.

- [ ] **Step 1: Capture the failing stale-term and ownership scan**

  Run contextual `rg -n` scans for the five excluded objects, `waiting_manual_submit`, publication discard wording, undefined account-group wording, and delayed `tracked_object` creation. Record only operational conflicts in the crosswalk evidence.

- [ ] **Step 2: Correct the product baseline minimally**

  Replace operational `content_lead` usage with `source_content`; remove independent result/batch/item/signal objects; normalize publication state to `pending_manual_submit` and `cancelled`; define first-version account groups as saved tag/filter snapshots unless a later decision creates a formal object; make M6/M8 the creation providers for `tracked_object`.

- [ ] **Step 3: Verify chapter authority and full capability coverage**

  Compare Chapter 3 account capabilities and Chapters 4-8 business flows to the consolidated PRD. Expected result: every P0/P1 capability has exactly one owning chapter and no contradictory lifecycle.

- [ ] **Step 4: Record evidence and checkpoint**

  Update `evidence/product-milestone-crosswalk.md` with source path, capability, owner, milestone and resolution; update `change.md` T-02/checkpoint.

- [ ] **Step 5: Commit**

  Commit only product baseline, crosswalk evidence and checkpoint changes with message `docs: normalize product facts for milestone planning`.

### Task 2: Align Engineering and Contract Governance

**Files:**
- Modify: `docs/engineering/architecture/模块化自媒体运营平台_系统架构设计说明书_V1.md`
- Modify: `docs/contracts/contract-map.md`
- Modify if factual wording requires it: `config/contract-map.yaml`
- Modify if historical release descriptions require clarification: `config/release-matrix.yaml`
- Modify: `delivery/active/CHG-20260715-001/change.md`

**Interfaces:**
- Consumes: Task 1 canonical facts.
- Produces: explicit delivery prerequisites for Master Plan tasks.

- [ ] **Step 1: Capture current infrastructure gaps**

  Verify Desktop dev/build/package commands, Tauri entry, Local Agent service source, Cloud task/registry persistence, scheduler/object-store state and `task_schemas` status against the architecture.

- [ ] **Step 2: Correct ownership and readiness descriptions**

  State that M0/M1 must provide real build/run paths, persistent task and Agent facts, offline result recovery, real Tauri/Local Agent control and formal task schemas before business executors. Keep `task_schemas` inactive until the provider publishes the definition.

- [ ] **Step 3: Synchronize human and machine governance wording**

  Update the human-readable contract map from its stale M0-only statement to the actual mixed active/placeholder state. Preserve machine revisions unless a factual description field requires change.

- [ ] **Step 4: Verify and commit**

  Run `python3 scripts/verify_m0_config.py`; inspect diff for provider-owned contract edits. Expected result: PASS and no runtime repository change. Commit with message `docs: align engineering readiness and contract governance`.

### Task 3: Rebuild M0 and M1

**Files:**
- Modify: `delivery/MASTER_IMPLEMENTATION_PLAN.md`
- Modify: `delivery/active/CHG-20260715-001/change.md`
- Modify: `delivery/active/CHG-20260715-001/evidence/product-milestone-crosswalk.md`

**Interfaces:**
- Consumes: Task 2 readiness prerequisites.
- Produces: a real end-to-end environment gate required by M2.

- [ ] **Step 1: Reset milestone status semantics**

  Set M0 to `IN_PROGRESS` and M1 to `NOT_STARTED` until their revised gates pass. Preserve former CHG/commit lists as inherited scaffold evidence, remove completion dates as current completion claims, and state explicitly that historical evidence is reusable but insufficient.

- [ ] **Step 2: Define M0 real component gates**

  Require real Cloud, Agent and Desktop dependency installation, build, test, start/stop, health checks, configuration, MySQL migration path and CI verification. Echo scripts, unavailable Cargo checks and mock-only entry points fail the gate.

- [ ] **Step 3: Define M1 persistent end-to-end gates**

  Require MySQL-backed task/Agent state, formal task schemas, Agent lease/recovery/offline result persistence, real Local Agent API/SSE, real Tauri bridge/process control, Cloud Web loading, login, task creation, execution, progress and restart recovery in one manual demonstration.

- [ ] **Step 4: Verify and commit**

  Cross-check every gate against current code facts and mark missing items as candidate CHGs, never PASS. Commit with message `docs: reopen m0 m1 for real end-to-end acceptance`.

### Task 4: Replan M2 Completely

**Files:**
- Modify: `delivery/MASTER_IMPLEMENTATION_PLAN.md`
- Modify: `delivery/active/CHG-20260715-001/change.md`
- Modify: `delivery/active/CHG-20260715-001/evidence/product-milestone-crosswalk.md`

**Interfaces:**
- Consumes: Chapter 3 capabilities and completed M1 gate.
- Produces: newly numbered M2-C1 through M2-C11 route.

- [ ] **Step 1: Reset M2 to `NOT_STARTED`**

  Record C1-C6 as inherited implementation/evidence only. Require each new CHG to audit and reuse valid code instead of assuming historical PASS or rewriting blindly.

- [ ] **Step 2: Define the new M2 route**

  Use these bounded deliverables:

  1. M2-C1 authentication, single-active session, roles, game scope and user administration UI.
  2. M2-C2 media accounts, lifecycle, tags, assignment and account workbench.
  3. M2-C3 BitBrowser main-tree binding, Profile scan, Diff and Cloud assignment.
  4. M2-C4 window/Profile create, update, open, check, archive and recovery UI.
  5. M2-C5 proxy import, parse, check, quota, assignment and readback.
  6. M2-C6 Cookie import/export/read/write, active Cookie and account health checks.
  7. M2-C7 bulk Cookie, SMS-link and manual-verification onboarding with partial-success retry.
  8. M2-C8 Agent node binding, runtime reporting and environment health UI.
  9. M2-C9 Profile concurrency, sensitive-task preflight, uncertain-result review and audit.
  10. M2-C10 integrated Web/Desktop account-environment workbench and role-specific UX.
  11. M2-C11 real MySQL, BitBrowser, proxy, Cookie, Desktop and three-role product acceptance.

- [ ] **Step 3: Define complete exit gates**

  Require automated contracts/tests, real dependency evidence, role-based UI acceptance, batch partial-failure behavior, secret safety, audit logs, recovery and independent commits.

- [ ] **Step 4: Verify and commit**

  Map every Chapter 3 P0/P1 row to one new M2 CHG. Expected result: no uncovered row and no duplicate owner. Commit with message `docs: replan complete m2 account environment milestone`.

### Task 5: Correct M3 through M10

**Files:**
- Modify: `delivery/MASTER_IMPLEMENTATION_PLAN.md`
- Modify: `delivery/active/CHG-20260715-001/change.md`
- Modify: `delivery/active/CHG-20260715-001/evidence/product-milestone-crosswalk.md`

**Interfaces:**
- Consumes: Tasks 1-4 canonical facts and infrastructure gates.
- Produces: executable downstream candidate CHGs.

- [ ] **Step 1: Correct M3 and M4**

  Split instant query from scheduled crawl; use only `source_content -> material`; add external API spike, scheduler/idempotency, material lifecycle, public/private review, download/hash validation, usage abandon/recover, local file index and real FFmpeg/Agent acceptance.

- [ ] **Step 2: Correct M5 through M7**

  Restore `compose_pool_item -> task` to cloud production; add risk review, object integrity, claim release and stuck recovery; normalize publication states; create `tracked_object` on valid publication; include publication workbench, manual backfill/link validation and Bilibili/Baijiahao regression.

- [ ] **Step 3: Correct M8 and M9**

  Use one `interaction_task` per `tracked_object` and an actual task per account; add external targets, risk, pause/cancel, captcha takeover and precise retry. Keep M9 to immutable `platform_metric_snapshot`, collection, aggregation, dashboard, environment statistics, export and reconciliation.

- [ ] **Step 4: Correct M10**

  Keep first real Desktop integration in M0/M1. Define M10 as Cloud deployment/TLS, migrations/backups/restore, object-storage recovery, dependency locking, installers, macOS signing/notarization, compatibility/update/rollback, logging/diagnostics, status/alerts and full recovery drills.

- [ ] **Step 5: Verify and commit**

  Run canonical-object and dependency-order scans. Expected result: no operational forbidden object and every infrastructure capability precedes its first consumer. Commit with message `docs: correct downstream milestone decomposition`.

### Task 6: Add Alignment Verification and Final Evidence

**Files:**
- Create: `scripts/verify_product_master_alignment.py`
- Create: `tests/test_verify_product_master_alignment.py`
- Create: `delivery/active/CHG-20260715-001/evidence/verification-summary.md`
- Create: `delivery/active/CHG-20260715-001/evidence/diff-summary.md`
- Modify: `delivery/active/CHG-20260715-001/change.md`
- Modify: `delivery/LEDGER.md`
- Generated root context: `.ai/CURRENT_CONTEXT.md`

**Interfaces:**
- Consumes: all corrected baselines and Master Plan.
- Produces: repeatable proof that future edits cannot silently restore the reviewed contradictions.

- [ ] **Step 1: Write failing verifier tests**

  Test exactly-one Active CHG, revised M0/M1/M2 statuses and gates, required M2 capability labels, canonical object exclusions in operational plan sections, `tracked_object` ordering, M10 packaging coverage and contract-map human/machine state wording.

- [ ] **Step 2: Run tests and confirm failure before verifier implementation**

  Run `python3 -m unittest tests.test_verify_product_master_alignment -v`. Expected result: FAIL because the verifier module or checks do not yet exist.

- [ ] **Step 3: Implement the minimal verifier**

  Add deterministic file reads and explicit error messages without parsing legacy root `docs/` or runtime code as requirements.

- [ ] **Step 4: Run the full verification matrix**

  Run:

  ```text
  python3 scripts/verify_product_master_alignment.py
  python3 scripts/verify_m0_config.py
  python3 -m unittest discover -s tests
  python3 scripts/prepare_ai_workspace.py --change CHG-20260715-001 --no-write
  git diff --check
  ```

  Expected result: all commands exit 0 and only Workspace files appear in the CHG diff.

- [ ] **Step 5: Record evidence and checkpoint**

  Record command, expected result, actual result and status in `verification-summary.md`; record every changed file and scope reason in `diff-summary.md`; update every AC and DONE gate from evidence only.

- [ ] **Step 6: Commit**

  Commit verifier, tests, evidence and checkpoint with message `test: verify product and master plan alignment`.

## Execution Handoff

The CHG package is intentionally paused after activation so the user can review scope, decisions, task boundaries and acceptance criteria before Task 1 modifies stable baselines.
