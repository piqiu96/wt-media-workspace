#!/usr/bin/env python3
"""Small CHG and scenario entry point over existing WT Media scripts."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.chg import WTError, active_change, repo_state, repositories, selected_change
from scripts.chg.resume import cmd_resume
from scripts.chg.start import cmd_start
from scripts.chg.verify import risk_note, scenarios_for
from scripts.lib.change_metadata import ChangeMetadata, read_change


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


# Each adapter delegates to an existing repository entry. No process, test, or
# environment implementation lives here.
FAST = {
    "wt-media-workspace": [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
    "wt-media-cloud": ["go", "test", "./internal/modules/..."],
    "wt-media-agent": ["bash", "scripts/test.sh"],
    "wt-media-desktop": ["bash", "scripts/test.sh"],
}
REPO_TEST = {
    "wt-media-workspace": [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
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
            for script in (
                "verify_delivery_governance.py",
                "verify_ai_workspace.py",
                "verify_skills.py",
                "verify_product_master_alignment.py",
                "verify_m0_config.py",
            ):
                run_command(root, ["python3", f"scripts/verify/{script}"], plan)
            run_command(root, ["python3", "scripts/docs/check.py"], plan)
            run_command(root, ["bash", "scripts/verify/verify-control.sh"], plan)
    elif scenario == "integration":
        if repo_name:
            raise WTError("integration is a cross-repository scenario; omit --repo")
        run_command(root, ["bash", "bin/control.sh", "verify"], plan)
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
        run_command(root, ["bash", "bin/control.sh", "start"], plan)
    elif scenario == "e2e":
        run_command(root, ["bash", "bin/control.sh", "start"], plan)
    elif scenario == "real":
        print("real: follow environment-bring-up and the CHG's manual acceptance; no external side effect is auto-started")
    else:
        raise WTError(f"unknown dev scenario: {scenario}")


def cmd_verify(change: ChangeMetadata, plan: bool, root: Path = ROOT) -> None:
    scenarios = scenarios_for(change)
    print(f"CHG {change.change_id} risk={change.risk}; affected={', '.join(change.affected_repos)}")
    for scenario in scenarios:
        if scenario in {"fast", "repo"}:
            for name in change.affected_repos:
                cmd_test(scenario, name, plan, root)
        else:
            cmd_test(scenario, None, plan, root)
    if change.risk == "H" and "repo" not in scenarios:
        run_command(root, ["python3", "scripts/verify/verify_m0_config.py"], plan)
    note = risk_note(change)
    if note:
        print(note)
    print("Verify CHG-specific regression and Done When against its evidence and acceptance record (plus checkpoint when present) before marking DONE")


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
