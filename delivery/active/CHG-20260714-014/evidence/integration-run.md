# Integration Run Evidence

- CHG: `CHG-20260714-014`
- Task: T-02/T-03 M1 integration verification.
- Status: PASS

## Failing Verification

Command:

```text
python3 scripts/verify_m1_integration.py
```

Expected result:

The command fails before the script exists.

Actual result:

```text
can't open file '.../scripts/verify_m1_integration.py': [Errno 2] No such file or directory
```

## Sandbox Verification

Command:

```text
python3 scripts/verify_m1_integration.py
```

Actual result in normal sandbox:

```text
PermissionError: [Errno 1] Operation not permitted
```

Reason:

The integration script needs loopback port binding for real Cloud and Local Agent HTTP processes.

## Passing Verification

Command:

```text
python3 scripts/verify_m1_integration.py
```

Mode:

Approved elevated local loopback execution.

Actual result:

```json
{
  "agent": {
    "agent_id": "agent-m1-c7",
    "claimed_task_id": "task_25f2b6abe309a27e79f9f91a",
    "noop_executor_result": "succeeded"
  },
  "cloud": {
    "compatibility_revision": "2026.07.14.4",
    "final_task_progress": 100,
    "final_task_status": "succeeded"
  },
  "desktop": {
    "output": "wt-media-desktop health ok",
    "verify": "passed"
  },
  "local_agent": {
    "sse_event": "status",
    "status": {
      "agent_id": "local-agent-dev",
      "current_task_id": null,
      "pending_result_count": 0,
      "status": "idle"
    }
  }
}
```

Ports are intentionally omitted from the stable evidence because the script allocates temporary free ports each run.
