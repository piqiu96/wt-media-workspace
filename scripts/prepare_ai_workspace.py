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
MILESTONE_RE = re.compile(r"^-\s*Milestone:\s*`([^`]+)`\s*$")
AFFECTED_KEY_RE = re.compile(r"^-\s*(?:Affected repositories|当前仓库)\s*[:：]\s*(.*)$")
REPO_TOKEN_RE = re.compile(r"wt-media-[a-z]+")

OWNERSHIP_BOUNDARIES = (
    "Cloud owns business state, orchestration, and the Cloud runtime.",
    "Agent owns local execution and external side effects.",
    "Desktop owns user interaction and the local bridge.",
    "Workspace owns governance and never becomes a runtime dependency.",
)


@dataclass(frozen=True)
class ChangeInfo:
    change_id: str
    title: str
    status: str
    path: Path
    milestone: str | None
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
            f"{change_id!r}, found: {', '.join(active_changes) or 'none'}; "
            "move every non-active CHG out of delivery/active first"
        )

    text = change_path.read_text(encoding="utf-8")
    title = change_id
    status = "UNKNOWN"
    milestone: str | None = None
    affected: list[str] = []
    in_affected = False
    for line in text.splitlines():
        if line.startswith("# "):
            title = line.removeprefix("# ").strip()
        elif line.startswith("- Status:"):
            status = line.split(":", 1)[1].strip()
        elif milestone is None and (match := MILESTONE_RE.match(line)):
            milestone = match.group(1).strip()
        elif in_affected and line.startswith("  - "):
            affected.append(line.removeprefix("  - ").strip().strip("`"))
        elif match := AFFECTED_KEY_RE.match(line):
            # Two record shapes are in use: a structured bullet list under
            # `- Affected repositories:`, and a prose `- 当前仓库：` line that
            # names the repositories inline before explaining the split.
            in_affected = not match.group(1).strip()
            affected.extend(REPO_TOKEN_RE.findall(match.group(1)))
        elif in_affected and line and not line.startswith("  "):
            in_affected = False

    affected = list(dict.fromkeys(affected))

    if status == "DONE":
        raise ValueError(f"active change must not be DONE: {change_id}")

    # Record headings usually repeat the id (`# CHG-...052：Title`). Drop that
    # prefix so the snapshot can render the id once, next to the title.
    title = re.sub(rf"^{re.escape(change_id)}\s*[:：]\s*", "", title).strip() or change_id

    return ChangeInfo(
        change_id=change_id,
        title=title,
        status=status,
        path=change_path,
        milestone=milestone,
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


def build_context(change: ChangeInfo | None, workspace_repo: Path) -> str:
    """Render the single execution snapshot.

    Every path is workspace-relative: the snapshot lives inside the workspace
    repository and must stay readable when that repository is checked out on
    its own, for example in a worktree.

    ``change`` may be None: closing the last active CHG legitimately leaves no
    active change, and `verify_delivery_governance.py` already accepts the
    empty state by rendering it as ``Active CHG: `none` ``. The snapshot stays
    generated in that state too, so it must still be renderable here.
    """
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    reading_order = [
        "`AGENTS.md`",
        "`CLAUDE.md`",
        "`AGENT-INDEX.md`",
        "`.ai/CURRENT_CONTEXT.md`",
        "`delivery/LEDGER.md`",
    ]
    if change is None:
        header_lines = "- Active CHG: `none`\n- Status: `NONE`\n"
        affected = "- None"
        change_dir_token = "<CHG>"
    else:
        change_path = change.path.relative_to(workspace_repo)
        header_lines = (
            f"- Active CHG: `{change.change_id}` — {change.title}\n"
            f"- Status: `{change.status}`\n"
        )
        if change.milestone:
            header_lines += f"- Current milestone: `{change.milestone}`\n"
            reading_order.append(f"`{change.milestone}`")
        header_lines += f"- Change file: `{change_path}`\n"
        affected = "\n".join(f"- `{repo}`" for repo in change.affected_repositories) or "- None"
        reading_order.append(f"`{change_path}`")
        reading_order.append(
            "Affected repository `AGENT-INDEX.md`, `AGENTS.md`, and `CLAUDE.md`"
        )
        change_dir_token = change.change_id
    reading_order_text = "\n".join(
        f"{index}. {entry}" for index, entry in enumerate(reading_order, start=1)
    )
    return f"""# WT Media Current AI Context

- Generated: {generated_at}
{header_lines}
This is the only execution snapshot. It is generated by
`scripts/prepare_ai_workspace.py` and must not be edited by hand. No copy of
this file exists in the outer execution root.

## Required Skill

- Plan the next CHG with `planning-wt-media-delivery`.
- Implement, resume, review, and complete a CHG with `executing-wt-media-change`.

## Required Reading Order

{reading_order_text}

## Affected Repositories

{affected}

## Stable Baselines

- Product: `docs/product`
- Engineering: `docs/engineering`
- Contracts: `docs/contracts`
- Decisions: `docs/decisions`
- Master route: `delivery/MASTER_IMPLEMENTATION_PLAN.md`

## Stable Ownership Boundaries

{chr(10).join(f"- {line}" for line in OWNERSHIP_BOUNDARIES)}

Milestone-specific decisions are not copied here. The active CHG names the
decision records it depends on; read those files instead of this summary.

## Execution Boundaries

- Execute only the active CHG.
- Do not start the next CHG.
- Do not modify Cloud, Agent, or Desktop business code unless listed in the active CHG.
- Stop and record `Q-xx` if scope, contracts, facts, or responsibilities need a new decision.
- Multi-repository CHGs record per-repository status under
  `delivery/active/{change_dir_token}/status/<repo>.md`. Never edit this
  snapshot concurrently from more than one agent.
"""


def write_current_context(change: ChangeInfo | None, workspace_repo: Path) -> Path:
    context_path = workspace_repo / ".ai" / "CURRENT_CONTEXT.md"
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_text(build_context(change, workspace_repo), encoding="utf-8")
    return context_path


def prepare_workspace(
    *,
    workspace_repo: Path = ROOT,
    change_id: str | None = None,
    write_context: bool = True,
    no_active: bool = False,
) -> dict[str, object]:
    workspace_repo = workspace_repo.resolve()
    workspace_root = workspace_repo.parent

    missing = required_directory_errors(workspace_root)
    if missing:
        raise FileNotFoundError(f"missing required directories: {', '.join(missing)}")

    if change_id and no_active:
        raise ValueError("pass either --change or --no-active, not both")

    # An explicit empty state must not silently mean "forgot the id": the
    # caller has to say the close-out left nothing active, and then the
    # directory has to agree with that claim.
    if no_active:
        remaining = sorted(
            path.parent.name
            for path in (workspace_repo / "delivery" / "active").glob("*/change.md")
        )
        if remaining:
            raise ValueError(
                "delivery/active is not empty: " + ", ".join(remaining)
            )

    summary: dict[str, object] = {
        "workspace_root": str(workspace_root),
        "mode": "workspace-governance-active",
        "runtime_repositories": REQUIRED_DIRS[1:],
        "docs_location": str(workspace_repo / "docs"),
        "delivery_active": str(workspace_repo / "delivery" / "active"),
        "workspace_repository": str(workspace_repo),
    }

    if no_active or change_id:
        change = read_change_info(change_id, workspace_repo) if change_id else None
        summary["active_change"] = change.change_id if change else None
        if change:
            summary["active_change_status"] = change.status
            summary["active_change_file"] = str(change.path)
            summary["active_milestone"] = change.milestone
            summary["affected_repositories"] = list(change.affected_repositories)
        if write_context:
            skill_path = write_execution_skill(workspace_root, workspace_repo)
            context_path = write_current_context(change, workspace_repo)
            summary["current_context"] = str(context_path)
            summary["generated_execution_skill"] = str(skill_path)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--change", help="active CHG id, for example CHG-20260714-002")
    parser.add_argument(
        "--no-active",
        action="store_true",
        help="render the snapshot for a close-out that leaves no active CHG",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="validate and print context summary without writing generated files",
    )
    args = parser.parse_args()

    try:
        summary = prepare_workspace(
            change_id=args.change,
            write_context=not args.no_write,
            no_active=args.no_active,
        )
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
