# Agent runtime verification

- Red: focused tests first failed because `wt_media_agent.runtimes.environment`, `register_local`, and `report_runtime` did not exist.
- Green collector: normalized OS/architecture, Agent/Python/FFmpeg versions, workdir/disk states, BitBrowser reachability, verified owner and sorted Profile IDs are emitted through a fixed allow-list.
- Secret boundary: reports contain no host name, IP, local path, raw command output, Cookie, proxy credential, or upstream error body.
- Green client: local registration consumes a one-use token without a session Cookie; runtime reports use only the bearer node credential.
- Full verification: 33 Python unittests and five Agent provider YAML parses pass.
- Commits: Agent `8652a90` and `d5a9e4d`.
