# Evidence: Diff And Scope Scan

- CHG: `CHG-20260714-005`
- Task: `T-05`
- Date: 2026-07-14
- Type: diff
- Status: PASS

## Runtime Diffs

Cloud changes:

```text
scripts/verify-health.sh
```

Agent changes:

```text
pyproject.toml
scripts/verify-health.sh
src/wt_media_agent/local_api/server.py
tests/test_app.py
```

Desktop changes:

```text
package.json
scripts/health-check.mjs
```

## Out-Of-Scope Scan

Cloud command:

```text
rg -n "identity|account|agent.register|task.claim|publication|Bilibili|Baijiahao|Douyin|Profile|LocalAgent|localAgent|task polling|result upload|heartbeat" README.md AGENTS.md cmd internal contracts migrations web scripts
```

Result:

```text
Only explanatory placeholder/future-scope lines were found.
```

Agent command:

```text
rg -n "Bilibili|Baijiahao|Douyin|publication|interaction|discovery|TaskRunner|cloud_client|task polling|result upload|heartbeat|Profile|account" README.md AGENTS.md src contracts tests scripts pyproject.toml
```

Result:

```text
No matches.
```

Desktop command:

```text
rg -n "localAgent|LocalAgent|AgentController|HTTP/SSE proxy|task progress|Agent status|publication|interaction|account|Profile" README.md AGENTS.md src src-tauri contracts.lock.json package.json scripts
```

Result:

```text
Only explanatory future-scope lines were found.
```
