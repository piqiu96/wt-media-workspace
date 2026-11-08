# CHG-20261109-127 — Migration verification

## Baselines and mapping

- Workspace source: `d6a97ef39fddb4b21be29e259081cb3e1b5df8c7`; Cloud source: `660e4e6d0855dd94ece257dbbd0573b17c118b86`. Results below apply to the CHG implementation diff against those bases.
- Before relocation, a temporary SHA-256 manifest captured all 111 tracked Workspace `example/` files. Comparing every mapped destination found 111 present, 94 byte-identical, and 17 with navigation/documentation changes only. All 87 original files outside HTML/Markdown are byte-identical. No Workspace `example/` directory remains.
- 105 prototype/resource files retain their relative layout under Cloud `web/example/`. Six Markdown working documents move to Workspace `docs/design/`: content-operations `design/README.md` → `content-operations.md`; the four business documents retain their names; content-mining `design/analysis.md` → `content-mining.md`.
- Local/known-repository references in the migrated files were resolved against their new destinations: zero missing targets. Historical delivery evidence was not rewritten.

## Acceptance results — PASS

| Check | Action | Actual result |
| --- | --- | --- |
| Original prototype regressions and documentation boundary | Cloud `web`: `npm run test:example` | 22 tests pass, including all 18 original prototype tests; local saved edits, missing root, unsafe paths, symlink escape, unsupported files, writes and API isolation exercised |
| Formal frontend regression | Cloud `web`: `npm test` | 134 files / 1,000 tests pass; isolated legacy Node tests are excluded from formal Vitest discovery |
| Preview build | Cloud `web`: `npm run build:example` | Pass; independent `dist-example`, original legacy resource paths preserved |
| Runtime build isolation | Cloud `web`: `npm run build:cloud` and `npm run build:desktop` | Both pass; neither output includes example files, documentation bridge or Workspace root references |
| Workspace tools | `python3 -m unittest discover -s tests` | 191 tests pass |
| Workspace governance | Docs check, AI workspace, delivery governance and product/master alignment verifiers; `git diff --check` in both repos | Pass; 16 documentation indexes checked |
| Launch ownership | `python3 scripts/wt.py dev example` and its `--plan` | Starts Cloud preview using repository-map and the selected Workspace; no additional repository map |
| Real rendered pages | Isolated headless installed Chrome against dev and built preview | Portal, browser/proxy, accounts, content operations, content mining and publishing review load; zero page-script errors or failed resources |
| Actual shared components | Open/edit the Vue sample | Actual `src/shared/ui` form, overlay and resource components work with mock data |
| Local documentation | Open design index and follow publishing link | Local documents render with relative navigation; reader tests verify changed saved contents are read without commit or push |
| Review continuity | Enter review text, reload, switch scene/back, export JSON | Text survives and export contains the edit; original review scripts/storage keys are byte-identical; default origin remains `http://127.0.0.1:8768` |
| Independent preview entry | Request `/`, `/index.html`, `/login` on dev and built preview | First two redirect to `/example/`; production login is 404; `/api` is blocked |

## Limits and delivery state

- Browser acceptance used an isolated browser context. Existing user-profile review notes were neither read nor copied nor removed; preservation is established by unchanged origin/storage keys and a fresh-context round trip, not by claiming to have inspected private existing notes.
- Standard Vite large-chunk notices remain; builds succeed. No business prototype was redesigned to optimize bundles.
- The usual Git transport timed out; GitHub API access is available. Publication must preserve and verify exact local Git objects before changing feature-branch refs.
- Independent review and PR merge are still required by repository policy. Keep the CHG in VERIFYING until review and merge into both local `main` branches are confirmed; then archive through the existing delivery workflow.
