# Result status normalization

- Account-check results are normalized to the Cloud `login_status` enum before projection; unknown or executor-error values become `environment_error`.
- Proxy connectivity `reachable` is normalized to the UI/Cloud `ok` check result.
- This prevents external executor vocabulary from violating MySQL business constraints.
