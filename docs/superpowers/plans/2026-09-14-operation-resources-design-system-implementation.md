# Operation Resources Design System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give browser windows, proxy management and social media accounts one reusable WT Media resource-management visual system without altering runtime behavior.

**Architecture:** A globally imported CSS token layer owns visual constants. Four presentation-only shared Vue components own repeated layout and semantic status display; each existing resource page retains its scripts, API clients and handlers while composing these components and shared classes.

**Tech Stack:** Vue 3, TDesign Vue Next, Vite, Vitest, scoped Vue CSS.

**Spec:** `docs/superpowers/specs/2026-09-14-operation-resources-design-system-design.md`

## Global Constraints

- Do not modify API calls, route definitions, data structures, permissions or Tauri/Local Agent invocation boundaries.
- Use `--wt-*` values from `src/styles/design-token.css`; do not introduce per-page hard-coded semantic colors.
- Keep all existing actions reachable. Browser-window overflow actions must call their existing functions.
- Do not stage generated `dist-desktop`, `.generated`, `target` or unrelated files.

---

### Task 1: Token layer and reusable resource presentation

**Files:**
- Create: `wt-media-cloud/web/src/styles/design-token.css`
- Create: `wt-media-cloud/web/src/shared/styles/resource-module.css`
- Create: `wt-media-cloud/web/src/shared/ui/resource/ResourcePageHeader.vue`
- Create: `wt-media-cloud/web/src/shared/ui/resource/ResourceCard.vue`
- Create: `wt-media-cloud/web/src/shared/ui/resource/ResourceStatGrid.vue`
- Create: `wt-media-cloud/web/src/shared/ui/resource/ResourceStatusBadge.vue`
- Modify: `wt-media-cloud/web/src/apps/cloud/main.ts`
- Modify: `wt-media-cloud/web/src/apps/desktop/main.ts`
- Test: `wt-media-cloud/web/src/shared/ui/resource/resourceModule.test.js`

- [ ] Write a failing source-level test requiring both entrypoints to import `design-token.css` and `resource-module.css`, and each component to expose its documented props/slots.
- [ ] Run `npm test -- --run src/shared/ui/resource/resourceModule.test.js`; expect failure because files and imports do not exist.
- [ ] Implement token values, style primitives, and presentation-only components. `ResourceStatusBadge` maps `success`, `warning`, `danger`, `neutral`, `info` to Token-backed classes.
- [ ] Run the targeted test; expect pass.
- [ ] Commit only the source, styles and test with `feat(web): add resource design primitives`.

### Task 2: Browser window resource page

**Files:**
- Modify: `wt-media-cloud/web/src/modules/profiles/pages/ProfilesPage.vue`
- Modify: `wt-media-cloud/web/src/modules/profiles/pages/ProfilesPage.test.js` (or create it when absent)

- [ ] Write a failing test asserting `ResourcePageHeader`, `ResourceCard`, `ResourceStatGrid`, `ResourceStatusBadge`, `wt-resource-table`, and a TDesign dropdown retain `openProfile`, `closeProfile`, `openProxyBinding`, `openEdit`, and `toggleBusinessStatus` bindings.
- [ ] Run the targeted test; expect failure because the page does not use resource primitives or the dropdown.
- [ ] Add display-only derived statistics. Recompose the existing template: Header and actions, stats, ResourceCard around filters/table, shared status badges, and “详情/打开/更多” action grouping. Do not alter handlers or availability conditions.
- [ ] Run targeted test and then `npm test -- --run src/layout/AppLayout.test.js src/modules/profiles/pages/ProfilesPage.test.js`; expect pass.
- [ ] Commit only window page and its test with `feat(web): unify browser window resource page`.

### Task 3: Proxy and social-account resource pages

**Files:**
- Modify: `wt-media-cloud/web/src/modules/proxy/pages/ProxyPage.vue`
- Modify: `wt-media-cloud/web/src/modules/accounts/pages/AccountsPage.vue`
- Modify: `wt-media-cloud/web/src/modules/proxy/pages/ProxyPage.test.js` (or create it when absent)
- Modify: `wt-media-cloud/web/src/modules/accounts/pages/AccountsPage.test.js` (or create it when absent)

- [ ] Write failing tests requiring both pages to use shared header/card/table/badge primitives and verifying their existing action handlers remain present.
- [ ] Run the two targeted tests; expect failure because neither template contains the resource primitive composition.
- [ ] Add derived proxy stats from `proxies`, adapt its search/actions/table status cells; adapt account’s existing `stats` to the four specified cards and update both templates to shared visual primitives. Retain all fields, filters and handler bindings.
- [ ] Run both targeted tests and all resource page tests; expect pass.
- [ ] Commit only the two pages and tests with `feat(web): unify proxy and account resource pages`.

### Task 4: Regression, package and evidence

**Files:**
- Modify: `wt-media-workspace/delivery/active/CHG-20260914-036/change.md`
- Create: `wt-media-workspace/delivery/active/CHG-20260914-036/evidence/2026-09-14-operation-resources-ui.md`

- [ ] Run `cd wt-media-cloud/web && npm test -- --run` and inspect zero failures.
- [ ] Run `cd wt-media-cloud/web && npm run build:desktop` and inspect a successful production build.
- [ ] Run `cd wt-media-workspace && ./scripts/local-control.sh start`; verify Cloud, Agent, BitBrowser, Desktop assets, DMG and login smoke all pass.
- [ ] Record exact commands, test counts, build result, running environment result and only committed source paths in evidence/checkpoint.
- [ ] Commit Workspace evidence independently with `docs(m2): record resource design system verification`.
