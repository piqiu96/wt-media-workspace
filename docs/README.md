<!-- governance: class=index default_load=always -->

# WT Media Governance Documents

This file is the entry index for the documentation tree. It defines how documents are classified, which one is authoritative, how they age, and how the tree is checked. Loading priority stays in `AGENT-INDEX.md` §4; this file does not repeat it.

## Directories

- [Product](product/README.md): current product facts and product acceptance.
- [Engineering](engineering/README.md): current architecture, module boundaries, and long-lived specs.
- [Standards](standards/README.md): shared engineering, design, and product practice standards.
- [Contracts](contracts/README.md): human-readable contract governance; provider repositories own the definitions.
- [Decisions](decisions/README.md): accepted architecture choices and ADRs, with their reasons.
- [DevOps](devops/README.md): port and deployment ledger; the configuration/provider file owns each value.
- [Reference](reference/README.md): reference material such as business state models; it does not independently decide product or interface facts.
- [History](superpowers/README.md): historical plans and specs. Not current facts, not loaded by default.

Temporary implementation plans, progress, handoffs, and verification notes belong under `../delivery/active/<change-id>/change.md`, not under `docs`.

This tree is the only documentation location. The execution root `wt-media/` carries no `docs/` directory of its own, so there is no second copy to fall back to: when a document here is wrong or stale, fix it here.

## Classification and authority

- **Stable facts**: `docs/product/`, `docs/engineering/`, `docs/contracts/`, `docs/decisions/`, `docs/devops/`, `docs/standards/`. Each answers a different question; there is no single global priority across them. `docs/reference/` is citable explanation, not an independent decision source.
- **Delivery state**: `delivery/LEDGER.md` is the Active CHG index; `delivery/active/<CHG>/change.md` is the status source; `delivery/milestones/` holds milestone closure cards.
- **Historical material**: `docs/superpowers/`, `delivery/reports/`, `delivery/completed/`. It is not current fact, is not loaded by default, and is not rewritten.
- **Generated content**: `.ai/CURRENT_CONTEXT.md` is regenerable navigation; `.ai/WORK_STATE.md` is optional local memory and is gitignored.
- **Provider definitions**: OpenAPI, schemas, DTOs, and events are owned by the provider repository. `docs/contracts/` governs them in human-readable form and does not copy the definitions.

`AGENT-INDEX.md` §3 and §4 remain authoritative for what counts as a fact and what is loaded by default.

## One fact, one place

- Keep a stable fact in exactly one directory. Delivery records cite it; they do not copy its body.
- Analysis, discussion, and proposals become formal only after they enter Product, Engineering, Contract, Decision, or Delivery.
- When two documents disagree, read the fact source for that domain; do not invent a global ordering that hides the difference.

## Document lifecycle

These four words describe the **document**, not a CHG:

- **Draft**: lives in `delivery/active/<CHG>/` while the change is being written or implemented.
- **Current**: lives under `docs/...` or as an accepted ADR.
- **Superseded**: mark `SUPERSEDED` at the top and point to the replacement; keep the original text.
- **Historical / archived**: move to `docs/superpowers/` or `delivery/completed/`; the archive boundary is read-only.

CHG status still uses only `DISCUSSION / PLANNED / IMPLEMENTING / VERIFYING / DONE / SUPERSEDED` (mapping in `AGENT-INDEX.md` §5). The two vocabularies do not replace each other.

Stable documents may be revised in place, but the CHG or ADR must record why. Historical records are not rewritten.

## Indexes and markers

- Every required index carries exactly one marker:
  `<!-- governance: class=stable|historical|index default_load=task|never|always -->`.
- `historical` requires `default_load=never`; `index` requires `default_load=always` or `task`.
- `delivery/completed/README.md` uses its existing `- 归档边界：READ-ONLY` line as the historical/never equivalent; it does not carry a second marker.
- Every top-level `docs/` directory must be linked in this file as `<dir>/README.md`, and that README must exist.
- A new long-lived spec under `docs/engineering/specs/` must be listed in that directory's index.

## Writing rules

- Do not put implementation plans, handoffs, progress, or temporary analysis under `docs/`; put them under `delivery/active`.
- Do not create a second copy of a stable fact, and do not copy OpenAPI or schema definitions.
- Do not silently delete an old plan: move it to a historical directory or mark it `SUPERSEDED`. Historical bodies are not rewritten.

## Validation

- `scripts/docs/check.py` checks required indexes, markers, the top-level directory registration, `AGENT-INDEX.md` fact paths, relative links, and spec-index completeness.
- `scripts/verify/verify_delivery_governance.py` checks delivery/archive boundaries.
- `scripts/verify/verify_product_master_alignment.py` checks status vocabulary and LEDGER rows.
- When a check fails, fix the fact or the index; do not bypass it with wording.
