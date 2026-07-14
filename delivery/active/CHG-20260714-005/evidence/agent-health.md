# Evidence: Agent Health

- CHG: `CHG-20260714-005`
- Task: `T-03`
- Date: 2026-07-14
- Type: command
- Status: PASS

## Initial Gap

Command:

```text
PYTHONPATH=src python3 -m wt_media_agent.local_api.server
```

Result:

```text
No process was started because the module had no executable entrypoint.
```

## Added

- `wt_media_agent.local_api.server` now provides a minimal stdlib HTTP health server.
- `pyproject.toml` now exposes `wt-media-local-health`.
- `scripts/verify-health.sh` runs tests, starts the local health server, and checks `/healthz`.

The health endpoint is M0 process health only and does not define Local Agent task, SSE, or Cloud communication contracts.

## Unit Test

Command:

```text
python3 -m unittest discover -s tests
```

Result:

```text
Ran 2 tests in 0.000s
OK
```

## Health Script

Command:

```text
scripts/verify-health.sh
```

Result:

```text
wt-media-agent local health listening on 127.0.0.1:18765
wt-media-agent health ok
```

Manual endpoint check:

```text
curl --silent --show-error --fail http://127.0.0.1:18765/healthz
{"status":"ok","service":"wt-media-agent","mode":"m0"}
```

Stop behavior:

```text
^Cwt-media-agent local health stopped
```

Sandbox note:

- Starting the local Agent health HTTP service without elevated execution failed with `PermissionError: [Errno 1] Operation not permitted`.
- Elevated execution was required only for binding a local M0 health port.
