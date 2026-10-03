# Workspace status

- Current: product `v0.1.0-rc.8` is published as a GitHub Pre-release after successful Run `37116209229`.
- Workspace release check now accepts only blank Cloud deployment templates, rejects private config, and validates Cloud Tag and source Commit.
- CHG-077 deployment design now fixes one template set with explicit staging/production variable tables; real values are rendered and validated on the target server rather than copied from the current release.
- Server acceptance template is `server-acceptance.md`; actual BaoTa evidence remains pending.
- RC7 product Run `37114670702` was cancelled before publishing because its Cloud guide omitted the static Web site route. Its Cloud Artifact was downloaded and verified, but is not the deployment candidate.
- Release readback: `isPrerelease=true`, `isDraft=false`; Windows x64, macOS Intel, macOS ARM Desktop assets, Manifest, checksums, and `build-info.json` are present. Published Cloud digest matches the downloaded Linux Artifact.
- User confirmed an appended CHG-077 deployment design: self-contained release directories, one `current` switch, BaoTa Go project for Server/HTTPS, BaoTa process manager for Scheduler/Worker, and no shared/systemd runtime layout. The implementation plan is in `plan.md`; RC8 remains immutable and is superseded as a deployment candidate once the new RC is produced.
- Remaining: execute the appended Cloud plan, produce and verify a new RC, then perform actual BaoTa deployment and manual server evidence. The current product workflow will rebuild unchanged Desktop/Agent components; a Cloud-only release path belongs to later delivery work.
