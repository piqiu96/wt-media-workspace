# CHG-20260924-061 activation baseline

- Date: 2026-09-26
- Scope: M4-A activation and current-fact inventory; no runtime implementation.

## Authoritative inputs

- M4 closure: `delivery/milestones/M4-content-production.md` §4.
- M5 dependency: `delivery/milestones/M5-automatic-production.md` §2.
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §§5.1–5.4.
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §§2–7.
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md` Decision items 1, 3, 7–10.

## Readiness facts

- M3 is `DONE`; M4 has no prerequisite milestone remaining.
- Before activation, `delivery/active` had no change and the delivery-governance and product/master-alignment gates both exited 0.
- M5 remains `NOT_STARTED` and cannot be activated until M4 is `DONE`; no M5 CHG is created or activated.

## Code and contract gap

- Cloud materialization currently inserts only the base `materials` record from `source_contents`; there is no `video_status`, `material_usage`, `file_transfer_task`, storage client, or production transfer Worker.
- Both Cloud Web and Desktop WebView currently route `/material-library` to the content-pool page and `/my-material` to a placeholder.
- Cloud has no M4 formal API/schema/enum/error-code contract files, and its latest migration is `20260922_038_audit_fields.sql`; Task 0 must select the next actual migration number at implementation time.
- Agent and Desktop have no M4 local-download contract or execution path. Their existing unrelated worktree changes are preserved and excluded from this CHG.

## Worktree baseline

| Repository | Status at activation | Scope treatment |
|---|---|---|
| `wt-media-cloud` | `D internal/architecture/boundary_test.go` | Pre-existing, unrelated; preserve untouched. |
| `wt-media-agent` | `M AGENT-INDEX.md` | Pre-existing, unrelated; preserve untouched. |
| `wt-media-desktop` | clean | No pre-existing change. |
| `wt-media-workspace` | clean before activation edits | This activation record only. |

## Result

PASS — the active CHG is a single M4-A closure, the ownership boundary is established, and no M5 work has started.
