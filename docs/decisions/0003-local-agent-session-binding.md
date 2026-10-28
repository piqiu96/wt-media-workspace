# ADR-0003: Local Agent session binding and runtime attestation

- Status: Accepted；设备证明、一次性票据与 node credential 部分由 [ADR-0022](0022-session-only-auth-and-agent-token.md) 取代，旧设备/节点中间决策已从当前文档树清理
- Date: 2026-07-14
- Change: CHG-20260714-018

## Context

The M1 registration endpoint trusts a caller-provided Agent ID and stores nodes only in memory. M2 requires local Profile operations to remain tied to the current system user, current single-active session, verified BitBrowser owner and actual local runtime. Passing a `user_id` or raw session Cookie to the Agent would make that boundary forgeable or leak the browser session.

## Decision

An authenticated Cloud session creates a short-lived, one-use binding ticket. Only the ticket hash is stored, together with its user and session IDs. A local Agent consumes it during registration and receives a random node credential once; Cloud stores only the credential hash. Runtime reports require that credential and an active bound session.

Reports are allow-listed: normalized OS/architecture and dependency statuses/versions plus the already secret-free BitBrowser owner and Profile IDs. Cloud accepts Profile runtime presence only when the node user, user's confirmed Bit owner, reported owner and confirmed active Profile all match. Runtime presence is separate from formal Profile ownership.

## Consequences

- A replacement login naturally makes the old local node unable to submit fresh runtime facts.
- Neither a user ID nor technical-role Cloud access can forge local resource presence.
- Desktop integration must transport a one-time ticket to the local Agent without exposing the HttpOnly session Cookie; that end-to-end bridge is verified in C6.
- C4 attestation alone grants no sensitive task permission. C5 still performs task-time validation and locking.

当前桌面执行只使用会话绑定的 Agent Token，不再保留稳定设备绑定、节点凭据或 runtime presence；历史实现由 Git 追溯。
