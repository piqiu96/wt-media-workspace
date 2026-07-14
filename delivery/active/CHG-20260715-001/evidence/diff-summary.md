# Diff Summary

- Change: `CHG-20260715-001`
- Date: 2026-07-15
- Allowed repository: `wt-media-workspace`
- Runtime repositories modified: None

## Commit Boundaries

| Commit | Purpose |
|---|---|
| `6e97d7b` | Close the completed prior Active record and activate the independent alignment CHG. |
| `d6c271b` | Add the section-for-section Chinese review companion. |
| `188f4c1` | Normalize product terminology, ownership and lifecycle facts. |
| `b6a8611` | Align engineering readiness, human contract governance and release wording. |
| `a44f52e` | Reopen M0/M1 and define real component/end-to-end gates. |
| `11a3e2e` | Reset and completely replan M2 as C1-C11. |
| `9b4530a` | Correct M3-M10 objects, dependencies, CHG decomposition and acceptance. |
| final verification commit | Add the regression verifier, tests, evidence and review checkpoint. |

## Changed Files by Scope

### Product baseline

- `docs/product/prd/社媒运营平台_产品需求说明书_V1.md`: canonical BitBrowser authorization, account-group, content, publication and metric facts.
- `docs/product/prd/详细文档/第三章_用户与账号管理.md`: main-account-tree sharing and Cloud Profile authorization semantics.
- `docs/product/prd/详细文档/第五章_素材生产.md`: remove operational `content_lead` terminology.
- `docs/product/prd/详细文档/第六章_发布管理.md`: normalize cancellation wording.
- `docs/product/prd/详细文档/第八章_数据统计.md`: normalize cancellation metrics.

### Engineering and contract governance

- `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`: real M0/M1 build, persistence, schema, Desktop and recovery prerequisites.
- `docs/contracts/contract-map.md`: document the actual mixed active/placeholder contract state.
- `config/release-matrix.yaml`: separate historical release evidence from revised milestone completion.

### Delivery governance

- `delivery/MASTER_IMPLEMENTATION_PLAN.md`: reset current statuses, rebuild M0-M2, correct M3-M10, and add common acceptance gates.
- `delivery/LEDGER.md`: point to the unique alignment CHG and keep its execution status synchronized.
- `delivery/active/CHG-20260715-001/change.md`: authoritative scope, decisions, acceptance and checkpoints.
- `delivery/active/CHG-20260715-001/change.zh-CN.md`: Chinese review companion.
- `delivery/active/CHG-20260715-001/plan.md`: executable test-first implementation plan and completed steps.
- `delivery/active/CHG-20260715-001/evidence/baseline-audit-20260715.md`: initial mismatch evidence.
- `delivery/active/CHG-20260715-001/evidence/product-milestone-crosswalk.md`: product capability/object/dependency mapping.
- `delivery/active/CHG-20260715-001/evidence/verification-summary.md`: final command results.
- `delivery/active/CHG-20260715-001/evidence/diff-summary.md`: scope and file inventory.
- `delivery/active/CHG-20260714-020/**`: removed from Active after its stable outcomes were committed; history remains in Git.

### Regression protection

- `scripts/verify_product_master_alignment.py`: deterministic product/Master/governance invariant checks.
- `tests/test_verify_product_master_alignment.py`: positive and regression tests, introduced with recorded RED/GREEN evidence.

## Excluded Scope Verification

- No Cloud, Agent, Desktop, Web, MySQL, Scheduler, object-storage or platform runtime behavior was changed.
- No placeholder contract was promoted to a formal provider contract.
- No M0-M10 milestone was marked `DONE` by this alignment CHG.
- Historical commits and verified partial implementations remain reusable evidence, not current milestone completion claims.
