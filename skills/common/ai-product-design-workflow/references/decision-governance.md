# Decision governance and consolidation

## Two independent axes

**Autonomy**
- D0: binding formal facts and user-confirmed decisions; follow.
- D1: business meaning, metrics, permissions, core workflow, irreversible or cross-module changes; human approval required.
- D2: evidence-based product/interaction judgment; AI may decide and record rationale.
- D3: presentation detail within the system; AI may decide and implement.

**Maturity**
- PROPOSED: recommendation, not binding.
- CONFIRMED: human-confirmed decision.
- IMPLEMENTED: reflected in prototype/code.
- ACCEPTED: verified and accepted by product owner.
- SUPERSEDED: replaced by a newer decision.

D0-D3 is not a status. IMPLEMENTED is not ACCEPTED.

## Record shape

Keep only decisions that affect future work: concise decision, autonomy/maturity, owner/source, non-obvious rationale, affected pages/modules, next action/formal destination. Do not record every thought or ordinary styling choice.

## Milestone consolidation

After a meaningful discussion round, page design, module/phase completion or acceptance:
1. merge duplicates;
2. resolve wording differences;
3. keep one active answer per question;
4. mark replaced decisions SUPERSEDED and remove them from active summaries;
5. remove dead options/transient reasoning from the active brief;
6. retain only rationale needed to understand non-obvious choices;
7. keep unresolved D1 decisions visible;
8. point to the formal source when promoted.

History belongs to Git/PR or the existing review mechanism. Do not build a permanent decision database or duplicate tracker.

## Avoid false authority

A proposal is not confirmed because it appears in a draft. Implementation is not acceptance. A user statement is binding only for the scope it confirms. Never silently upgrade maturity.
