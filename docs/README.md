<!-- governance: class=index default_load=always -->

# WT Media Governance Documents

This file is the entry index for the documentation tree. It defines directory roles and the machine-checked index rules. Classification, fact ownership, conflict resolution, lifecycle, historical disposal, and close rules live in [文档与知识事实治理规范](standards/文档与知识事实治理规范.md). Loading priority stays in `AGENT-INDEX.md` §4; this file does not repeat it.

## Directories

- [Product](product/README.md): current product facts and product acceptance.
- [Engineering](engineering/README.md): current architecture, module boundaries, and long-lived specs.
- [Standards](standards/README.md): current engineering, design, product, and documentation practice standards.
- [Contracts](contracts/README.md): human-readable contract governance; provider repositories own the definitions.
- [Decisions](decisions/README.md): accepted architecture choices and ADRs, with their reasons.
- [DevOps](devops/README.md): port and deployment ledger; the configuration/provider file owns each value.
- [Reference](reference/README.md): reference material such as business state models; it does not independently decide product or interface facts.
- [Legacy plans](superpowers/README.md): mixed old plans and specs. Not current facts, not loaded by default; judge each file by content.

Temporary execution state belongs in `.ai/WORK_STATE.md` (optional, gitignored, not a fact source). A CHG's formal record is `../delivery/active/<change-id>/change.md`; `evidence/` is added only when needed. Do not put plans, progress, handoffs, or temporary analysis under `docs`.

This tree is the only documentation location. The execution root `wt-media/` carries no `docs/` directory of its own, so there is no second copy to fall back to: when a document here is wrong or stale, fix it here.

## Fact sources

- **Current facts**: `docs/product/`, `docs/engineering/`, `docs/contracts/`, `docs/decisions/`, `docs/devops/`, `docs/standards/`. Each answers a different question; there is no single global priority across them. `docs/reference/` is citable explanation, not an independent decision source.
- **Delivery state**: `delivery/LEDGER.md` is the Active CHG index; `delivery/active/<CHG>/change.md` is the status source; `delivery/milestones/` holds milestone closure cards. `delivery/planned/` is confirmed work that has not started.
- **Traceable history**: `delivery/completed/` keeps completed records with audit value; `delivery/reports/` keeps reports with independent value. Neither is current fact or loaded by default.
- **Legacy material**: `docs/superpowers/` is a mixed collection, not automatically historical. Effective methods belong in `docs/`; old analysis and process content exit the default context.
- **Generated content**: `.ai/CURRENT_CONTEXT.md` is regenerable navigation; `.ai/WORK_STATE.md` is optional local memory and is gitignored.
- **Provider definitions**: OpenAPI, schemas, DTOs, and events are owned by the provider repository. `docs/contracts/` governs them in human-readable form and does not copy the definitions.

Conflict resolution follows fact ownership, not a global product/engineering/implementation order; see the [standard](standards/文档与知识事实治理规范.md) §4. `AGENT-INDEX.md` §3 and §4 remain authoritative for what counts as a fact and what is loaded by default.

## One fact, one place

- Keep a stable fact in exactly one directory. Delivery records cite it; they do not copy its body.
- Analysis, discussion, and proposals become formal only after they enter Product, Engineering, Contract, Decision, or Delivery.
- Code proves current behavior, but current behavior does not by itself change a formal requirement.

## Lifecycle and history

- `docs/` holds current facts only. The `docs/superpowers/` legacy collection below is a temporary exception, not a place for new facts. Git keeps old versions; do not keep a second current copy for history.
- `delivery/active/` holds the current CHG; `delivery/planned/` holds confirmed work not yet started; `delivery/milestones/` holds current business closure.
- `delivery/completed/` and `delivery/reports/` hold only material with independent traceability value. Both exit the default context.
- `docs/superpowers/` is judged by content. Promote still-effective methods to `docs/`; delete or retire content without continuing value.
- The temporary marker `SUPERSEDED` is only for an old document that cannot be deleted yet because external references remain. It must name a resolvable replacement and is removed after references migrate.
- No long-term Draft / Current / Superseded / Historical status vocabulary is maintained. Directory position expresses lifecycle.

CHG status still uses only `DISCUSSION / PLANNED / IMPLEMENTING / VERIFYING / DONE / SUPERSEDED` (mapping in `AGENT-INDEX.md` §5). The two concepts do not replace each other.

## Indexes and markers

- Every required index carries exactly one marker:
  `<!-- governance: class=stable|historical|index default_load=task|never|always -->`.
- `historical` requires `default_load=never`; `index` allows `default_load=always`, `task`, or `never`.
- `delivery/completed/README.md` uses its existing `- 归档边界：READ-ONLY` line as the historical/never equivalent; it does not carry a second marker.
- Every top-level `docs/` directory must be linked in this file as `<dir>/README.md`, and that README must exist.
- A new long-lived spec under `docs/engineering/specs/` must be listed in that directory's index.

## Writing rules

- Do not put implementation plans, handoffs, progress, or temporary analysis under `docs/`; use `.ai/WORK_STATE.md` or the current CHG's `change.md`.
- Do not create a second copy of a stable fact, and do not copy OpenAPI or schema definitions.
- Default to exit: delete old versions fully absorbed by current facts and records without audit value; keep only what has continuing traceability value. Do not rewrite archived bodies.
- Use the temporary `SUPERSEDED` marker only while external references still require the old document; do not turn it into a permanent status.

## Validation

- `scripts/docs/check.py` checks required indexes, markers, the top-level directory registration, `AGENT-INDEX.md` fact paths, relative links in current documents, `SUPERSEDED` replacement pointers, and spec-index completeness.
- `scripts/verify/verify_delivery_governance.py` checks delivery/archive boundaries.
- `scripts/verify/verify_product_master_alignment.py` checks status vocabulary and LEDGER rows.
- When a check fails, fix the fact or the index; do not bypass it with wording.
