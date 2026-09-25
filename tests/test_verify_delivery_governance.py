from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "verify_delivery_governance.py"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_delivery_governance", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify_delivery_governance.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class VerifyDeliveryGovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "wt-media"
        self.workspace = self.root / "wt-media-workspace"
        (self.workspace / "delivery" / "active").mkdir(parents=True)
        (self.workspace / "delivery" / "milestones").mkdir(parents=True)
        # The fixture is compliant by default: the archive exists and declares its
        # boundary.  A fixture that is invalid out of the box would make every
        # unrelated test carry an unrelated error (CHG-20260925-065 T-04).
        self.write_archive_boundary()
        (self.workspace / "scripts").mkdir()
        self.module = load_module()

    def write_archive_boundary(self, marker: str = "- 归档边界：`READ-ONLY`\n") -> None:
        archive = self.workspace / "delivery" / "completed"
        archive.mkdir(parents=True, exist_ok=True)
        (archive / "README.md").write_text(
            f"# Archive\n\n{marker}\nRecords are read-only.\n", encoding="utf-8"
        )

    def write_script(self, name: str, body: str) -> None:
        path = self.workspace / "scripts" / name
        path.write_text(body, encoding="utf-8")

    def write_context(self, change_id: str) -> None:
        (self.workspace / ".ai" / "CURRENT_CONTEXT.md").parent.mkdir(
            parents=True, exist_ok=True
        )
        (self.workspace / ".ai" / "CURRENT_CONTEXT.md").write_text(
            f"# Context\n\n- Active CHG: `{change_id}`\n",
            encoding="utf-8",
        )

    def write_ledger(self, change_id: str) -> None:
        (self.workspace / "delivery" / "LEDGER.md").write_text(
            "# Delivery Ledger\n\n"
            "| Change | Title | Status | Current Repository |\n"
            "|---|---|---|---|\n"
            f"| {change_id} | Test | IMPLEMENTING | wt-media-workspace |\n",
            encoding="utf-8",
        )

    def write_active_change(self, change_id: str, milestone: str | None) -> None:
        path = self.workspace / "delivery" / "active" / change_id / "change.md"
        path.parent.mkdir(parents=True)
        milestone_line = f"- Milestone: `{milestone}`\n" if milestone else ""
        path.write_text(
            f"# {change_id}: Test\n\n"
            "- Level: M\n"
            "- Status: IMPLEMENTING\n"
            f"{milestone_line}",
            encoding="utf-8",
        )
        # The active directory holds a pair: `change.md` is the plan, and
        # `checkpoint.md` is where progress is recorded.  A CHG that has only
        # the first is an active change nobody can resume.
        (path.parent / "checkpoint.md").write_text(
            f"# Checkpoint: {change_id}\n\nCompleted:\n- None.\n",
            encoding="utf-8",
        )

    def test_valid_active_change_has_no_errors(self) -> None:
        change_id = "CHG-20260722-021"
        milestone = "delivery/milestones/M2-account-runtime.md#m2-b"
        self.write_context(change_id)
        self.write_ledger(change_id)
        self.write_active_change(change_id, milestone)
        (self.workspace / "delivery" / "milestones" / "M2-account-runtime.md").write_text(
            "# M2\n\n## M2-B\n",
            encoding="utf-8",
        )

        errors = self.module.validate_delivery_governance(self.workspace)

        self.assertEqual(errors, [])

    def test_stale_context_and_missing_milestone_are_reported(self) -> None:
        self.write_context("CHG-20260715-010")
        self.write_ledger("CHG-20260721-020")
        self.write_active_change("CHG-20260721-020", milestone=None)

        errors = self.module.validate_delivery_governance(self.workspace)

        self.assertIn(
            "current context references missing CHG: CHG-20260715-010",
            errors,
        )
        self.assertIn(
            "active CHG has no milestone reference: CHG-20260721-020",
            errors,
        )

    def test_no_active_change_is_valid_when_context_and_ledger_are_empty(self) -> None:
        self.write_context("none")
        (self.workspace / "delivery" / "LEDGER.md").write_text(
            "# Delivery Ledger\n\nNo active M/L CHG.\n",
            encoding="utf-8",
        )

        errors = self.module.validate_delivery_governance(self.workspace)

        self.assertEqual(errors, [])

    def test_ledger_prose_mention_is_not_a_second_active_change(self) -> None:
        change_id = "CHG-20260722-021"
        milestone = "delivery/milestones/M2-account-runtime.md#m2-b"
        self.write_context(change_id)
        (self.workspace / "delivery" / "milestones" / "M2-account-runtime.md").write_text(
            "# M2\n\n## M2-B\n",
            encoding="utf-8",
        )
        self.write_active_change(change_id, milestone)
        (self.workspace / "delivery" / "LEDGER.md").write_text(
            "# Delivery Ledger\n\n"
            "| Change | Title | Status | Current Repository |\n"
            "|---|---|---|---|\n"
            f"| {change_id} | Test | IMPLEMENTING | wt-media-workspace |\n"
            "\nEarlier scope was folded into CHG-20260715-010, which is no longer active.\n",
            encoding="utf-8",
        )

        errors = self.module.validate_delivery_governance(self.workspace)

        self.assertEqual(errors, [])

    def test_active_change_without_checkpoint_is_reported(self) -> None:
        """An active CHG directory holds a pair; only half of it is an error.

        The check is turned off in the mutation control: with the check
        removed from the script, this test fails, which is what makes it
        evidence that the check exists rather than that the fixture is tidy.
        """
        change_id = "CHG-20260722-021"
        milestone = "delivery/milestones/M2-account-runtime.md#m2-b"
        self.write_context(change_id)
        self.write_ledger(change_id)
        self.write_active_change(change_id, milestone)
        (self.workspace / "delivery" / "milestones" / "M2-account-runtime.md").write_text(
            "# M2\n\n## M2-B\n",
            encoding="utf-8",
        )
        (self.workspace / "delivery" / "active" / change_id / "checkpoint.md").unlink()

        errors = self.module.validate_delivery_governance(self.workspace)

        self.assertEqual(errors, [f"active CHG is missing checkpoint.md: {change_id}"])

    # ----------------------------------------------------------------------
    # 归档边界（`delivery/completed/` 只读）
    # ----------------------------------------------------------------------
    # 两条判据都要**能失败**。用例断言的是完整错误集合，不是「存在某条错」：
    # 只断言「至少有一条」的用例，在判据退化成什么都报时依然是绿的。

    WRITER_SCRIPT = (
        "from pathlib import Path\n"
        "ROOT = Path(__file__).resolve().parents[1]\n"
        "ARCHIVE = ROOT / 'delivery' / 'completed'\n"
        "def save():\n"
        "    (ARCHIVE / 'note.md').parent.mkdir(parents=True, exist_ok=True)\n"
        "    (ARCHIVE / 'note.md').write_text('x', encoding='utf-8')\n"
    )

    def test_archive_write_from_script_is_reported(self) -> None:
        """`scripts/` 下的脚本写归档区 → 每一处写都报出。"""
        self.write_script("writer.py", self.WRITER_SCRIPT)

        errors = self.module.validate_delivery_governance(self.workspace)

        self.assertEqual(
            errors,
            [
                "archive readonly: scripts/writer.py:5 writes under "
                "delivery/completed/ ((ARCHIVE / 'note.md').parent)",
                "archive readonly: scripts/writer.py:6 writes under "
                "delivery/completed/ (ARCHIVE / 'note.md')",
            ],
        )

    def test_archive_reads_and_filter_literals_are_not_reported(self) -> None:
        """只读面与「只是提了一嘴归档路径」的字面量不得被报出。

        三种形态各一条，都是 T-03 实测踩过的：`read_text`（读）、
        `open('rb')`（读——方法形式的 mode 是第 0 个实参，按内建形式取第 1 个
        就会把它读成写）、以及 `own_artifacts` 那种只用来过滤的路径串
        （CHG-20260925-066 §14 第 11 项）。
        """
        self.write_script(
            "reader.py",
            "from pathlib import Path\n"
            "ROOT = Path(__file__).resolve().parents[1]\n"
            "ARCHIVE = ROOT / 'delivery' / 'completed'\n"
            "NEVER_UPLOAD = ('delivery/completed',)\n"
            "def load():\n"
            "    return (ARCHIVE / 'README.md').read_text(encoding='utf-8')\n"
            "def head():\n"
            "    with (ARCHIVE / 'README.md').open('rb') as handle:\n"
            "        return handle.read(1)\n"
            "def keep(path):\n"
            "    return path not in NEVER_UPLOAD\n",
        )

        errors = self.module.validate_delivery_governance(self.workspace)

        self.assertEqual(errors, [])

    def test_archive_boundary_marker_is_required(self) -> None:
        """`README.md` 在但机读键不在 → 报出（缺一个反引号也算不在）。"""
        self.write_archive_boundary(marker="- 归档边界：READ-ONLY\n")

        errors = self.module.validate_delivery_governance(self.workspace)

        self.assertEqual(
            errors,
            [
                "archive boundary: delivery/completed/README.md has no "
                "machine-readable boundary marker"
            ],
        )

    def test_archive_boundary_readme_is_required(self) -> None:
        (self.workspace / "delivery" / "completed" / "README.md").unlink()

        errors = self.module.validate_delivery_governance(self.workspace)

        self.assertEqual(
            errors, ["archive boundary: delivery/completed/README.md is missing"]
        )

    def test_missing_archive_is_reported(self) -> None:
        shutil.rmtree(self.workspace / "delivery" / "completed")

        errors = self.module.validate_delivery_governance(self.workspace)

        self.assertEqual(errors, ["archive boundary: delivery/completed/ is missing"])

    def test_archive_checks_report_their_denominators(self) -> None:
        """「0 命中」必须带分母，否则它和「什么都没扫」分不开。"""
        self.write_script("noop.py", "VALUE = 1\n")

        readonly_errors, readonly_summary = self.module.check_archive_readonly(
            self.workspace
        )
        boundary_errors, boundary_summary = self.module.check_completed_has_boundary(
            self.workspace
        )

        self.assertEqual(readonly_errors, [])
        self.assertEqual(
            readonly_summary,
            "archive readonly: scanned 1 script(s) under scripts/, "
            "0 write(s) reaching delivery/completed/",
        )
        self.assertEqual(boundary_errors, [])
        self.assertEqual(
            boundary_summary,
            "archive boundary: checked delivery/completed/README.md, "
            "1 boundary marker(s)",
        )


if __name__ == "__main__":
    unittest.main()
