#!/usr/bin/env python3
"""Sync WT Media skill source files into generated tool directories.

The distribution targets are declared in `config/skills-distribution.yaml` and
read from there; this script holds no copy of that list. The implementation is
deliberately conservative: unknown files in generated directories stop sync
instead of being overwritten.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "skills-distribution.yaml"
SKILLS_ROOT = ROOT / "skills"


def load_sibling(name: str):
    """Load a sibling script by file path, since scripts are not a package."""
    path = Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


agent_config = load_sibling("agent_config")


def execution_root(workspace: Path) -> Path:
    """Resolve the shared cross-repo root from a normal checkout or worktree.

    Detection is repository-based, not snapshot-based: the outer root is the
    directory that holds the governance repository alongside the runtime
    repositories. It deliberately does not probe for `.ai/`, which lives
    inside the workspace repository and is not a property of the outer root.
    """
    for candidate in (workspace.parent, *workspace.parents):
        if (candidate / "wt-media-workspace").is_dir() and (
            candidate / "wt-media-cloud"
        ).is_dir():
            return candidate
    return workspace.parent


WORKSPACE_ROOT = execution_root(ROOT)


@dataclass(frozen=True)
class Target:
    name: str
    path: Path
    groups: tuple[str, ...]
    kind: str = "repository"


def resolve_target_path(declared: str, workspace_root: Path) -> Path:
    """Resolve a declared target path to an absolute directory.

    A declared path is written relative to the workspace repository's parent, so
    `../wt-media-cloud` names the sibling repository and `..` names the
    execution root itself. The path is re-anchored to the execution root rather
    than joined literally, because a linked worktree sits in a different
    directory than the repository it checks out: joining `../x` to the worktree
    directory would leave the cross-repo workspace entirely.
    """
    declared_path = Path(declared)
    if declared_path.is_absolute():
        raise agent_config.ConfigError(
            f"target path must be relative to the execution root: {declared}"
        )
    parts = [part for part in declared_path.parts if part != ".."]
    if not parts:
        return workspace_root
    return workspace_root.joinpath(*parts)


def load_targets(
    config_path: Path, workspace_root: Path
) -> tuple[dict[str, Target], tuple[str, ...]]:
    """Build the distribution targets and tools from the configuration file."""
    targets: dict[str, Target] = {}
    for name, settings in agent_config.read_section(config_path, "targets").items():
        declared = settings.get("path")
        groups = settings.get("groups")
        kind = settings.get("kind", "repository")
        if not isinstance(declared, str):
            raise agent_config.ConfigError(f"{config_path}: target '{name}' has no path")
        if not isinstance(groups, list) or not groups:
            raise agent_config.ConfigError(
                f"{config_path}: target '{name}' declares no groups"
            )
        if kind not in {"repository", "distribution"}:
            raise agent_config.ConfigError(
                f"{config_path}: target '{name}' has unknown kind: {kind}"
            )
        targets[name] = Target(
            name=name,
            path=resolve_target_path(declared, workspace_root),
            groups=tuple(str(group) for group in groups),
            kind=str(kind),
        )
    if not targets:
        raise agent_config.ConfigError(f"{config_path}: no targets declared")
    return targets, tuple(agent_config.read_sequence(config_path, "tools"))


TARGETS, TOOLS = load_targets(CONFIG_PATH, WORKSPACE_ROOT)


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


def unresolved_targets(targets: list[Target]) -> list[str]:
    """Report targets whose directory does not exist.

    Writing would otherwise create a tool directory inside a repository that is
    not checked out here, which is how a stale list of targets silently produces
    skill copies nothing can load.
    """
    return [
        f"{target.name}: target directory does not exist: {target.path}"
        for target in targets
        if not target.path.is_dir()
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["check", "diff", "sync"])
    parser.add_argument("--repo", choices=sorted(TARGETS), default=None)
    parser.add_argument("--tool", choices=TOOLS, default=None)
    args = parser.parse_args()

    tools = (args.tool,) if args.tool else TOOLS
    targets = selected_targets(args.repo)

    missing = unresolved_targets(targets)
    if missing:
        for line in missing:
            print(line, file=sys.stderr)
        return 1

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
