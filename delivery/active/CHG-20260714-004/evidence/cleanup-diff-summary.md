# Evidence: Cleanup Diff Summary

- CHG: `CHG-20260714-004`
- Task: `T-03`
- Date: 2026-07-14
- Type: diff
- Status: PASS

## Scope

This CHG changed runtime repositories only to close M0 scaffold state:

- keep neutral engineering skeleton;
- remove future business implementations and platform-specific placeholders;
- add minimal scaffold tests where possible;
- preserve generated skill copies and repository rule files.

## Cloud Cleanup

Removed from M0:

- formal identity module;
- formal account/profile/proxy module;
- formal Agent registration/heartbeat module;
- formal task create/claim/result module;
- business module placeholder package set;
- business table migration files.

Kept in M0:

- Go + Hertz process skeleton;
- health routes;
- config loader;
- common JSON helpers;
- infra placeholder packages;
- Cloud contract ownership placeholders marked as placeholder-only, with no formal API/schema/DTO/event definitions active in M0;
- minimal config tests.

Additional cleanup:

- Fixed the Cloud health-route skeleton import set so `context.Context` is explicitly imported.
- Updated Cloud repository rules to avoid listing removed business module directories as current M0 structure.

Known verification limitation:

- current local Go is `1.19.9`;
- Hertz `netpoll` requires Go >= 1.20.

## Agent Cleanup

Removed from M0:

- platform-specific Douyin/Bilibili/Baijiahao adapters;
- Cloud communication client placeholder;
- task runner placeholder.

Kept in M0:

- package skeleton;
- Local/Cloud entrypoints;
- app shell;
- local API health scaffold;
- neutral package placeholders;
- Agent contract ownership placeholders marked as placeholder-only, with no formal Local Agent API/SSE/error definitions active in M0;
- minimal unittest coverage.

## Desktop Cleanup

Removed from M0:

- Rust Local Agent lifecycle/proxy placeholder;
- frontend `localAgent` service placeholder.

Kept in M0:

- Tauri/Vue project skeleton;
- Rust neutral bridge module placeholders;
- frontend placeholder directories;
- packaging/scripts/tests placeholders;
- npm scaffold test script.
- `contracts.lock.json` with an empty M0 consumption map.

## Out-Of-Scope Scan

Residual matches are explanatory only:

- Cloud README states that user/account/Agent/task/publication/discovery/production/interaction/analytics are intentionally not implemented in M0.
- Agent AGENTS says platform adapters must not mutate Cloud state once introduced by future CHGs.
- Desktop local-pages README says Agent status and task progress pages are introduced by M1 Desktop CHGs.
