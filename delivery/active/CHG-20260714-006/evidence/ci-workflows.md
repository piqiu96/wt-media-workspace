# Evidence: CI Workflows

- CHG: `CHG-20260714-006`
- Task: `T-03`
- Date: 2026-07-14
- Type: inspection
- Status: PASS

## Added Workflows

| Repository | Workflow | Checks |
|---|---|---|
| `wt-media-workspace` | `.github/workflows/m0-workspace.yml` | Python 3.12, Workspace tests, skill verification, M0 config verification |
| `wt-media-cloud` | `.github/workflows/m0-cloud.yml` | Go 1.26.5, `scripts/verify-health.sh` |
| `wt-media-agent` | `.github/workflows/m0-agent.yml` | Python 3.12, `scripts/verify-health.sh` |
| `wt-media-desktop` | `.github/workflows/m0-desktop.yml` | Node 25, `npm run verify` |

## Inspection Command

```text
find .github/workflows -type f -maxdepth 2 -print -exec sed -n '1,180p' {} \;
```

## Result

- All four repositories now define an M0 CI workflow.
- CI commands are repository-local.
- Workspace CI uses `--allow-missing-repos` because a single-repo checkout cannot validate sibling provider paths.
