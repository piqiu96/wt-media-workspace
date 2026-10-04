# Workspace status

- Current: product `v0.1.0-rc.13` GitHub Actions Run `37199184328` completed successfully with Cloud `v0.1.0-rc.11`, Agent `v0.2.2-rc.2`, Desktop `v0.1.0-rc.3`, environment `online`; its Artifact digest and server acceptance remain pending. Task 10 path/logging changes are committed in Cloud `620cf89` and untagged.
- Manifest: `releases/manifests/v0.1.0-rc.13.yaml` validated (channel `rc`, environment `online`, origin `https://wt.longyanyue.cn`).
- Cloud payload checks: `scripts/release/package_assets.py` and its tests now require `bin/wt-media-cloud`; the fixture packages were updated to match.
- Verification: Workspace release tests pass; Delivery governance and AI workspace verifications pass.
- Remaining: publish and observe RC13, download and verify the Cloud artifact, record Run/Artifact/SHA-256, and complete the BaoTa server acceptance.
