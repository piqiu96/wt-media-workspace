from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "prepare_ai_workspace.py"
GOVERNANCE_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "verify_delivery_governance.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("prepare_ai_workspace", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load prepare_ai_workspace.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_governance_module():
    spec = importlib.util.spec_from_file_location(
        "verify_delivery_governance", GOVERNANCE_SCRIPT_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify_delivery_governance.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PrepareAiWorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.outer = Path(self.tmp.name) / "wt-media"
        self.workspace = self.outer / "wt-media-workspace"
        for name in (
            "wt-media-workspace",
            "wt-media-cloud",
            "wt-media-agent",
            "wt-media-desktop",
        ):
            (self.outer / name).mkdir(parents=True, exist_ok=True)

        skill = self.workspace / "skills" / "workspace" / "executing-wt-media-change" / "SKILL.md"
        skill.parent.mkdir(parents=True, exist_ok=True)
        skill.write_text(
            "---\n"
            "name: executing-wt-media-change\n"
            "description: test skill\n"
            "---\n\n"
            "# Test Skill\n",
            encoding="utf-8",
        )
        self.module = load_module()

    def write_change(self, change_id: str, status: str = "IMPLEMENTING") -> Path:
        path = self.workspace / "delivery" / "active" / change_id / "change.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# {change_id}: Test Change\n\n"
            "## 1. Basic Information\n\n"
            "- Level: M\n"
            f"- Status: {status}\n"
            "- Milestone: `delivery/milestones/M2-account-runtime.md`\n"
            "- Affected repositories:\n"
            "  - `wt-media-workspace`\n"
            "  - `outer execution root rule files`\n",
            encoding="utf-8",
        )
        return path

    def test_prepare_change_writes_context_and_execution_skill(self) -> None:
        self.write_change("CHG-20260714-002")

        summary = self.module.prepare_workspace(
            workspace_repo=self.workspace,
            change_id="CHG-20260714-002",
            write_context=True,
        )

        context = self.workspace / ".ai" / "CURRENT_CONTEXT.md"
        outer_context = self.outer / ".ai" / "CURRENT_CONTEXT.md"
        generated_skill = (
            self.outer
            / ".agents"
            / "skills"
            / "executing-wt-media-change"
            / "SKILL.md"
        )
        text = context.read_text(encoding="utf-8")
        self.assertEqual(summary["active_change"], "CHG-20260714-002")
        self.assertEqual(
            summary["active_milestone"], "delivery/milestones/M2-account-runtime.md"
        )
        self.assertTrue(context.is_file())
        self.assertTrue(generated_skill.is_file())
        # The id appears once, next to a title stripped of its own id prefix.
        self.assertIn("Active CHG: `CHG-20260714-002` — Test Change", text)
        self.assertNotIn("— CHG-20260714-002", text)
        self.assertIn(
            "- Current milestone: `delivery/milestones/M2-account-runtime.md`", text
        )
        self.assertIn("- `outer execution root rule files`", text)
        self.assertIn("GENERATED FILE", generated_skill.read_text(encoding="utf-8"))
        self.assertFalse(
            outer_context.exists(),
            "the execution snapshot must exist only inside the workspace repository",
        )

    def test_missing_change_fails(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.module.prepare_workspace(
                workspace_repo=self.workspace,
                change_id="CHG-20260714-999",
                write_context=False,
            )

    def test_no_active_change_renders_none_snapshot(self) -> None:
        """Closing the last CHG must stay a generated state, not a hand edit.

        The verifier already accepts `Active CHG: `none`` with an empty ledger
        (see test_verify_delivery_governance), so the generator has to be able
        to produce exactly that pair.
        """
        summary = self.module.prepare_workspace(
            workspace_repo=self.workspace,
            no_active=True,
            write_context=True,
        )

        text = (self.workspace / ".ai" / "CURRENT_CONTEXT.md").read_text(encoding="utf-8")
        self.assertIsNone(summary["active_change"])
        self.assertIn("- Active CHG: `none`", text)
        self.assertIn("- Status: `NONE`", text)
        self.assertNotIn("Current milestone:", text)
        self.assertNotIn("Change file:", text)
        self.assertIn(
            "- None",
            text,
            "an empty active set must still render the affected-repositories block",
        )

        ledger = self.workspace / "delivery" / "LEDGER.md"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text(
            "# Delivery Ledger\n\nNo active M/L CHG.\n",
            encoding="utf-8",
        )
        self.assertEqual(
            load_governance_module().validate_delivery_governance(self.workspace),
            [],
        )

    def test_no_active_refuses_while_a_change_is_still_active(self) -> None:
        self.write_change("CHG-20260714-002")

        with self.assertRaises(ValueError):
            self.module.prepare_workspace(
                workspace_repo=self.workspace,
                no_active=True,
                write_context=False,
            )

    def test_change_and_no_active_together_fail(self) -> None:
        self.write_change("CHG-20260714-002")

        with self.assertRaises(ValueError):
            self.module.prepare_workspace(
                workspace_repo=self.workspace,
                change_id="CHG-20260714-002",
                no_active=True,
                write_context=False,
            )

    def test_multiple_active_changes_fail(self) -> None:
        self.write_change("CHG-20260714-002")
        self.write_change("CHG-20260714-003")

        with self.assertRaises(ValueError):
            self.module.prepare_workspace(
                workspace_repo=self.workspace,
                change_id="CHG-20260714-002",
                write_context=False,
            )


if __name__ == "__main__":
    unittest.main()
