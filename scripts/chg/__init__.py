"""Shared CHG navigation and preconditions used by `wt chg` and `wt status`."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.lib.change_metadata import ChangeMetadata, read_change
from scripts.lib.workspace_config import read_section


class WTError(Exception):
    pass


def repositories(root: Path = ROOT) -> dict[str, Path]:
    mapping = read_section(root / "config" / "repository-map.yaml", "repositories")
    return {f"wt-media-{name}": (root / settings["path"]).resolve() for name, settings in mapping.items()}


def git(repo: Path, *args: str, required: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if result.returncode and required:
        raise WTError(f"{repo.name}: git {' '.join(args)}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip() if result.returncode == 0 else ""


def change_path(change_id: str, root: Path = ROOT) -> Path:
    return root / "delivery" / "active" / change_id / "change.md"


def active_change(change_id: str, root: Path = ROOT) -> ChangeMetadata:
    path = change_path(change_id, root)
    if not path.is_file():
        raise WTError(f"active CHG not found: {change_id}")
    try:
        metadata = read_change(path)
    except ValueError as exc:
        raise WTError(f"{change_id}: {exc}") from exc
    if metadata.status not in {"IMPLEMENTING", "VERIFYING"}:
        raise WTError(f"{change_id} is not executable: {metadata.status}")
    return metadata


def selected_change(root: Path = ROOT) -> str | None:
    context = root / ".ai" / "CURRENT_CONTEXT.md"
    if not context.is_file():
        return None
    match = re.search(r"^- Current CHG: `(CHG-\d{8}-\d{3})`", context.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else None


def repo_state(repo: Path) -> tuple[str, str, str]:
    if not repo.is_dir():
        return "missing", "", ""
    branch = git(repo, "branch", "--show-current", required=False) or "detached"
    status = git(repo, "status", "--short", required=False)
    diff = git(repo, "diff", "--stat", required=False)
    return branch, status, diff


def references(change: ChangeMetadata, root: Path = ROOT) -> list[str]:
    result = [str(change.path.relative_to(root))]
    if change.parent != "none":
        result.append(change.parent)
    body = change.path.read_text(encoding="utf-8")
    for label in ("Product", "Engineering", "Decision"):
        result.extend(re.findall(rf"^- {label}: `([^`]+)`", body, re.MULTILINE))
    if "## References" in body:
        section = body.split("## References", 1)[1].split("\n## ", 1)[0]
        result.extend(value for value in re.findall(r"`([^`]+)`", section) if value.startswith(("docs/", "delivery/", "AGENT-")))
    return list(dict.fromkeys(result))


def verify_merged_dependencies(change: ChangeMetadata, root: Path = ROOT) -> None:
    paths = repositories(root)
    for dep_id in change.depends_on:
        if change_path(dep_id, root).exists():
            raise WTError(f"{dep_id} is still active; merge it before starting {change.change_id}")
        archive = root / "delivery" / "completed" / dep_id / "change.md"
        if not archive.is_file():
            raise WTError(f"{dep_id} is not archived under delivery/completed")
        try:
            dependency = read_change(archive)
        except ValueError as exc:
            raise WTError(f"cannot read archived {dep_id}: {exc}") from exc
        commits = dependency.merge_commits or change.dependency_merge_commits.get(dep_id, {})
        affected = dependency.affected_repos or tuple(commits)
        if not affected:
            raise WTError(
                f"{dep_id} has no affected-repository evidence; review its archive and add "
                f"dependency_merge_commits to {change.change_id} before start"
            )
        for repo_name in affected:
            sha = commits.get(repo_name)
            if not sha:
                raise WTError(
                    f"{dep_id}: missing merged commit for {repo_name}; review archived evidence "
                    f"and add dependency_merge_commits to {change.change_id} before start"
                )
            repo = paths.get(repo_name)
            if repo is None or not repo.is_dir():
                raise WTError(f"{dep_id}: repository {repo_name} unavailable")
            if subprocess.run(
                ["git", "-C", str(repo), "cat-file", "-e", f"{sha}^{{commit}}"],
                capture_output=True, check=False,
            ).returncode:
                raise WTError(f"{dep_id}: commit {sha} absent in {repo_name}")
            ancestor = subprocess.run(
                ["git", "-C", str(repo), "merge-base", "--is-ancestor", sha, "main"],
                capture_output=True, check=False,
            )
            if ancestor.returncode:
                raise WTError(f"{dep_id}: commit {sha} is not merged into {repo_name} local main")


def _main_counts(repo: Path) -> tuple[int, int] | None:
    if not git(repo, "rev-parse", "--verify", "main", required=False):
        raise WTError(f"{repo.name}: local main missing")
    upstream = git(repo, "rev-parse", "--verify", "origin/main", required=False)
    if not upstream:
        return None
    counts = git(repo, "rev-list", "--left-right", "--count", "main...origin/main").split()
    ahead, behind = map(int, counts)
    return ahead, behind


def check_main(repo: Path) -> list[str]:
    counts = _main_counts(repo)
    if counts is None:
        return [f"{repo.name}: origin/main unavailable; confirm main freshness manually"]
    ahead, behind = counts
    if behind:
        raise WTError(f"{repo.name}: main is {behind} commit(s) behind origin/main; sync before start")
    return [f"{repo.name}: main is {ahead} commit(s) ahead of origin/main"] if ahead else []


def main_drift(repo: Path) -> list[str]:
    """Report a non-blocking main drift for `wt chg resume`."""
    try:
        counts = _main_counts(repo)
    except WTError as exc:
        return [str(exc)]
    if counts is None:
        return []
    _, behind = counts
    return [f"{repo.name}: local main is behind origin/main by {behind} commit(s)"] if behind else []


def print_handoff(change: ChangeMetadata, root: Path = ROOT) -> None:
    from scripts.chg.verify import scenarios_for

    paths = repositories(root)
    print(f"CHG {change.change_id} | {change.title} | risk {change.risk}")
    print("References:")
    for reference in references(change, root):
        print(f"  {reference}")
    print("Repositories:")
    for name in change.affected_repos:
        repo = paths.get(name)
        branch, status, diff = repo_state(repo) if repo else ("missing", "", "")
        print(f"  {name}: branch={branch}; status={status or 'clean'}")
        if diff:
            print(f"    diff --stat:\n{diff}")
    checkpoint = change.path.parent / "checkpoint.md"
    if checkpoint.is_file():
        print(f"Checkpoint: {checkpoint.relative_to(root)}")
        text = checkpoint.read_text(encoding="utf-8")
        for heading in ("Current", "Next", "Blockers", "Blocked"):
            match = re.search(rf"^## {heading}\s*$\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
            if match:
                print(f"  {heading}: {match.group(1).strip()[:1200]}")
    work_state = root / ".ai" / "WORK_STATE.md"
    if work_state.is_file():
        print(f"Optional local WORK_STATE:\n{work_state.read_text(encoding='utf-8')}")
    scenarios = scenarios_for(change)
    print(f"Recommended verification: wt chg verify {change.change_id} --plan (scenarios: {', '.join(scenarios)})")
