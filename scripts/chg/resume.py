"""`wt chg resume`: regenerate local context and report the handoff."""

from __future__ import annotations

from pathlib import Path

from scripts.chg import ROOT, main_drift, print_handoff, repositories
from scripts.lib.change_metadata import ChangeMetadata
from scripts.prepare_ai_workspace import prepare_workspace


def cmd_resume(change: ChangeMetadata, root: Path = ROOT) -> None:
    prepare_workspace(workspace_repo=root, change_id=change.change_id)
    paths = repositories(root)
    for name in change.affected_repos:
        repo = paths.get(name)
        if repo is None or not repo.is_dir():
            print(f"WARN {name}: repository unavailable; cannot compare local main")
            continue
        for warning in main_drift(repo):
            print(f"WARN {warning}")
    print_handoff(change, root)
