#!/usr/bin/env python3
"""Small CHG and scenario entry point over existing WT Media scripts."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.change_metadata import ChangeMetadata, read_change
from scripts.prepare_ai_workspace import prepare_workspace
from scripts.workspace_config import read_section


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


def check_main(repo: Path) -> list[str]:
    if not git(repo, "rev-parse", "--verify", "main", required=False):
        raise WTError(f"{repo.name}: local main missing")
    upstream = git(repo, "rev-parse", "--verify", "origin/main", required=False)
    if not upstream:
        return [f"{repo.name}: origin/main unavailable; confirm main freshness manually"]
    counts = git(repo, "rev-list", "--left-right", "--count", "main...origin/main").split()
    ahead, behind = map(int, counts)
    if behind:
        raise WTError(f"{repo.name}: main is {behind} commit(s) behind origin/main; sync before start")
    return [f"{repo.name}: main is {ahead} commit(s) ahead of origin/main"] if ahead else []


def print_handoff(change: ChangeMetadata, root: Path = ROOT) -> None:
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
    print("Recommended targeted verification: wt chg verify " + change.change_id + " --plan")


def cmd_status(root: Path = ROOT) -> None:
    active = sorted((root / "delivery" / "active").glob("CHG-*/change.md"))
    print(f"Selected CHG: {selected_change(root) or 'none'}")
    print(f"Active CHGs: {len(active)}")
    for path in active:
        try:
            change = read_change(path)
            print(f"  {change.change_id} {change.status} risk={change.risk} repos={','.join(change.affected_repos)}")
        except ValueError as exc:
            print(f"  {path.parent.name} INVALID: {exc}")
    for name, repo in repositories(root).items():
        branch, status, _ = repo_state(repo)
        print(f"{name}: branch={branch}; status={status or 'clean'}")


def cmd_start(change: ChangeMetadata, plan: bool = False, root: Path = ROOT) -> None:
    verify_merged_dependencies(change, root)
    paths = repositories(root)
    target = f"codex/{change.change_id}"
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
        warnings.extend(check_main(repo))
        branch, status, _ = repo_state(repo)
        if status:
            warnings.append(f"{name}: uncommitted changes:\n{status}")
        if branch == target:
            continue
        if change.legacy and branch == "main":
            warnings.append(f"{name}: legacy {change.change_id} keeps its existing main workflow")
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


def cmd_resume(change: ChangeMetadata, root: Path = ROOT) -> None:
    prepare_workspace(workspace_repo=root, change_id=change.change_id)
    print_handoff(change, root)


# Each adapter delegates to an existing repository entry. No process, test, or
# environment implementation lives here.
FAST = {
    "wt-media-workspace": ["python3", "-m", "unittest", "discover", "-s", "tests"],
    "wt-media-cloud": ["go", "test", "./internal/modules/..."],
    "wt-media-agent": ["bash", "scripts/test.sh"],
    "wt-media-desktop": ["bash", "scripts/test.sh"],
}
REPO_TEST = {
    "wt-media-workspace": ["python3", "-m", "unittest", "discover", "-s", "tests"],
    "wt-media-cloud": ["bash", "scripts/test.sh"],
    "wt-media-agent": ["bash", "scripts/test.sh"],
    "wt-media-desktop": ["bash", "scripts/test.sh"],
}


def run_command(repo: Path, command: list[str], plan: bool) -> None:
    print(f"{repo.name}: {' '.join(command)}", flush=True)
    if plan:
        return
    result = subprocess.run(command, cwd=repo, check=False)
    if result.returncode:
        raise WTError(f"{repo.name}: command failed with exit {result.returncode}: {' '.join(command)}")


def cmd_test(scenario: str, repo_name: str | None, plan: bool, root: Path = ROOT) -> None:
    paths = repositories(root)
    if repo_name is not None and repo_name not in paths:
        raise WTError(f"unknown repository: {repo_name}")
    if scenario in {"fast", "repo"}:
        repo_name = repo_name or "wt-media-workspace"
        command = (FAST if scenario == "fast" else REPO_TEST)[repo_name]
        run_command(paths[repo_name], command, plan)
        if scenario == "repo" and repo_name == "wt-media-workspace":
            for script in ("verify_delivery_governance.py", "verify_ai_workspace.py", "verify_skills.py", "verify_product_master_alignment.py"):
                run_command(root, ["python3", f"scripts/{script}"], plan)
    elif scenario == "integration":
        if repo_name:
            raise WTError("integration is a cross-repository scenario; omit --repo")
        run_command(root, ["python3", "scripts/verify_m1_integration.py"], plan)
    elif scenario == "e2e":
        if repo_name:
            raise WTError("e2e is a cross-repository scenario; omit --repo")
        run_command(root, ["bash", "bin/control.sh", "verify"], plan)
    elif scenario == "real":
        if repo_name:
            raise WTError("real is a cross-repository scenario; omit --repo")
        print("real: use environment-bring-up, then record real external effects, file hashes and user acceptance in CHG evidence")
    else:
        raise WTError(f"unknown test scenario: {scenario}")


def cmd_dev(scenario: str, repo_name: str | None, plan: bool, root: Path = ROOT) -> None:
    paths = repositories(root)
    if scenario == "fast":
        print("fast: no environment startup; use wt test fast")
    elif scenario == "repo":
        if not repo_name or repo_name == "wt-media-workspace" or repo_name not in paths:
            raise WTError("dev repo needs --repo wt-media-cloud|wt-media-agent|wt-media-desktop")
        run_command(paths[repo_name], ["bash", "bin/control.sh", "start"], plan)
    elif scenario == "integration":
        for name in ("wt-media-cloud", "wt-media-agent"):
            run_command(paths[name], ["bash", "bin/control.sh", "start"], plan)
        print("M1 integration: run wt test integration for the existing cross-end check")
    elif scenario == "e2e":
        run_command(root, ["bash", "bin/control.sh", "start"], plan)
    elif scenario == "real":
        print("real: follow environment-bring-up and the CHG's manual acceptance; no external side effect is auto-started")
    else:
        raise WTError(f"unknown dev scenario: {scenario}")


def cmd_verify(change: ChangeMetadata, plan: bool, root: Path = ROOT) -> None:
    runtime_repos = set(change.affected_repos) - {"wt-media-workspace"}
    scenarios = ["fast"]
    if change.risk in {"M", "H"}:
        scenarios.append("integration" if runtime_repos else "repo")
    scenarios.extend(change.verify_scenarios)
    scenarios = list(dict.fromkeys(scenarios))
    if "repo" in scenarios and "fast" in scenarios:
        scenarios.remove("fast")  # The repository suite includes its fast tests.
    print(f"CHG {change.change_id} risk={change.risk}; affected={', '.join(change.affected_repos)}")
    for scenario in scenarios:
        if scenario in {"fast", "repo"}:
            for name in change.affected_repos:
                cmd_test(scenario, name, plan, root)
        else:
            cmd_test(scenario, None, plan, root)
    if change.risk == "H":
        print("H risk: also run targeted contract and e2e/real smoke when the CHG requires them; record evidence")
    print("Verify CHG-specific regression and Done When against its checkpoint/evidence before marking DONE")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wt")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    chg = commands.add_parser("chg")
    chg_commands = chg.add_subparsers(dest="chg_command", required=True)
    for name in ("start", "resume", "verify"):
        part = chg_commands.add_parser(name)
        part.add_argument("change_id")
        if name != "resume":
            part.add_argument("--plan", action="store_true")
    for name in ("dev", "test"):
        part = commands.add_parser(name)
        part.add_argument("scenario", choices=("fast", "repo", "integration", "e2e", "real"))
        part.add_argument("--repo", choices=("wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"))
        part.add_argument("--plan", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            cmd_status()
        elif args.command == "chg":
            change = active_change(args.change_id)
            if args.chg_command == "start":
                cmd_start(change, args.plan)
            elif args.chg_command == "resume":
                cmd_resume(change)
            else:
                cmd_verify(change, args.plan)
        elif args.command == "dev":
            cmd_dev(args.scenario, args.repo, args.plan)
        else:
            cmd_test(args.scenario, args.repo, args.plan)
    except (WTError, OSError, ValueError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
