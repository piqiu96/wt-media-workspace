# Workspace status

- Current: product `v0.1.0-rc.8` is published as a GitHub Pre-release after successful Run `37116209229`.
- Workspace release check now accepts only blank Cloud deployment templates, rejects private config, and validates Cloud Tag and source Commit.
- Server acceptance template is `server-acceptance.md`; actual BaoTa evidence remains pending.
- RC7 product Run `37114670702` was cancelled before publishing because its Cloud guide omitted the static Web site route. Its Cloud Artifact was downloaded and verified, but is not the deployment candidate.
- Release readback: `isPrerelease=true`, `isDraft=false`; Windows x64, macOS Intel, macOS ARM Desktop assets, Manifest, checksums, and `build-info.json` are present. Published Cloud digest matches the downloaded Linux Artifact.
- Remaining: actual BaoTa deployment and manual server evidence. The product workflow rebuilt unchanged Desktop/Agent components because that is its current release behavior; a Cloud-only release path belongs to later delivery work.
