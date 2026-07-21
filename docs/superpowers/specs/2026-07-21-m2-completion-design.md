# M2 Completion Design

> Date: 2026-07-21  
> Scope: M2 用户、角色、媒体账号、BitBrowser Profile、代理、Cookie、开户、Desktop 与安全闭环  
> Governing baseline: `delivery/MASTER_IMPLEMENTATION_PLAN.md` and current product, engineering, contract, and decision documents

## 1. Goal

Complete M2 as five sequential, independently verifiable business closures and move M2 from `IN_PROGRESS` to `VERIFYING`, then to `DONE` only after final human acceptance.

M2 completion means an operator can use Cloud Web or Desktop to prepare a correctly authorized BitBrowser environment, manage media accounts and Profiles, assign and verify proxies, complete supported account-opening paths, observe execution, and recover from failures without leaking credentials or confusing formal Cloud facts with local runtime state.

## 2. Current State

The previous 64-point gap matrix contains an arithmetic error: its row-level PASS values total 31, not 30. A fresh code and test review supports the following working assessment:

| Classification | Count | Meaning |
|---|---:|---|
| Complete and reusable | 35 | Implementation exists and the currently available evidence is sufficient to carry it forward. |
| Partially implemented | 16 | Some code exists, but the user-visible or real-dependency closure is incomplete. |
| Not implemented | 13 | Required behavior has no usable implementation. |

The working completion estimate is therefore 35/64, approximately 55%. This estimate is planning input, not a milestone acceptance result. The 64-point matrix must be re-evaluated during execution and final acceptance.

Known baseline facts:

- Cloud Go tests pass.
- Agent has 44 passing unit tests.
- Cloud and Desktop Vue builds pass.
- Desktop Rust has 2 passing unit tests and unused-code warnings.
- All 8 current Web API-client tests fail because relative URLs reach Node's native `fetch` without a test base URL.
- `verify_m2_acceptance.py` references a removed Desktop source path and crashes.
- `verify_product_master_alignment.py` asserts obsolete M1/M2 milestone states.
- BitBrowser Local API is reachable and returns one verified main-account identity with 37 visible Profiles.
- A dedicated disposable test Profile may be created and modified for M2 acceptance.
- Real proxy, Cookie, and SMS-code dependencies are available for acceptance.

## 3. Delivery Strategy

M2 will be completed as five sequential CHGs. Only one CHG may be active at a time.

```text
M2-A 权限与可信验收基础
→ M2-B 媒体账号与 Profile
→ M2-C 代理与 Profile
→ M2-D Cookie 与开户
→ M2-E Desktop、安全与 M2 综合验收
```

Each CHG must produce a usable vertical closure rather than a set of disconnected endpoints. Existing correct code is reused and re-verified; it is not rewritten merely to fit new numbering.

## 4. Cross-Cutting Architecture

### 4.1 Ownership

- Cloud owns users, roles, game scopes, media accounts, Profile formal facts, proxy configuration, tasks, audit records, and all Cloud-provided contracts.
- Agent owns BitBrowser calls, proxy execution checks, Cookie read/write, account identification, SMS or browser automation, and other external effects.
- Desktop owns the Tauri shell, secure local bridge, Local Agent process lifecycle, local status, local logs, and local file selection.
- Workspace owns M2 planning, cross-repository contract governance, evidence indexes, and verified release combinations.

Handlers do not execute long-running external work. Cloud creates typed tasks; Agent claims and executes them; Cloud receives idempotent progress and results. Desktop does not duplicate Cloud business rules and does not read Agent SQLite directly.

### 4.2 Formal Facts and Runtime Facts

Cloud remains the source of truth for media accounts, assignments, and business status. BitBrowser and Agent reports are runtime observations. A runtime observation becomes a formal Cloud update only through a validated service operation with authorization and audit.

Profile and proxy mutations follow:

```text
Cloud preflight and authorization
→ typed sensitive task
→ Agent local lock
→ BitBrowser mutation
→ BitBrowser read-back
→ Agent result
→ Cloud validates and records formal fact
→ audit event
```

