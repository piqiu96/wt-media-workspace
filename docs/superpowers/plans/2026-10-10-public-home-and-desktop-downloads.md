# Public Home and Desktop Downloads Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the branded public `/home`, redesigned shared login page, and verified release links for three desktop platforms.

**Architecture:** Cloud Web serves the public page and a JSON download manifest from its existing static root. A Workspace release script validates a named public stable GitHub Release and atomically writes that manifest to an explicit output path. The login component retains its session code and changes only presentation.

**Tech Stack:** Vue 3, Vite, Vitest, Python 3.12, GitHub CLI, Go Cloud static server.

**Spec:** `docs/superpowers/specs/2026-10-10-public-home-and-desktop-downloads-design.md`

## Global Constraints

- `/home` is Cloud-only and public; `/` and all business routes still require authentication.
- Three supported installer targets are `windows-x64`, `macos-x64`, and `macos-arm64`.
- Only a published stable product Tag is eligible; no Draft, RC, or floating latest.
- The script writes only its explicit output path and preserves the previous manifest on validation failure.
- Existing Desktop login/session replacement behavior remains intact.
- Do not edit unrelated dirty files in any repository.

## Review Focus

- A nonexistent or malformed manifest must not render usable download buttons.
- A missing, duplicate, or hostile URL in GitHub assets must not overwrite a valid manifest.
- Static browser refresh on `/home` must serve the Cloud entry page.
- Mobile layout must keep login fields and download links reachable without horizontal overflow.
- A newly deployed version must be able to receive the updated manifest after deployment.

---

### Task 1: Release manifest writer

**Files:** Create `scripts/release/update_desktop_downloads.py`, `scripts/release/test_update_desktop_downloads.py`; modify `scripts/release/README.md`.

- [ ] Write failing tests for stable three-platform mapping, Draft/RC/missing/duplicate asset rejection, URL validation, and old-output preservation.
- [ ] Run focused Python unittest and confirm failure.
- [ ] Implement `--tag` and `--output` CLI using GitHub Release JSON, deterministic JSON schema, and atomic same-directory replacement.
- [ ] Run focused tests and read back `v0.1.0` from GitHub; generate initial Cloud Web manifest at its target path.
- [ ] Document upgrade command for deployed `current/web/desktop-downloads.json` and review diff.

### Task 2: Public home and download view

**Files:** Create `web/src/modules/public/pages/HomePage.vue`, `web/src/modules/public/downloadManifest.js`, relevant focused tests; modify `web/src/apps/cloud/router.ts`, `web/src/apps/cloud/main.ts`, `internal/bootstrap/cloud_web_test.go`.

- [ ] Add failing route/manifest tests for public access and exact three-platform links.
- [ ] Add failing Go static route test for `/home` and the manifest path.
- [ ] Implement `/home`, validation/loading/error states, responsive marketing layout, and functional navigation.
- [ ] Run focused Web and Go tests; confirm no Desktop `/home` route.

### Task 3: Shared login visual and brand asset

**Files:** Modify `web/src/modules/auth/pages/LoginPage.vue`, `web/src/shared/ui/BrandLogo.vue`; add one shared public brand asset.

- [ ] Verify existing login and role tests; add targeted assertions only where behavior changes.
- [ ] Apply reference visual as a responsive layout while preserving session calls and replace-session prompt.
- [ ] Run Cloud and Desktop Web builds plus focused auth tests; manually inspect wide and narrow renderings.

### Task 4: Integrated verification and delivery evidence

**Files:** Active CHG evidence/checkpoint and acceptance record in Workspace.

- [ ] Run focused Python, Go, and Web checks; run both Web builds.
- [ ] Query published `v0.1.0` Release, compare generated manifest with the three actual asset URLs, and record browser/download reachability limitations separately.
- [ ] Inspect Cloud and Workspace diffs, preserve unrelated dirty files, and record exact commands/results.
- [ ] Commit Cloud and Workspace changes independently; hand over deploy/update command and any manual browser acceptance remaining.
