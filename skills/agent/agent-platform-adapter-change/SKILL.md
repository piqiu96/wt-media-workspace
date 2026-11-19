---
name: agent-platform-adapter-change
description: Add or modify Agent platform adapters for Douyin, Bilibili, or Baijiahao.
---

# Agent Platform Adapter Change

Use this skill when changing platform-specific execution behavior.

## Check

- Platform API calls stay under `src/wt_media_agent/clients/<platform>/`.
  Independent capabilities belong under `src/wt_media_agent/platforms/` (ADR-0034):
  `publish.py` defines the publication contract; `baidu/publisher.py` contains
  BaiduPublisher and BrowserPublisher. Common browser sessions/CDP/Cookie access
  remain in `services/browser/`. Capabilities may combine API and browser work.
- Publication method is explicitly/default `PublishMethod.BROWSER` for the current
  implementation. Unsupported methods fail before publication actions; do not
  add API stubs, automatic channel fallback or default submit permission.
- High-risk actions report uncertain results when confirmation fails.
- Capabilities organize execution steps, but never duplicate Cloud authorization,
  formal state transitions, task persistence or retry decisions.
- Agent does not decide formal Cloud business status.
- External e2e actions require explicit opt-in.

## Output

Summarize platform, action type, risk handling, and test isolation.
