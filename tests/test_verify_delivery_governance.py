from __future__ import annotations

import importlib.util
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
        self.module = load_module()

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
            f"| {change_id} | Test | IN_PROGRESS | wt-media-workspace |\n",
            encoding="utf-8",
        )

    def write_active_change(self, change_id: str, milestone: str | None) -> None:
        path = self.workspace / "delivery" / "active" / change_id / "change.md"
        path.parent.mkdir(parents=True)
        milestone_line = f"- Milestone: `{milestone}`\n" if milestone else ""
        path.write_text(
            f"# {change_id}: Test\n\n"
            "- Level: M\n"
            "- Status: IN_PROGRESS\n"
            f"{milestone_line}",
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
            f"| {change_id} | Test | IN_PROGRESS | wt-media-workspace |\n"
            "\nEarlier scope was folded into CHG-20260715-010, which is no longer active.\n",
            encoding="utf-8",
        )

        errors = self.module.validate_delivery_governance(self.workspace)

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