Failure before read-back is not success. An ambiguous external result becomes `result_uncertain` or review-required behavior and is not blindly retried.

### 4.3 Credentials

- Cookie, SMS token, proxy password, binding ticket, node credential, and Profile permit must not be committed, copied into evidence, logged, or returned in ordinary API responses.
- Real credentials are injected only through temporary process environment, local secure storage, or an interactive acceptance input that does not persist them.
- Evidence records only redacted identifiers, action outcomes, timestamps, error codes, and read-back summaries.
- Externally exposed credentials must be rotated after acceptance.

## 5. CHG Designs

### 5.1 M2-A: Permissions and Trustworthy Acceptance Foundation

Goal: make M2 verification reliable and complete the user/session/security closure before adding more external effects.

Scope:

- repair the Web API-client test environment and restore all existing Web tests;
- update M2 and product-plan governance validators to current paths and milestone states;
- verify game-scope authorization at every M2 business entry point with positive and negative tests;
- make invalidated Local Agent sessions stop claiming new work and safely finish, cancel, or mark uncertain any in-flight sensitive task according to task state;
- add a dedicated audit action for initial BitBrowser binding and rebinding;
- perform three-role UI and API acceptance for user creation, role/game assignment, login replacement, disablement, password actions, and audit visibility.

Exit: all M2-A matrix points pass, automation is green, and governance scripts produce deterministic failures instead of exceptions.

### 5.2 M2-B: Media Account and Profile Closure

Goal: bind one Cloud user to one verified BitBrowser main-account tree and make media-account/Profile operations real rather than response placeholders.

Scope:

- implement the first-binding guided flow and identity warnings;
- replace placeholder Cloud Profile create/open/close/update responses with typed tasks and Agent execution;
- validate `main_user_id`, `profile_user_id`, Cloud assignment, active node, and visible Profile before sensitive operations;
- protect Cloud-owned operational fields during scans;
- show complete Profile Diff details, including proxy changes;
- support accepting BitBrowser state or restoring the approved Cloud configuration through Agent mutation and read-back;
- implement single and batch account checks with the required login-state mapping and media-account identity/status updates;
- keep retries attempt-based and preserve previous task history.

Exit: a user can bind, scan, review, confirm or restore, create/bind/open/check an account, and observe formal Cloud facts updated from verified Agent results.

### 5.3 M2-C: Proxy and Profile Closure

Goal: import, verify, allocate, write, and read back a real proxy for an authorized Profile.

Scope:

- support text, CSV, TXT, and Excel import with redacted preview and per-row validation;
- move real connectivity and protocol validation to an Agent executor;
- define global platform defaults and per-proxy platform quotas in Cloud;
- calculate deterministic allocation previews without mutating Profiles;
- create a sensitive proxy-mutation task after confirmation;
- write the selected proxy to BitBrowser and read it back before Cloud records the assignment;
- surface partial success, quota conflicts, failed read-back, and precise retry actions;
- show expiry reminders and prevent allocation of disabled or expired proxies;
- allow Diff-discovered proxies to create incomplete Cloud records that require review.

Exit: the dedicated test Profile opens with the assigned real proxy after write/read-back verification, and failures cannot create false Cloud assignments.

### 5.4 M2-D: Cookie and Account-Opening Closure

Goal: complete Cookie read/write and the three required account-opening paths with partial-success and retry behavior.

Scope:

- parse imported Cookie text into structured browser cookies without exposing values in normal list/detail views;
- execute Cookie write and read-back on the dedicated Profile and update `original_cookie`/`active_cookie` according to product semantics;
- make Cookie export an explicitly authorized, audited sensitive action;
- complete batch Cookie opening: create/allocate Profile, reserve proxy capacity, write proxy, write Cookie, open/check identity, and update the media account;
- implement SMS-link/code polling through a configurable adapter using transient credentials;
- implement manual verification-code handoff without storing one-time codes;
- record per-item state and task attempt, allow successful items to remain committed, and retry only failed or uncertain-safe items;
- perform capacity checks before task creation.

