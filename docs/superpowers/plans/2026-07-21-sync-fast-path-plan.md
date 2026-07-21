# M2 synchronous fast-path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make bounded proxy checks synchronous while keeping complex BitBrowser interactions taskized.

**Architecture:** Cloud calls a local Agent synchronous check endpoint and persists the verified result. Existing Cloud tasks remain the path for browser-opening and page-interaction operations; no automatic sync-to-async fallback is added.

**Tech Stack:** Go/Hertz Cloud, Python Agent HTTP runtime, Vue/Vite Web, MySQL persistence.

## Global Constraints

- Do not return proxy credentials in Cloud or Web responses.
- Keep existing task contracts and complex-operation executors unchanged.
- Use the active CHG checkpoint and repository-specific commits.

### Task 1: Agent synchronous proxy-check endpoint

**Files:**
- Modify: `wt-media-agent/src/wt_media_agent/local_main.py` and the Agent HTTP route module that owns health/status endpoints.
- Test: `wt-media-agent/tests/test_proxy_executor.py` or the Agent HTTP route tests.

- [ ] Add a bounded authenticated `POST /api/v1/proxy-check` route accepting protocol, host, port, and optional credentials, returning only `connectivity`, `observed_exit_ip` when available, and a sanitized error.
- [ ] Reuse the existing proxy connectivity implementation and enforce the configured timeout.
- [ ] Add tests for reachable/unreachable and malformed input; assert credentials are absent from responses.
- [ ] Run `python3 -m unittest discover -s tests -q`.
- [ ] Commit Agent changes.

### Task 2: Cloud synchronous Agent client and proxy route

**Files:**
- Modify: `wt-media-cloud/internal/modules/proxy/routes.go` and Cloud Agent client/HTTP dependency wiring.
- Test: `wt-media-cloud/internal/modules/proxy` route tests.

- [ ] Add a bounded local-Agent client dependency with a fixed timeout and explicit unavailable/timeout errors.
- [ ] Change `POST /api/v1/proxies/:id/check` to call the Agent synchronously, persist the verified result through the proxy service, and return the sanitized proxy result.
- [ ] Do not create a task on the normal path; preserve the existing task endpoint for explicit background retry.
- [ ] Add route tests for success, Agent unavailable, timeout, and credential redaction.
- [ ] Run `GOCACHE=/private/tmp/wt-media-go-cache go test ./internal/modules/proxy ./internal/modules/cloudagent`.
- [ ] Commit Cloud changes.

### Task 3: Web synchronous result and explicit background retry

**Files:**
- Modify: `wt-media-cloud/web/src/shared/api/proxy.js`, `web/src/modules/proxy/pages/ProxyPage.vue`, and task navigation helpers.
- Test: `wt-media-cloud/web/src/proxy.test.js` or the existing API-client test files.

- [ ] Render the synchronous connectivity result inline and refresh the proxy row.
- [ ] Replace the current unconditional “created task” notice with a clear synchronous success/error notice.
- [ ] Add an explicit “后台重试” action that calls the taskized endpoint only after the user chooses it.
- [ ] Add tests for synchronous response handling and explicit retry action.
- [ ] Run `npm test -- --run`, `npm run build:cloud`, and `npm run build:desktop`.
- [ ] Commit Web changes.

### Task 4: Integrated evidence and checkpoint

**Files:**
- Create: `wt-media-workspace/delivery/active/CHG-20260721-020/evidence/sync-fast-path.md`.
- Modify: `wt-media-workspace/delivery/active/CHG-20260721-020/change.md`.

- [ ] Record Cloud, Agent, Web, and local environment verification without secrets.
- [ ] Run both workspace validators and update the active checkpoint.
- [ ] Commit workspace evidence.
