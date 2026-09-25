# Decision 0007: Visual and Frontend Engineering Baseline

## Status

Accepted

## Context

M1 (Cloud-Agent-Desktop Minimum Task Loop) has been completed and accepted. The current Cloud Web frontend at `wt-media-cloud/web/` uses hand-written CSS with no UI component library, resulting in inconsistent styling, low development velocity, and poor visual quality. A comprehensive visual proposal exists at `docs/engineering/specs/web-desktop-visual-system.md`.

The following decisions are needed before M2 business module development begins, to ensure all subsequent pages share a consistent visual system.

## Decision

### 1. Frontend Architecture

> **Updated 2026-07-16:** The frontend architecture has been refined in the separate architecture document at `docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md`. That document supersedes the frontend architecture section below for module boundaries, directory structure, routing, build pipeline, and communication models. Decision 0007 remains authoritative for **visual conventions** (component library, templates, status colors, interaction rules).

- **Single Vue source repository.** All Cloud and Desktop Vue source code lives in `wt-media-cloud/web/`.
- **Two independent applications.** Cloud and Desktop are independent frontend applications with separate entry points, separate routers, separate menus, and separate build outputs — but they share the same source tree via `apps/modules/shared` layering.
- **`wt-media-desktop` does not hold Vue pages.** Desktop only keeps the Tauri Rust shell, native capabilities, packaging, and update infrastructure. Vue code moves to `wt-media-cloud/web/src/apps/desktop/`.
- For detailed directory structure, dependency direction, routing rules, communication models (Cloud API direct / Tauri Runtime / Mixed), and build pipeline, see the architecture document above.

### 2. UI Component Library

- **TDesign Vue Next** is the single UI component library for the entire project.
- No other UI component library (Element Plus, Ant Design Vue, Naive UI, Arco Design, shadcn-vue) may be introduced.
- **TDesign Starter** (`tdesign-vue-next-starter`) is used as the initial application skeleton—layout, sidebar navigation, route structure, and basic auth page. Starter demo content (dashboard widgets, sample charts, marketing pages) is removed; the skeleton is treated as project source code, not a template to re-copy on upgrades.
- **TDesign Icons** is the single icon set. Missing icons are added as project-local SVG files.
- **Apache ECharts** is the single charting engine, used only for data dashboards and statistics (M9). Not used as a general UI component.
- **State management**: Pinia.
- **CSS approach**: TDesign Design Tokens + project-level CSS custom properties. No atomic CSS framework (Tailwind, UnoCSS) in the first version.

### 3. Prohibited Practices

- Overriding TDesign component internals with `!important` or project-level CSS that targets `.t-*` classes.
- Introducing a second UI library under any circumstance.
- Using multiple icon sets.
- Writing per-module CSS that duplicates Design Token semantics.
- Mixing presentation patterns across modules (one module using cards, another using raw tables, without template standardization).

### 4. Page Template System

All business pages conform to one of six unified templates:

1. **Resource List Page** — table + filter bar + batch actions + side drawer for details. Used for content discovery, media accounts, material library,成品 management, comment templates.
2. **Task Workbench** — task statistics + status tabs + task list + progress + logs. Used for crawl, compose, publish, interact, auto-production tasks.
3. **Batch Configuration Wizard** — step-by-step (select → configure → preview → execute → results). Used for batch publish, batch interact, batch claim.
4. **Detail Drawer** — unified tabs (basic info → related records → execution history → audit log). Used everywhere for detail views.
5. **Settings Page** — left category navigation + right grouped form + save bar. Used for platform config, risk control, production rules, permissions.
6. **Data Dashboard** — first-page workbench and statistics only. Not used for operational management pages.

### 5. Status and Color Convention

| Status | Color |
|---|---|
| running, pending, queued | Blue |
| success, normal | Green |
| warning, pending_review | Orange |
| failed, error | Red |
| discarded, cancelled, expired | Gray |
| automated, ai_generated | Purple |

A single `<BusinessStatus>` component encapsulates this mapping. Individual pages must not assign tag colors directly.

### 6. Interaction Rules

1. One primary action per page.
2. Cards for summary only, not for data management.
3. Table action buttons: max 2–3 visible, rest in "More" menu.
4. Short messages → modal. Detail/light edit → drawer. Complex flows → dedicated page.
5. Batch operations must use a fixed bottom action bar.
6. Local data labeled "本地". Cloud data labeled "云端".
7. Failure states must show the failure reason and next action.
8. No large-area gradients, glows, or frosted glass.
9. All list pages must provide empty state, loading state, and error state.

### 7. First Refactoring Batch

The following three pages are built first to establish template patterns:

1. **Desktop System Status Center** — validates Desktop-specific capabilities, Agent status, local environment, logging, local/cloud labeling.
2. **Content Discovery List** — validates filter area, table, cover preview, detail drawer, batch conversion.
3. **Compose Task Workbench** — validates task status, queue, progress, failure reason, retry, interrupt, local vs cloud execution.

After these three are established, templates are replicated to material management,成品 management, publish management, interact management, and task pages.

### 8. Timing

UI refactoring begins as **M2-R0**, before any M2 business module (R1–R11). Estimated 3–5 days for the full migration.

## Consequences

- Positive: all M2+ pages follow a consistent visual system from the start; no retroactive UI cleanup needed after business modules are built.
- Negative: M2-R0 adds ~3–5 days before business feature development begins.
- Follow-up: dark mode is deferred past first version. TDesign Starter skeleton is adopted and customized, not periodically re-fetched from upstream.
- **2026-07-16 follow-up:** Architecture doc `docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md` created. Decision 0007's visual decisions remain authoritative; frontend architecture layout is superseded by the new doc.
