#!/usr/bin/env python3
"""Verify WT Media agent entry files and the invariants declared around them.

This script intentionally uses only the Python standard library, and it never
writes anything. It reports two severities:

- ``ERROR``: a declared invariant is broken. Exit code is 1.
- ``WARN``: a heuristic finding that needs a human decision. Exit code stays 0.

The heuristics are deliberately narrow. They must not turn into a second,
unreviewed source of truth for repository rules.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXECUTION_ROOT = ROOT.parent

ENTRY_FILES = ("AGENTS.md", "CLAUDE.md", "AGENT-INDEX.md")
CONTEXT_RELATIVE = Path(".ai") / "CURRENT_CONTEXT.md"
CONTEXT_CHAR_BUDGET = 8000
CHARS_PER_TOKEN = 2.5

REPOSITORY_MAP_RELATIVE = Path("config") / "repository-map.yaml"
SKILLS_DISTRIBUTION_RELATIVE = Path("config") / "skills-distribution.yaml"

FORBIDDEN_RE = re.compile(
    r"禁止|不得|不创建|不新增|不允许|不应|不可|不要|不做|must not|do not|never",
    re.IGNORECASE,
)
# Path-like tokens are matched with or without backticks: rule files mark them
# inconsistently, and a heading such as `## internal/runtime` is a real claim
# even though nothing is quoting it.
PATH_TOKEN_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*(?:/[A-Za-z0-9_.-]+)+")
DRIFT_TOKEN_RE = re.compile(r"^[a-z][A-Za-z0-9_-]*(?:/[A-Za-z0-9_-]+)+$")

GOVERNANCE_SCRIPT = "verify_delivery_governance.py"


def load_governance_module():
    """Load the delivery governance script so parsing rules stay in one place."""
    path = ROOT / "scripts" / GOVERNANCE_SCRIPT
    spec = importlib.util.spec_from_file_location("verify_delivery_governance", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {GOVERNANCE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_path_map(text: str, section: str) -> dict[str, str]:
    """Collect `name:` -> `path:` pairs from a two-level YAML section."""
    result: dict[str, str] = {}
    current: str | None = None
    in_section = False
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" "):
            in_section = line.strip() == f"{section}:"
            current = None
            continue
        if not in_section:
            continue
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if indent == 2 and stripped.endswith(":"):
            current = stripped.removesuffix(":").strip().strip('"')
        elif indent == 4 and current and stripped.startswith("path:"):
            result[current] = stripped.split(":", 1)[1].strip().strip('"')
    return result


def check_entry_files() -> list[str]:
    errors: list[str] = []
    for name in ENTRY_FILES:
        if not (ROOT / name).is_file():
            errors.append(f"missing agent entry file: wt-media-workspace/{name}")
    if not (ROOT / CONTEXT_RELATIVE).is_file():
        errors.append(f"missing execution snapshot: {CONTEXT_RELATIVE.as_posix()}")
    return errors


def check_single_snapshot() -> list[str]:
    """The snapshot must exist exactly once, inside the workspace repository."""
    duplicate = EXECUTION_ROOT / CONTEXT_RELATIVE
    if duplicate.exists():
        return [
            "duplicate execution snapshot outside the workspace repository: "
            f"{duplicate} (the only snapshot is wt-media-workspace/{CONTEXT_RELATIVE.as_posix()})"
        ]
    return []


def check_context_budget() -> tuple[list[str], str]:
    context = ROOT / CONTEXT_RELATIVE
    if not context.is_file():
        return [], "execution snapshot not readable"
    text = context.read_text(encoding="utf-8")
    estimated_tokens = round(len(text) / CHARS_PER_TOKEN)
    summary = (
        f"execution snapshot: {len(text)} characters "
        f"(~{estimated_tokens} tokens, budget {CONTEXT_CHAR_BUDGET} characters)"
    )
    if len(text) > CONTEXT_CHAR_BUDGET:
        return [f"execution snapshot exceeds budget: {len(text)} characters"], summary
    return [], summary


def check_delivery_pointers() -> list[str]:
    """The snapshot, the LEDGER, and delivery/active must name the same CHG."""
    governance = load_governance_module()
    context_change = governance.parse_context_change(
        ROOT / CONTEXT_RELATIVE
    )
    ledger_changes = governance.parse_ledger_changes(ROOT / "delivery" / "LEDGER.md")
    active_ids = sorted(
        path.parent.name for path in (ROOT / "delivery" / "active").glob("CHG-*/change.md")
    )

    errors: list[str] = []
    if len(ledger_changes) > 1:
        errors.append(
            "LEDGER table lists more than one active CHG: " + ", ".join(ledger_changes)
        )
    if len(active_ids) > 1:
        errors.append("delivery/active contains more than one CHG: " + ", ".join(active_ids))

    ledger_change = ledger_changes[0] if len(ledger_changes) == 1 else None
    if context_change != ledger_change:
        errors.append(
            "execution snapshot and LEDGER disagree: "
            f"{context_change or 'none'} != {ledger_change or 'none'}"
        )
    if context_change and context_change not in active_ids:
        errors.append(f"execution snapshot references missing CHG: {context_change}")
    if ledger_change and ledger_change not in active_ids:
        errors.append(f"LEDGER references missing active CHG: {ledger_change}")
    return errors


def check_config_agreement() -> tuple[list[str], list[str], dict[str, str]]:
    """repository-map and skills-distribution must agree on repository paths."""
    errors: list[str] = []
    warnings: list[str] = []
    repository_map = ROOT / REPOSITORY_MAP_RELATIVE
    skills_distribution = ROOT / SKILLS_DISTRIBUTION_RELATIVE
    if not repository_map.is_file() or not skills_distribution.is_file():
        errors.append(
            f"missing {REPOSITORY_MAP_RELATIVE.as_posix()} "
            f"or {SKILLS_DISTRIBUTION_RELATIVE.as_posix()}"
        )
        return errors, warnings, {}

    repository_paths = parse_path_map(
        repository_map.read_text(encoding="utf-8"), "repositories"
    )
    target_paths = parse_path_map(
        skills_distribution.read_text(encoding="utf-8"), "targets"
    )
    if not repository_paths:
        errors.append("config/repository-map.yaml declares no repositories")

    for name, path in sorted(repository_paths.items()):
        other = target_paths.get(name)
        if other is None:
            errors.append(
                f"repository '{name}' is missing from config/skills-distribution.yaml targets"
            )
        elif other != path:
            errors.append(
                f"repository '{name}' path disagrees: "
                f"repository-map '{path}' != skills-distribution '{other}'"
            )
        if not (ROOT / path).is_dir():
            warnings.append(f"repository '{name}' path does not resolve here: {path}")
    return errors, warnings, repository_paths


def path_tokens(line: str) -> set[str]:
    return {
        token
        for token in PATH_TOKEN_RE.findall(line)
        if DRIFT_TOKEN_RE.match(token)
    }


def check_entry_drift(repository_paths: dict[str, str]) -> list[str]:
    """Heuristic: a path forbidden by AGENTS.md must not be described as normal
    in CLAUDE.md.

    This is a review prompt, not a verdict. A hit means a human must read both
    files; it does not prove the CLAUDE.md line is wrong.
    """
    warnings: list[str] = []
    for name, path in sorted(repository_paths.items()):
        repo = ROOT / path
        agents = repo / "AGENTS.md"
        claude = repo / "CLAUDE.md"
        if not agents.is_file() or not claude.is_file():
            continue

        forbidden: set[str] = set()
        for line in agents.read_text(encoding="utf-8").splitlines():
            if FORBIDDEN_RE.search(line):
                forbidden |= path_tokens(line)

        described: set[str] = set()
        for line in claude.read_text(encoding="utf-8").splitlines():
            if not FORBIDDEN_RE.search(line):
                described |= path_tokens(line)

        for token in sorted(forbidden & described):
            warnings.append(
                f"{name}: AGENTS.md forbids `{token}` but CLAUDE.md mentions it "
                "outside a forbidding sentence - review both files"
            )
    return warnings


def check_layer3_entries(repository_paths: dict[str, str]) -> list[str]:
    warnings: list[str] = []
    for name, path in sorted(repository_paths.items()):
        repo = ROOT / path
        if not repo.is_dir():
            continue
        if not (repo / "AGENT-INDEX.md").is_file():
            warnings.append(f"{name}: no AGENT-INDEX.md (AGENT-INDEX.md Layer 3 is unresolved)")
    return warnings


def validate_agent_entry() -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    errors.extend(check_entry_files())
    errors.extend(check_single_snapshot())

    budget_errors, budget_note = check_context_budget()
    errors.extend(budget_errors)
    notes.append(budget_note)

    errors.extend(check_delivery_pointers())

    config_errors, config_warnings, repository_paths = check_config_agreement()
    errors.extend(config_errors)
    warnings.extend(config_warnings)

    warnings.extend(check_entry_drift(repository_paths))
    warnings.extend(check_layer3_entries(repository_paths))
    return errors, warnings, notes


def main() -> int:
    errors, warnings, notes = validate_agent_entry()
    for note in notes:
        print(note)
    for warning in warnings:
        print(f"WARN {warning}")
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    if errors:
        return 1
    print(
        f"Agent entry verification ok. {len(warnings)} warning(s) need review."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
