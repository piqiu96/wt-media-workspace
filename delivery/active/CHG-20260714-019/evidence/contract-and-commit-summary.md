# Contract and commit summary

- Contract state: `m2_sensitive_profile_guard`.
- Cloud-Agent API/current minimum: `2026.07.14.6`.
- Cloud error revision: `2026.07.14.5`.
- Agent Local API remains `2026.07.14.6`; event/status advance to `2026.07.14.8`; Agent version is `0.2.2`.
- Release: `0.2.4-m2-sensitive-profile-guard`.
- Workspace start: `5c59c5a`; Agent: `5cd9212`, `3d4081a`; Cloud: `d1d0ddc`, `2753715`.

The guard is deliberately usable only with tasks inserted by trusted future Cloud business modules. C5 adds no user-facing generic task creator and no sensitive executor.
