# CHG-20260715-001: 产品基线与 Master Plan 端到端对齐

## 1. Basic Information

- Level: L
- Status: VERIFYING
- Created: 2026-07-15
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`

## 2. Change Goal

重新对齐当前产品事实、工程事实和 M0-M10 实施路线：把 M0/M1 重新定义为完成后能够通过真实 Cloud、MySQL、Agent、Desktop 和 Web 端到端人工验收的工程环境；把 M2 按完整用户、账号、窗口、代理、Cookie、开户、运行环境和权限范围重新规划并重新执行；修正 M3-M10 的对象、依赖、状态和漏项，使后续每个 CHG 都能从唯一产品事实推导并独立验收。

本 CHG 只修订稳定基线、治理映射和实施计划，不实现任何运行时业务功能。

## 3. Baseline References

- Product baseline:
  - `docs/product/prd/社媒运营平台_产品需求说明书_V1.md`
  - `docs/product/prd/详细文档/第一章_项目概述.md`
  - `docs/product/prd/详细文档/第二章_系统架构.md`
  - `docs/product/prd/详细文档/第三章_用户与账号管理.md`
  - `docs/product/prd/详细文档/第四章_内容发现.md`
  - `docs/product/prd/详细文档/第五章_素材生产.md`
  - `docs/product/prd/详细文档/第六章_发布管理.md`
  - `docs/product/prd/详细文档/第七章_互动管理.md`
  - `docs/product/prd/详细文档/第八章_数据统计.md`
- Engineering baseline: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Contract governance: `docs/contracts/contract-map.md`, `config/contract-map.yaml`
- Release governance: `config/release-matrix.yaml`
- Decisions: `docs/decisions/0002-bitbrowser-profile-identity-normalization.md`
- Master route: `delivery/MASTER_IMPLEMENTATION_PLAN.md`
- Audit evidence: `evidence/baseline-audit-20260715.md`

## 4. Current Facts

- CHG-20260714-020 closed the M2 C1-C6 foundation acceptance with real MySQL and BitBrowser evidence; it did not deliver the complete user/account product domain.
- M0 and M1 are marked `DONE`, but Desktop build/package remain scaffold commands, the Desktop entry still uses a mock Local Agent service, and Cloud task/Agent registries remain in memory.
- The current M2 plan does not include complete user management UI, browser window/Profile management, proxy management, Cookie operations, account checks, or the three onboarding paths required by Chapter 3.
- The current M3 plan still uses `crawl_result` and `content_lead`, although the product baseline defines `source_content` as canonical and explicitly excludes an independent `crawl_result`.
- The current M8 plan still uses `interaction_batch` and `interaction_item`, although the product baseline explicitly excludes both as core objects.
- `tracked_object` must be created when publication succeeds or an external interaction target is recorded; it cannot first appear in M9.
- `task_schemas` are still `placeholder_only` and must become formal before real business executors depend on them.
- Human-readable contract governance and generated AI context have drifted from the current machine-readable facts.

## 5. Scope

### Add

- A product-to-milestone capability crosswalk covering all P0/P1 requirements and explicit exclusions.
- Corrected M0/M1 remediation CHGs and end-to-end acceptance gates.
- A newly numbered M2 execution route that reuses valid existing code only after re-verification and closes the complete product/UI/runtime scope.
- Corrected M3-M10 candidate CHGs, dependency gates, canonical objects, real-integration gates, and manual acceptance requirements.
- Automated static checks for forbidden stale object usage and milestone/contract governance consistency.

### Modify

- Consolidated PRD and detailed Chapters 2-8 where stale terminology or cross-chapter ownership conflicts remain.
- Engineering architecture where the real Desktop/Agent/task persistence delivery point is ambiguous.
- `delivery/MASTER_IMPLEMENTATION_PLAN.md` in full, including current statuses, inherited evidence, candidate CHGs, dependencies and exit conditions.
- Human-readable contract map, machine-readable governance descriptions, release evidence wording, and generated AI context.

### Delete

- Operational use of `content_lead`, independent `crawl_result`, `interaction_batch`, `interaction_item`, and `production_signal` from current product and implementation plans.
- Any statement that treats scaffold-only Desktop checks or in-memory task infrastructure as production-complete end-to-end evidence.

Historical Git evidence and migration/replacement tables are retained; deletion applies only to current operational design.

### Explicitly Not Doing

- Implementing or modifying Cloud, Agent, Desktop, Web, MySQL schema, scheduler, object storage, proxy, Cookie, publication, interaction, or packaging runtime behavior.
- Marking M0, M1, M2, or any later milestone `DONE` in this alignment CHG.
- Activating placeholder task schemas before a provider-owned formal contract exists.
- Deleting historical commits, completed CHG evidence from Git history, or valid C1-C6 runtime code.
- Creating a new top-level M11 business milestone.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | M0/M1 are reopened in the Master Plan. M0 establishes independently buildable/runnable real components; M1 completes a persistent Cloud-Agent-Desktop-Web end-to-end environment that can be manually accepted without mocks. | CONFIRMED |
| D-02 | Historical M0/M1 commits remain inherited evidence, but scaffold checks, echo build/package commands, mock Desktop services, and in-memory registries cannot satisfy the revised exit gates. | CONFIRMED |
| D-03 | M2 is replanned and re-executed from a newly numbered complete route. Existing C1-C6 code may be reused after audit, but their historical PASS status does not automatically close any new product-level CHG. | CONFIRMED |
| D-04 | Canonical content discovery flow is `crawl_strategy -> crawl_task` for scheduled work and direct query for instant work; selected results become `source_content -> material`. No independent `crawl_result` or `content_lead` is built. | CONFIRMED |
| D-05 | Interaction uses `tracked_object -> interaction_task -> account-level task`; batch selection is an operation, not an `interaction_batch` object, and no `interaction_item` is built. | CONFIRMED |
| D-06 | `production_signal` is not built. Production hints and repeat-risk views are derived from formal business facts and `platform_metric_snapshot`. | CONFIRMED |
| D-07 | One Cloud user binds at most one BitBrowser main account tree; the same `main_user_id` may be shared by multiple Cloud users/operators; authorization is enforced by Cloud Profile assignment, while `profile_user_id` remains audit metadata. | CONFIRMED |
| D-08 | `tracked_object` is created or reused by M6 after a valid published result and by M8 for external targets; M9 only collects and aggregates metrics. | CONFIRMED |
| D-09 | Real Desktop/Tauri/Local Agent integration is an M0/M1 prerequisite and an earlier business acceptance dependency; M10 owns final installers, signing, update, diagnostics and recovery rather than the first real Desktop integration. | CONFIRMED |
| D-10 | The M0-M10 top-level route is retained; completeness is achieved by correcting CHG decomposition and gates rather than adding M11. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

Each task follows:

```text
failing verification
→ minimal baseline/plan correction
→ verification
→ diff check
→ evidence
→ checkpoint
→ independent Workspace commit
```

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Activate the independent alignment CHG and record the approved audit/decisions. | DONE | Single Active CHG scan; `evidence/baseline-audit-20260715.md`. |
| T-02 | Normalize product terminology, object ownership and cross-chapter status rules. | DONE | Stale-object contextual scan plus product cross-reference review. |
| T-03 | Correct engineering/contract governance descriptions for real Desktop, persistent task infrastructure and formal schema gates. | DONE | Architecture/contract-map consistency scan. |
| T-04 | Rewrite M0/M1 as real component and end-to-end environment milestones and reset their status/evidence semantics. | DONE | Exit-gate checklist against current code facts. |
| T-05 | Replace M2 with the complete newly numbered product execution route and product-level acceptance. | DONE | Chapter 3 capability crosswalk with no uncovered P0/P1 row. |
| T-06 | Correct M3-M10 flows, objects, dependencies, missing CHGs and acceptance gates. | DONE | Chapters 4-8 and architecture crosswalk; forbidden-object scan. |
| T-07 | Align Ledger, human/machine contract governance, release wording and generated AI context. | DONE | Workspace governance scripts and single Active CHG verification. |
| T-08 | Run full Workspace regression, record diff/coverage evidence, and prepare the CHG for user review/closure. | DONE | `verify_m0_config.py`, Workspace tests, new alignment verifier, `git diff --check`. |

## 9. Repository Checklist

### wt-media-workspace

- [x] Product baseline terminology and ownership corrected.
- [x] Engineering and contract governance boundaries corrected.
- [x] M0/M1 reset to real end-to-end gates.
- [x] M2 replanned and renumbered completely.
- [x] M3-M10 corrected and cross-checked.
- [x] Static verifier and evidence added.
- [x] Ledger, generated context and checkpoint aligned.

### wt-media-cloud

- [x] Not affected; runtime implementation is explicitly deferred to later CHGs.

### wt-media-agent

- [x] Not affected; runtime implementation is explicitly deferred to later CHGs.

### wt-media-desktop

- [x] Not affected; runtime implementation is explicitly deferred to later CHGs.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Only CHG-20260715-001 is Active and all approved decisions are recorded without an open blocking question. | Active directory/Ledger/context scan. | PASS |
| AC-02 | M0/M1 completion requires independently real builds plus a persistent, mock-free Cloud-Agent-Desktop-Web end-to-end manual acceptance environment. | Master exit-gate review against architecture. | PASS |
| AC-03 | M2 contains user management, media accounts, Profile/window management, proxy management, Cookie/account checks, onboarding, runtime binding, sensitive-task guard, UI and real acceptance. | Chapter 3 capability crosswalk. | PASS |
| AC-04 | M3-M10 use only canonical objects and place `tracked_object`, task schemas, scheduler, object storage and Desktop dependencies before their first consumer. | Cross-milestone dependency and forbidden-object scan. | PASS |
| AC-05 | Product, engineering, contract governance and Master Plan agree on BitBrowser main/sub-account identity and Cloud authorization. | D-07 reference scan and terminology verifier. | PASS |
| AC-06 | Every milestone has automated, real dependency, UI/manual, recovery/security and independent-commit gates where applicable. | Milestone acceptance crosswalk. | PASS |
| AC-07 | Workspace automated verification passes and diff contains no runtime-repository edits. | Full Workspace regression and repository status check. | PASS |

## 11. Evidence

- `evidence/baseline-audit-20260715.md`
- `evidence/product-milestone-crosswalk.md`
- `evidence/verification-summary.md`
- `evidence/diff-summary.md`

Evidence records facts and verification results; requirements remain in stable baselines and this change record.

## 12. Current Checkpoint

Completed:
- CHG-020 was closed under its original C1-C6 foundation scope with independent repository commits.
- User confirmed D-01 through D-10: reopen M0/M1, replan/re-execute M2, normalize canonical objects, and retain the M0-M10 top-level route.
- Baseline audit and the independent alignment CHG were created.
- A section-for-section Chinese review companion was created at `change.zh-CN.md`; `change.md` remains the execution authority.
- T-02 normalized `source_content`, publication cancellation metrics, account-group semantics, tracked-object ownership, and shared BitBrowser main-tree authorization language across the product baseline.
- T-03 aligned the engineering architecture, human contract map and release-matrix planning note with real Desktop, persistent task/Agent state, scheduler/object-storage ordering and formal task-schema gates.
- T-04 reopened M0 as `IN_PROGRESS`, reset M1 to `NOT_STARTED`, retained historical scaffold/noop evidence, and defined M0-R1..R6 plus M1-R1..R8 real component and mock-free end-to-end gates.
- T-05 reset M2 to `NOT_STARTED` and mapped the complete Chapter 3 account/environment domain to M2-C1..C11, with historical C1-C6 code and evidence retained only as reusable inputs.
- T-06 corrected M3-M10 canonical flows, restored missing task/infrastructure dependencies, expanded candidate CHGs and added automated/real/UI/recovery/security acceptance gates.
- T-07 synchronized the Ledger, mixed contract/release wording and generated root AI context with the unique Active CHG.
- T-08 added a test-first alignment verifier, passed the full 12-test Workspace regression and recorded scope/verification evidence.

Current:
- Final user review before closing and removing the completed Active record.

Next:
- After review confirmation, mark the CHG `DONE`, remove it from `delivery/active` and clear the Active Ledger row according to governance.

Blocked:
- None.

Recent verification:
- CHG-020 final closure matrix passed on 2026-07-15 before this CHG was activated.
- Active CHG discovery and generated AI context both resolve uniquely to CHG-20260715-001; no blocking question exists.
- Chinese review companion D/T/AC identifiers match the authoritative change record one-for-one.
- Product stale-term scan now leaves removed objects only in explicit exclusion, migration, or historical-reference contexts.
- `python3 scripts/verify_m0_config.py` passes with the mixed active/placeholder contract state documented consistently.
- M0/M1 exit-gate review now rejects echo builds, Mock-only Desktop entry points, in-memory production task state and placeholder task schemas.
- Chapter 3 crosswalk maps every user/account/Profile/proxy/Cookie/onboarding/runtime/UI cluster to exactly one new M2 delivery group.
- Product/milestone crosswalk is PASS: M3-M10 now use canonical objects and each infrastructure dependency precedes its first consumer.
- The alignment verifier was introduced test-first: 5 tests first failed because the verifier did not exist, then all 5 passed after implementation.
- Final matrix passes: alignment verifier, M0 config verifier, 12 Workspace tests, Active CHG no-write preparation, 8 skill sources and `git diff --check`.
- Cloud, Agent and Desktop repository status checks are clean; this CHG changed only `wt-media-workspace` tracked files.

## 13. DONE Gate

- [x] Scope completed.
- [x] No blocking `Q-xx`.
- [x] Acceptance matrix all PASS.
- [x] Automated tests passed or justified.
- [x] Manual review evidence recorded where required.
- [x] Diff checked for out-of-scope changes.
- [x] Runtime repositories touched only if listed in scope.
- [x] Required baselines updated.
- [x] Affected repository committed independently.
