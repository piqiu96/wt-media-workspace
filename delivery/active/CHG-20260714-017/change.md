# CHG-20260714-017: M2-C3 比特浏览器用户与 Profile 绑定

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

建立 Agent-owned BitBrowser Profile 脱敏扫描与 Cloud-owned 比特用户/Profile 正式镜像绑定：所有 Profile 身份先全量校验、扫描只生成待确认 Diff、用户确认后才应用正式数据，并允许同属主媒体账号绑定有效 Profile。

## 3. Baseline References

- Product: `docs/product/prd/详细文档/第三章_用户与账号管理.md` 3.4
- Product summary: `docs/product/prd/社媒运营平台_产品需求说明书_V1.md` 3.3-3.6
- Engineering: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` 2.4-2.8, 6.2-6.4
- Contract governance: `docs/contracts/跨项目协议治理与变更规范_V1.md`
- Decision: `docs/decisions/0002-bitbrowser-profile-identity-normalization.md`
- Official BitBrowser API: `https://doc.bitbrowser.cn/api-jie-kou-wen-dang/liu-lan-qi-jie-kou`

## 4. Current Facts

- C1 provides authenticated users/game scopes; C2 provides media accounts and nullable Profile references.
- Agent owns BitBrowser calls but has no BitBrowser adapter yet.
- Workspace currently marks Local Agent API/Event contracts active at revision `2026.07.14.5`, while the Agent provider contains only README placeholders. C3 must resolve this provider/governance conflict before extending the contract.
- C4 owns Agent node identity, Profile runtime owner, and ongoing environment reporting; C3 must not claim that an un-attested browser payload is sufficient for sensitive task execution.

## 5. Scope

### Add

- Agent BitBrowser list client with paging, timeout/error mapping, secret stripping, and uniform `userId` validation.
- Agent Local API Profile scan endpoint and formal provider-owned Local API/error/schema definitions, including the missing existing M1 status/event surface.
- Cloud user Bit account binding fields, `browser_profile`, staged scan/candidate, and Diff persistence.
- Cloud scan submission/confirmation services and authenticated API; formal Profile schema/enum/error contracts.
- Media-account-to-Profile binding with same-user and same-platform uniqueness validation.
- Minimal Cloud Web scan review/confirm and media-account Profile binding client behavior.

### Modify

- Contract map/release matrix to provider revisions after verification.
- C2 media-account module to apply validated Profile references.

### Delete

- None.

### Explicitly Not Doing

- Agent node ownership, device attestation, continuous runtime/environment reporting (C4).
- Profile task locks or sensitive task preflight (C5).
- Profile create/update/delete, proxy changes, Cookie write/read, opening browsers, login checks, publication, or interaction.
- Automatic Diff application, automatic identity rebind, remote local Profile deletion, or permanent Diff ignore.
- Treating `operUserId` or `mainUserId` as `owner_user_id`.

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Normalize official BitBrowser `userId` to product `owner_user_id`; never use `operUserId` as ownership. | CONFIRMED |
| D-02 | Agent calls `POST /browser/list` with page starting at 0 and page size 100, returning only allow-listed Profile facts and no Cookie/proxy credentials. | CONFIRMED |
| D-03 | Empty lists, missing identities, mixed identities, failed API responses, or mismatch with an existing binding are unverifiable and create no applicable formal change. | CONFIRMED |
| D-04 | Scan data is staged; only explicit confirmation applies the user binding and Profile mirror. No automatic rebind occurs. | CONFIRMED |
| D-05 | A user confirms only their own Bit identity. Technician visibility does not grant a remote bypass of the user's local environment. | CONFIRMED |
| D-06 | Media accounts bind only to active Profiles with the same `user_id`; a Profile may bind different platforms but only one account per platform. | CONFIRMED |
| D-07 | C3 does not authorize sensitive tasks. C4/C5 add attested runtime ownership and task preflight/locks. | CONFIRMED |
| D-08 | C3 repairs the missing Agent provider definitions at the same time it extends Local API contracts; Workspace must not claim definitions absent from the provider. | CONFIRMED |
| D-09 | User authorization D-05 from CHG-015 continues to permit C3 execution without another approval wait. | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Activate C3, record external-field ADR and provider-contract conflict resolution plan. | DONE | Context generator and Workspace gates pass. |
| T-02 | Implement Agent BitBrowser scan/identity validation test-first. | DONE | Focused tests failed on the absent adapter, then the full Python suite passed. |
| T-03 | Publish Agent Local API provider definitions and expose the scan endpoint test-first. | DONE | Local API tests, four provider YAML parses, and real local health passed. |
| T-04 | Implement Cloud staged scans, binding, Profile mirror, and MySQL persistence test-first. | DONE | Focused domain/sqlmock tests and the full Go suite passed. |
| T-05 | Implement authenticated Cloud API, media-account Profile binding, Web client, and Cloud contracts test-first. | DONE | Route tests, Web client tests/build, and sixteen provider YAML parses passed. |
| T-06 | Run cross-repo verification, record limitations, close C3, then activate C4 under D-09. | IN_PROGRESS | Acceptance matrix and independent commits complete. |

