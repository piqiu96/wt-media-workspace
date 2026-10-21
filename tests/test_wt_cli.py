from __future__ import annotations

import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.change_metadata import read_change
from scripts.wt import WTError, cmd_resume, cmd_start, cmd_test, cmd_verify, verify_merged_dependencies


class WTCLITests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        outer = Path(temporary.name)
        self.root = outer / "wt-media-workspace"
        self.cloud = outer / "wt-media-cloud"
        for path in (self.root, self.cloud):
            path.mkdir()
            self.git(path, "init", "-b", "main")
            self.git(path, "config", "user.name", "WT Test")
            self.git(path, "config", "user.email", "wt@example.test")
        mapping = self.root / "config" / "repository-map.yaml"
        mapping.parent.mkdir()
        mapping.write_text(
            "schema_version: 1\nrepositories:\n"
            "  workspace:\n    path: ../wt-media-workspace\n"
            "  cloud:\n    path: ../wt-media-cloud\n",
            encoding="utf-8",
        )
        (self.cloud / "README.md").write_text("cloud\n", encoding="utf-8")
        self.commit(self.cloud)

    @staticmethod
    def git(repo: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], text=True, capture_output=True, check=True
        )
        return result.stdout.strip()

    def commit(self, repo: Path) -> str:
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-qm", "fixture")
        return self.git(repo, "rev-parse", "HEAD")

    def change(
        self,
        change_id: str = "CHG-20261022-099",
        *,
        depends: str = "[]",
        affected: str = '["wt-media-workspace"]',
        extra: str = "",
    ) -> Path:
        path = self.root / "delivery" / "active" / change_id / "change.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nid: {change_id}\nparent: none\nstatus: IMPLEMENTING\n"
            f"depends_on: {depends}\naffected_repos: {affected}\nrisk: M\n{extra}---\n"
            f"# {change_id}: Test\n\n## Change\n\nTest.\n\n## Done When\n\nPass.\n",
            encoding="utf-8",
        )
        return path

    def archived_dependency(self, merge_commits: str = "") -> str:
        dep_id = "CHG-20261020-001"
        path = self.root / "delivery" / "completed" / dep_id / "change.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nid: {dep_id}\nparent: none\nstatus: DONE\n"
            f"depends_on: []\naffected_repos: [\"wt-media-cloud\"]\nrisk: M\n"
            f"{merge_commits}---\n# {dep_id}: Done\n## Change\nDone.\n## Done When\nPass.\n",
            encoding="utf-8",
        )
        return dep_id

    def test_start_creates_branch_after_preflight(self) -> None:
        change = read_change(self.change())
        self.commit(self.root)
        with patch("scripts.wt.prepare_workspace") as prepare:
            with contextlib.redirect_stdout(io.StringIO()):
                cmd_start(change, root=self.root)
        self.assertEqual(self.git(self.root, "branch", "--show-current"), "codex/CHG-20261022-099")
        prepare.assert_called_once_with(workspace_repo=self.root, change_id=change.change_id)

    def test_start_rejects_uncommitted_record_before_switch(self) -> None:
        self.commit(self.root)
        change = read_change(self.change())
        with self.assertRaisesRegex(WTError, "uncommitted changes"):
            cmd_start(change, root=self.root)
        self.assertEqual(self.git(self.root, "branch", "--show-current"), "main")

    def test_dependency_requires_machine_checked_main_commit(self) -> None:
        sha = self.git(self.cloud, "rev-parse", "HEAD")
        dep_id = self.archived_dependency(f'merge_commits: {{"wt-media-cloud": "{sha}"}}\n')
        change = read_change(self.change(depends=f'["{dep_id}"]'))
        verify_merged_dependencies(change, self.root)

    def test_dependency_without_commit_evidence_blocks(self) -> None:
        dep_id = self.archived_dependency()
        change = read_change(self.change(depends=f'["{dep_id}"]'))
        with self.assertRaisesRegex(WTError, "missing merged commit"):
            verify_merged_dependencies(change, self.root)

    def test_dependency_commit_off_main_blocks(self) -> None:
        self.git(self.cloud, "switch", "-c", "feature")
        (self.cloud / "feature.txt").write_text("feature\n", encoding="utf-8")
        sha = self.commit(self.cloud)
        dep_id = self.archived_dependency(f'merge_commits: {{"wt-media-cloud": "{sha}"}}\n')
        change = read_change(self.change(depends=f'["{dep_id}"]'))
        with self.assertRaisesRegex(WTError, "not merged into"):
            verify_merged_dependencies(change, self.root)

    def test_verify_uses_risk_and_optional_scenario(self) -> None:
        change = read_change(self.change(extra='verify_scenarios: ["real"]\n'))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            cmd_verify(change, plan=True, root=self.root)
        self.assertIn("unittest discover", output.getvalue())
        self.assertIn("verify_delivery_governance.py", output.getvalue())
        self.assertIn("real: use environment-bring-up", output.getvalue())

    def test_scenario_plan_maps_existing_entries(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            cmd_test("integration", None, True, self.root)
            cmd_test("e2e", None, True, self.root)
        self.assertIn("scripts/verify_m1_integration.py", output.getvalue())
        self.assertIn("bin/control.sh verify", output.getvalue())

    def test_resume_reads_checkpoint_and_optional_state(self) -> None:
        change = read_change(self.change())
        checkpoint = change.path.parent / "checkpoint.md"
        checkpoint.write_text("## Current\nAt handoff.\n\n## Next\nRun tests.\n", encoding="utf-8")
        local = self.root / ".ai" / "WORK_STATE.md"
        local.parent.mkdir()
        local.write_text("Local note.\n", encoding="utf-8")
        output = io.StringIO()
        with patch("scripts.wt.prepare_workspace"), contextlib.redirect_stdout(output):
            cmd_resume(change, self.root)
        self.assertIn("At handoff.", output.getvalue())
        self.assertIn("Local note.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
