# WT Media Agent Index

## Current Repository

`wt-media-workspace`

## Repository Role

- Governance control plane for WT Media.
- Owns product, engineering, contract, decision, delivery, and release governance.
- Does not own runtime code or runtime dependencies.

## Related Repositories

Paths are maintained in [`config/repository-map.yaml`](config/repository-map.yaml).

- `cloud`: `../wt-media-cloud`
- `agent`: `../wt-media-agent`
- `desktop`: `../wt-media-desktop`

## Current Context

`.ai/CURRENT_CONTEXT.md` in this repository is the **only** execution snapshot.

- It is generated, not authored: `python3 scripts/prepare_ai_workspace.py --change <CHG>`.
- When a close-out leaves no active CHG, the same script renders that state too:
  `python3 scripts/prepare_ai_workspace.py --no-active` (writes `Active CHG: \`none\``).
  It refuses if `delivery/active/` still holds a CHG.
- Do not edit it by hand.
- Do not create or keep a copy at the outer execution root. `scripts/verify_agent_entry.py` fails if one reappears there.
- Keep it a snapshot, not a knowledge base: no history, no full decision library, no temporary verification notes.

## Context Loading Rules

### Layer 1 — Fixed Entry

Always read:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `AGENT-INDEX.md`
4. `.ai/CURRENT_CONTEXT.md`

### Layer 2 — Current Task

Read only the active CHG identified by `.ai/CURRENT_CONTEXT.md`:

- `delivery/active/<change-id>/change.md`
- Its current plan, spec, and checkpoint, when present

### Layer 3 — Target Repository

Before modifying code, enter the affected repository and read:

1. `AGENT-INDEX.md`
2. `AGENTS.md`
3. `CLAUDE.md`
4. `DIRECTORY_MAP.md`（目录导航，按它定位目标目录）

Then read only the relevant code and tests.

When the target repository has no `AGENT-INDEX.md` yet, do not invent one.
Fall back to this file plus that repository's `AGENTS.md`, and record the gap
in the active CHG. `scripts/verify_agent_entry.py` reports which repositories
are still missing the file.

## 跨工程需求定位

不得只根据需求关键词判断工程，必须根据真正发生修改的能力定位：

| 用户需求 | 主要责任工程 |
| --- | --- |
| 修改用户权限和数据库规则 | Cloud |
| 修改正式业务状态和 API | Cloud |
| 修改内容发现策略与当前 M3 抓取执行 | Cloud |
| 修改 Cloud Web 页面 | Cloud Web |
| 修改 Desktop 使用的 Vue 业务页面 | Cloud Web |
| 修改 Desktop Vue Runtime 适配 | Cloud Web，必要时联动 Desktop |
| 修改 BitBrowser 实际执行逻辑 | Agent |
| 修改 Playwright 平台适配 | Agent |
| 修改 M4-M5 Cloud FFmpeg / 视频合成执行 | Cloud |
| 修改文件下载到运营电脑 | Agent |
| 修改 Agent Sidecar 启停 | Desktop |
| 修改 Tauri 安全桥 | Desktop |
| 修改 Windows/macOS 安装包 | Desktop |
| 修改 Milestone、Plan、Spec 和 CHG | Workspace |
| 修改跨工程 API 或通信契约 | Workspace 协调，责任工程分别实施 |

工程定位后，进入对应仓库的 `AGENT-INDEX.md` 与 `DIRECTORY_MAP.md` 定位目录。
工程可以并行执行，但不得同时修改其他工程拥有的代码和正式治理状态。

## Default Exclusions

Do not load by default:

- `delivery/completed`
- old evidence
- historical decisions
- historical specs
- temporary experiment directories

Load them only when the current task explicitly requires them.

## Execution Boundary

- Workspace is the governance source of truth.
- Runtime code changes belong in the corresponding repository.
- Do not turn workspace into a runtime dependency.
- For parallel multi-repo work, use per-repository status files under the active CHG; do not concurrently edit `.ai/CURRENT_CONTEXT.md`.
