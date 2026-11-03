# Interaction design

Design around the user's task, not the inventory of controls.

## Page contract

Define page purpose/non-goals, entry and return points, primary decision information, list/detail/form responsibilities, role actions and upstream/downstream relationships.

## Lists and filters

- Put frequent, high-value filters first; move genuinely low-frequency filters to advanced filters.
- Choose single/multi-select from the real query task.
- Define defaults, apply/reset, pagination reset, sorting and cross-page context retention.
- Search identifiers users actually use, not just internal database IDs.
- Keep independently useful fields searchable/sortable even when visually grouped.
- Do not make horizontal scrolling the only way to discover essential information.

## Actions

For each consequential action define eligibility, side effects, idempotency, duplicates, confirmation need, result feedback and recovery. Bulk actions define selection scope, cross-page selection, partial success and failed-only retry.

Do not confirm every action. Confirm destructive, irreversible, broad-scope or risk-bearing actions. Preserve context after completion.

## Overlays and navigation

Use established project Dialog/Drawer patterns. Choose a temporary detail, focused confirmation or full page based on the task. Avoid duplicate actions in list and detail unless context gives the detail action a distinct purpose.

Define close/focus behavior, nested overlays, loading locks and parent-state preservation.

## State coverage

Cover only states relevant to the flow: initial/loading, normal, empty source vs no matches, unavailable, submitting/in progress, success, failure, partial success, unknown/pending confirmation, retry and cancel where supported. State what users see and what they can do next. Never invent backend transitions.
