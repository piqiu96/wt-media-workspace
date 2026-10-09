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

## RC15 Windows verification build

- Product `v0.1.0-rc.15` Manifest fixed Cloud `v0.1.0-rc.13`, Agent `v0.2.2-rc.2`, and Desktop `v0.1.0-rc.4`; Workspace commit `30cc1eb` pushed the Tag.
- [`release.yml` Run 37743439203](https://github.com/piqiu96/wt-media-workspace/actions/runs/37743439203) succeeded and published the RC15 Pre-release.
- All release assets passed `SHA256SUMS`; the Windows installer was unpacked and its main EXE PE subsystem was verified as `WINDOWS_GUI`.
- Remaining: Windows real-machine regression. Evidence: `evidence/rc15-windows-verification-build.md`.

## RC16 Windows free-space fix

- Desktop `v0.1.0-rc.5` fixed Windows free-space measurement at commit `2231944`; product `v0.1.0-rc.16` uses Cloud `v0.1.0-rc.13`, Agent `v0.2.2-rc.2`, and that Desktop Tag.
- [`release.yml` Run 37767071497](https://github.com/piqiu96/wt-media-workspace/actions/runs/37767071497) succeeded. All release assets passed checksum verification.
- Remaining: real-machine confirmation that 本机设置 shows disk free space without the former `statvfs` error. Evidence: `evidence/rc16-windows-free-space-fix.md`.
- RC versions are fixed by the product Manifest; `config/release-matrix.yaml` remains the historical engineering release matrix for earlier milestone records.

## Windows Agent download commit fix

- Windows RC16 real-machine download reached 99% and Agent logged `[Errno 9] Bad file descriptor` after all shards were merged. Agent is now included in CHG-077 scope.
- Agent commit `106f6ff` fixes Windows part-file fsync and directory handling; local working-tree 701-test suite, clean-clone release-source 690-test suite, and Workspace governance checks pass. Evidence: `evidence/windows-agent-download-commit.md`.
- Agent `v0.2.2-rc.3` component Tag and product `v0.1.0-rc.17` Tag are published. [`release.yml` Run 37804164020](https://github.com/piqiu96/wt-media-workspace/actions/runs/37804164020) succeeded and published the [RC17 Pre-release](https://github.com/piqiu96/wt-media-workspace/releases/tag/v0.1.0-rc.17). The Windows installer SHA-256 in the published inventory is `28b9e48548c0fc59997ea4b1f6ef008fddf00f213a8c09c16f2dd06ebd416ac1`; `build-info.json` fixes Agent to `106f6ff`. The publish job downloaded all assets and checked SHA-256. Real-machine final-file/Cloud-success verification remains pending. Existing `.part` files are untouched.
- RC17 assets were also downloaded locally: all five entries in `SHA256SUMS` passed. The unpacked Windows installer contains the Agent binary with SHA-256 `b739ec73bdf6157083b41bf49b357658411c4844be7cc8fc215b84271fef039b`, matching `build-info.json`; Desktop is PE32+ GUI and Agent is PE32+ console.
- Operator scripts now provide explicit component Tag preflight/push and product Tag push/verification commands. Twelve targeted tests pass; details are in `evidence/release-operator-scripts.md`. Windows real-machine acceptance remains open.
