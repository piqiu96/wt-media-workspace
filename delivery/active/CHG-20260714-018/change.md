# CHG-20260714-018: M2-C4 Agent 节点、Profile 属主和运行环境上报

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`
  - `wt-media-agent`

## 2. Change Goal

把 M1 的内存 Agent 注册/心跳升级为可验证的本地节点绑定：当前有效用户会话签发一次性绑定票据，本地 Agent 换取节点凭证，并持续上报脱敏运行环境和已确认 Profile 的本地可见性；Cloud 只在用户、比特账号和 Profile 三者一致时记录运行属主事实。

## 3. Baseline References

- Product: `docs/product/prd/详细文档/第二章_系统架构.md` 2.4.6, 2.5, 2.6.4, 2.10.4-2.10.5
- Product: `docs/product/prd/详细文档/第三章_用户与账号管理.md` 3.4, 3.7
- Engineering: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` 2.4, 5.1-5.6
- Contract governance: `docs/contracts/跨项目协议治理与变更规范_V1.md`
- Decision: `docs/decisions/0003-local-agent-session-binding.md`

## 4. Current Facts

- C1 provides single-active authenticated sessions; C3 provides confirmed user/Bit account/Profile mirrors.
- M1 Agent registration and heartbeat are in-memory compatibility scaffolding and accept only caller-supplied `agent_id`.
- Agent can scan secret-free BitBrowser Profile facts, but does not yet produce a normalized host/dependency environment report.
- C5, not C4, owns Profile concurrency locks and sensitive-task preflight.

## 5. Scope

### Add

- Authenticated, short-lived, single-use local Agent binding tickets tied to the current user session.
- Durable Agent node identity, hashed node credential, heartbeat, environment summary, and Profile runtime presence.
- Agent environment collector for OS/architecture, Python, FFmpeg, disk/workdir, BitBrowser reachability and verified owner/Profile IDs.
- Cloud validation that reported owner/Profile IDs match the bound user and confirmed Profile mirror.
- Provider contracts and explicit runtime status/error enums.

### Modify

- Existing Agent register/heartbeat client and Cloud routes to use binding/node credentials for local runtime reports.
- App wiring to use MySQL persistence when configured while retaining the M1 no-DSN health scaffold.
- Contract Map/release matrix after provider definitions and verification.

### Delete

- None.

### Explicitly Not Doing

- Profile task locks, sensitive task eligibility, claim filtering, or execution authorization (C5).
- Desktop bridge/UI for issuing or transporting binding tickets (C6 integration surface).
- Automatic Profile reassignment, Bit account rebind, local Profile mutation, Cookie/proxy/file disclosure.
- Treating host name, local paths, IP addresses, disk contents, Cookie, or proxy credentials as reportable environment facts.
- Cloud Agent production service enrollment; the existing M1 cloud-mode compatibility path remains non-sensitive until its later deployment credential work.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | A local Agent cannot bind by sending `user_id`; an authenticated active session creates a hashed, short-lived, single-use ticket. | CONFIRMED |
| D-02 | Ticket consumption issues a random node credential returned once; Cloud stores only its hash and requires it on heartbeat/report. | CONFIRMED |
| D-03 | A ticket records the active session ID. A replacement login invalidates the node binding for further runtime reports. | CONFIRMED |
| D-04 | Environment reports use allow-listed normalized statuses and versions only; no host name, IP, local path, secrets, or raw command output. | CONFIRMED |
| D-05 | Profile runtime presence is accepted only when node user, user Bit owner, reported owner, and confirmed active Profile all match. The report never changes formal Profile ownership. | CONFIRMED |
| D-06 | A Profile may be visible from only one current local node for a user; a newer valid report moves runtime presence but does not change `browser_profile.user_id`. | CONFIRMED |
| D-07 | C4 facts are observability/attestation inputs only. C5 must still perform task-time checks and acquire a Profile lock. | CONFIRMED |
| D-08 | The user's continuous M2 authorization permits implementation and transition to C5 without another approval wait. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Activate C4 and record binding/security decisions. | DONE | Context and Workspace gates pass. |
| T-02 | Implement Agent allow-listed environment/Profile runtime report test-first. | DONE | Focused red/green and 33-test full Python suite pass. |
| T-03 | Implement Cloud ticket/node/runtime domain and MySQL persistence test-first. | DONE | Service, sqlmock, migration, full Go and vet gates pass. |
| T-04 | Implement authenticated/credentialed routes, Agent client, and provider contracts test-first. | DONE | Route/client and 18 Cloud/5 Agent YAML parses pass. |
| T-05 | Advance governance, run cross-repo gates, close C4, and activate C5. | IN_PROGRESS | Acceptance/evidence/independent commits complete. |

## 9. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Only a current authenticated session can mint a short-lived one-use local Agent binding ticket. | Identity/domain/route tests. | PASS |
| AC-02 | Local registration consumes the ticket, stores only credential hashes, and replacement login prevents later reports. | Service/MySQL/route tests. | PASS |
| AC-03 | Agent reports only allow-listed environment facts and verified Bit owner/Profile IDs without local paths or secrets. | Python tests/contracts/diff. | PASS |
| AC-04 | Cloud records Profile runtime presence only for the node's user and matching bound Bit owner/active Profile mirror. | Service/MySQL tests. | PASS |
| AC-05 | Runtime presence remains separate from formal Profile ownership and grants no sensitive task permission or lock. | Migration/domain/diff review. | PASS |

## 10. Current Checkpoint

Completed:
- C3 closed after all Agent/Cloud/Web/Contract/Workspace gates passed.
- Product/security constraints and the C5 boundary were extracted from stable baselines.
- Agent collects normalized secret-safe environment/Profile facts and uses a one-use binding token plus bearer node credential.
- Cloud persists binding tickets, nodes, structured environment facts and Profile runtime presence while storing only token/credential hashes.
- Provider contracts advanced to Cloud-Agent `2026.07.14.5` and Agent runtime event/status `2026.07.14.7`.

Current:
- Run fresh final cross-repository gates and record closure evidence.

Next:
- Close C4 and activate M2-C5 without an approval pause.

Blocked:
- None.

Recent verification:
- Agent 33-test full suite and five YAML provider definitions pass.
- Cloud full Go/vet and eighteen YAML provider definitions pass.
- Workspace deliberately observed the prior verifier reject the C4 state/revisions, then the updated verifier and all six tests passed.

## 11. DONE Gate

- [x] Scope completed.
- [x] No blocking `Q-xx`.
- [x] Acceptance matrix all PASS.
- [x] Automated tests passed or justified.
- [x] Evidence and limitations recorded.
- [x] Diff checked for out-of-scope behavior.
- [x] Affected repositories committed independently.
