# CHG-20260714-016: M2-C2 媒体账号模型和分配

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING
- Created: 2026-07-14
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`

## 2. Change Goal

建立 Cloud-owned `media_account` 正式模型、用户/游戏归属、待识别回填、用户内去重、简单标签和授权 API，使运营能创建和筛选自己的媒体账号、技术能管理全局账号，并为 C3 的 Browser Profile 绑定提供稳定引用。

## 3. Baseline References

- Product baseline: `docs/product/prd/详细文档/第三章_用户与账号管理.md` 3.3
- Product summary: `docs/product/prd/社媒运营平台_产品需求说明书_V1.md` 3.4-3.5
- Engineering baseline: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` 2.4-2.8
- Contract governance: `docs/contracts/跨项目协议治理与变更规范_V1.md`
- Decisions: `docs/decisions/0001-identity-bootstrap-and-game-scope.md`

## 4. Current Facts

- CHG-015 已提供用户、固定角色、游戏范围、单活会话、审计和 Cloud API Cookie 认证。
- Cloud 当前没有 `media_account`、标签表、媒体账号 API 或 Cloud Web 管理能力。
- Browser Profile、比特账号身份和本地运行环境将在 C3-C5 建立；C2 不伪造这些本地事实。

## 5. Scope

### Add

- Cloud `mediaaccount` domain/service with business and login status enums.
- MySQL `media_accounts` and `media_account_tags` migrations and stores.
- Create/list/get/update/identify account operations with user/game authorization and user-scoped duplicate detection.
- Bulk tag add/remove and any/all/exclude tag filtering.
- Cloud-owned media-account API/schema/enum/error contracts.
- Cloud Web media-account client and minimal authenticated list/create/tag interaction.

### Modify

- Wire media-account routes to the C1 authenticated identity service.
- Advance Contract Map and release matrix after verification.

### Delete

- None.

### Explicitly Not Doing

- Browser Profile synchronization, creation, binding or BitBrowser `owner_user_id` validation (C3).
- Agent node/Profile ownership/runtime reporting (C4).
- Profile concurrency locks or sensitive task validation (C5).
- Cookie export, Profile Cookie write/read, login checking, account automation or proxy operations.
- Global tag definitions, tag hierarchy/colors/approval, account owner/handoff workflow, or multi-game accounts.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Implement C2 as a separate Cloud `mediaaccount` module; do not couple business accounts into `identity`. | CONFIRMED |
| D-02 | `media_account.user_id` is direct ownership. Operators and senior operators access only their own accounts and allowed games; technicians may manage all users' accounts. | CONFIRMED |
| D-03 | Each account has exactly one opaque `game_id`; no game catalog is introduced. | CONFIRMED |
| D-04 | New/imported accounts start `pending_identification`; later identity backfill uses `user_id + platform + platform_account_id` uniqueness. Duplicate backfill marks the candidate duplicate without overwriting the existing account. | CONFIRMED |
| D-05 | Store nullable `browser_profile_id`, `original_cookie`, and `active_cookie` columns for the stable model, but expose no C2 API that binds Profile or returns/writes Cookie values after creation. | CONFIRMED |
| D-06 | Tags are per-user account relations with unique `user_id + media_account_id + tag_name`; filtering supports any/all/exclude. | CONFIRMED |
| D-07 | The user explicitly authorized continuous M2-C1 through C6 execution without per-CHG approval; this design is derived from confirmed product baselines and may proceed directly. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

Each task follows failing test → minimal implementation → test → diff check → evidence → checkpoint → independent commit.

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Activate CHG-016, map scope, and refresh AI context. | DONE | Workspace validation and generated context reference CHG-016. |
| T-02 | Implement media-account domain authorization, lifecycle, duplicate handling, and tags test-first. | IN_PROGRESS | Focused Go service tests fail first and pass after implementation. |
| T-03 | Implement MySQL persistence/migration test-first. | TODO | SQL mock tests plus migration review pass. |
| T-04 | Implement authenticated Cloud API and Cloud Web account interaction test-first. | TODO | Route tests and Web tests/build pass. |
| T-05 | Publish Cloud-owned contracts and run full verification. | TODO | Go/Web/contract/Workspace gates pass. |
| T-06 | Close C2 only when the acceptance matrix is PASS, then activate C3 per D-07. | TODO | Independent commits and delivery checkpoint complete. |

## 9. Repository Checklist

### wt-media-workspace

- [x] Create active CHG and record the approved design boundary.
- [x] Refresh AI context and commit plan.
- [ ] Update contract map/release matrix and close the active record.

### wt-media-cloud

- [ ] Add domain/service tests and implementation.
- [ ] Add migration/store tests and implementation.
- [ ] Add authenticated API, Web client, and provider contracts.

### wt-media-agent

- [x] Not affected by C2.

### wt-media-desktop

- [x] Not affected by C2.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Operators/senior operators create and manage only their own accounts within game scope; technicians manage global accounts. | Service and route authorization tests. | TODO |
| AC-02 | Each account belongs to one user and one game, starts pending identification, and exposes no Cookie secret. | Domain, route, contract, and redaction tests. | TODO |
| AC-03 | Identified accounts are unique only by user/platform/platform account ID; duplicates do not overwrite existing account/Profile/Cookie facts. | Service and MySQL duplicate tests. | TODO |
| AC-04 | Business/login statuses are validated independently and tags support add/remove plus any/all/exclude filters. | Service/store/API tests. | TODO |
| AC-05 | Cloud MySQL and Cloud-owned contracts are authoritative; no Agent/Desktop rule copy or C3-C5 behavior is introduced. | Diff review, contract checks, and repository status. | TODO |

## 11. Evidence

- `evidence/task-01-context.md`
- `evidence/cloud-media-account-verification.md`
- `evidence/contract-and-diff-summary.md`
- `evidence/commit-summary.md`

## 12. Current Checkpoint

Completed:
- CHG-015 was verified, committed independently, and removed from active delivery.
- C2 design options were reviewed against the product baseline; the separate domain module was selected over identity coupling or direct SQL route handlers.

Current:
- Add the first failing media-account domain tests.

Next:
- Implement the minimal domain service required by the focused tests.

Blocked:
- None.

Recent verification:
- `python3 scripts/prepare_ai_workspace.py --change CHG-20260714-016` generated an IMPLEMENTING context with Workspace and Cloud scope.

## 13. DONE Gate

- [ ] Scope completed.
- [x] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Manual verification evidence recorded where required.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories touched only if listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.
