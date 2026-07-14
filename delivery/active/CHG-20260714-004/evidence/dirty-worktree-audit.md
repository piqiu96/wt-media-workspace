# Evidence: Dirty Worktree Audit

- CHG: `CHG-20260714-004`
- Task: `T-02`
- Date: 2026-07-14
- Type: audit
- Status: PASS

## Purpose

Classify the pre-existing dirty runtime repository files and decide what can be kept in M0.

## Initial Findings

### Cloud

Pre-existing dirty worktree included:

- M0-compatible skeleton:
  - repository rules and generated skill copies;
  - `cmd/server`;
  - `internal/app`;
  - `internal/common`;
  - `internal/infra`;
  - `contracts`, `configs`, `deploy`, `scripts`, `tests`, `web`;
  - `go.mod`, `go.sum`, `Dockerfile`.
- Out-of-scope implementation:
  - `internal/modules/identity`;
  - `internal/modules/account`;
  - `internal/modules/agent`;
  - `internal/modules/task`;
  - business module placeholders for discovery/material/production/publication/interaction/analytics/settings;
  - business table migrations for users, accounts, agents, tasks, and audit events.

Decision:

- Keep the Cloud process, health route, config, common API helpers, infra placeholders, contracts placeholders, and repository rule files.
- Delete formal business module implementations and business migrations from M0.
- Keep Go + Hertz as the architecture target. Full Cloud test requires Go >= 1.20 because Hertz `netpoll` uses Go 1.20 unsafe APIs.

### Agent

Pre-existing dirty worktree included:

- M0-compatible skeleton:
  - Python package under `src/wt_media_agent`;
  - local/cloud entrypoints;
  - minimal app shell;
  - local API health scaffold;
  - config, generated, modes, core, runtimes, storage, executors package placeholders;
  - contracts, packaging, patches, scripts, tests placeholders.
- Out-of-scope implementation or future placeholders:
  - `communication/cloud_client.py`;
  - `core/task_runner.py`;
  - platform-specific directories for Douyin, Bilibili, and Baijiahao.

Decision:

- Keep the installable Python package skeleton, entrypoints, local health surface, and neutral package placeholders.
- Delete Cloud polling/task runner and platform adapter placeholders from M0.

### Desktop

Pre-existing dirty worktree included:

- M0-compatible skeleton:
  - Tauri/Vue root files;
  - `src-tauri` shell;
  - Rust bridge placeholders for commands, filesystem, secure store, system, updater;
  - `src` frontend placeholders;
  - packaging/scripts/tests placeholders.
- Out-of-scope implementation or future placeholders:
  - Rust `agent` module;
  - frontend `localAgent.ts`.

Decision:

- Keep the Tauri/Vue shell and neutral Rust bridge placeholders.
- Delete Local Agent lifecycle/proxy code from M0; it belongs to M1 Desktop CHGs.

## Post-Cleanup Structure

Cloud retained source files:

```text
internal/middleware/doc.go
internal/infra/database/doc.go
internal/infra/logger/doc.go
internal/infra/config/config.go
internal/infra/config/config_test.go
internal/infra/scheduler/doc.go
internal/infra/objectstore/doc.go
internal/app/app.go
internal/app/routes.go
internal/common/id.go
internal/common/doc.go
internal/common/api.go
```

Agent retained source files:

```text
src/wt_media_agent/generated/__init__.py
src/wt_media_agent/config.py
src/wt_media_agent/core/__init__.py
src/wt_media_agent/modes/__init__.py
src/wt_media_agent/cloud_main.py
src/wt_media_agent/runtimes/__init__.py
src/wt_media_agent/__init__.py
src/wt_media_agent/storage/__init__.py
src/wt_media_agent/local_api/server.py
src/wt_media_agent/local_api/__init__.py
src/wt_media_agent/executors/__init__.py
src/wt_media_agent/app.py
src/wt_media_agent/local_main.py
```

Desktop retained source files:

```text
src/generated/README.md
src/local-pages/README.md
src/main.ts
src/stores/README.md
src/components/README.md
src/services/README.md
src-tauri/src/updater/mod.rs
src-tauri/src/filesystem/mod.rs
src-tauri/src/secure_store/mod.rs
src-tauri/src/system/mod.rs
src-tauri/src/main.rs
src-tauri/src/commands/mod.rs
```

## Follow-Up

- Record cleanup diff and test results.
