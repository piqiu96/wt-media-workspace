---
name: ai-product-design-workflow
description: Use when designing or improving a product, website, SaaS, admin workspace, user flows, interaction patterns, visual consistency, prototypes, or coordinating product design with code agents across an existing or new project.
---

# AI Product Design Workflow

A reusable, lean workflow for turning an evolving product idea into a coherent, testable product and prototype. The skill defines the method; the active project defines business facts, design standards, components, and constraints.

## Core rules

1. **Understand before changing.** Inspect project instructions, relevant product facts, standards, reusable patterns, prototype, and accepted decisions. Load only what the task needs.
2. **One fact, one owner.** Never create a parallel PRD, design system, component library, decision log, or tracker when the project already has one.
3. **Separate fact from maturity.** Formal requirements, user-confirmed decisions, AI proposals, current implementation, and accepted experience are different things. Existing UI proves implementation, not correctness.
4. **Reuse before inventing.** Inspect actual components and common patterns first. Extend shared patterns only for real repeated needs; keep one-off business behavior in its module.
5. **Design for the actual product.** Solve the stated user need with the smallest sufficient design. Do not add hypothetical dashboards, workflows, states, filters, settings, or abstractions.
6. **Protect human attention.** Decide routine field ordering, layout, copy, and interaction details autonomously when evidence is sufficient. Ask only when business meaning, data semantics, permissions, irreversible actions, cross-module ownership, or an accepted baseline changes.
7. **Keep one current answer.** Consolidate decisions at milestones. Remove duplicates and dead options from active briefs; preserve history only as project governance requires.
8. **Verify before claiming.** Design review, implementation, browser verification, and product acceptance are separate. Never claim a test or review that was not run.

## Workflow

Read `references/workflow.md` for the end-to-end process. Load only relevant specialist references:
- Product logic: `references/product-analysis.md`
- Interaction: `references/interaction-design.md`
- Visual consistency/reuse: `references/visual-consistency.md`
- Decisions/consolidation: `references/decision-governance.md`
- Reconciling PRD, reviews and evolving prototypes: `references/source-reconciliation.md`
- ChatGPT/Codex handoff and QA: `references/handoff-and-qa.md`

## Project onboarding

Use `templates/project-profile.md` to point to existing sources; never copy their rules into the profile. In an established repository, inspect its governance before adding files or changing document policy.

## Decision permissions

D0-D3 are autonomy levels, not lifecycle statuses:
- **D0:** binding formal facts and user-confirmed decisions; follow.
- **D1:** business meaning, metrics, permissions, core workflow, irreversible or cross-module changes; human approval required.
- **D2:** evidence-based product/interaction judgment; AI may decide and record rationale.
- **D3:** presentation detail within the system; AI may decide and implement.

Track maturity separately: PROPOSED → CONFIRMED → IMPLEMENTED → ACCEPTED; replace obsolete active decisions with SUPERSEDED. IMPLEMENTED is not ACCEPTED.

## Stop and ask

Ask one concise, decision-focused question when formal sources conflict, a business rule is missing, a core workflow or permission changes, or a shared/global baseline must be broken. Otherwise make a proportionate recommendation, label assumptions, and proceed within scope.
