---
id: CHG-20261109-127
parent: none
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
---

# CHG-20261109-127: Unify prototypes in Cloud and current design drafts in Workspace

## Change

Move Workspace `example/common` and `example/proto` to Cloud `web/example` without redesigning approved browser, account, content-production or file-management experiences. Move their design working documents to Workspace `docs/design`; remove Workspace `example` after checking the complete file mapping. This is an independent development-governance change, with no business milestone, database, account, storage or runtime API changes.

Provide one independent local preview service, preserving the existing `127.0.0.1:8768/example/` URL and review storage keys. New Vue examples import actual Cloud components and themes; legacy HTML remains independently rendered. Preview can read the explicitly selected local Workspace documentation, including uncommitted saved edits. Product builds never depend on Workspace. GitHub links remain usable remotely; commit-pinned references retain their version semantics.

Tasks: record the source checksums; relocate files and repair references; add the isolated preview/component/documentation entries; update ownership, draft lifecycle and navigation; verify legacy interactions, review persistence, local document updates and production-build separation; commit and review each repository.

## Done When

- Every original prototype/resource/design file has a verified destination; Workspace `example` no longer exists. Approved prototype styling and interaction scripts retain their original contents except necessary navigation references.
- Design drafts reside only in `docs/design`; indexes and governance define confirmation, write-back and removal after formal owners and Delivery have absorbed their contents. Existing completion decisions are preserved.
- One command starts legacy prototypes and a Vue example using real `src/shared/ui` components, without production authentication, API proxy or execution.
- Legacy resource links and all four prototype entries work; existing model tests pass; review keys and export behavior remain compatible and reload preserves review input.
- Local documentation links, images and anchors resolve within the allowed documentation root; saved edits are visible without commit/push. Missing local documents are explicit, and fixed GitHub revisions are never silently replaced by local working files.
- Workspace documentation checks pass and Cloud/Desktop builds remain independent of examples and local Workspace documentation.

## References

- Decision: `docs/decisions/0033-prototype-and-design-draft-ownership.md`
- `docs/standards/文档与知识事实治理规范.md`
- `docs/standards/frontend/README.md`

## Verification

Implementation and local acceptance are complete. See `evidence/verification.md` for measured results and limitations. Independent PR review and merge remain pending; this CHG is not DONE.
