# Windows Desktop Console And Logging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Windows release Desktop window-only while giving Desktop/Agent explicit per-user data, cache, and log paths that survive restarts and preserve old data.

**Architecture:** Resolve one `SystemPaths` value at startup and manage it as application state. Windows production uses `%LOCALAPPDATA%\WTMedia\...`; macOS keeps its current `HOME`-based layout; Windows log fallback uses an explicit temp directory. Existing path, logging, command, and sidecar consumers receive that resolved value instead of independently reading `HOME`.

**Tech Stack:** Rust/Tauri 2, existing tracing/logging modules, Rust unit tests, Vue 3 tests for Cloud Web copy.

**Spec:** `docs/superpowers/specs/2026-10-08-windows-desktop-console-logging-design.md`

## Global Constraints

- Windows release only: `#![windows_subsystem = "windows"]`; debug builds keep the console.
- Desktop Windows roots: `%LOCALAPPDATA%\WTMedia\Desktop\{data,logs,cache}`.
- Agent Windows default data root: `%LOCALAPPDATA%\WTMedia\Agent`; Desktop always passes it as `WT_MEDIA_AGENT_DATA_DIR` on Windows unless explicitly configured.
- macOS behavior remains `~/Library/Application Support/WTMedia/Desktop`, `~/Library/Logs/WTMedia/Desktop`, and `~/Library/Caches/WTMedia/Desktop`.
- Never fall back to the executable directory or current working directory.
- If Local AppData is unavailable, Windows logs only use an explicit temporary directory and the failure is visible.
- Migration copies only when the legacy directory exists and the new data directory is empty; it never deletes and never overwrites.
- No Cloud API or Agent runtime-code changes.

## Review Focus

- Windows without `LOCALAPPDATA`: logging must use temp and diagnostics must not pretend success — Task 2.
- Existing old Desktop data and empty new data: migration must copy without overwrite — Task 5.
- Existing non-empty new data: migration must not run — Task 5.
- Explicit Agent data directory: Windows computed default must not override it — Task 4.
- Repeated Windows launches: download settings must remain at the same writable path — Tasks 2, 3, and 6.

---

### Task 1: Add The Shared System Path Resolver

**Files:**
- Create: `src-tauri/src/system_paths.rs`
- Modify: `src-tauri/src/main.rs`
- Test: inline `#[cfg(test)] mod tests`

**Interfaces:**
- Produces: `struct SystemPaths { home: Option<PathBuf>, local_app_data: Option<PathBuf>, temp_dir: PathBuf }`
- Produces: `SystemPaths::from_parts(home, local_app_data, temp_dir) -> SystemPaths`
- Produces: `SystemPaths::production_base(&self) -> Result<&Path, SystemPathError>`
- Produces: `SystemPaths::agent_default_data_dir(&self) -> Result<PathBuf, SystemPathError>`
- Produces: `SystemPaths::log_fallback(&self) -> PathBuf`

- [ ] **Step 1: Write failing resolver tests.** Assert Windows returns `local/WTMedia/Desktop` as base and `local/WTMedia/Agent`; macOS returns `home` as base and `home/Library/Application Support/WTMedia/Agent`; missing inputs return `SystemPathError`; fallback is `temp/wt-media-desktop-logs`.
- [ ] **Step 2: Run the new tests and watch them fail.** Run: `cargo test system_paths` in `src-tauri`. Expected: compile/fail on missing API.
- [ ] **Step 3: Implement the resolver and register it in Tauri state.** Keep environment input injectable; `main` computes it once and calls `.manage(SystemPaths::...)`.
- [ ] **Step 4: Run tests.** Run: `cargo test system_paths`. Expected: PASS.

### Task 2: Route Desktop And Logging Paths Through SystemPaths

**Files:**
- Modify: `src-tauri/src/app_paths.rs`
- Modify: `src-tauri/src/logging/paths.rs`
- Modify: `src-tauri/src/logging/setup.rs`
- Modify: `src-tauri/src/main.rs`
- Test: existing inline modules plus new Windows tests

**Interfaces:**
- Consumes: `SystemPaths::production_base`.
- Produces: `app_paths::resolve(base: Option<&Path>, environment, manifest)`; on Windows production `base` is Local AppData.
- Produces: `logging::paths::directory(base, environment, manifest)` and `agent_directory(base, configured)` using the same Windows base rule.

- [ ] **Step 1: Add failing Windows and fallback tests.** Pin Desktop roots, Agent log root, macOS retention, and temp fallback path.
- [ ] **Step 2: Run path tests.** Run: `cargo test app_paths && cargo test logging::paths`. Expected: new tests fail.
- [ ] **Step 3: Implement Windows branches.** Add explicit temp fallback only for logging when Local AppData is missing; retain production base errors for data/cache.
- [ ] **Step 4: Update logging setup.** Pass the resolved base and fallback into `plan`; install fallback when production base is unavailable while keeping the visible problem.
- [ ] **Step 5: Run tests.** Run: `cargo test app_paths && cargo test logging`. Expected: PASS.

