# Cloud status

- Current: BaoTa site routing corrected in Cloud `v0.1.0-rc.6` (`27050a4`); Cloud CI Run `37115882244` passed.
- Implemented: Linux package now carries SQL migrations, private-config templates, provenance, install/migrate/activate/verify/rollback scripts, database SQL example, systemd units, and BaoTa guide.
- Local verification: 9 package/script tests passed; MySQL 8.4 empty database applied all 50 migrations, rerun applied 0; Server health and admin login passed; Scheduler and Worker remained running alongside Server. Temporary test database was removed.
- Cloud CI Run `37113763595` for RC4 failed only because its duplicate-install test omitted `--service-user` on Linux; test corrected in RC5 without moving RC4. RC5 Cloud CI Run `37114213158` passed.
- RC7 product Run `37114670702` was cancelled after finding that the original BaoTa guide would proxy the Cloud Web homepage to an API-only Go Server. RC6 package adds the static site root, SPA fallback, and `/api/` proxy example.
- RC8 product Run `37116209229` succeeded. Downloaded Cloud Artifact matched its SHA256SUMS and published `build-info.json` digest `c02b55ec6d52432fdd54e2fab0d4a045f066f67bbc7c23c83eb4cf80082c5865`; archive has 50 SQL files, six executable Linux x86_64 ELF binaries, and the BaoTa Nginx site snippet. The extracted package passed `deploy/verify-package.sh`.
- Remaining: user uploads RC8 Cloud Artifact to BaoTa, creates the target database/account, follows the package deployment guide, and fills the actual server evidence in `server-acceptance.md`.
