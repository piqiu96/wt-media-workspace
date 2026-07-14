# Evidence: Repository And CI Status

- CHG: `CHG-20260714-007`
- Task: `T-03`
- Date: 2026-07-14
- Type: git/ci
- Status: PASS

## Initial Repository Status

Before CHG-007:

```text
wt-media-workspace: ## main...origin/main
wt-media-cloud: ## main...origin/main
wt-media-agent: ## main...origin/main
wt-media-desktop: ## main...origin/main
```

## Initial CI Observation

Command:

```text
gh run list --repo piqiu96/wt-media-workspace --limit 5
gh run view 29312918411 --repo piqiu96/wt-media-workspace --log-failed
```

Result:

```text
M0 Workspace Governance failed because test_verify_m0_config required sibling provider repositories in a single-repo GitHub Actions checkout.
```

Fix:

```text
tests/test_verify_m0_config.py now validates placeholder-only structure with allow_missing_repos=True, and only enforces provider paths when sibling repositories are present.
```

## Pending

None.

## Final CI Observation

Commands:

```text
gh run list --repo piqiu96/wt-media-workspace --limit 5
gh run list --repo piqiu96/wt-media-cloud --limit 5
gh run list --repo piqiu96/wt-media-agent --limit 5
gh run list --repo piqiu96/wt-media-desktop --limit 5
```

Results:

```text
wt-media-workspace: completed success, M0 Workspace Governance, run 29313212483
wt-media-cloud: completed success, M0 Cloud, run 29312918409
wt-media-agent: completed success, M0 Agent, run 29312918875
wt-media-desktop: completed success, M0 Desktop, run 29312918263
```

## Final Repository Status

```text
wt-media-workspace: ## main...origin/main
wt-media-cloud: ## main...origin/main
wt-media-agent: ## main...origin/main
wt-media-desktop: ## main...origin/main
```
