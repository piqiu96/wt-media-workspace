from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "verify_ai_workspace.py"
GOVERNANCE_SCRIPT = ROOT / "scripts" / "verify_delivery_governance.py"
CONFIG_SCRIPT = ROOT / "scripts" / "workspace_config.py"
CHANGE_ID = "CHG-20260722-021"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_ai_workspace", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify_ai_workspace.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class VerifyAIWorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.outer = Path(self.tmp.name) / "wt-media"
        self.workspace = self.outer / "wt-media-workspace"
        self.workspace.mkdir(parents=True)
        self.repos = {}
        for name in ("cloud", "agent", "desktop"):
            repo = self.outer / f"wt-media-{name}"
            repo.mkdir()
            self.repos[name] = repo
            for entry in ("AGENTS.md", "CLAUDE.md"):
                (repo / entry).write_text(
                    f"# {name} entry\n\n本仓规则见 AGENT-INDEX.md；目录见 DIRECTORY_MAP.md。\n",
                    encoding="utf-8",
                )
            (repo / "AGENT-INDEX.md").write_text(
                f"# {name} rules\n\n## 本仓职责\n\n按任务判断。\n",
                encoding="utf-8",
            )
            (repo / "DIRECTORY_MAP.md").write_text(
                f"# {name} map\n\n## 目录\n\n- `src/`\n",
                encoding="utf-8",
            )

        for entry in ("AGENTS.md", "CLAUDE.md"):
            (self.workspace / entry).write_text(
                "# Workspace entry\n\n规则见 AGENT-INDEX.md。\n",
                encoding="utf-8",
            )
        (self.workspace / "AGENT-INDEX.md").write_text(
            "# Workspace rules\n", encoding="utf-8"
        )
        (self.workspace / ".ai").mkdir()
        self.write_context(f"- Active CHG: `{CHANGE_ID}`\n")
        (self.workspace / "config").mkdir()
        (self.workspace / "config" / "repository-map.yaml").write_text(
            "repositories:\n"
            '  cloud:\n    path: "../wt-media-cloud"\n'
            '  agent:\n    path: "../wt-media-agent"\n'
            '  desktop:\n    path: "../wt-media-desktop"\n'
            '  workspace:\n    path: "../wt-media-workspace"\n',
            encoding="utf-8",
        )
        self.write_distribution(
            "targets:\n"
            '  cloud:\n    path: "../wt-media-cloud"\n    groups:\n      - common\n'
            '  agent:\n    path: "../wt-media-agent"\n    groups:\n      - common\n'
            '  desktop:\n    path: "../wt-media-desktop"\n    groups:\n      - common\n'
            '  workspace:\n    path: "../wt-media-workspace"\n    groups:\n      - common\n'
        )
        (self.workspace / "skills" / "common").mkdir(parents=True)
        (self.workspace / "delivery" / "active" / CHANGE_ID).mkdir(parents=True)
        (self.workspace / "delivery" / "active" / CHANGE_ID / "change.md").write_text(
            f"# {CHANGE_ID}: Test\n\n- Status: ACTIVE\n", encoding="utf-8"
        )
        self.write_ledger(CHANGE_ID)
        (self.workspace / "scripts").mkdir()
        for script in (GOVERNANCE_SCRIPT, CONFIG_SCRIPT):
            shutil.copy(script, self.workspace / "scripts" / script.name)
        self.module = load_module()
        self.module.ROOT = self.workspace
        self.module.EXECUTION_ROOT = self.outer

    def write_context(self, body: str) -> None:
        (self.workspace / ".ai" / "CURRENT_CONTEXT.md").write_text(
            f"# WT Media Current AI Context\n\n{body}", encoding="utf-8"
        )

    def write_distribution(self, body: str) -> None:
        (self.workspace / "config" / "skills-distribution.yaml").write_text(
            body, encoding="utf-8"
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
        return self.module.validate_ai_workspace()[0]

    def warnings(self) -> list[str]:
        return self.module.validate_ai_workspace()[1]

    def test_valid_layout(self) -> None:
        self.assertEqual(self.errors(), [])
        self.assertEqual(self.warnings(), [])

    def test_rich_entries_and_different_index_sections_are_allowed(self) -> None:
        with (self.repos["cloud"] / "AGENTS.md").open("a", encoding="utf-8") as handle:
            handle.write("## 项目定位\n\n业务状态归 Cloud。\n" * 30)
        (self.repos["agent"] / "AGENT-INDEX.md").write_text(
            "# Agent rules\n\n## 与 Cloud 协作\n\n按任务判断。\n", encoding="utf-8"
        )
        self.assertEqual(self.errors(), [])

    def test_missing_and_empty_entry_files_are_errors(self) -> None:
        (self.workspace / "CLAUDE.md").unlink()
        (self.repos["agent"] / "AGENTS.md").write_text("", encoding="utf-8")
        errors = self.errors()
        self.assertIn("missing agent entry file: wt-media-workspace/CLAUDE.md", errors)
        self.assertIn("agent: empty agent entry file: AGENTS.md", errors)

    def test_entry_must_reference_local_index_and_map(self) -> None:
        (self.repos["cloud"] / "CLAUDE.md").write_text(
            "# Cloud entry\n\nOnly AGENT-INDEX.md is named.\n", encoding="utf-8"
        )
        self.assertIn(
            "cloud: CLAUDE.md does not reference DIRECTORY_MAP.md", self.errors()
        )

        (self.repos["cloud"] / "CLAUDE.md").write_text(
            "# Cloud entry\n\nOnly DIRECTORY_MAP.md is named.\n", encoding="utf-8"
        )
        self.assertIn(
            "cloud: CLAUDE.md does not reference AGENT-INDEX.md", self.errors()
        )

    def test_peer_entry_cannot_be_a_symlink(self) -> None:
        target = self.repos["desktop"] / "CLAUDE.md"
        target.unlink()
        target.symlink_to("AGENTS.md")
        self.assertIn(
            "desktop: CLAUDE.md must be an independent entry file", self.errors()
        )

    def test_hardcoded_sibling_path_is_an_error(self) -> None:
        with (self.repos["agent"] / "AGENTS.md").open("a", encoding="utf-8") as handle:
            handle.write("\n位置：`../wt-media-cloud`。\n")
        self.assertIn(
            "agent: AGENTS.md hardcodes a sibling repository path; use the workspace repository map",
            self.errors(),
        )

    def test_absent_runtime_repo_is_a_warning(self) -> None:
        shutil.rmtree(self.repos["desktop"])
        self.assertEqual(self.errors(), [])
        self.assertIn(
            "desktop: repository not present at ../wt-media-desktop, entry files not checked",
            self.warnings(),
        )

    def test_duplicate_snapshot_is_an_error(self) -> None:
        (self.outer / ".ai").mkdir()
        (self.outer / ".ai" / "CURRENT_CONTEXT.md").write_text("# duplicate\n")
        self.assertTrue(any("duplicate execution snapshot" in error for error in self.errors()))

    def test_oversized_snapshot_is_an_error(self) -> None:
        self.module.CONTEXT_CHAR_BUDGET = 10
        self.assertTrue(any("execution snapshot exceeds budget" in error for error in self.errors()))

    def test_snapshot_and_ledger_disagreement_is_an_error(self) -> None:
        self.write_ledger("CHG-20260722-999")
        self.assertTrue(any("execution snapshot and LEDGER disagree" in error for error in self.errors()))

    def test_repository_and_skill_target_paths_must_agree(self) -> None:
        body = (self.workspace / "config" / "skills-distribution.yaml").read_text()
        self.write_distribution(body.replace("../wt-media-cloud", "../wt-media-cloud-web"))
        self.assertTrue(any("repository 'cloud' path disagrees" in error for error in self.errors()))

    def test_repository_target_must_exist_in_distribution(self) -> None:
        body = (self.workspace / "config" / "skills-distribution.yaml").read_text()
        body = body.replace(
            '  cloud:\n    path: "../wt-media-cloud"\n    groups:\n      - common\n', ""
        )
        self.write_distribution(body)
        self.assertTrue(any("repository 'cloud' is missing" in error for error in self.errors()))

    def test_distribution_repository_target_must_exist_in_map(self) -> None:
        body = (self.workspace / "config" / "skills-distribution.yaml").read_text()
        body += '  cloud-web:\n    path: "../wt-media-cloud-web"\n    groups:\n      - common\n'
        self.write_distribution(body)
        self.assertTrue(any("target 'cloud-web' is kind: repository" in error for error in self.errors()))

    def test_all_skill_groups_must_be_claimed(self) -> None:
        (self.workspace / "skills" / "desktop").mkdir()
        self.assertTrue(any("skill group 'skills/desktop' is not claimed" in error for error in self.errors()))

    def test_claimed_skill_group_must_exist(self) -> None:
        body = (self.workspace / "config" / "skills-distribution.yaml").read_text()
        self.write_distribution(body.replace("      - common", "      - missing", 1))
        self.assertTrue(any("targets claim a missing skill group" in error for error in self.errors()))

    def test_malformed_distribution_is_reported(self) -> None:
        self.write_distribution('targets:\n  cloud: ["../wt-media-cloud"]\n')
        self.assertTrue(any("skills-distribution.yaml:2:" in error for error in self.errors()))

    def test_config_reader_comes_from_workspace_under_test(self) -> None:
        config = self.module.load_workspace_config()
        self.assertEqual(Path(config.__file__), self.workspace / "scripts" / "workspace_config.py")


if __name__ == "__main__":
    unittest.main()
