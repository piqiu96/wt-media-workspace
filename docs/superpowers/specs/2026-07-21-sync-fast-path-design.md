# M2 synchronous fast-path design

## Goal

Use synchronous calls for deterministic, short BitBrowser/Agent operations and
reserve Cloud tasks for long-running browser interaction.

## Boundary

- Synchronous: proxy connectivity checks, Profile list/status reads, and
  direct proxy configuration reads/writes when the local Agent API can complete
  within a bounded timeout.
- Asynchronous: opening a browser, page-element interaction, Cookie operations,
  account checks, and any operation that needs progress, retry, cancellation,
  or recovery after a process restart.

## Proxy check flow

`POST /api/v1/proxies/:id/check` calls the Agent's bounded synchronous check
endpoint. Cloud persists the verified result and returns it to Web. It does
not create a task for normal success or a normal, bounded failure. If the
Agent is unavailable or the call exceeds the timeout, Cloud returns a clear
availability error; a separate explicit background retry remains taskized.

## Error and security rules

- Agent calls have a fixed timeout and never block indefinitely.
- Cloud remains the owner of persisted proxy state and audit records.
- Credentials are passed only over the local authenticated Agent boundary and
  are never returned in Web responses or task detail responses.
- Complex operations continue using the existing task lease/report lifecycle.

## Acceptance

- A successful proxy check returns its result in the same HTTP response.
- The proxy page displays the result without creating a task.
- Agent unavailable/timeout produces a user-visible error with an explicit
  option to create a background retry task.
- Existing asynchronous Profile/Cookie/account flows remain unchanged.
