# Cloud Web download prompt evidence

- Implementation commit: `wt-media-cloud` `codex/cloud-runtime-paths-logs` @ `9478a64`.
- Change: the 本机设置 save-location description now says exactly `请先选择下载目录`. The page does not create or imply a default download directory.
- Test progression:
  - Added a failing assertion in `web/src/localSettingsWiring.test.js` for the exact prompt and absence of the old “由任务自行决定” wording.
  - Replaced only the page description; the focused test then passed.
- Verification:
  - `npm test -- src/localSettingsWiring.test.js` passed: 9 tests.
  - `npm test` passed: 50 test files and 488 tests.
- Boundary: this verifies the Cloud Web copy and source wiring only. Windows download persistence and the real-machine download flow are part of the pending Windows regression.
