# M2-A Start Gate Evidence

Date: 2026-07-21

## Commands

| Command | Expected | Actual | Status |
|---|---|---|---|
| `/Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go test ./...` in `wt-media-cloud` | Cloud suite passes | All Cloud packages passed; proxy has no test files | PASS |
| `PYTHONPATH=src python3 -m unittest discover -s tests` in `wt-media-agent` | Agent suite passes | 44 tests passed | PASS |
| `npm test -- --run` in `wt-media-cloud/web` | Web suite passes | 8 tests failed with Node `ERR_INVALID_URL` for relative `/api/v1/...` paths | FAIL / Task 2 |
| `python3 scripts/verify_m2_acceptance.py` | Deterministic M2 gate | Script crashed reading removed `wt-media-desktop/src/services/local-agent.js` | FAIL / Task 3 |
| `python3 scripts/verify_product_master_alignment.py` | Current plan alignment | Script reported obsolete M1/M2 status and candidate assertions | FAIL / Task 3 |

## Dirty-tree boundary

- `wt-media-cloud` already contains unrelated proxy source edits and generated `web/dist-*` changes. They are excluded from this CHG.
- `wt-media-workspace` already contains the assessment report, a separate planning document, and `.DS_Store` modification. They are excluded from this CHG.
- `wt-media-agent` and `wt-media-desktop` have no pre-existing dirty files at the start gate.

## Decision

Start gate accepted. The current failures are within the declared M2-A scope and have deterministic reproduction. No blocking product, contract, or ownership question is open.
