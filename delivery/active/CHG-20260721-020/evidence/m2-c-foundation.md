# M2-C foundation progress

- Cloud proxy connectivity checks now create `proxy_check_task` with a structured, secret-bearing payload retained only in the task store for Agent execution.
- Agent registers a local proxy connectivity executor; failures are reported as a task result instead of being presented as synchronous Cloud success.
- Proxy check route remains authenticated and returns HTTP 201 task creation semantics.
- Cloud focused tests and Agent 46-test suite pass after the change.

The proxy credential is never written to evidence. Protocol-level exit-IP/read-back and Profile assignment remain pending in M2-C.
