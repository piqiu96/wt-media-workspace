#!/usr/bin/env python3
"""Verify WT Media skill source files.

This script intentionally uses only the Python standard library.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
SKILL_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing frontmatter start")
    try:
        end = lines[1:].index("---") + 1
    except ValueError as exc:
        raise ValueError("missing frontmatter end") from exc

    data: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def iter_skill_files() -> list[Path]:
    return sorted(SKILLS_ROOT.glob("*/*/SKILL.md"))


def main() -> int:
    errors: list[str] = []
    skill_files = iter_skill_files()
    if not skill_files:
        errors.append("no skill source files found")

    names: set[str] = set()
    for path in skill_files:
        rel = path.relative_to(ROOT)
        try:
            meta = parse_frontmatter(path)
        except ValueError as exc:
            errors.append(f"{rel}: {exc}")
            continue

        name = meta.get("name", "")
        description = meta.get("description", "")
        if not name:
            errors.append(f"{rel}: missing name")
        elif not SKILL_NAME_RE.match(name):
            errors.append(f"{rel}: invalid name {name!r}")
        elif name in names:
            errors.append(f"{rel}: duplicate name {name!r}")
        else:
            names.add(name)

        if not description:
            errors.append(f"{rel}: missing description")

        expected_dir = path.parent.name
        if name and name != expected_dir:
            errors.append(f"{rel}: name must match directory {expected_dir!r}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"verified {len(skill_files)} skill source files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
