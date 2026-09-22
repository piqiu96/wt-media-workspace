from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "verify_agent_entry.py"
GOVERNANCE_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "verify_delivery_governance.py"
)
CHANGE_ID = "CHG-20260722-021"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_agent_entry", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify_agent_entry.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class VerifyAgentEntryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.outer = Path(self.tmp.name) / "wt-media"
        self.workspace = self.outer / "wt-media-workspace"
        self.cloud = self.outer / "wt-media-cloud"

        self.workspace.mkdir(parents=True)
        (self.cloud).mkdir()
        for name in ("AGENTS.md", "CLAUDE.md", "AGENT-INDEX.md"):
            (self.workspace / name).write_text(f"# {name}\n", encoding="utf-8")
            (self.cloud / name).write_text(f"# cloud {name}\n", encoding="utf-8")
        (self.workspace / ".ai").mkdir()
        self.write_context(f"- Active CHG: `{CHANGE_ID}`\n")
        (self.workspace / "config").mkdir()
        (self.workspace / "config" / "repository-map.yaml").write_text(
            "repositories:\n  cloud:\n    path: ../wt-media-cloud\n", encoding="utf-8"
        )
        (self.workspace / "config" / "skills-distribution.yaml").write_text(
            'targets:\n  cloud:\n    path: "../wt-media-cloud"\n', encoding="utf-8"
        )
        (self.workspace / "delivery").mkdir()
        self.write_ledger(CHANGE_ID)
        change = self.workspace / "delivery" / "active" / CHANGE_ID / "change.md"
        change.parent.mkdir(parents=True)
        change.write_text(f"# {CHANGE_ID}: Test\n\n- Status: ACTIVE\n", encoding="utf-8")
        (self.workspace / "scripts").mkdir()
        shutil.copy(GOVERNANCE_SCRIPT, self.workspace / "scripts" / GOVERNANCE_SCRIPT.name)

        self.module = load_module()
        self.module.ROOT = self.workspace
        self.module.EXECUTION_ROOT = self.outer

    def write_context(self, body: str) -> None:
        (self.workspace / ".ai" / "CURRENT_CONTEXT.md").write_text(
            f"# WT Media Current AI Context\n\n{body}", encoding="utf-8"
        )

    def write_ledger(self, change_id: str) -> None:
        (self.workspace / "delivery" / "LEDGER.md").write_text(
            "# Delivery Ledger\n\n"
            "| Change | Title | Status | Current Repository |\n"
            "|---|---|---|---|\n"
            f"| {change_id} | Test | ACTIVE | wt-media-workspace |\n",
            encoding="utf-8",
        )

    def errors(self) -> list[str]:
        errors, _, _ = self.module.validate_agent_entry()
        return errors

    def warnings(self) -> list[str]:
        _, warnings, _ = self.module.validate_agent_entry()
        return warnings

    def test_valid_layout_has_no_errors(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_duplicate_snapshot_outside_workspace_is_an_error(self) -> None:
        (self.outer / ".ai").mkdir()
        (self.outer / ".ai" / "CURRENT_CONTEXT.md").write_text(
            "# stale\n", encoding="utf-8"
        )

        errors = self.errors()

        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate execution snapshot", errors[0])

    def test_missing_entry_file_is_an_error(self) -> None:
        (self.workspace / "CLAUDE.md").unlink()

        errors = self.errors()

        self.assertIn(
            "missing agent entry file: wt-media-workspace/CLAUDE.md", errors
        )

    def test_oversized_snapshot_is_an_error(self) -> None:
        self.module.CONTEXT_CHAR_BUDGET = 10

        errors = self.errors()

        self.assertIn(
            "execution snapshot exceeds budget: "
            f"{len((self.workspace / '.ai' / 'CURRENT_CONTEXT.md').read_text(encoding='utf-8'))} characters",
            errors,
        )

    def test_snapshot_and_ledger_disagreement_is_an_error(self) -> None:
        self.write_ledger("CHG-20260722-999")

        errors = self.errors()

        self.assertIn(
            f"execution snapshot and LEDGER disagree: {CHANGE_ID} != CHG-20260722-999",
            errors,
        )
        self.assertIn("LEDGER references missing active CHG: CHG-20260722-999", errors)

    def test_config_path_disagreement_is_an_error(self) -> None:
        (self.workspace / "config" / "skills-distribution.yaml").write_text(
            'targets:\n  cloud:\n    path: "../wt-media-cloud-web"\n', encoding="utf-8"
        )

        errors = self.errors()

        self.assertIn(
            "repository 'cloud' path disagrees: "
            "repository-map '../wt-media-cloud' != skills-distribution '../wt-media-cloud-web'",
            errors,
        )

    def test_config_without_matching_target_is_an_error(self) -> None:
        (self.workspace / "config" / "skills-distribution.yaml").write_text(
            "targets:\n  workspace:\n    path: '.'\n", encoding="utf-8"
        )

        errors = self.errors()

        self.assertIn(
            "repository 'cloud' is missing from config/skills-distribution.yaml targets",
            errors,
        )

    def test_forbidden_path_described_in_claude_md_is_warned(self) -> None:
        (self.cloud / "AGENTS.md").write_text(
            "- 不创建 `internal/runtime`。\n", encoding="utf-8"
        )
        (self.cloud / "CLAUDE.md").write_text(
            "## internal/runtime\n\n- resources live here.\n", encoding="utf-8"
        )

        warnings = self.warnings()

        self.assertIn(
            "cloud: AGENTS.md forbids `internal/runtime` but CLAUDE.md mentions it "
            "outside a forbidding sentence - review both files",
            warnings,
        )

    def test_path_forbidden_in_both_files_is_not_warned(self) -> None:
        (self.cloud / "AGENTS.md").write_text(
            "- 不创建 `internal/runtime`。\n", encoding="utf-8"
        )
        (self.cloud / "CLAUDE.md").write_text(
            "- 不创建 `internal/runtime`。\n", encoding="utf-8"
        )

        warnings = self.warnings()

        self.assertEqual([w for w in warnings if "internal/runtime" in w], [])

    def test_missing_layer3_entry_is_warned(self) -> None:
        (self.cloud / "AGENT-INDEX.md").unlink()

        warnings = self.warnings()

        self.assertIn(
            "cloud: no AGENT-INDEX.md (AGENT-INDEX.md Layer 3 is unresolved)", warnings
        )

    def test_parse_path_map_handles_quoted_and_bare_paths(self) -> None:
        text = (
            "schema_version: 1\n"
            "\n"
            "targets:\n"
            "  root:\n"
            '    path: ".."\n'
            "    commit_generated: false\n"
            "  cloud:\n"
            "    path: ../wt-media-cloud\n"
        )

        self.assertEqual(
            self.module.parse_path_map(text, "targets"),
            {"root": "..", "cloud": "../wt-media-cloud"},
        )


if __name__ == "__main__":
    unittest.main()
