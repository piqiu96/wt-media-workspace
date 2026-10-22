#!/usr/bin/env python3
"""Check the documentation governance index, markers, and relative links.

Rules live in `docs/README.md`. This script only enforces them: required
indexes exist, every index carries one valid governance marker, the docs
directory is registered once, `AGENT-INDEX.md` facts resolve, and relative
links in active indexes point at real files.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_INDEXES = (
    "docs/README.md",
    "docs/product/README.md",
    "docs/engineering/README.md",
    "docs/engineering/specs/README.md",
    "docs/standards/README.md",
    "docs/standards/frontend/README.md",
    "docs/contracts/README.md",
    "docs/decisions/README.md",
    "docs/devops/README.md",
    "docs/reference/README.md",
    "docs/reference/state-models/README.md",
    "docs/superpowers/README.md",
    "delivery/milestones/README.md",
    "delivery/planned/README.md",
    "delivery/reports/README.md",
    "delivery/completed/README.md",
)

FACT_PREFIXES = ("docs/", "delivery/", "config/", "skills/", "scripts/", "bin/")
MARKER_RE = re.compile(
    r"<!--\s*governance:\s*class=(stable|historical|index)\s+"
    r"default_load=(task|never|always)\s*-->"
)
ARCHIVE_MARKER = "- 归档边界：`READ-ONLY`"
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^## \d+\.", re.MULTILINE)


def strip_code(text: str) -> str:
    return INLINE_CODE_RE.sub("", FENCED_CODE_RE.sub("", text))


def links_in(text: str) -> list[str]:
    return LINK_RE.findall(strip_code(text))


def section(text: str, prefix: str) -> str:
    for heading in HEADING_RE.finditer(text):
        if text[heading.start():].startswith(prefix):
            rest = text[heading.end():]
            following = HEADING_RE.search(rest)
            return rest[:following.start()] if following else rest
    return ""


def check(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}

    for relative in REQUIRED_INDEXES:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing documentation index: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        texts[relative] = text
        if not text.strip():
            errors.append(f"empty documentation index: {relative}")

    for relative, text in texts.items():
        if relative == "delivery/completed/README.md":
            if ARCHIVE_MARKER not in text:
                errors.append(
                    "delivery/completed/README.md is missing the archive boundary marker "
                    f"({ARCHIVE_MARKER})"
                )
            continue
        markers = MARKER_RE.findall(strip_code(text))
        if len(markers) != 1:
            errors.append(
                f"expected exactly one governance marker in {relative}, found {len(markers)}"
            )
            continue
        kind, default_load = markers[0]
        if kind == "historical" and default_load != "never":
            errors.append(f"{relative}: historical documents must use default_load=never")
        if kind == "index" and default_load not in {"always", "task"}:
            errors.append(f"{relative}: index documents must use default_load=always or task")

    docs_root = root / "docs"
    docs_readme = texts.get("docs/README.md", "")
    disk_directories = {
        path.name for path in docs_root.iterdir() if path.is_dir()
    } if docs_root.is_dir() else set()
    registered: set[str] = set()
    for target in links_in(docs_readme):
        clean = target.split("#", 1)[0]
        if not clean or clean.startswith(("http://", "https://", "mailto:", "/")):
            continue
        try:
            relative = (docs_root / clean).resolve().relative_to(docs_root.resolve())
        except ValueError:
            continue
        if len(relative.parts) == 2 and relative.parts[1] == "README.md":
            registered.add(relative.parts[0])
    for name in sorted(disk_directories - registered):
        errors.append(f"docs/{name}/ is not registered in docs/README.md")
    for name in sorted(registered - disk_directories):
        errors.append(f"docs/README.md registers a missing directory: docs/{name}/")
    for name in sorted(disk_directories):
        relative = f"docs/{name}/README.md"
        if relative not in texts and not (docs_root / name / "README.md").is_file():
            errors.append(f"missing directory index: {relative}")

    agent_index = root / "AGENT-INDEX.md"
    agent_text = agent_index.read_text(encoding="utf-8") if agent_index.is_file() else ""
    if not agent_text:
        errors.append("missing AGENT-INDEX.md")
    else:
        facts = section(agent_text, "## 3.")
        for path_text in re.findall(r"`([^`]+)`", facts):
            if path_text.startswith(FACT_PREFIXES) and not (root / path_text.rstrip("/")).exists():
                errors.append(f"AGENT-INDEX.md section 3 path does not exist: {path_text}")
        load = section(agent_text, "## 4.")
        if "默认不加载" not in load:
            errors.append("AGENT-INDEX.md section 4 is missing the default-load subsection")
        else:
            excluded = load.split("默认不加载", 1)[1]
            for required in ("docs/superpowers/", "delivery/reports/"):
                if required not in excluded:
                    errors.append(
                        f"AGENT-INDEX.md section 4 must list {required} as not loaded by default"
                    )

    for relative, text in texts.items():
        if relative == "delivery/completed/README.md":
            continue
        path = root / relative
        for target in links_in(text):
            clean = target.split("#", 1)[0]
            if not clean or clean.startswith(("http://", "https://", "mailto:", "#", "/")):
                continue
            candidate = path.parent / clean
            if not candidate.exists():
                errors.append(f"broken relative link: {relative} -> {target}")

    specs_relative = "docs/engineering/specs/README.md"
    specs_dir = root / "docs" / "engineering" / "specs"
    if specs_relative in texts and specs_dir.is_dir():
        listed: set[str] = set()
        for target in links_in(texts[specs_relative]):
            clean = target.split("#", 1)[0]
            if not clean or clean.startswith(("http://", "https://", "mailto:", "#", "/")):
                continue
            candidate = (specs_dir / clean).resolve()
            try:
                candidate.relative_to(specs_dir.resolve())
            except ValueError:
                continue
            if candidate.suffix == ".md":
                listed.add(candidate.name)
        actual = {path.name for path in specs_dir.glob("*.md") if path.name != "README.md"}
        for name in sorted(actual - listed):
            errors.append(f"spec is not listed in docs/engineering/specs/README.md: {name}")

    return errors


def main() -> int:
    errors = check(ROOT)
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"docs governance ok ({len(REQUIRED_INDEXES)} indexes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
