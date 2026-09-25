#!/usr/bin/env python3
"""Verify WT Media agent entry files and the invariants declared around them.

This script intentionally uses only the Python standard library, and it never
writes anything. It reports two severities:

- ``ERROR``: a declared invariant is broken. Exit code is 1.
- ``WARN``: a heuristic finding that needs a human decision. Exit code stays 0.

The heuristics are deliberately narrow. They must not turn into a second,
unreviewed source of truth for repository rules.

The entry-file shape is specified by
``docs/engineering/specs/agent-workspace-conventions.md`` section 3. Every ERROR
here judges existence, a declaration, a count, or an equality of counts - never
the wording of a rule. Wording is only ever a WARN, because a gate that freezes
prose turns every legitimate rewrite into a false failure.
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

# Entry-file shape, specified by docs/engineering/specs/agent-workspace-conventions.md
# section 3. The running repositories carry one more file than the workspace.
WORKSPACE_REPOSITORY = "workspace"
RUNNING_REPO_ENTRY_FILES = ("AGENT-INDEX.md", "AGENTS.md", "CLAUDE.md", "DIRECTORY_MAP.md")
POINTER_FILES = ("AGENTS.md", "CLAUDE.md")
BODY_FILE = "AGENT-INDEX.md"
MACHINE_KEY_RE = re.compile(r"^-\s*正文：\s*`(?P<target>[^`]+)`\s*$")

# Rule words mark a sentence as a claim, not a pointer. The criterion is
# deliberately crude: a line that claims must also name the body file, so the
# test is "is this line a pointer instruction or a restated rule?".
RULE_WORD_RE = re.compile(
    r"禁止|严禁|不得|必须|不允许|不应|不可|不要|不做|不创建|不新增|不存放|不修改|只能|只允许|应当"
    r"|must not|do not|never",
    re.IGNORECASE,
)

# Heading lines are naming, not claiming: `## 模块规则` is only a violation once
# rule text lands underneath it, and that is caught line by line.
POINTER_MAX_LINES = 30
POINTER_MAX_BYTES = 2000
POINTER_MAX_H2 = 4

PROJECT_ORDER_SECTIONS = (
    "依赖",
    "定位",
    "本仓库拥有",
    "本仓库不拥有",
    "需求路由",
    "本仓规则",
    "禁止",
    "本仓内加载顺序",
)
# The running repositories keep their own in-repository reading order. That
# list must not become a second copy of the project-level order.
LOCAL_ORDER_HEADING = "本仓内加载顺序"
LOCAL_ORDER_FORBIDDEN = ("CURRENT_CONTEXT", "LEDGER.md", "delivery/")

DUPLICATION_FILES = ("AGENT-INDEX.md", "DIRECTORY_MAP.md", "README.md")
EMPHASIS_RE = re.compile(r"[*_`]")
WHITESPACE_RE = re.compile(r"\s+")

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


def load_agent_config():
    """Load the shared configuration reader."""
    path = ROOT / "scripts" / "agent_config.py"
    spec = importlib.util.spec_from_file_location("agent_config", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load agent_config.py")
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
    config = load_agent_config()
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


def pointer_body(repo: Path, filename: str) -> tuple[str | None, list[str]]:
    """Read the body a pointer file declares, plus the errors in that declaration.

    The declared target is returned even when it is rejected: the pointer-pair
    check needs to see *what* each file claims, or a broken pair would report a
    self-reference and hide the disagreement that made it broken.
    """
    text = (repo / filename).read_text(encoding="utf-8")
    keys = [
        match.group("target")
        for line in text.splitlines()
        if (match := MACHINE_KEY_RE.match(line))
    ]
    if not keys:
        return None, [f"{filename} declares no rule body: expected `- 正文：`<file>``"]
    if len(keys) > 1:
        return None, [
            f"{filename} declares more than one rule body: {', '.join(sorted(set(keys)))}"
        ]
    target = keys[0]
    if target == filename:
        return target, [f"{filename} declares itself as the rule body"]
    if target not in ENTRY_FILES:
        return target, [f"{filename} declares an unknown rule body: {target}"]
    if not (repo / target).is_file():
        return target, [f"{filename} declares a rule body that does not resolve: {target}"]
    return target, []


def check_pointer_shape(repository_paths: dict[str, str]) -> list[str]:
    """A pointer file declares exactly one body, carries no rule text, and is small.

    The three parts are independent: the declaration makes the pointer
    followable, the rule-word criterion keeps restated rules out, and the
    budget keeps the file from growing into a second body by accretion.
    """
    errors: list[str] = []
    for name, path in sorted(repository_paths.items()):
        repo = ROOT / path
        for filename in POINTER_FILES:
            source = repo / filename
            if not source.is_file():
                continue
            body, declaration_errors = pointer_body(repo, filename)
            errors.extend(f"{name}: {error}" for error in declaration_errors)
            text = source.read_text(encoding="utf-8")
            lines = text.splitlines()
            expected = body or BODY_FILE
            for number, line in enumerate(lines, start=1):
                if line.startswith("#"):
                    continue
                if RULE_WORD_RE.search(line) and expected not in line:
                    errors.append(
                        f"{name}: {filename}:{number} restates a rule without naming "
                        f"{expected}: {line.strip()}"
                    )
            h2 = sum(1 for line in lines if line.startswith("## "))
            over = [
                label
                for label, value, limit in (
                    ("lines", len(lines), POINTER_MAX_LINES),
                    ("bytes", len(text.encode("utf-8")), POINTER_MAX_BYTES),
                    ("H2 headings", h2, POINTER_MAX_H2),
                )
                if value > limit
            ]
            if over:
                errors.append(
                    f"{name}: {filename} exceeds the pointer budget "
                    f"({', '.join(over)}): {len(lines)} lines, "
                    f"{len(text.encode('utf-8'))} bytes, {h2} H2 headings"
                )
    return errors


def check_rule_body_consistency(repository_paths: dict[str, str]) -> list[str]:
    """All pointers in one repository name the same body, and the chain stops there.

    Two pointers that name different bodies give the two Harnesses different
    answers, so the reader of a rule ends up with two. A body that forwards to
    another body (`A -> B`, `B -> A`) resolves nowhere, which is the failure the
    terminal-body rule exists to catch.
    """
    errors: list[str] = []
    for name, path in sorted(repository_paths.items()):
        repo = ROOT / path
        declared: dict[str, str] = {}
        for filename in POINTER_FILES:
            if not (repo / filename).is_file():
                continue
            body, _ = pointer_body(repo, filename)
            if body is not None:
                declared[filename] = body
        if len(set(declared.values())) > 1:
            pairs = ", ".join(f"{k} -> {v}" for k, v in sorted(declared.items()))
            errors.append(f"{name}: pointer files disagree on the rule body: {pairs}")
        # One message per distinct defect: both pointers naming the same broken
        # body is one problem to fix, not two.
        for body in sorted(set(declared.values())):
            declaring = sorted(
                pointer for pointer, target in declared.items() if target == body
            )
            if body in POINTER_FILES:
                errors.append(
                    f"{name}: {', '.join(declaring)} declares a pointer as the rule body "
                    f"({body}); the body must not itself be a pointer"
                )
            elif (repo / body).is_file() and any(
                MACHINE_KEY_RE.match(line)
                for line in (repo / body).read_text(encoding="utf-8").splitlines()
            ):
                errors.append(
                    f"{name}: {body} is declared as the rule body but declares one "
                    "itself; the chain must end at the body"
                )
    return errors


def check_layer3_shape(repository_paths: dict[str, str]) -> list[str]:
    """The running repositories' AGENT-INDEX.md share one eight-section order.

    The workspace is exempt: there the same filename is the governance body
    itself, not a repository index.
    """
    errors: list[str] = []
    sequences: dict[str, list[str]] = {}
    for name, path in sorted(running_repositories(repository_paths).items()):
        source = ROOT / path / BODY_FILE
        if not source.is_file():
            continue
        headings = [
            line[3:].strip()
            for line in source.read_text(encoding="utf-8").splitlines()
            if line.startswith("## ")
        ]
        sequences[name] = headings
        if len(headings) != len(PROJECT_ORDER_SECTIONS):
            errors.append(
                f"{name}: {BODY_FILE} has {len(headings)} H2 sections, expected "
                f"{len(PROJECT_ORDER_SECTIONS)}: {', '.join(headings)}"
            )
    ordered = sorted(sequences.items())
    for (name, headings), (reference, expected) in zip(ordered[1:], ordered):
        for position, (actual, want) in enumerate(zip(headings, expected), start=1):
            if actual != want:
                errors.append(
                    f"{name}: {BODY_FILE} H2 sequence diverges from {reference} at "
                    f"position {position}: '{actual}' != '{want}'"
                )
                break
    return errors


def rule_sentences(path: Path, body: str) -> list[str]:
    """Lines that are rule claims: not headings, not pointers, not role tables.

    A line naming the body file is the pointer's own machinery; a line naming any
    entry file is describing a file's role. Neither is a rule, and both repeat by
    design - two pointers to one body are supposed to overlap.
    """
    if not path.is_file():
        return []
    sentences: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue
        if body in line or any(name in line for name in RUNNING_REPO_ENTRY_FILES):
            continue
        if not RULE_WORD_RE.search(line):
            continue
        normalized = WHITESPACE_RE.sub(" ", EMPHASIS_RE.sub("", line)).strip()
        if normalized:
            sentences.append(normalized)
    return sentences


def check_rule_text_duplication(
    repository_paths: dict[str, str],
) -> tuple[list[str], str]:
    """The same rule sentence in two files of one repository is one landing point too many.

    Reports the denominator on every run: a zero without a denominator is a
    green with no evidence, since a comparator that matches nothing also
    reports zero.
    """
    warnings: list[str] = []
    repositories = 0
    files = 0
    compared = 0
    for name, path in sorted(repository_paths.items()):
        repo = ROOT / path
        if not repo.is_dir():
            continue
        repositories += 1
        seen: dict[str, list[str]] = {}
        body = BODY_FILE
        for filename in DUPLICATION_FILES:
            source = repo / filename
            if not source.is_file():
                continue
            files += 1
            for sentence in rule_sentences(source, body):
                compared += 1
                seen.setdefault(sentence, []).append(filename)
        for sentence, where in sorted(seen.items()):
            if len(set(where)) > 1:
                warnings.append(
                    f"{name}: rule sentence repeated in {', '.join(sorted(set(where)))}: "
                    f"{sentence}"
                )
    note = (
        f"rule-text duplication: compared {compared} rule sentence(s) across "
        f"{files} file(s) in {repositories} repositor{'y' if repositories == 1 else 'ies'}"
    )
    return warnings, note


def check_local_order_scope(repository_paths: dict[str, str]) -> list[str]:
    """A repository's own reading order must not restate the project-level one.

    The project-level order is the workspace's; a local list that names the
    snapshot, the ledger, or `delivery/` is a second landing point for it.
    """
    warnings: list[str] = []
    for name, path in sorted(running_repositories(repository_paths).items()):
        source = ROOT / path / BODY_FILE
        if not source.is_file():
            continue
        lines = source.read_text(encoding="utf-8").splitlines()
        section: list[str] = []
        inside = False
        for line in lines:
            if line.startswith("## "):
                inside = line[3:].strip() == LOCAL_ORDER_HEADING
                continue
            if inside:
                section.append(line)
        for forbidden in LOCAL_ORDER_FORBIDDEN:
            if any(forbidden in line for line in section):
                warnings.append(
                    f"{name}: {BODY_FILE} section '{LOCAL_ORDER_HEADING}' names "
                    f"`{forbidden}` - the project-level order belongs to the workspace"
                )
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

    entry_errors, entry_warnings = check_repo_entry_files(repository_paths)
    errors.extend(entry_errors)
    warnings.extend(entry_warnings)
    errors.extend(check_pointer_shape(repository_paths))
    errors.extend(check_rule_body_consistency(repository_paths))
    errors.extend(check_layer3_shape(repository_paths))

    duplication_warnings, duplication_note = check_rule_text_duplication(repository_paths)
    warnings.extend(duplication_warnings)
    notes.append(duplication_note)
    warnings.extend(check_local_order_scope(repository_paths))
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
