# Workspace status

- Current: product `v0.1.0-rc.14` GitHub Actions Run `37581481877` completed successfully with Cloud `v0.1.0-rc.12`, Agent `v0.2.2-rc.2`, Desktop `v0.1.0-rc.3`, environment `online`; Cloud Artifact has been downloaded and verified. Server acceptance remains pending.
- Manifest: `releases/manifests/v0.1.0-rc.14.yaml` validated (channel `rc`, environment `online`, origin `https://wt.longyanyue.cn`).
- Cloud payload checks: `scripts/release/package_assets.py` and its tests now require `bin/wt-media-cloud`; the fixture packages were updated to match.
- Verification: RC14 `validate`、Cloud/Agent/Desktop builds、`package` 和 `publish-pre` 全部成功；Cloud Artifact ZIP 与 tar 的 SHA-256、ZIP CRC、包内 `SHA256SUMS`、Tag/Commit、50 个 Migration 及所需程序均通过回读。详细证据见 `evidence/rc14-manual-tag-and-build.md`。Workspace 全量测试仍有 5 项既有 M0/Contract/交付对齐断言失败，未记为通过。
- Server acquisition: `server-acceptance.md` now provides direct GitHub Actions Artifact download with `GH_TOKEN`, fixed Run/name, `SHA256SUMS` and Cloud tar SHA-256 verification; no local download/upload is needed. Syntax and existing local RC14 tar hash were checked in `evidence/server-direct-pull.md`.
- Remaining: execute the pull and deployment on BaoTa, then record the actual result.

## Task 12 release preparation

- Cloud `v0.1.0-rc.12` has been pushed and read back at `be1d1a1`; the new product Manifest pins it with the existing Agent `v0.2.2-rc.2` and Desktop `v0.1.0-rc.3` Tags.
- `scripts/release/submit_tag.py` adds a manual preflight and an explicit `--push` action. Workspace branch and annotated product `v0.1.0-rc.14` Tag were pushed and read back at `7a781c3`; the Tag push triggered Run `37581481877`.

## 2026-10-08 Windows deployment fix increment

- Desktop and Cloud Web fixes are implemented in `5deebf9` and `9478a64`, and recorded in `evidence/windows-desktop-console-logging.md` and `evidence/cloud-web-download-prompt.md`.
- Desktop verification passed `cargo check`, full `cargo test` (527 passed / 6 ignored), `git diff --check`, and the release-only GUI subsystem source check. Cloud Web full `npm test` passed (50 files / 488 tests).
- Windows PE subsystem inspection and real-machine regression remain open; the CHG stays IMPLEMENTING.
- RC versions are fixed by the product Manifest; `config/release-matrix.yaml` remains the historical engineering release matrix for earlier milestone records.
