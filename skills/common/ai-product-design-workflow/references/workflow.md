# End-to-end workflow

## 0. Discover

Identify product type, users, jobs, success criteria, repository ownership, formal requirements, accepted decisions, design standards, actual shared components, prototype entry points and available tools. Follow indexes; do not scan the entire repository by default. A README does not prove a capability exists. When PRD, review documents and prototype coexist, apply references/source-reconciliation.md before treating any difference as a requirement.

## 1. Product logic first

Map the relevant business area:
- objects and responsibilities;
- actors, roles and access boundaries;
- lifecycle and source-of-truth data;
- user scenarios and entry/exit points;
- field definitions, derivation, freshness and missing-data behavior;
- status meanings and transitions;
- cross-page dependencies;
- duplicate, failure, retry, cancellation, partial-success and unknown-result cases.

Separate formal facts, user-confirmed decisions, AI proposals and unresolved questions. Use the smallest useful model; do not invent entities or statuses.

**Gate:** primary objects, rules and cross-module boundaries are sufficiently clear. Only unresolved D1 decisions block progress.

## 2. Interaction design

For each relevant page/flow specify the user goal, page responsibilities, information hierarchy, search/filter/sort/pagination, single/bulk actions, overlays/navigation, defaults, dependencies, validation, context retention and relevant loading/empty/error/retry/partial-result states.

Use state tables only where they resolve ambiguity. Do not create matrices for every static field.

**Gate:** important user scenarios are completable and consequential actions are unambiguous.

## 3. Visual design

Start from the active design system, actual shared components and common examples. Compose existing patterns first. Tune hierarchy, density, alignment, responsiveness and clarity to the real page. A new shared pattern needs repeated use or a genuine system-wide gap; a one-off stays local. A static common gallery is not automatically a runtime component library.

**Gate:** the page belongs to the same product while fitting its own task.

## 4. Prototype implementation

Prepare a concise handoff pointing to the active brief, formal facts, common patterns and exact scope. Implement confirmed requirements and authorized D2/D3 choices. Preserve unrelated behavior. Keep unresolved D1 behavior pending; do not fabricate rules to make a demo look complete.

## 5. Verification and acceptance

Verify the actual running prototype: normal and long content, primary interactions, roles, empty/no-result and representative failures, narrow viewports/containers, overflow and shared-consumer regressions. Use real browser screenshots/tests when available. State what remains unverified. A successful build is not product acceptance.

## 6. Milestone close

Merge duplicate decisions; keep one current statement per question; remove superseded options from active context; retain only necessary rationale and open D1 items; update the active brief. After acceptance, promote stable business facts to the existing PRD and shared rules to the existing standards. Retire temporary material under repository policy. Never create a parallel tracker or archive of chat transcripts.
