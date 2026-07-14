#!/usr/bin/env python3
"""Prepare or inspect the outer WT Media AI workspace."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
REQUIRED_DIRS = [
    "wt-media-workspace",
    "wt-media-cloud",
    "wt-media-agent",
    "wt-media-desktop",
]
CHANGE_ID_RE = re.compile(r"^CHG-\d{8}-\d{3}$")
EXECUTION_SKILL = "executing-wt-media-change"


@dataclass(frozen=True)
class ChangeInfo:
    change_id: str
    title: str
    status: str
    path: Path
    affected_repositories: tuple[str, ...]


def read_change_info(change_id: str, workspace_repo: Path) -> ChangeInfo:
    if not CHANGE_ID_RE.match(change_id):
        raise ValueError(f"invalid change id: {change_id}")

    active_root = workspace_repo / "delivery" / "active"
    change_path = active_root / change_id / "change.md"
    if not change_path.is_file():
        raise FileNotFoundError(f"active change not found: {change_path}")

    active_changes = sorted(path.parent.name for path in active_root.glob("*/change.md"))
    if active_changes != [change_id]:
        raise ValueError(
            "expected exactly one active change "
            f"{change_id!r}, found: {', '.join(active_changes) or 'none'}"
        )

    text = change_path.read_text(encoding="utf-8")
    title = change_id
    status = "UNKNOWN"
    affected: list[str] = []
    in_affected = False
    for line in text.splitlines():
        if line.startswith("# "):
            title = line.removeprefix("# ").strip()
        elif line.startswith("- Status:"):
            status = line.split(":", 1)[1].strip()
        elif line.strip() == "- Affected repositories:":
            in_affected = True
        elif in_affected and line.startswith("  - "):
            affected.append(line.removeprefix("  - ").strip().strip("`"))
        elif in_affected and line and not line.startswith("  "):
            in_affected = False

    if status == "DONE":
        raise ValueError(f"active change must not be DONE: {change_id}")

    return ChangeInfo(
        change_id=change_id,
        title=title,
        status=status,
        path=change_path,
        affected_repositories=tuple(affected),
    )


def required_directory_errors(workspace_root: Path) -> list[str]:
    return [name for name in REQUIRED_DIRS if not (workspace_root / name).is_dir()]


def generated_skill_text(source: Path, workspace_repo: Path) -> str:
    text = source.read_text(encoding="utf-8")
    return (
        "<!-- GENERATED FILE - DO NOT EDIT DIRECTLY -->\n"
        f"<!-- Source: {source.relative_to(workspace_repo)} -->\n\n{text}"
    )


def write_execution_skill(workspace_root: Path, workspace_repo: Path) -> Path:
    source = workspace_repo / "skills" / "workspace" / EXECUTION_SKILL / "SKILL.md"
    if not source.is_file():
        raise FileNotFoundError(f"execution skill source not found: {source}")

    dest = workspace_root / ".agents" / "skills" / EXECUTION_SKILL / "SKILL.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(generated_skill_text(source, workspace_repo), encoding="utf-8")
    return dest


def build_context(change: ChangeInfo, workspace_root: Path, workspace_repo: Path) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    affected = "\n".join(f"- `{repo}`" for repo in change.affected_repositories) or "- None"
    return f"""# WT Media Current AI Context

- Generated: {generated_at}
- Active CHG: `{change.change_id}`
- Status: `{change.status}`
- Title: {change.title}
- Change file: `{change.path.relative_to(workspace_root)}`
- Workspace governance repo: `{workspace_repo.relative_to(workspace_root)}`

## Required Skill

Use `executing-wt-media-change` for CHG implementation, resume, review, and completion.

Generated copy:

```text
.agents/skills/executing-wt-media-change/SKILL.md
```

Unique source:

```text
wt-media-workspace/skills/workspace/executing-wt-media-change/SKILL.md
```

## Required Reading Order

1. `AGENTS.md`
2. `.ai/CURRENT_CONTEXT.md`
3. `{change.path.relative_to(workspace_root)}`
4. Baselines referenced by the active CHG
5. Affected repository `AGENTS.md` files
6. Current code, tests, and Git status

## Affected Repositories

{affected}

## Stable Baselines

- Product: `wt-media-workspace/docs/product`
- Engineering: `wt-media-workspace/docs/engineering`
- Contracts: `wt-media-workspace/docs/contracts`
- Decisions: `wt-media-workspace/docs/decisions`
- Master route: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`

## Execution Boundaries

- Execute only the active CHG.
- Do not start the next CHG.
- Do not modify Cloud, Agent, or Desktop business code unless listed in the active CHG.
- Stop and record `Q-xx` if scope, contracts, facts, or responsibilities need a new decision.
"""


def write_current_context(change: ChangeInfo, workspace_root: Path, workspace_repo: Path) -> Path:
    context_path = workspace_root / ".ai" / "CURRENT_CONTEXT.md"
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_text(build_context(change, workspace_root, workspace_repo), encoding="utf-8")
    return context_path


def prepare_workspace(
    *,
    workspace_repo: Path = ROOT,
    change_id: str | None = None,
    write_context: bool = True,
) -> dict[str, object]:
    workspace_repo = workspace_repo.resolve()
    workspace_root = workspace_repo.parent

    missing = required_directory_errors(workspace_root)
    if missing:
        raise FileNotFoundError(f"missing required directories: {', '.join(missing)}")

    summary: dict[str, object] = {
        "workspace_root": str(workspace_root),
        "mode": "workspace-governance-active",
        "runtime_repositories": REQUIRED_DIRS[1:],
        "docs_location": str(workspace_repo / "docs"),
        "delivery_active": str(workspace_repo / "delivery" / "active"),
        "workspace_repository": str(workspace_repo),
    }

    if change_id:
        change = read_change_info(change_id, workspace_repo)
        summary["active_change"] = change.change_id
        summary["active_change_status"] = change.status
        summary["active_change_file"] = str(change.path)
        summary["affected_repositories"] = list(change.affected_repositories)
        if write_context:
            skill_path = write_execution_skill(workspace_root, workspace_repo)
            context_path = write_current_context(change, workspace_root, workspace_repo)
            summary["current_context"] = str(context_path)
            summary["generated_execution_skill"] = str(skill_path)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--change", help="active CHG id, for example CHG-20260714-002")
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="validate and print context summary without writing generated files",
    )
    args = parser.parse_args()

    try:
        summary = prepare_workspace(change_id=args.change, write_context=not args.no_write)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
