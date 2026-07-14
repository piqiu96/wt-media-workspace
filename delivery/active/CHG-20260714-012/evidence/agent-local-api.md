# Evidence: Agent Local API

- CHG: `CHG-20260714-012`
- Task: `T-02`
- Date: 2026-07-14
- Type: test
- Status: PASS

## Actual

```text
PYTHONPATH=src python3 -m unittest discover -s tests
Ran 20 tests
OK
```

Manual HTTP verification:

```text
GET /api/v1/status -> {"agent_id":"local-agent-dev","status":"idle","current_task_id":null,"pending_result_count":0}
GET /api/v1/events -> event: status
```
