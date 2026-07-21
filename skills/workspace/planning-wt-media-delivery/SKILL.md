---
name: planning-wt-media-delivery
description: Use when planning a new WT Media milestone, correcting an inaccurate milestone or oversized CHG, assessing a bug or requirement change, or deciding which Product, Engineering, Milestone, Decision, or CHG records must change before implementation.
---

# Planning WT Media Delivery

Maintain the path from stable project facts to one bounded executable CHG. This Skill plans and corrects delivery; it never implements runtime code.

## Authority

Read in order:

1. root `AGENTS.md` and `.ai/CURRENT_CONTEXT.md`;
2. `docs/product`, `docs/engineering`, `docs/contracts`, `docs/decisions`;
3. `delivery/MASTER_IMPLEMENTATION_PLAN.md`;
4. applicable `delivery/milestones/M*.md`;
5. AI analysis under `docs/superpowers/specs`;
6. current CHGs, Evidence, code, tests, and Git status.

AI Specs are analysis material. Product and Engineering remain stable facts; Milestones contain the human-confirmed business closure; CHGs are execution contracts.

## Classify Before Writing

| Observed change | Update |
|---|---|
| Implementation defect that preserves the business closure | Create or adjust one small CHG |
| User goal, operation order, success effect, or false-success rule changes | Update the Milestone, then create or adjust CHGs |
| Product capability or rule changes | Update Product, then Milestone and CHGs |
| Cloud/Agent/Desktop ownership or engineering principle changes | Record a Decision and update Engineering before Milestone/CHGs |
| Existing M is incomplete or implemented incorrectly | Audit code and Evidence against the Milestone; correct the Milestone only when the business truth itself changes |

Do not rewrite a Milestone for a field display Bug. Do not patch code when the business closure is missing.

## Planning Protocol

1. Report current facts, contradictions, dirty files, and the exact source sections used.
2. State the user-visible outcome and the earliest unproven closure.
3. Ask the user only for decisions that cannot be derived safely:
   - final user goal;
   - prerequisites and operation order;
   - required database and external side effects;
   - forbidden false-success behavior.
4. Update or create one concise Milestone closure card with:
   - user goal;
   - prerequisites;
   - user operation;
   - system and external actions;
   - success facts that must all hold;
   - failure behavior that must not occur;
   - linked CHGs.
5. Propose CHGs in dependency order. Activate at most one M/L CHG.
6. For the next CHG, define one independently verifiable vertical result, explicit exclusions, ordered Tasks, real acceptance, Evidence, and commit boundaries.
7. Synchronize `delivery/LEDGER.md` and root `.ai/CURRENT_CONTEXT.md` with the actual active directory.
8. Stop before runtime implementation and hand off to `executing-wt-media-change`.

## CHG Boundary

A CHG may cover one closure card or a smaller vertical slice. It must not combine unrelated closure cards merely to finish an M faster.

Every M/L CHG must reference an exact Milestone file and closure anchor. A small Bug CHG may instead reference the stable Product, Engineering, or Contract rule when the impact analysis proves the business closure is unchanged.

## Reverse Correction

When implementation or acceptance exposes a gap:

```text
reproduce the real user failure
→ compare Evidence with Milestone success facts
→ classify Product / Engineering / Milestone / CHG / implementation
→ update only the owning fact source
→ re-split the remaining CHG scope
```

Preserve correct code and Evidence as inherited facts. Never mark a closure complete from code presence, task creation, HTTP success, or mock-only evidence.

## Stop Conditions

Stop and ask for a decision when:

- Product, Engineering, Contract, Milestone, code, or tests conflict;
- a business choice has two materially different outcomes;
- an architecture change lacks a Decision;
- the proposed CHG spans multiple independent closures;
- real acceptance requires credentials, external mutation, or authority not provided;
- unrelated dirty files overlap planned edits.

Do not create another planning, impact-analysis, spec-planning, milestone-planning, or CHG-planning Skill. These are modes of this Skill.
