# M2 Completion Program Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the 64-point M2 scope as five independently verified vertical closures.

**Architecture:** Cloud retains formal facts and creates tasks; Agent performs every BitBrowser, proxy, Cookie, SMS, and account effect; Desktop manages the Local Agent and local observation. Each CHG produces redacted evidence and independent commits before the next begins.

**Tech Stack:** Go/Hertz/MySQL, Vue 3/Vite/Vitest, Python 3.12/unittest/SQLite, Rust/Tauri, BitBrowser Local API.

## Global Constraints

- Only one M/L CHG is active in `delivery/active` at a time.
- Do not enter M3 before M2 reaches `DONE` through human acceptance.
- No real Cookie, proxy password, SMS token, binding ticket, node credential, or permit credential may enter Git, output, or evidence.
- Use a new dedicated `WT-M2-TEST` BitBrowser Profile; do not mutate any existing Profile.
- External side effects use: Cloud authorization → typed task → Agent lock/effect → read-back → validated Cloud update → audit.
- A failed or ambiguous external effect is not blindly retried; every retry creates a new task attempt.

---

## Program File Map

| CHG | Primary repositories | Primary outcome | Detailed plan |
|---|---|---|---|
| M2-A | Workspace, Cloud, Agent, Web | Restore trustworthy acceptance; complete permissions/session/audit closure | `2026-07-21-m2-a-trustworthy-acceptance.md` |
| M2-B | Cloud, Agent, Web | Complete account and Profile lifecycle and verified account check | Written after M2-A closes. |
| M2-C | Cloud, Agent, Web | Real proxy import, allocation, BitBrowser write/read-back | Written after M2-B closes. |
| M2-D | Cloud, Agent, Web | Cookie read/write and three account-opening paths | Written after M2-C closes. |
| M2-E | Desktop, Agent, Cloud, Web, Workspace | Real Sidecar lifecycle, recovery/security, full M2 acceptance | Written after M2-D closes. |

## CHG Gates

### CHG M2-A: Trustworthy Acceptance and Permissions

- [ ] Create one active record with scope restricted to Web test repair, validator repair, authorization coverage, session replacement behavior, Agent claim stop behavior, and BitBrowser bind/rebind audit.
- [ ] Complete the detailed M2-A plan, record redacted evidence, and independently commit each affected repository.
- [ ] Recount M2-A matrix items and close M2-A only when each is PASS.

### CHG M2-B: Media Account and Profile

- [ ] Define exact Cloud task schema changes and Agent local API behavior before implementation; update owner contracts first.
- [ ] Replace Profile create/open/close/update response placeholders with Agent-backed, read-back-verified task flows.
- [ ] Add first-binding guidance, field protection, restore-vs-accept Diff behavior, and single/batch account check UI.
- [ ] Verify using the dedicated Profile without modifying an existing Profile.

### CHG M2-C: Proxy and Profile

- [ ] Define the proxy mutation task payload/result and Agent contract changes before implementation.
- [ ] Implement file import, Agent protocol validation, Cloud quota/allocation preview, task execution, BitBrowser write/read-back, and expiry behavior.
- [ ] Verify the dedicated Profile opens through the selected proxy and record only redacted endpoint facts.

### CHG M2-D: Cookie and Opening

- [ ] Define Cookie task payload/result and SMS adapter boundary before implementation.
- [ ] Implement Cookie write/read-back, authorized/audited export, batch Cookie opening, SMS path, and manual-code path.
- [ ] Verify mixed-batch partial success, exact retry, and secret redaction with the dedicated Profile.

### CHG M2-E: Desktop and Comprehensive Acceptance

- [ ] Resolve a real Local Agent sidecar for the production acceptance path and verify lifecycle/recovery.
- [ ] Run all M2 64-point, role, real-dependency, recovery, and security matrices.
- [ ] Update stable baselines and release matrix; move M2 only to `VERIFYING`; request human acceptance before `DONE`.

## Program Completion Check

- [ ] Every CHG has its own active record, checkpoint, acceptance matrix, redacted evidence, and independent repository commits.
- [ ] All 64 M2 points are PASS with real-dependency proof where applicable.
- [ ] The dedicated test Profile is closed and deleted after acceptance.
- [ ] Exposed test credentials are rotated by the user after acceptance.
