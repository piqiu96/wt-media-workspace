# Workspace status

- Current: preparing product `v0.1.0-rc.12` with Cloud `v0.1.0-rc.9` (wtmctl one-command deployment), Agent `v0.2.2-rc.2`, Desktop `v0.1.0-rc.3`, environment `online`; previous product `v0.1.0-rc.11` remains published and immutable.
- Manifest: `releases/manifests/v0.1.0-rc.12.yaml` validated (channel `rc`, environment `online`, origin `https://wt.longyanyue.cn`, Linux amd64 + three Desktop platforms).
- Cloud payload checks: `scripts/release/package_assets.py` now requires `bin/wtmctl`, `deploy/config-variable-schema.toml`, and the example TOML files, and rejects any `deploy/*.py` or `deploy/*.sh`.
- Verification: Workspace release tests passed; Delivery governance and AI workspace verifications passed; Cloud `M0 Cloud` CI `37182796598` passed.
- Remaining: publish and observe product RC12 Release workflow, download and verify the Cloud artifact, record Run/Artifact/SHA-256, and complete the BaoTa server acceptance.
