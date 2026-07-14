# CHG-20260714-015: M2-C1 用户认证、单活会话和三角色权限

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`

## 2. Change Goal

建立 Cloud 作为正式事实来源的首版身份基础：技术创建用户，用户名和密码登录，单用户单活会话，固定的普通运营、高级运营、技术三角色，以及按游戏范围的授权边界。

## 3. Baseline References

- Product baseline: `docs/product/prd/详细文档/第三章_用户与账号管理.md#32-用户管理`
- Product baseline: `docs/product/prd/详细文档/第三章_用户与账号管理.md#371-权限异常与验收要求`
- Engineering baseline: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md#13-核心设计原则`
- Contract governance: `docs/contracts/ownership.md`
- Contract governance: `docs/contracts/contract-map.md`
- Contract compatibility: `docs/contracts/compatibility-policy.md`
- Master plan: `delivery/MASTER_IMPLEMENTATION_PLAN.md#M2用户角色媒体账号与运行环境`

## 4. Current Facts

- M1 is `DONE`; its Cloud-Agent-Desktop integration evidence is recorded in the M1 master-plan entry.
- Cloud currently contains only the M1 `cloudagent` module; no identity, Cloud API, business-schema, or business-enum formal contract is active.
- Cloud is the formal source for users, permissions, and business objects; Agent and Desktop do not own identity decisions.
- M2-C2 through M2-C6 are not started.
- The baseline requires a first technical user and game-scope assignments, but it does not prescribe first-user provisioning or a game-catalog module.

## 5. Scope

### Add

- Cloud identity domain model, persistence migration, password authentication, and session invalidation.
- Fixed roles (`operator`, `senior_operator`, `technician`) and game-scope authorization primitives.
- Cloud-owned v1 identity/authentication API contract and error/enum definitions needed by C1.
- Cloud Web login/session integration and authorization coverage needed to exercise C1.
- M2-C1 evidence and release-matrix entry after verification.
- A durable identity bootstrap and game-scope decision record.

### Modify

- Workspace delivery status, active ledger, contract map, and release matrix as formal C1 contracts become active.

### Delete

- None.

### Explicitly Not Doing

- Do not implement media-account, Cookie, proxy, Browser Profile, or Bit Browser binding code (M2-C2 and M2-C3).
- Do not implement Agent environment reporting, Profile ownership validation, sensitive-task execution, or Profile concurrency locking (M2-C4 and M2-C5).
- Do not implement M2-C6 comprehensive acceptance before its own active CHG.
- Do not add departments, teams, custom roles, role editors, mobile/third-party/SSO/MFA login, account handoff, or a Desktop copy of authorization rules.
- Do not change existing M1 Cloud-Agent or Local Agent contracts unless a demonstrated C1 compatibility defect requires a separately recorded decision.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | C1 uses username/password authentication. Technical users create users, may reset passwords, and users may change their own passwords. | CONFIRMED |
| D-02 | A user has exactly one active session; a new login invalidates the prior session and subsequent prior-session requests are rejected. | CONFIRMED |
| D-03 | The role set is fixed to ordinary operator, senior operator, and technician; no custom role system is introduced. | CONFIRMED |
| D-04 | Ordinary and senior operators are constrained by assigned game scopes; technicians have global business and data permission but cannot bypass Local Agent, Bit Browser, or other local-resource boundaries. | CONFIRMED |
| D-05 | M2 candidate changes proceed in C1-to-C6 order after each change satisfies its own active-CHG completion gate; the user has authorized this sequence without per-C confirmation. | CONFIRMED |
| D-06 | An empty MySQL database provisions exactly one initial technical user only when both `WT_MEDIA_INITIAL_TECHNICIAN_USERNAME` and `WT_MEDIA_INITIAL_TECHNICIAN_PASSWORD` are supplied. There is no default credential and later starts never reset this user. | CONFIRMED |
| D-07 | C1 stores assigned `game_id` values as opaque stable identifiers and does not introduce a game catalog or game-management API; later modules consume the same values. | CONFIRMED |
| D-08 | The Cloud Web session is an opaque server-side session represented in the browser by an HttpOnly, SameSite=Lax cookie. Tokens and password material never appear in JSON responses, logs, or audit records. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

