# Workspace status

- Current: preparing product `v0.1.0-rc.13` with Cloud `v0.1.0-rc.11`, Agent `v0.2.2-rc.2`, Desktop `v0.1.0-rc.3`, environment `online`; product `v0.1.0-rc.12` remains published and immutable.
- Manifest: `releases/manifests/v0.1.0-rc.13.yaml` validated (channel `rc`, environment `online`, origin `https://wt.longyanyue.cn`).
- Cloud payload checks: `scripts/release/package_assets.py` and its tests now require `bin/wt-media-cloud`; the fixture packages were updated to match.
- Verification: Workspace release tests pass; Delivery governance and AI workspace verifications pass.
- Remaining: publish and observe RC13, download and verify the Cloud artifact, record Run/Artifact/SHA-256, and complete the BaoTa server acceptance.
