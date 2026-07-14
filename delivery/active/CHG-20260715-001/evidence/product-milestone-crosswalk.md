# Evidence: Product Capability and Milestone Crosswalk

- CHG: `CHG-20260715-001`
- Task: `T-02` through `T-06`
- Date: 2026-07-15
- Type: product and plan cross-reference
- Status: PASS

## Canonical Object and Ownership Resolutions

| Capability or term | Product owner | Canonical rule | First delivery milestone |
|---|---|---|---|
| BitBrowser root identity | Chapter 3 | One Cloud user binds at most one `main_user_id`; one `main_user_id` may serve multiple Cloud users; Cloud Profile assignment enforces authorization. | M2 |
| Account group | Chapter 3 | Saved tag/filter selection snapshot, not an independent core object; formal tasks freeze actual account IDs. | M2 |
| Instant content query | Chapter 4 | Does not create `crawl_task`; only selected results become formal data. | M3 |
| Scheduled discovery | Chapter 4 | `crawl_strategy -> crawl_task -> source_content`; no independent `crawl_result`. | M3 |
| Material source | Chapters 4-5 | `source_content -> material`; no operational `content_lead`. | M3/M4 |
| Cloud and local composition | Chapter 5 | Both use `material -> compose_pool_item -> task -> composite_output`. | M4/M5 |
| Publication result | Chapter 6 | Formal states include `pending_manual_submit` and `cancelled`; only `published` creates or reuses `tracked_object`. | M6/M7 |
| Interaction target and execution | Chapter 7 | `tracked_object -> interaction_task -> account-level task`; no `interaction_batch` or `interaction_item`. | M8 |
| Metrics | Chapter 8 | Immutable `platform_metric_snapshot` plus derived aggregation; no `production_signal`. | M9 |
| Desktop first real integration | Chapter 2 and engineering architecture | Real Tauri/Local Agent integration is an M0/M1 prerequisite; M10 owns final packaging and recovery. | M0/M1, finalized in M10 |

## Product Capability Ownership

| Product capability cluster | Source | Milestone | Resolution status |
|---|---|---|---|
| Real component build/run/test and cross-end task environment | Chapters 1-2 | M0-M1 | M0-R1 through R6 and M1-R1 through R8 now define real component and mock-free persistent end-to-end gates. |
| Users, roles, game scope and user administration | Chapter 3 | M2 | M2-C1. |
| Media accounts, tags, assignment and account workbench | Chapter 3 | M2 | M2-C2. |
| BitBrowser binding, Profile synchronization and Cloud assignment | Chapter 3 | M2 | M2-C3/C4. |
| Proxy, Cookie, account health and onboarding | Chapter 3 | M2 | M2-C5/C6/C7. |
| Agent runtime, environment, Profile concurrency and product UI acceptance | Chapters 2-3 | M2 | M2-C8 through C11. |
| Douyin instant query, monitoring, `source_content` and material conversion | Chapter 4 | M3 | M3-C1 through C9. |
| Material lifecycle and local composition | Chapter 5 | M4 | M4-C1 through C10. |
| Cloud composition and output pool | Chapter 5 | M5 | M5-C1 through C9. |
| Common publication plus Bilibili | Chapter 6 | M6 | M6-C1 through C10. |
| Baijiahao adapter and regression | Chapter 6 | M7 | M7-C1 through C5. |
| Interaction target, task and action execution | Chapter 7 | M8 | M8-C1 through C9. |
| Metric collection, operations statistics and dashboards | Chapter 8 | M9 | M9-C1 through C8. |
| Deployment, packaging, update, diagnostics and recovery | Chapter 2 and engineering architecture | M10 | M10-C1 through C10. |

## Verification Notes

- Historical/deprecation tables may name removed objects to state that they are not built.
- Current operational flows and candidate CHGs must use only canonical objects.
- All capability clusters now have one owning product chapter, one first delivery milestone and an explicit candidate CHG range.
- The Master Plan places formal task schemas and persistent task infrastructure in M1, Scheduler before M3 monitoring, Object Storage before M5 cloud outputs, and `tracked_object` creation in M6/M8 before M9 metrics.