Exit: one real account succeeds through each applicable path, a mixed batch proves partial success and failed-item retry, and all secrets remain absent from logs/evidence.

### 5.5 M2-E: Desktop, Security, Recovery, and Final Acceptance

Goal: prove the complete M2 experience through the real Desktop shell and close the milestone.

Scope:

- package or resolve the Local Agent sidecar and verify start, health, status, event stream, stop, restart, and cleanup;
- remove development fallback behavior from the production acceptance path;
- expose real local environment, task progress, error, and recovery state through Desktop pages;
- verify that Vue never holds Local Agent dynamic credentials and Tauri does not read SQLite;
- test Desktop, Agent, Cloud, and BitBrowser interruption/restart behavior;
- run the 64-point M2 matrix, three-role UI matrix, real dependency matrix, security checks, and cross-repository regression;
- update contracts, release matrix, baselines, evidence, checkpoints, and independent repository commits;
- move M2 to `VERIFYING`; only final human acceptance may move it to `DONE`.

Exit: all 64 points pass, required real-dependency evidence exists, all automated gates pass, and the user completes final manual acceptance.

## 6. Test Profile Lifecycle

A dedicated Profile with a recognizable `WT-M2-TEST` name is used for destructive acceptance.

```text
create dedicated Profile
→ verify main/profile identity
→ assign and read back proxy
→ write and read back Cookie
→ run account check and opening paths
→ exercise restart/recovery
→ export redacted evidence
→ close and delete the test Profile
```

The Profile ID may be recorded in local evidence only in redacted form. Existing user Profiles are read-only unless separately authorized.

## 7. Error and Recovery Rules

- Validation or authorization failure creates no external mutation task.
- A task failing before an external effect may be retried with a new task attempt.
- A task failing after a possible external effect must read back state; if state cannot be proven, it becomes uncertain and requires review.
- Batch operations are itemized. Successful items are never rolled back merely because another item failed.
- Re-login invalidates the previous session and stops new claims from the old Local Agent binding.
- Profile-sensitive tasks remain exclusive per Profile across account check, Cookie, proxy, publication-preflight, and other protected operations.
- Cloud and Agent restarts preserve formal state, checkpoints, pending reports, and retry history.

## 8. Verification Model

Every CHG uses the same evidence ladder:

1. failing unit, contract, or integration test;
2. minimal implementation;
3. repository-local automated tests;
4. cross-repository contract and governance validation;
5. real MySQL and applicable BitBrowser/proxy/Cookie/SMS/Desktop verification;
6. browser/Desktop role and error-path acceptance;
7. diff scope review, redacted evidence, checkpoint, and independent commit.

Mock or fixture evidence can prove deterministic logic but cannot satisfy a real-dependency exit condition.

## 9. Commit and Governance Boundaries

- Each M2 closure is a separate M/L CHG.
- Only one CHG is active in `delivery/active` and `delivery/LEDGER.md`.
- Runtime repositories are committed independently.
- Workspace evidence/checkpoints are committed separately from runtime implementation.
- Existing unrelated dirty files and generated build artifacts are preserved and excluded from commits.
- A CHG is closed only when its acceptance matrix passes and its checkpoint has no blocker.

## 10. Explicitly Not Doing

- M3 or later business objects and workflows;
- new role types, organizations, custom RBAC, or a workflow engine;
- automatic final publishing;
- storing real credentials in repository fixtures or evidence;
- modifying any existing non-test BitBrowser Profile;
- treating TCP reachability alone as successful proxy acceptance;
- marking M2 `DONE` from code presence without real dependency and human acceptance.

## 11. Success Criteria

M2 is complete only when:

- all 64 M2 points are PASS;
- five business closures work through Web and applicable Desktop paths;
- real MySQL, BitBrowser, proxy, Cookie, SMS/manual verification, and Sidecar evidence is recorded where applicable;
- authorization, session replacement, sensitive-task exclusivity, redaction, restart, idempotency, partial success, and precise retry are verified;
- Cloud, Agent, Web, Desktop, contract, governance, and regression gates pass;
- the release matrix reflects the verified component combination;
- the user completes final manual acceptance.
