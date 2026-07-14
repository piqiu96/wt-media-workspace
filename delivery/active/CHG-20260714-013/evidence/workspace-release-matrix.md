# Workspace Release Matrix Evidence

- CHG: `CHG-20260714-013`
- Task: T-04 Workspace release matrix and evidence.
- Status: PASS

## Action

Added release matrix entry:

```text
0.1.0-m1-desktop-local-agent-controls
```

The entry records Desktop consumption of:

```text
local_agent_api: v1@2026.07.14.5
local_event_schemas: status@2026.07.14.5
```

## Expected Result

Workspace config verification recognizes the M1-C6 release entry while contract ownership remains unchanged.

## Actual Result

```text
python3 -m unittest discover -s tests
python3 scripts/verify_skills.py
python3 scripts/verify_m0_config.py
```

All passed.
