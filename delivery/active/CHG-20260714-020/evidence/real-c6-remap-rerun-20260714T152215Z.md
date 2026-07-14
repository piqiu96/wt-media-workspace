# Real C6 rerun after BitBrowser identity remap

- Timestamp: 2026-07-14T15:22:15Z
- Scope: CHG-20260714-020
- Purpose: Verify the new `main_user_id` / `profile_user_id` model against real local MySQL, Cloud API, and BitBrowser Local API.

## MySQL schema refresh

Command:

```text
go run .cache/create_c6_db.go -host 127.0.0.1 -port 3306 -user root -db wt-media-cloud -reset -apply -migrations migrations
```

Result:

```text
database=wt-media-cloud
migrations_applied=5
table_count=14
```

Schema spot-check:

```text
users.bit_main_user_id
browser_profiles.main_user_id
browser_profiles.profile_user_id
profile_sync_scans.main_user_id
profile_sync_candidates.main_user_id
profile_sync_candidates.profile_user_id
local_agent_nodes.reported_main_user_id
browser_profile_runtime_presence.main_user_id
users.idx_users_bit_main_user_id non_unique=1
browser_profiles.uq_browser_profiles_bit_profile non_unique=0
```

Status: PASS.

## Real Cloud / MySQL C6 flow

Cloud started with local MySQL and initial technician bootstrap. The C6 verifier exercised:

- health;
- single-active session;
- three roles and role boundaries;
- media account creation and identification;
- staged Profile scan and confirmation using `main_user_id` plus `profile_user_id`;
- media account Profile bind;
- one-use Local Agent binding ticket;
- runtime report with `main_user_id`;
- concurrent sensitive permit grant/waiting;
- expired uncertain permit review.

Result:

```text
status=pass
database=wt-media-cloud
steps=health,single_active_session,three_roles,role_boundaries,media_accounts,profile_confirm_and_account_bind,one_use_binding,runtime_report,concurrent_permit,expired_permit_review
users=3 profiles=1 nodes=1 tasks=4 permits=2
secrets_printed=false
```

Status: PASS.

## BitBrowser Local API port and scan

Findings:

- Project default BitBrowser Local API URL is `http://127.0.0.1:54345`.
- `127.0.0.1:54345` is listening.
- `127.0.0.1:8899` is not the current project default and was not the active BitBrowser Local API port in this run.

Real adapter scan against `http://127.0.0.1:54345`:

```text
profile_count=37
main_user_id=2c9bc06191effa4e0191f9589996619f
profile_user_count=2
payload_keys=[bit_profile_id, bit_updated_at, group_id, group_name, main_user_id, name, profile_user_id, seq, status]
forbidden_present=[]
```

Status: PASS.

## Runtime environment effect

Runtime environment collection against the real BitBrowser Local API reports:

```text
operating_system=macos
cpu_architecture=arm64
agent_version=0.2.2
ffmpeg.status=not_installed
workdir_status=normal
disk.status=normal
bitbrowser_status=normal
main_user_id=2c9bc06191effa4e0191f9589996619f
bit_profile_ids_count=37
```

Status: PASS for BitBrowser/runtime identity. FFmpeg remains `not_installed`, which is reported as an environment fact rather than a blocker for this C6 identity/runtime flow.
