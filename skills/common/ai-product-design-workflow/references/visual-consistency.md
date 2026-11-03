# Visual consistency and reuse

## Source order

1. Read project design/frontend rules.
2. Inspect actual shared component/theme implementation.
3. Inspect common visual/interaction examples.
4. Inspect accepted neighboring pages.
5. Design page-specific composition.

Documentation describes intended rules; code shows current implementation. If they differ, identify the discrepancy.

## Reuse boundary

- Base controls/overlays: chosen component library.
- Tokens/theme: one project-owned source.
- Cross-page patterns: actual shared UI capability.
- Business patterns: business module.
- One-off layout: local styles when genuinely unique.

A static common HTML/CSS/JS gallery may be a reference, not a production component library. Do not import demo scripts into runtime unless explicitly allowed.

## Consistency checks

Compare representative pages for title/action placement, filters, table density/sorting/copy/pagination, state wording/colors, row actions, Drawer/Dialog, empty/loading/error feedback, typography, spacing and responsive behavior.

Consistency means shared patterns look and behave alike; it does not mean forcing identical layouts onto different tasks.

## Minimal design

Make the smallest change that solves the observed problem. Do not add decorative cards, metrics, tabs, badges, filters or settings without a user task they improve. Preserve operational information density. A page-specific exception needs a reason and must not silently change the shared baseline.
