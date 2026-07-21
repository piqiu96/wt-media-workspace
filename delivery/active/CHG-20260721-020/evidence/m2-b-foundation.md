# M2-B foundation progress

## Implemented

- Cloud Profile create/open/close/update routes no longer return placeholder success responses; they create typed tasks with a structured payload.
- Cloud task model accepts Profile mutation task types and persists `payload_json` in MySQL.
- Agent runner registers BitBrowser Profile create/open/close/update executors.
- MySQL acceptance schema now includes Profile proxy fields required by the Cloud Profile read model.

## Verification

- Cloud full Go suite: PASS.
- Agent suite: 46 tests PASS.
- Local MySQL migration `20260721_009_task_payload` and `20260721_010_profile_proxy_fields`: PASS.
- Live acceptance probe: `POST /api/v1/browser-profiles` returned HTTP 201 with `task_type=profile_create_task`, `status=pending`, and a structured payload.
- Live Profile list probe: HTTP 200, `errcode=0`, empty list.

## Remaining M2-B work

Read-back/formal Cloud updates, uncertain-result handling, Profile UI actions, and single/batch account-check closure remain in progress. No real BitBrowser Profile was mutated by this probe.
