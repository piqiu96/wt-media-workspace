# Skill acceptance scenarios

Run these in a fresh Codex context after distribution. They are behavior checks, not product requirements.

## Scenario A — existing project, conflicting prototype and PRD

A product owner asks to improve an existing admin list. The PRD defines the business status and role visibility; the current prototype exposes extra backend states and has a repeated action. The common reference already has a suitable table and Drawer pattern. Ask the agent to design the improvement.

**Pass when the agent:**
- reads repository instructions, relevant PRD, frontend rules, common reference and current page;
- treats the prototype as implementation evidence, not overriding business truth;
- reuses the common pattern instead of creating a new component;
- separates formal facts, confirmed decisions, AI proposals and D1 unknowns;
- does not ask again about facts already documented;
- does not rewrite unrelated pages.

## Scenario B — business rule missing under time pressure

A request says: “Show how many times this material was used and let the team sort by it. We need this today.” The PRD has no definition of “used”; possible meanings include task attempts, successful outputs, unique operators or publications.

**Pass when the agent:**
- identifies this as a D1 data/metric definition;
- explains the materially different counting options and recommends a product-appropriate option;
- asks one focused human decision instead of inventing a metric;
- proceeds with independent work that does not depend on the missing rule;
- does not label its recommendation CONFIRMED.

## Scenario C — milestone consolidation

A discussion has three alternative names for the same state, two repeated decisions, one rejected option and a confirmed rule. The user asks to prepare Codex handoff.

**Pass when the agent:**
- emits one current answer per decision;
- keeps only necessary rationale and formal-source links;
- removes rejected/dead options from the active brief or marks them SUPERSEDED;
- preserves unresolved D1 decisions as blockers;
- references existing PRD/common standards instead of copying them;
- produces a concise handoff with exact files, scope, reuse requirements and verification;
- does not mark IMPLEMENTED or ACCEPTED without evidence.

## Scenario D — different product, same skill

A new SaaS project has different terminology, design tokens and component library, but no established process skill. Ask the agent to onboard and improve one page.

**Pass when the agent:**
- adapts to the new repository and its sources;
- does not import WT Media business rules or UI assumptions;
- reuses that project's actual component library and design standards;
- creates no duplicate PRD or component library;
- applies the same product → interaction → visual → implementation → verification lifecycle.

## Reporting

For each scenario record: PASS / FAIL / NOT RUN, the exact evidence, and any skill wording that caused ambiguity. Do not claim skill acceptance until the scenarios have been run in the target agent environment.


## Scenario E — formal PRD plus a long-running review and evolving prototype

An established product has a current PRD, a review page with several rounds of user feedback, a latest README summary, and a runnable prototype. Some review recommendations have been accepted, some remain proposals, and some contradict the PRD. Ask the agent to continue the product design using all sources.

**Pass when the agent:**
- reads the latest PRD, review summary, current review decisions and actual prototype files;
- does not blindly treat the PRD as infallible or the review page as entirely approved;
- distinguishes confirmed review decisions, proposals, historical/rejected options and prototype-only behavior;
- classifies each difference as aligned, PRD detail gap, confirmed change requiring PRD update, true conflict, or prototype drift;
- evaluates the operational rationale and recommends the smallest coherent resolution;
- does not ask the user again about already confirmed decisions;
- groups only material D1 decisions for human approval;
- updates one active working brief and avoids copying the PRD or chat transcript;
- does not modify the formal PRD until the relevant change is approved.

**Failure examples:** “PRD always wins”; “everything in review is approved”; treating a prototype mock batch ID as a backend field; copying all review text into a second PRD.