## 9. Repository Checklist

### wt-media-workspace

- [x] Record active CHG and durable external identity mapping.
- [x] Refresh context, verify, and commit plan.
- [x] Advance contract/release governance.
- [ ] Close after final cross-repository regression.

### wt-media-cloud

- [x] Add staged Profile identity/domain persistence.
- [x] Add Profile/media-account binding APIs and contracts.
- [x] Add secret-safe Web review/confirm client behavior.

### wt-media-agent

- [x] Add BitBrowser adapter and full-list identity validation.
- [x] Repair/publish Local API v1 definitions and add scan route.

### wt-media-desktop

- [x] Not affected; C3 does not duplicate browser rules or add a direct Vue-to-Agent call.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Agent pages through all Profiles, strips secrets, and yields one verified normalized owner only when every Profile has the same non-empty `userId`. | Adapter tests. | PASS |
| AC-02 | Cloud scan submission does not modify formal binding/Profile data; confirmation applies only a ready self-owned scan. | Service/store/route tests. | PASS |
| AC-03 | Mismatch, mixed/empty identity, failed/expired scan, or attempted rebind applies no formal change and produces an explicit error/status. | Domain/API tests. | PASS |
| AC-04 | Media accounts bind only to same-user active Profiles and enforce one account per Profile/platform. | Service/MySQL tests. | PASS |
| AC-05 | Agent and Cloud provider definitions exist, match runtime behavior, and contain no Cookie/proxy secrets; C4/C5 behavior is absent. | YAML/diff/full verification. | PASS |

## 11. Evidence

- `evidence/task-01-context.md`
- `evidence/agent-bitbrowser-verification.md`
- `evidence/cloud-profile-binding-verification.md`
- `evidence/contract-and-commit-summary.md`

## 12. Current Checkpoint

Completed:
- C2 completed and was removed from active delivery.
- Official BitBrowser API was checked and ADR-0002 records the external identity normalization.
- Missing Agent provider definitions were identified before C3 runtime edits.
- Agent revision `2026.07.14.6` now provides secret-safe BitBrowser paging/identity validation and the Local scan API.
- Cloud revision `2026.07.14.3` now provides staged scan review/confirmation, Profile mirrors, and media-account Profile binding.
- Contract Map and release matrix advance only after provider definitions and runtime verification exist.

Current:
- Run the final fresh cross-repository regression and record commit/evidence closure.

Next:
- Close C3 and activate M2-C4 without an approval pause under D-09.

Blocked:
- None; the provider-contract conflict is explicitly in C3 scope and must be resolved before contract advancement.

Recent verification:
- Agent 28-test full suite, four provider YAML files, and real local health passed.
- Cloud full Go/vet, eight Web tests/build, and sixteen provider YAML files passed before the final fresh regression.
- Workspace contract/release verifier accepts the C3 revisions; the old verifier first rejected the intentional governance advance.

## 13. DONE Gate

- [x] Scope completed.
- [x] No blocking `Q-xx`.
- [x] Acceptance matrix all PASS.
- [x] Automated tests passed or justified.
- [x] Manual verification evidence recorded where required.
- [x] Diff checked for out-of-scope changes.
- [x] Runtime repositories touched only if listed in scope.
- [x] Required baselines updated.
- [x] Affected repositories committed independently.
