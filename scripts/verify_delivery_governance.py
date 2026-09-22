#!/usr/bin/env python3
"""Verify that WT Media delivery pointers and milestone references agree."""

from __future__ import annotations

import re
import sys
from pathlib import Path


CHANGE_ID_RE = re.compile(r"CHG-\d{8}-\d{3}")
CONTEXT_RE = re.compile(r"Active CHG:\s*`([^`]+)`", re.IGNORECASE)
LEVEL_RE = re.compile(r"^- Level:\s*([A-Z])\s*$", re.MULTILINE)
MILESTONE_RE = re.compile(r"^- Milestone:\s*`([^`]+)`\s*$", re.MULTILINE)


def current_context_path(workspace: Path) -> Path:
    """Return the single execution snapshot owned by the workspace repository.

    The snapshot lives inside the workspace repository so that a worktree
    checkout carries it, and so that no second copy can drift in the outer
    execution root.
    """
    return workspace / ".ai" / "CURRENT_CONTEXT.md"


def parse_context_change(context: Path) -> str | None:
    if not context.is_file():
        return None
    match = CONTEXT_RE.search(context.read_text(encoding="utf-8"))
    if match is None:
        return None
    value = match.group(1).strip()
    return None if value.lower() == "none" else value


LEDGER_ROW_RE = re.compile(r"^\|\s*(CHG-\d{8}-\d{3})\s*\|")


def parse_ledger_changes(ledger: Path) -> list[str]:
    """Return the CHG ids listed in the LEDGER table.

    Only table rows count. Prose in the LEDGER body may mention a CHG id
    (for example to point at where earlier work was folded in), and that
    mention must not be read as a second active change.
    """
    if not ledger.is_file():
        return []
    changes: list[str] = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        match = LEDGER_ROW_RE.match(line)
        if match is not None:
            changes.append(match.group(1))
    return changes


def heading_anchors(markdown: str) -> set[str]:
    anchors: set[str] = set()
    for line in markdown.splitlines():
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip().lower()
        heading = re.sub(r"[^a-z0-9\u4e00-\u9fff -]", "", heading)
        anchors.add(re.sub(r"[\s-]+", "-", heading).strip("-"))
    return anchors


def validate_milestone_reference(
    workspace: Path, change_id: str, change_text: str
) -> list[str]:
    match = MILESTONE_RE.search(change_text)
    if match is None:
        return [f"active CHG has no milestone reference: {change_id}"]

    reference = match.group(1)
    path_text, separator, anchor = reference.partition("#")
    milestone = workspace / path_text
    if not milestone.is_file():
        return [f"active CHG references missing milestone: {reference}"]
    if separator and anchor.lower() not in heading_anchors(
        milestone.read_text(encoding="utf-8")
    ):
        return [f"active CHG references missing milestone anchor: {reference}"]
    return []


def validate_delivery_governance(workspace: Path) -> list[str]:
    workspace = workspace.resolve()
    context = current_context_path(workspace)
    ledger = workspace / "delivery" / "LEDGER.md"
    active_root = workspace / "delivery" / "active"

    errors: list[str] = []
    context_change = parse_context_change(context)
    ledger_changes = parse_ledger_changes(ledger)
    active_changes = sorted(active_root.glob("CHG-*/change.md"))
    active_ids = [path.parent.name for path in active_changes]

    if context_change and context_change not in active_ids:
        errors.append(f"current context references missing CHG: {context_change}")
    if len(ledger_changes) > 1:
        errors.append("ledger lists more than one active CHG: " + ", ".join(ledger_changes))
    if len(active_ids) > 1:
        errors.append("delivery/active contains more than one CHG: " + ", ".join(active_ids))

    ledger_change = ledger_changes[0] if len(ledger_changes) == 1 else None
    if context_change != ledger_change:
        errors.append(
            "current context and ledger disagree: "
            f"{context_change or 'none'} != {ledger_change or 'none'}"
        )
    if ledger_change and ledger_change not in active_ids:
        errors.append(f"ledger references missing active CHG: {ledger_change}")

    for change_path in active_changes:
        change_id = change_path.parent.name
        change_text = change_path.read_text(encoding="utf-8")
        level_match = LEVEL_RE.search(change_text)
        if level_match and level_match.group(1) in {"M", "L"}:
            errors.extend(
                validate_milestone_reference(workspace, change_id, change_text)
            )

    return errors


def main() -> int:
    workspace = Path(__file__).resolve().parents[1]
    errors = validate_delivery_governance(workspace)
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1

    ledger_changes = parse_ledger_changes(workspace / "delivery" / "LEDGER.md")
    active = ledger_changes[0] if ledger_changes else "none"
    print(f"Delivery governance verification ok. Active CHG: {active}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
