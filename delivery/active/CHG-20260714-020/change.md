# CHG-20260714-020: M2-C6 用户账号运行环境综合验收

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`
  - `wt-media-agent`
  - `wt-media-desktop`

## 2. Change Goal

完成 M2 用户、媒体账号、BitBrowser Profile、Agent 节点、运行环境和敏感任务锁的真实跨端验收；补齐 Desktop 一次性绑定票据传递边界和可重复的验收工具。真实依赖缺失时明确阻塞，不用 mock 冒充真实证据。

## 3. Baselines

- M2 C1-C5 stable code/contracts and CHG evidence reflected in Workspace baselines.
- Product: user/account core acceptance in `第三章_用户与账号管理.md` 3.7.4.
- Product: local environment checks and Agent security in `第二章_系统架构.md` 2.6.4, 2.10.4-2.10.5.
- Engineering: real cross-end verification and concurrency rules in architecture 2.7-2.8.

## 4. Scope

### Add/Verify

- Desktop-owned bridge method that accepts a one-use Cloud binding ticket and passes it to the Local Agent without exposing the HttpOnly session Cookie or persisting the ticket.
- Cross-repo contract locks and deterministic C6 verifier for Cloud/Agent/Desktop revisions.
- Real MySQL migration/bootstrap/login/media account/Profile scan confirmation/node binding/runtime presence/sensitive permit flow.
- Real BitBrowser full Profile scan and owner consistency when the installed local dependency is available.
- Concurrent preflight waiting and expired-lock review behavior against real MySQL.
- Full regression, health, security and dirty-tree gates across four repositories.

### Explicitly Not Doing

- Fabricating real MySQL/BitBrowser evidence with mocks.
- Platform publication/interaction executors, proxy/CK mutation, packaging, or deployment.
- Persisting the binding ticket, node credential, permit credential, Cookie, proxy secret, or local path in Desktop state/logs.

## 5. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Automated/unit/sqlmock evidence and real dependency evidence are recorded separately; only the latter satisfies the real integration gate. | CONFIRMED |
| D-02 | Desktop transports a one-use binding ticket through its native command boundary and immediately forgets it; Vue never receives the HttpOnly Cloud session Cookie. | CONFIRMED |
| D-03 | Docker may be used for isolated MySQL only if the local daemon is available and the environment permits it; no dependency download is silently substituted. | CONFIRMED |
| D-04 | Missing BitBrowser installation/login/Profile data is a genuine external blocker for that acceptance row, not a reason to weaken identity checks. | CONFIRMED |
| D-05 | User authorization permits all safe in-scope C6 work without stepwise approval, but cannot override tool quota or absent external dependencies. | CONFIRMED |

## 6. Tasks

| Task | Goal | Status |
|---|---|---|
| T-01 | Activate C6, inventory real dependencies and current repo state. | DONE |
| T-02 | Implement/test Desktop one-use binding bridge and contract locks. | DONE |
| T-03 | Add deterministic cross-repo C6 verifier and execute full automated matrix. | DONE |
| T-04 | Execute real MySQL and BitBrowser integration matrix where dependencies exist. | BLOCKED |
| T-05 | Resolve findings, record evidence, close M2 only if all mandatory real gates pass. | BLOCKED |

## 7. Acceptance Matrix

| AC | Requirement | Status |
|---|---|---|
| AC-01 | C1-C5 automated/full contract/security gates pass from clean independent repositories. | PASS |
| AC-02 | Desktop passes one-use binding ticket through native boundary without session/secret persistence. | PASS |
| AC-03 | Real MySQL migrations and end-to-end Cloud state transitions pass. | BLOCKED |
| AC-04 | Real BitBrowser scan proves full-list uniform owner and secret-free payload. | BLOCKED |
| AC-05 | Real concurrency shows one grant/one waiting and expired uncertain permit becomes review-required. | BLOCKED |
| AC-06 | Final M2 baselines/contracts/releases agree and no blocking limitation remains. | BLOCKED |

## 8. Current Checkpoint

Completed:
- C1-C5 implemented and closed.
- Docker CLI exists; MySQL CLI/server are absent. A follow-up application search found BitBrowser installed, but its Local API is not running.
- Desktop contract locks and ephemeral `local_agent_bind_session` boundary pass `npm run verify`; node/permit credentials are excluded from Vue response/state.
- Rust native boundary moves the ticket once into `BindingTransport`; its return type contains only non-secret node facts.
- Static cross-repository C1-C5 contract/security matrix, seven Workspace tests, Cloud Go/vet plus 20 YAML contracts, Agent 38 tests plus six YAML contracts, and Desktop verification pass.

Current:
- Automated C6 work is complete. CHG remains active solely for mandatory real dependency evidence.

Next:
- When Docker/MySQL and the installed BitBrowser Local API are available, execute AC-03 through AC-05 exactly as described in `evidence/real-integration-runbook.md`, then close M2 only on PASS.

Blocked:
- Docker CLI is installed but its daemon is not running; MySQL binaries/DSN are absent.
- BitBrowser is installed at `/Applications/比特浏览器.app` but its Local API is not listening on `127.0.0.1:54345`.
- Codex escalation quota currently rejects GUI/process launch approvals, so these external dependencies cannot be started from this task at present.
- A fresh M1 localhost integration rerun is also denied socket bind permission in this sandbox; its previously closed CHG evidence is retained and is not relabeled as a fresh C6 run.

## 9. DONE Gate

- [ ] All acceptance rows PASS with real evidence where required.
- [ ] Full four-repository regression passes.
- [ ] No secret persistence/logging.
- [ ] Stable baselines and release matrix finalized.
- [ ] Repositories committed independently.
