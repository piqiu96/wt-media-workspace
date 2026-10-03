# Cloud status

- Current: deployment payload fixed at Cloud `v0.1.0-rc.5` (`6f9fab6`); Cloud CI Run `37114213158` passed.
- Implemented: Linux package now carries SQL migrations, private-config templates, provenance, install/migrate/activate/verify/rollback scripts, database SQL example, systemd units, and BaoTa guide.
- Local verification: 8 package/script tests passed; MySQL 8.4 empty database applied all 50 migrations, rerun applied 0; Server health and admin login passed; Scheduler and Worker remained running alongside Server. Temporary test database was removed.
- Cloud CI Run `37113763595` for RC4 failed only because its duplicate-install test omitted `--service-user` on Linux; test corrected in RC5 without moving RC4.
- Remaining: verify product RC7 artifact, then collect actual BaoTa deployment evidence.