### Task 3: Wire Commands To The Single Resolved State

**Files:**
- Modify: `src-tauri/src/commands/storage.rs`
- Modify: `src-tauri/src/commands/settings.rs`
- Modify: `src-tauri/src/commands/diagnostic.rs`
- Modify: `src-tauri/src/commands/reveal.rs`
- Modify: `src-tauri/src/commands/cleanup.rs`
- Modify: `src-tauri/src/main.rs`

**Interfaces:**
- Consumes: managed `SystemPaths`.
- Produces: `commands::storage::resolve(config, system)` remains the shared resolver for read, reveal, cleanup, and diagnostic commands.

- [ ] **Step 1: Add a resolver test proving no command calls `HOME` independently.** Use a synthetic `SystemPaths`; assert command helper roots match it.
- [ ] **Step 2: Run command tests.** Run: `cargo test commands::`. Expected: new test fails.
- [ ] **Step 3: Inject `State<SystemPaths>` and replace direct environment reads.**
- [ ] **Step 4: Run tests.** Run: `cargo test commands::`. Expected: PASS.

### Task 4: Pass The Windows Agent Data Directory

**Files:**
- Modify: `src-tauri/src/sidecar/mod.rs`
- Modify: `src-tauri/src/main.rs` or the sidecar start call path

**Interfaces:**
- Consumes: `SystemPaths::agent_default_data_dir`.
- Produces: `sidecar::environment(config, token, system) -> Vec<(String, String)>`.

- [ ] **Step 1: Add failing sidecar tests.** Windows unset config sends the computed Agent directory; explicit config wins; macOS unset omits the variable.
- [ ] **Step 2: Run sidecar tests.** Run: `cargo test sidecar::environment`. Expected: fail.
- [ ] **Step 3: Implement the platform-aware environment.**
- [ ] **Step 4: Run tests.** Run: `cargo test sidecar`. Expected: PASS.

### Task 5: Migrate Legacy Windows Data Safely

**Files:**
- Create or modify: `src-tauri/src/system_paths.rs` (migration functions)
- Modify: `src-tauri/src/main.rs`

**Interfaces:**
- Consumes: `SystemPaths`, old/new Desktop data roots.
- Produces: `migrate_windows_legacy_data(old, new) -> Result<Option<MigrationReport>, MigrationError>` with `copied_files`, `skipped_files`, and `source`.

- [ ] **Step 1: Add failing migration tests.** Cover absent old, old plus empty new, old plus non-empty new, collision, and explicit Agent data excluded.
- [ ] **Step 2: Run migration tests.** Run: `cargo test migrate_windows_legacy_data`. Expected: fail.
- [ ] **Step 3: Implement recursive copy-if-absent and startup invocation.** Log the report; never remove either directory.
- [ ] **Step 4: Run tests.** Run: `cargo test migrate_windows_legacy_data`. Expected: PASS.

### Task 6: Enable GUI Subsystem And Preserve Development Console

**Files:**
- Modify: `src-tauri/src/main.rs:1-12`
- Test: `tests/windows_release_subsystem.py` or equivalent CI assertion

- [ ] **Step 1: Add a source-level test.** Assert the conditional attribute exists for non-debug Windows and there is no unconditional GUI subsystem.
- [ ] **Step 2: Run it.** Run: `python3 tests/windows_release_subsystem.py`. Expected: fail before edit.
- [ ] **Step 3: Add `#![cfg_attr(all(target_os = "windows", not(debug_assertions)), windows_subsystem = "windows")]`.**
- [ ] **Step 4: Run all Desktop tests.** Run: `cargo test`. Expected: PASS.

### Task 7: Fix Cloud Web Download Prompt And Verify

**Files:**
- Modify: `wt-media-cloud/web/src/apps/desktop/features/local-settings/LocalSettingsPage.vue`
- Test: nearest existing Cloud Web component test

- [ ] **Step 1: Add/update failing text test.** Expected prompt is exactly `请先选择下载目录`.
- [ ] **Step 2: Run the relevant test.** Run the existing `npm test` target from `wt-media-cloud/web`. Expected: fail.
- [ ] **Step 3: Change the prompt only; do not add a default download directory.**
- [ ] **Step 4: Run related and then full web tests.** Expected: PASS.

### Task 8: Governance, Evidence, And Independent Commits

**Files:**
- Modify: `wt-media-workspace/delivery/active/CHG-20261008-078/checkpoint.md`
- Modify: `wt-media-workspace/delivery/active/CHG-20261008-078/status/*.md`

- [ ] **Step 1: Record commands and results, including known Windows CI/manual gaps.**
- [ ] **Step 2: Run Workspace governance:** `python3 scripts/verify_delivery_governance.py && python3 scripts/verify_product_master_alignment.py`.
- [ ] **Step 3: Commit Desktop, Cloud Web, and Workspace independently.** Do not commit unrelated dirty files.
- [ ] **Step 4: Explicitly report that PE subsystem and real Windows regression are not proven until Windows CI/user regression runs.**