Each task must follow:

```text
failing verification or test
→ minimal implementation
→ test
→ diff check
→ evidence
→ checkpoint
→ independent commit
```

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Create active CHG, update M2 delivery state, and refresh AI context. | DONE | `python3 scripts/prepare_ai_workspace.py --change CHG-20260714-015` |
| T-02 | Map Cloud identity/API files and record the C1 implementation plan, contracts, and test matrix. | DONE | `plan.md` maps every acceptance criterion to an owned provider contract and test command. |
| T-03 | Implement password authentication, user lifecycle, and single-active-session behavior test-first. | DONE | Focused Cloud tests failed before implementation and pass after it. |
| T-04 | Implement fixed roles, game-scope authorization, audit-safe operations, and Cloud Web session handling test-first. | DONE | Focused authorization and Web tests pass. |
| T-05 | Publish C1 Cloud-owned contracts, run full verification, and record evidence. | DONE | Contract checks plus Cloud test/build verification pass. |
| T-06 | Close C1 only when its acceptance matrix is PASS; then prepare the next CHG according to D-05. | IN_PROGRESS | Active record and delivery checkpoint are complete. |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG and refresh AI context.
- [x] Record C1 implementation plan and durable decisions.
- [x] Update contract map and release matrix for validated C1 contracts.
- [ ] Remove active record only after the C1 completion gate passes.

### wt-media-cloud

- [x] Define Cloud-owned identity/API contracts.
- [x] Implement and test identity, authorization, session, and Web behavior.
- [x] Add migration validation and audit-safe verification.

### wt-media-agent

- [ ] Not affected by C1.

### wt-media-desktop

- [ ] Not affected by C1.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Technical users can create users; enabled users authenticate with username/password, disabled users cannot authenticate, and secrets never appear in responses or audit logs. | Focused Cloud identity tests and API contract tests. | PASS |
| AC-02 | A new login invalidates the former session, while multiple tabs sharing the same current session remain valid. | Focused Cloud session tests. | PASS |
| AC-03 | Only the three fixed roles exist; ordinary/senior users are constrained by their game scopes and technicians have global Cloud authorization. | Focused Cloud authorization tests. | PASS |
| AC-04 | Authorization is enforced by Cloud APIs and Web session handling; no Agent or Desktop authorization duplicate is introduced. | Cloud route tests, Web tests, and diff review. | PASS |
| AC-05 | Identity/API contracts are owned by Cloud and compatible consumers are documented before publishing. | Contract validation, `go test ./...`, and Web verification. | PASS |

## 11. Evidence

Evidence files live in `evidence/` and must record facts, not repeat requirements.

- `evidence/task-01-context.md`
- `evidence/identity-contract-and-plan.md`
- `evidence/cloud-identity-verification.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- Created CHG-015 active record and marked M2 as in progress for C1.

Current:
- C1 active-record closure.

Next:
- Commit Workspace evidence and governance, remove the completed active record, then create the authorized M2-C2 CHG.

Blocked:
- None.

Recent verification:
- Cloud provider commit `03b0dcc`; Cloud `go test ./...`, real-process `scripts/verify-health.sh`, Web tests/build, npm audit, contract YAML parsing, Workspace unit tests, skill verification, and config verification all passed.

## 13. DONE Gate

- [x] Scope completed.
- [x] No blocking `Q-xx`.
- [x] Acceptance matrix all PASS.
- [x] Automated tests passed or justified.
- [x] Manual verification evidence recorded where required.
- [x] Diff checked for out-of-scope changes.
- [x] Runtime repositories touched only if listed in scope.
- [x] Required baselines updated.
- [ ] Affected repositories committed independently.
