# Reconciling product facts, reviews and evolving prototypes

Use this reference when an existing project has formal PRDs plus review documents, mockups or prototypes that have evolved through discussion.

## Do not use a simplistic winner-takes-all hierarchy

Different sources answer different questions:

- **Formal PRD / contracts / ADRs:** current approved business meaning, object/data contracts, permissions and acceptance obligations.
- **User-confirmed decisions:** explicit product-owner choices, including decisions made during current design work that may not yet have been back-written to the PRD.
- **Review documents:** product exploration, problem statements, alternatives, recommendations, recorded human feedback and review maturity. A review document may contain both confirmed decisions and unapproved proposals.
- **Prototype:** current implemented expression and evidence of what can be experienced. It does not prove that its business semantics are correct or approved.
- **Frontend standards / common references:** shared presentation and interaction conventions, not module-specific business facts.

No source wins every conflict. Determine who owns the fact and what maturity the statement has.

## Reconciliation procedure

1. Read the latest version of the formal PRD and the relevant review document, not an old copied excerpt.
2. Identify explicit user-confirmed decisions and their exact scope. Do not upgrade a proposal simply because it is in a review file or implemented in a prototype.
3. Extract the relevant prototype behavior and identify where it differs from both sources.
4. Compare by topic: object responsibility, user flow, field/metric definition, lifecycle/status, permission, cross-module handoff, exception/recovery and UI expression.
5. Classify each difference:
   - **Aligned:** review clarifies presentation without changing the PRD fact.
   - **PRD gap:** review adds a needed experience detail not specified by the PRD.
   - **Review proposal:** useful but not yet confirmed.
   - **Confirmed product change not back-written:** user confirmed it, PRD needs a controlled update.
   - **True conflict:** the sources prescribe different business behavior or data semantics.
   - **Prototype-only drift:** code diverges without supporting decision.
6. Evaluate the operational reason, simplicity, data truth, permissions, implementation evidence and cross-module impact. Recommend the smallest coherent resolution.
7. D2/D3 presentation decisions can be resolved autonomously when grounded. D1 business/data/permission/core-flow conflicts must be presented as a concise decision with a recommendation; do not silently rewrite the formal source.
8. Once approved, update the existing owning PRD/standard in place. Do not create a parallel "final design PRD". Keep the temporary module brief as the current working surface until acceptance.

## Conflict report shape

| Topic | Formal fact | Review/user decision | Prototype evidence | Assessment | Recommendation | Approval |
|---|---|---|---|---|---|---|

Use exact section references. Distinguish "not in PRD" from "contradicts PRD". A review detail missing from the PRD is not automatically a conflict.

## Special cautions

- A prototype may simulate data, states, APIs, batch IDs or external platform behavior that do not exist. Never describe these as delivered capabilities.
- A formal PRD can be stale or internally inconsistent. Treat it as the current approved baseline, not as infallible truth; recommend a change when the product evidence justifies it.
- A review file can preserve old alternatives and rejected decisions. Only current effective decisions guide implementation.
- A status label in a UI does not define its underlying state machine.
- A new aggregate view does not automatically justify a new business entity or database table.
- A convenience shortcut may link to another module without transferring ownership of that module's workflow.
- When a data capability is not available, show the limitation or defer the field; never derive a substitute metric from a nearby but semantically different fact.
