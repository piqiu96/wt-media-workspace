# Product logic analysis

Use before detailed interaction or visual design when the business model is not clear.

## Analysis frame

1. **Users/jobs:** who uses this, in what situation, to achieve what outcome?
2. **Objects:** what is managed? Define each object's responsibility; avoid duplicate entities.
3. **Lifecycle:** how is it created, changed, completed, removed, restored or retired?
4. **Relationships:** which user, team, account, source or parent owns each record?
5. **Facts/metrics:** source, counting unit, attribution, time window, freshness, null-vs-zero and role visibility.
6. **Permissions:** distinguish visibility, action authority and data returned by the server.
7. **Workflow:** entry points, handoffs, downstream effects and independent actions.
8. **Exceptions:** duplicate submission, stale source, missing file, failed task, partial success, unknown result, retry and cancellation.

## Field decision

For each proposed field determine what question it answers; whether it is a fact, derived metric, status, action or link; source and update timing; list/detail/filter/sort need; duplication; permissions; and missing-data behavior.

Do not expose every backend state as a separate badge. Translate independent backend facts into the few operational concepts users need without conflating their underlying meaning.

## Status decision

A status has one subject, one meaning, entry/exit conditions, source of truth, permitted next actions and recovery behavior. Do not combine unrelated state dimensions into one ambiguous backend status.

## Output

Prefer a concise object map, scenario flow and field/status tables. Add detailed state diagrams only for non-trivial lifecycles. Label statements as formal fact, user-confirmed decision, AI recommendation or unresolved question.
