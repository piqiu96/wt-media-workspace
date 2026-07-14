# CHG-20260714-019: M2-C5 Profile 并发控制与敏感任务校验

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

建立敏感浏览器任务的双层互斥与执行前强校验：Cloud 基于 C1/C3/C4 的会话、节点、运行环境和 Profile 事实原子签发执行许可并持有 Profile 锁；Agent 在本机同一 Profile 再加资源锁。锁冲突进入等待，异常失联进入人工核实，不允许盲目重试。

## 3. Baseline References

- Product: `docs/product/prd/详细文档/第二章_系统架构.md` 2.5.7-2.5.10
- Product: `docs/product/prd/详细文档/第七章_互动管理.md` 7.4.9-7.4.10
- Engineering: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` 2.7-2.8
- Decision: `docs/decisions/0004-sensitive-profile-task-locking.md`

## 4. Scope

### Add

- Cloud-owned sensitive task authorization facts and per-Profile lock/permit persistence.
- Preflight checks for assigned node/user, active bound session, fresh matching runtime presence, active confirmed Profile, normalized owner and supported operation.
- Explicit waiting and result-review-required outcomes; permit renewal/release with hashed permit credentials.
- Agent local per-Profile mutex and guarded execution helper/client behavior.
- Cloud/Agent contracts, statuses and error codes.

### Explicitly Not Doing

- Actual publication, interaction, Cookie, Profile, proxy, or account-check executors.
- Public generic task creation or arbitrary command execution.
- Treating a stale/expired sensitive lock as safe to retry automatically.
- Cross-Profile bulk concurrency tuning or cloud compute concurrency.

## 5. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Sensitive operations are fixed enums: assisted publication, interaction, authenticated account check, Cookie read/write, Profile mutation, and proxy mutation. | CONFIRMED |
| D-02 | Only a Cloud-authorized task already bound to user, active Profile and node may request preflight; request payload cannot choose a different owner. | CONFIRMED |
| D-03 | Preflight validates the C4 node credential/session and a fresh `visible` runtime presence with matching owner before locking. | CONFIRMED |
| D-04 | Cloud serializes by Profile; Agent also locks the Profile locally before calling preflight. Both are required. | CONFIRMED |
| D-05 | An active lock conflict is a waiting outcome, not task failure. | CONFIRMED |
| D-06 | An expired unreleased sensitive lock becomes `review_required`; Cloud does not automatically grant the next permit until resolved. | CONFIRMED |
| D-07 | Permit credentials are random, returned once, stored only as hashes, and required for renew/release. | CONFIRMED |
| D-08 | The user's continuous M2 authorization permits C5 execution and transition to C6 without another approval wait. | CONFIRMED |

## 6. Tasks

| Task | Goal | Status |
|---|---|---|
| T-01 | Activate C5 and record lock/retry decisions. | DONE |
| T-02 | Implement Agent local Profile lock and guarded preflight client test-first. | IN_PROGRESS |
| T-03 | Implement Cloud preflight/permit domain and MySQL transaction test-first. | TODO |
| T-04 | Add credentialed routes/contracts and cross-repo verification. | TODO |
| T-05 | Advance governance, close C5, and activate C6. | TODO |

## 7. Acceptance Matrix

| AC | Requirement | Status |
|---|---|---|
| AC-01 | Same Profile cannot execute two local sensitive operations concurrently. | TODO |
| AC-02 | Cloud grants only an authorized task on the assigned active node with a fresh matching runtime presence. | TODO |
| AC-03 | Active conflict returns waiting; expired unreleased permit returns review-required and is not auto-reused. | TODO |
| AC-04 | Renew/release require the one-time permit credential whose plaintext is never stored. | TODO |
| AC-05 | No sensitive executor or arbitrary task/command surface is introduced. | TODO |

## 8. Current Checkpoint

Completed:
- C4 closed with all gates passing.
- Product and engineering concurrency/retry rules extracted.

Current:
- Write failing Agent local Profile lock tests.

Next:
- Write failing Agent local Profile lock tests.

Blocked:
- None.

## 9. DONE Gate

- [ ] Scope completed.
- [x] No blocking question.
- [ ] All acceptance criteria PASS.
- [ ] Full verification and evidence recorded.
- [ ] Repositories committed independently.
