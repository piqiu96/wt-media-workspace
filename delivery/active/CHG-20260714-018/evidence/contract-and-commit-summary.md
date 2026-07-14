# Contract and commit summary

- Contract state: `m2_agent_runtime_binding`.
- Cloud-Agent API/current minimum revision: `2026.07.14.5`.
- Cloud runtime error revision: `2026.07.14.4`.
- Agent Local API remains `2026.07.14.6`; runtime event and status revisions advance to `2026.07.14.7`; local BitBrowser errors remain `2026.07.14.6`.
- Release: `0.2.3-m2-agent-runtime-binding`; Agent component `0.2.1`.
- The old Workspace verifier rejected the intentional revision advance before its expectations were updated.

Independent commits:

- Workspace start: `f54c08c`.
- Agent collector: `8652a90`.
- Agent client/contracts: `d5a9e4d`.
- Cloud runtime persistence/routes: `6ef0308`.
- Cloud provider contract: `866364e`.
- Cloud one-time credential contract clarification: `9770e1b`.

C4 facts are attestation inputs only. C5 must use them at task time and acquire a Profile lock before any sensitive execution.
