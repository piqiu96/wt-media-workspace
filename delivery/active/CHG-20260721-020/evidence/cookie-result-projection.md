# M2-D Cookie task result projection

## Scope

Cookie read/write tasks now return only non-secret execution metadata to Cloud:
`profile_id`, counts, and the optional Cloud `account_id`. Raw Cookie values are
never included in the result payload.

## Implementation

- Agent Cookie executors report structured summaries through the existing task
  report API, while retaining compatibility with lightweight test doubles.
- Cloud `MySQLTaskStore.projectResult` records `cookie_status=read` after a
  successful read and `cookie_status=active` plus
  `active_cookie_updated_at` after a successful write.
- Task detail redaction remains enabled for sensitive payload keys.

## Verification

- Agent: `python3 -m unittest discover -s tests -q` — 46 tests passed.
- Cloud: `GOCACHE=/private/tmp/wt-media-go-cache go test ./internal/modules/cloudagent ./internal/modules/mediaaccount ./internal/modules/proxy ./internal/modules/profilebinding` — passed.

## Acceptance boundary

This proves task/result persistence and state projection. It does not claim a
real external platform Cookie refresh until the final authorized acceptance run.
