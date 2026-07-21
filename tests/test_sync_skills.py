from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "sync_skills.py"


def load_module():
    spec = importlib.util.spec_from_file_location("sync_skills", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load sync_skills.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SyncSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_execution_root_resolves_normal_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wt-media"
            workspace = root / "wt-media-workspace"
            (root / ".ai").mkdir(parents=True)
            workspace.mkdir()

            self.assertEqual(self.module.execution_root(workspace), root)

    def test_execution_root_resolves_linked_worktree_to_shared_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wt-media"
            workspace = root / "wt-media-workspace"
            worktree = workspace / ".worktrees" / "delivery-fix"
            (root / ".ai").mkdir(parents=True)
            worktree.mkdir(parents=True)

            self.assertEqual(self.module.execution_root(worktree), root)


if __name__ == "__main__":
    unittest.main()
