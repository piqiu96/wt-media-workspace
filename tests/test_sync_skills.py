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
            workspace.mkdir(parents=True)
            (root / "wt-media-cloud").mkdir()

            self.assertEqual(self.module.execution_root(workspace), root)

    def test_execution_root_ignores_the_execution_snapshot_location(self) -> None:
        """Root detection is repository-based, not snapshot-based.

        The snapshot directory is not created here on purpose: `.ai/` lives
        inside the workspace repository and must not be required at the outer
        root for root detection to succeed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wt-media"
            workspace = root / "wt-media-workspace"
            workspace.mkdir(parents=True)
            (root / "wt-media-cloud").mkdir()

            self.assertFalse((root / ".ai").exists())
            self.assertEqual(self.module.execution_root(workspace), root)

    def test_execution_root_resolves_linked_worktree_to_shared_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wt-media"
            workspace = root / "wt-media-workspace"
            worktree = workspace / ".worktrees" / "delivery-fix"
            worktree.mkdir(parents=True)
            (root / "wt-media-cloud").mkdir()

            self.assertEqual(self.module.execution_root(worktree), root)

    def test_targets_come_from_the_declared_configuration(self) -> None:
        """The distribution list must be the one in config/, not a copy in code."""
        targets = self.module.TARGETS

        self.assertEqual(
            sorted(targets), ["agent", "cloud", "desktop", "root", "workspace"]
        )
        self.assertEqual(targets["root"].kind, "distribution")
        self.assertEqual(targets["cloud"].kind, "repository")
        self.assertEqual(targets["cloud"].groups, ("common", "cloud"))
        self.assertEqual(self.module.TOOLS, ("codex", "claude"))

    def test_declared_path_is_anchored_to_the_execution_root(self) -> None:
        root = Path("/tmp/wt-media")

        self.assertEqual(self.module.resolve_target_path("..", root), root)
        self.assertEqual(
            self.module.resolve_target_path("../wt-media-cloud", root),
            root / "wt-media-cloud",
        )

    def test_declared_path_is_re_anchored_for_a_linked_worktree(self) -> None:
        """A linked worktree is not a sibling of the repositories, so `../x`
        cannot be joined literally to the worktree directory."""
        with tempfile.TemporaryDirectory() as tmp:
            shared = Path(tmp) / "wt-media"
            workspace = shared / "wt-media-workspace"
            worktree = workspace / ".worktrees" / "delivery-fix"
            worktree.mkdir(parents=True)
            (shared / "wt-media-cloud").mkdir()

            resolved_root = self.module.execution_root(worktree)

            self.assertEqual(resolved_root, shared)
            self.assertEqual(
                self.module.resolve_target_path("../wt-media-cloud", resolved_root),
                shared / "wt-media-cloud",
            )
            self.assertEqual(self.module.resolve_target_path("..", resolved_root), shared)

    def test_absolute_declared_path_is_rejected(self) -> None:
        with self.assertRaises(self.module.agent_config.ConfigError):
            self.module.resolve_target_path("/tmp/elsewhere", Path("/tmp/wt-media"))

    def test_load_targets_reads_groups_and_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "skills-distribution.yaml"
            path.write_text(
                "targets:\n"
                "  root:\n"
                '    path: ".."\n'
                "    kind: distribution\n"
                "    groups:\n"
                "      - common\n"
                "  cloud:\n"
                '    path: "../wt-media-cloud"\n'
                "    groups:\n"
                "      - common\n"
                "      - cloud\n"
                "tools:\n"
                "  - codex\n",
                encoding="utf-8",
            )

            targets, tools = self.module.load_targets(path, Path("/tmp/wt-media"))

        self.assertEqual(targets["root"].kind, "distribution")
        self.assertEqual(targets["cloud"].groups, ("common", "cloud"))
        self.assertEqual(targets["cloud"].path, Path("/tmp/wt-media/wt-media-cloud"))
        self.assertEqual(tools, ("codex",))

    def test_load_targets_rejects_a_target_without_groups(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "skills-distribution.yaml"
            path.write_text(
                'targets:\n  cloud:\n    path: "../wt-media-cloud"\n', encoding="utf-8"
            )

            with self.assertRaises(self.module.agent_config.ConfigError) as caught:
                self.module.load_targets(path, Path("/tmp/wt-media"))

        self.assertIn("declares no groups", str(caught.exception))

    def test_load_targets_rejects_an_unknown_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "skills-distribution.yaml"
            path.write_text(
                "targets:\n"
                "  cloud:\n"
                '    path: "../wt-media-cloud"\n'
                "    kind: sibling\n"
                "    groups:\n"
                "      - common\n",
                encoding="utf-8",
            )

            with self.assertRaises(self.module.agent_config.ConfigError) as caught:
                self.module.load_targets(path, Path("/tmp/wt-media"))

        self.assertIn("unknown kind: sibling", str(caught.exception))

    def test_unresolved_target_is_reported_before_writing(self) -> None:
        missing = self.module.Target("cloud", Path("/tmp/absent-repo"), ("common",))
        present = self.module.Target("root", Path("/tmp"), ("common",))

        self.assertEqual(
            self.module.unresolved_targets([missing, present]),
            ["cloud: target directory does not exist: /tmp/absent-repo"],
        )


if __name__ == "__main__":
    unittest.main()
