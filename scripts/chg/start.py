"""`wt chg start`: preflight a CHG and select its branch."""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.chg import (
    ROOT,
    WTError,
    check_main,
    git,
    print_handoff,
    repositories,
    repo_state,
    verify_merged_dependencies,
)
from scripts.lib.change_metadata import ChangeMetadata, read_change
from scripts.prepare_ai_workspace import prepare_workspace


def cmd_start(change: ChangeMetadata, plan: bool = False, root: Path = ROOT) -> None:
    verify_merged_dependencies(change, root)
    paths = repositories(root)
    target = f"chg/{change.change_id}"
    actions: list[tuple[Path, str]] = []
    warnings: list[str] = []
    for other_path in sorted((root / "delivery" / "active").glob("CHG-*/change.md")):
        if other_path == change.path:
            continue
        other = read_change(other_path)
        overlap = sorted(set(change.affected_repos) & set(other.affected_repos))
        if overlap:
            warnings.append(
                f"{other.change_id} also affects {', '.join(overlap)}; coordinate file ownership before editing"
            )
    for name in change.affected_repos:
        repo = paths.get(name)
        if repo is None or not repo.is_dir():
            raise WTError(f"affected repository unavailable: {name}")
        branch, status, _ = repo_state(repo)
        if status:
            warnings.append(f"{name}: uncommitted changes:\n{status}")
        if change.legacy:
            warnings.append(
                f"{name}: legacy {change.change_id} keeps its existing {branch} workflow; no branch switch"
            )
            continue
        warnings.extend(check_main(repo))
        if branch == target:
            continue
        if status:
            raise WTError(f"{name}: uncommitted changes on {branch}; commit or move them before switching to {target}")
        existing = git(repo, "branch", "--list", target)
        if name == "wt-media-workspace":
            source = target if existing else "main"
            record = f"delivery/active/{change.change_id}/change.md"
            present = subprocess.run(
                ["git", "-C", str(repo), "cat-file", "-e", f"{source}:{record}"],
                capture_output=True, check=False,
            )
            if present.returncode:
                raise WTError(f"{name}: {record} is absent on {source}; commit the CHG record before start")
        actions.append((repo, "switch" if existing else "create"))
    for warning in warnings:
        print("WARN", warning)
    for repo, action in actions:
        print(f"{repo.name}: {'switch to' if action == 'switch' else 'create'} {target} from main")
    if plan:
        print("PLAN ONLY: no branch or context changed")
        print_handoff(change, root)
        return
    for repo, action in actions:
        args = ["git", "-C", str(repo), "switch", target] if action == "switch" else ["git", "-C", str(repo), "switch", "-c", target, "main"]
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        if result.returncode:
            raise WTError(f"{repo.name}: branch switch failed: {result.stderr.strip()}")
    prepare_workspace(workspace_repo=root, change_id=change.change_id)
    print_handoff(change, root)
