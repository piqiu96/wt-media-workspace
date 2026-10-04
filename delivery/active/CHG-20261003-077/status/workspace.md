# Workspace status

- Current: product `v0.1.0-rc.12` is published as a successful Pre-release after Run `37182978601` (all jobs green), with Cloud `v0.1.0-rc.9`, Agent `v0.2.2-rc.2`, Desktop `v0.1.0-rc.3`, environment `online`; previous product `v0.1.0-rc.11` remains published and immutable.
- Manifest: `releases/manifests/v0.1.0-rc.12.yaml` validated (channel `rc`, environment `online`, origin `https://wt.longyanyue.cn`, Linux amd64 + three Desktop platforms).
- Cloud payload checks: `scripts/release/package_assets.py` now requires `bin/wtmctl`, `deploy/config-variable-schema.toml`, and the example TOML files, and rejects any `deploy/*.py` or `deploy/*.sh`.
- Verification: Workspace release tests passed; Delivery governance and AI workspace verifications passed; Cloud `M0 Cloud` CI `37182796598` passed.
- Release result: Run `37182978601` success; Cloud artifact `wt-media-cloud_v0.1.0-rc.12_linux-amd64.tar.gz` SHA-256 `90026317ef333c6609a7bedd5d51aadfbdedc056a3365c1be00bb1dfab956fb6`; Desktop Web `desktop-web_v0.1.0-rc.12.tar.gz` SHA-256 `15dc93cb4cf912f6bc17f524686b17bfb211381e33d0926a2b3970d085e33e52`; `build-info.json` records workspace `82de3ce` and cloud `1d6457f`.
- Remaining: complete the BaoTa server acceptance in `server-acceptance.md`.
