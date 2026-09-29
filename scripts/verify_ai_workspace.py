#!/usr/bin/env python3
"""Verify AI entry documents and workspace execution invariants.

This read-only check verifies file presence, navigable references, the single
execution snapshot, and configuration agreement. It does not enforce prose,
section counts, or size limits on the repository entries.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXECUTION_ROOT = ROOT.parent
ENTRY_FILES = ("AGENTS.md", "CLAUDE.md", "AGENT-INDEX.md")
RUNNING_REPO_ENTRY_FILES = ("AGENT-INDEX.md", "AGENTS.md", "CLAUDE.md", "DIRECTORY_MAP.md")
ENTRY_PAGES = ("AGENTS.md", "CLAUDE.md")
WORKSPACE_REPOSITORY = "workspace"
CONTEXT_RELATIVE = Path(".ai") / "CURRENT_CONTEXT.md"
CONTEXT_CHAR_BUDGET = 8000
CHARS_PER_TOKEN = 2.5
REPOSITORY_MAP_RELATIVE = Path("config") / "repository-map.yaml"
SKILLS_DISTRIBUTION_RELATIVE = Path("config") / "skills-distribution.yaml"
HARDCODED_SIBLING_RE = re.compile(r"\.\./wt-media-(?:cloud|agent|desktop|workspace)\b")
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


def load_workspace_config():
    """Load the shared configuration reader."""
    path = ROOT / "scripts" / "workspace_config.py"
    spec = importlib.util.spec_from_file_location("workspace_config", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load workspace_config.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
    """The two configuration files and `skills/` must agree.

    Agreement is required in both directions. A repository missing from the
    distribution targets would silently never receive its skills, and a target
    missing from the repository map cannot be recognised as a repository at all
    unless it declares itself a distribution location.
    """
    errors: list[str] = []
    warnings: list[str] = []
    config = load_workspace_config()
    repository_map = ROOT / REPOSITORY_MAP_RELATIVE
    skills_distribution = ROOT / SKILLS_DISTRIBUTION_RELATIVE
    try:
        repositories = config.read_section(repository_map, "repositories")
        targets = config.read_section(skills_distribution, "targets")
    except config.ConfigError as error:
        return [str(error)], warnings, {}

    repository_paths: dict[str, str] = {}
    for name, settings in sorted(repositories.items()):
        path = settings.get("path")
        if not isinstance(path, str):
            errors.append(
                f"repository '{name}' declares no path in "
                f"{REPOSITORY_MAP_RELATIVE.as_posix()}"
            )
            continue
        repository_paths[name] = path
    if not repository_paths:
        errors.append("config/repository-map.yaml declares no repositories")

    for name, path in sorted(repository_paths.items()):
        target = targets.get(name)
        if target is None:
            errors.append(
                f"repository '{name}' is missing from config/skills-distribution.yaml targets"
            )
        elif target.get("path") != path:
            errors.append(
                f"repository '{name}' path disagrees: "
                f"repository-map '{path}' != skills-distribution '{target.get('path')}'"
            )
        if not (ROOT / path).is_dir():
            warnings.append(f"repository '{name}' path does not resolve here: {path}")

    for name, settings in sorted(targets.items()):
        kind = settings.get("kind", "repository")
        if kind not in {"repository", "distribution"}:
            errors.append(
                f"target '{name}' has unknown kind '{kind}' in "
                f"{SKILLS_DISTRIBUTION_RELATIVE.as_posix()}"
            )
        elif kind == "repository" and name not in repository_paths:
            errors.append(
                f"target '{name}' is kind: repository but is missing from "
                f"{REPOSITORY_MAP_RELATIVE.as_posix()}"
            )

    errors.extend(check_group_coverage(targets))
    return errors, warnings, repository_paths


def check_group_coverage(targets: dict[str, dict[str, object]]) -> list[str]:
    """Every `skills/<group>` must be claimed, and every claim must exist.

    A group that no target claims produces skills that are never distributed,
    which is invisible: sync reports success because it only walks what the
    configuration lists.
    """
    errors: list[str] = []
    skills_root = ROOT / "skills"
    available = (
        {entry.name for entry in skills_root.iterdir() if entry.is_dir()}
        if skills_root.is_dir()
        else set()
    )
    claimed: set[str] = set()
    for name, settings in sorted(targets.items()):
        groups = settings.get("groups")
        if groups is None:
            errors.append(f"target '{name}' declares no groups")
            continue
        if not isinstance(groups, list):
            errors.append(f"target '{name}' has a malformed groups list")
            continue
        claimed |= {str(group) for group in groups}
    for group in sorted(available - claimed):
        errors.append(f"skill group 'skills/{group}' is not claimed by any distribution target")
    for group in sorted(claimed - available):
        errors.append(f"distribution targets claim a missing skill group: skills/{group}")
    return errors


def running_repositories(repository_paths: dict[str, str]) -> dict[str, str]:
    """Repositories that must carry the four entry files, i.e. all but the workspace."""
    return {
        name: path
        for name, path in repository_paths.items()
        if name != WORKSPACE_REPOSITORY
    }


def check_repo_entry_files(
    repository_paths: dict[str, str],
) -> tuple[list[str], list[str]]:
    """Every running repository carries all four entry files, non-empty.

    A repository whose directory is not next to this one is skipped with a
    warning rather than an error: the check must survive a checkout that does
    not include the sibling repositories. That skip is a WARN, so a genuinely
    absent directory never reads as a pass.
    """
    errors: list[str] = []
    warnings: list[str] = []
    for name, path in sorted(running_repositories(repository_paths).items()):
        repo = ROOT / path
        if not repo.is_dir():
            warnings.append(
                f"{name}: repository not present at {path}, entry files not checked"
            )
            continue
        for filename in RUNNING_REPO_ENTRY_FILES:
            target = repo / filename
            if not target.is_file():
                errors.append(f"{name}: missing agent entry file: {filename}")
            elif target.stat().st_size == 0:
                errors.append(f"{name}: empty agent entry file: {filename}")
    return errors, warnings


def check_entry_navigation(repository_paths: dict[str, str]) -> list[str]:
    """Entries must lead to local rules and maps without fixing their prose shape."""
    errors: list[str] = []
    locations = {"workspace": ROOT}
    locations.update(
        (name, ROOT / path)
        for name, path in running_repositories(repository_paths).items()
    )
    for name, repo in sorted(locations.items()):
        if not repo.is_dir():
            continue
        references = ("AGENT-INDEX.md",) if name == "workspace" else (
            "AGENT-INDEX.md", "DIRECTORY_MAP.md"
        )
        for filename in ENTRY_PAGES:
            source = repo / filename
            if not source.is_file() or source.stat().st_size == 0:
                continue
            if source.is_symlink():
                errors.append(f"{name}: {filename} must be an independent entry file")
            content = source.read_text(encoding="utf-8")
            for reference in references:
                if reference not in content:
                    errors.append(f"{name}: {filename} does not reference {reference}")
            if HARDCODED_SIBLING_RE.search(content):
                errors.append(
                    f"{name}: {filename} hardcodes a sibling repository path; "
                    "use the workspace repository map"
                )
    return errors


def validate_ai_workspace() -> tuple[list[str], list[str], list[str]]:
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
    entry_errors, entry_warnings = check_repo_entry_files(repository_paths)
    errors.extend(entry_errors)
    warnings.extend(entry_warnings)
    errors.extend(check_entry_navigation(repository_paths))
    return errors, warnings, notes


def main() -> int:
    errors, warnings, notes = validate_ai_workspace()
    for note in notes:
        print(note)
    for warning in warnings:
        print(f"WARN {warning}")
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"AI workspace verification ok. {len(warnings)} warning(s) need review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
