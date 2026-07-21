#!/usr/bin/env python3
"""Sync WT Media skill source files into generated tool directories.

The implementation is deliberately conservative: unknown files in generated
directories stop sync instead of being overwritten.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def execution_root(workspace: Path) -> Path:
    """Resolve the shared cross-repo root from a normal checkout or worktree."""
    for candidate in (workspace.parent, *workspace.parents):
        if (candidate / ".ai").is_dir() and (
            candidate / "wt-media-workspace"
        ).is_dir():
            return candidate
    return workspace.parent


WORKSPACE_ROOT = execution_root(ROOT)
SKILLS_ROOT = ROOT / "skills"
TOOLS = ("codex", "claude")


@dataclass(frozen=True)
class Target:
    name: str
    path: Path
    groups: tuple[str, ...]


TARGETS = {
    "root": Target("root", WORKSPACE_ROOT, ("common", "workspace", "cloud", "agent", "desktop")),
    "cloud": Target("cloud", WORKSPACE_ROOT / "wt-media-cloud", ("common", "cloud")),
    "agent": Target("agent", WORKSPACE_ROOT / "wt-media-agent", ("common", "agent")),
    "desktop": Target("desktop", WORKSPACE_ROOT / "wt-media-desktop", ("common", "desktop")),
}


def skill_sources(groups: tuple[str, ...]) -> dict[str, Path]:
    sources: dict[str, Path] = {}
    for group in groups:
        group_dir = SKILLS_ROOT / group
        if not group_dir.exists():
            continue
        for skill_dir in sorted(group_dir.iterdir()):
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                sources[skill_dir.name] = skill_file
    return sources


def target_tool_dir(target: Target, tool: str) -> Path:
    return target.path / f".{tool}" / "skills"


def generated_text(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0] == "---":
        try:
            end = lines[1:].index("---") + 1
        except ValueError:
            end = -1
        if end > 0:
            header = [
                "<!-- GENERATED FILE - DO NOT EDIT DIRECTLY -->",
                f"<!-- Source: {source.relative_to(ROOT)} -->",
                "",
            ]
            lines = lines[: end + 1] + header + lines[end + 1 :]
            return "\n".join(lines) + "\n"
    return (
        "<!-- GENERATED FILE - DO NOT EDIT DIRECTLY -->\n"
        f"<!-- Source: {source.relative_to(ROOT)} -->\n\n{text}"
    )


def unknown_entries(target_dir: Path, expected: set[str]) -> list[Path]:
    if not target_dir.exists():
        return []
    unknown: list[Path] = []
    for entry in sorted(target_dir.iterdir()):
        if entry.name == ".gitkeep":
            continue
        if entry.name not in expected:
            unknown.append(entry)
    return unknown


def check_target(target: Target, tool: str) -> list[str]:
    errors: list[str] = []
    sources = skill_sources(target.groups)
    target_dir = target_tool_dir(target, tool)
    for entry in unknown_entries(target_dir, set(sources)):
        errors.append(f"{target.name}/{tool}: unknown generated entry {entry}")
    for name, source in sources.items():
        dest = target_dir / name / "SKILL.md"
        if not dest.exists():
            errors.append(f"{target.name}/{tool}: missing {dest}")
            continue
        expected = generated_text(source)
        actual = dest.read_text(encoding="utf-8")
        if actual != expected:
            errors.append(f"{target.name}/{tool}: out of date {dest}")
    return errors


def sync_target(target: Target, tool: str) -> None:
    sources = skill_sources(target.groups)
    target_dir = target_tool_dir(target, tool)
    unknown = unknown_entries(target_dir, set(sources))
    if unknown:
        details = ", ".join(str(path) for path in unknown)
        raise RuntimeError(f"{target.name}/{tool}: unknown generated entries: {details}")

    target_dir.mkdir(parents=True, exist_ok=True)
    for name, source in sources.items():
        skill_dir = target_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(generated_text(source), encoding="utf-8")


def selected_targets(name: str | None) -> list[Target]:
    if name:
        if name not in TARGETS:
            raise SystemExit(f"unknown target: {name}")
        return [TARGETS[name]]
    return list(TARGETS.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["check", "diff", "sync"])
    parser.add_argument("--repo", choices=sorted(TARGETS), default=None)
    parser.add_argument("--tool", choices=TOOLS, default=None)
    args = parser.parse_args()

    tools = (args.tool,) if args.tool else TOOLS
    targets = selected_targets(args.repo)

    if args.command in {"check", "diff"}:
        errors: list[str] = []
        for target in targets:
            for tool in tools:
                errors.extend(check_target(target, tool))
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print("skill outputs are up to date")
        return 0

    for target in targets:
        for tool in tools:
            sync_target(target, tool)
            print(f"synced {target.name}/{tool}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
