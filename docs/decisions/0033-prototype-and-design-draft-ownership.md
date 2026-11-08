# Decision 0033: Prototype code and current design working documents

## Status

Accepted — 2026-11-09, following the user's confirmed migration and draft-lifecycle decisions.

## Context

Offline HTML examples in Workspace duplicate controls already implemented in Cloud's shared Vue source. Keeping old and new prototype sources in different repositories complicates navigation. Design working documents require local edits, cross-module discussion and references to Workspace's formal product, engineering and standards documents.

## Decision

- Cloud owns prototype code in `web/example/common` and `web/example/proto`; approved prototypes move unchanged in behavior and appearance. New and actively revised prototypes incrementally use actual Cloud shared UI; there is no mandatory rewrite of approved pages.
- Workspace owns current design working documents in `docs/design`. This is an explicit working-document category within `docs`, not an independent formal product or delivery source. On confirmation, transfer stable rules to their formal owners and implementation/acceptance scope to Delivery; remove a working document once its unique content has been absorbed and references repaired. Git preserves history.
- Workspace's old `example` directory is removed, not maintained as a second copy. Formal product, engineering, standards and delivery documents remain in Workspace.
- An independent development preview serves legacy HTML and Vue component examples, and can read only an explicitly selected Workspace documentation tree. Local saved edits are read directly, not synchronized into another copy. Repository paths use the existing repository map/local launch context; no second repository map is introduced.
- Same-repository documents use relative links. Cross-repository canonical GitHub branch links can resolve to the selected local working tree in preview; immutable revision links retain their remote version. Local working files are explicitly identified as local. Formal Cloud/Desktop builds and runtimes do not depend on Workspace or preview tooling.

## Consequences

- Positive: prototype controls can share production implementations; design drafts remain next to their formal sources, with one maintained source per artifact.
- Negative: locally viewing cross-repository working documents requires a selected Workspace checkout. Without one, preview must clearly provide remote links rather than pretending local content is available.
- Follow-up: existing navigation and governance must reflect the ownership change; legacy dependencies remain until their actual consumers are revised.
