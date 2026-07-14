# Agent BitBrowser verification

- Red: the focused adapter test initially failed because `wt_media_agent.runtimes.bitbrowser` did not exist; the Local API test then failed because the server had no injectable BitBrowser client or scan response.
- Green: `BitBrowserClient` calls official `POST /browser/list` pages from page 0 in batches of 100, retains only allow-listed Profile facts, and rejects empty, missing, or mixed `userId` identity.
- Local API: `POST /api/v1/bit-browser/profile-scans` returns the normalized owner and secret-free Profile snapshot. Upstream URLs, raw bodies, Cookie, password, and proxy credentials are not returned.
- Provider repair: Local API, event schemas, status enums, and BitBrowser error definitions now exist at revision `2026.07.14.6`; Workspace no longer claims definitions that are absent from the Agent provider.
- Verification: 28 Python unittests, four YAML parses, and the real local health command passed.
- Commits: Agent `14e51be` and `f0257b5`.

No live BitBrowser installation/account was available in C3. Transport behavior is verified with deterministic fixtures; the real BitBrowser integration belongs to the C6 comprehensive acceptance run.
