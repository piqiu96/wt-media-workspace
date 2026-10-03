# Desktop status

- RC3 component Tag: `v0.1.0-rc.1` → `50f707a807a3a1d935c051425201211015ae9f2b`; RC3 macOS ARM/x64 packaging passed, Windows NSIS build failed on Unix-only Rustix APIs.
- Fix commit: `63e8380d1ede36f134d85479f61fe19413a00ff4` (`v0.1.0-rc.2`) splits Unix signal and cross-device handling from Windows, and uses Win32 process liveness APIs.
- Verification: local `cargo check --workspace` passed; `scripts/test.sh` passed with 507 Rust tests, 6 existing ignores, control 12 checks and release-version 20 checks.
- Remaining: validate Windows compile/package in RC4, then full product package and release checks.
