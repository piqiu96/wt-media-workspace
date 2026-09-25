from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "verify_agent_entry.py"
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
GOVERNANCE_SCRIPT = SCRIPTS_DIR / "verify_delivery_governance.py"
CONFIG_SCRIPT = SCRIPTS_DIR / "agent_config.py"
CHANGE_ID = "CHG-20260722-021"

RUNNING_REPOS = ("cloud", "agent", "desktop")
ORDER_SECTIONS = (
    "依赖",
    "定位",
    "本仓库拥有",
    "本仓库不拥有",
    "需求路由",
    "本仓规则",
    "禁止",
    "本仓内加载顺序",
)
POINTER_TEMPLATE = (
    "# {repo} entry\n"
    "\n"
    "- 正文：`AGENT-INDEX.md`\n"
    "\n"
    "## 权威源\n"
    "\n"
    "本仓规则与路由的唯一落点是 [`AGENT-INDEX.md`](AGENT-INDEX.md)。本文件只做指针。\n"
)
BODY_TEMPLATE = "# {repo} Agent Index\n\n" + "".join(
    f"## {section}\n\n- 内容。\n\n" for section in ORDER_SECTIONS
)
DIRECTORY_TEMPLATE = (
    "# {repo} Directory Map\n"
    "\n"
    "> 目录事实与禁止扫描区的唯一落点。\n"
    "\n"
    "## 目录\n"
    "\n"
    "- `src/`\n"
    "\n"
    "## 禁止扫描区\n"
    "\n"
    "（暂无。）\n"
)


def load_module():
    spec = importlib.util.spec_from_file_location("verify_agent_entry", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify_agent_entry.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_pointer(repo: Path, filename: str, repo_name: str, **fields: str) -> None:
    body = POINTER_TEMPLATE.format(repo=repo_name)
    for old, new in fields.items():
        body = body.replace(old, new)
    (repo / filename).write_text(body, encoding="utf-8")


class VerifyAgentEntryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.outer = Path(self.tmp.name) / "wt-media"
        self.workspace = self.outer / "wt-media-workspace"
        self.repos = {name: self.outer / f"wt-media-{name}" for name in RUNNING_REPOS}

        self.workspace.mkdir(parents=True)
        # The fixture is conforming by default: every entry-shape assertion below
        # is then a statement about the one thing the test changed.
        for name in ("AGENTS.md", "CLAUDE.md"):
            write_pointer(self.workspace, name, "workspace")
        (self.workspace / "AGENT-INDEX.md").write_text(
            "# WT Media Agent Index\n\n治理规范正文。\n", encoding="utf-8"
        )
        for name, repo in self.repos.items():
            repo.mkdir()
            for filename in ("AGENTS.md", "CLAUDE.md"):
                write_pointer(repo, filename, name)
            (repo / "AGENT-INDEX.md").write_text(
                BODY_TEMPLATE.format(repo=name), encoding="utf-8"
            )
            (repo / "DIRECTORY_MAP.md").write_text(
                DIRECTORY_TEMPLATE.format(repo=name), encoding="utf-8"
            )

        (self.workspace / ".ai").mkdir()
        self.write_context(f"- Active CHG: `{CHANGE_ID}`\n")
        (self.workspace / "config").mkdir()
        (self.workspace / "config" / "repository-map.yaml").write_text(
            "repositories:\n"
            '  cloud:\n    path: "../wt-media-cloud"\n'
            '  agent:\n    path: "../wt-media-agent"\n'
            '  desktop:\n    path: "../wt-media-desktop"\n',
            encoding="utf-8",
        )
        self.write_distribution(
            "targets:\n"
            '  cloud:\n    path: "../wt-media-cloud"\n    groups:\n      - common\n'
            '  agent:\n    path: "../wt-media-agent"\n    groups:\n      - common\n'
            '  desktop:\n    path: "../wt-media-desktop"\n    groups:\n      - common\n'
        )
        (self.workspace / "skills" / "common").mkdir(parents=True)
        (self.workspace / "delivery").mkdir()
        self.write_ledger(CHANGE_ID)
        change = self.workspace / "delivery" / "active" / CHANGE_ID / "change.md"
        change.parent.mkdir(parents=True)
        change.write_text(f"# {CHANGE_ID}: Test\n\n- Status: ACTIVE\n", encoding="utf-8")
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

    def write_distribution(self, text: str) -> None:
        (self.workspace / "config" / "skills-distribution.yaml").write_text(
            text, encoding="utf-8"
        )

    def write_ledger(self, change_id: str) -> None:
        (self.workspace / "delivery" / "LEDGER.md").write_text(
            "# Delivery Ledger\n\n"
            "| Change | Title | Status | Current Repository |\n"
            "|---|---|---|---|\n"
            f"| {change_id} | Test | ACTIVE | wt-media-workspace |\n",
            encoding="utf-8",
        )

    def results(self) -> tuple[list[str], list[str], list[str]]:
        return self.module.validate_agent_entry()

    def errors(self) -> list[str]:
        return self.results()[0]

    def warnings(self) -> list[str]:
        return self.results()[1]

    def notes(self) -> list[str]:
        return self.results()[2]

    def duplication_note(self) -> str:
        return next(note for note in self.notes() if note.startswith("rule-text"))

    # --- baseline -----------------------------------------------------------

    def test_valid_layout_has_no_errors(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_valid_layout_has_no_warnings(self) -> None:
        self.assertEqual(self.warnings(), [])

    def test_duplication_denominator_is_reported(self) -> None:
        """A zero from the duplication check must come with what it compared."""
        note = self.duplication_note()

        self.assertIn("compared 3 rule sentence(s)", note)
        self.assertIn("across 6 file(s) in 3 repositories", note)

    # --- snapshot and ledger ------------------------------------------------

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

        self.assertIn(
            "missing agent entry file: wt-media-workspace/CLAUDE.md", self.errors()
        )

    def test_oversized_snapshot_is_an_error(self) -> None:
        self.module.CONTEXT_CHAR_BUDGET = 10

        self.assertIn(
            "execution snapshot exceeds budget: "
            f"{len((self.workspace / '.ai' / 'CURRENT_CONTEXT.md').read_text(encoding='utf-8'))} characters",
            self.errors(),
        )

    def test_snapshot_and_ledger_disagreement_is_an_error(self) -> None:
        self.write_ledger("CHG-20260722-999")

        errors = self.errors()

        self.assertIn(
            f"execution snapshot and LEDGER disagree: {CHANGE_ID} != CHG-20260722-999",
            errors,
        )
        self.assertIn("LEDGER references missing active CHG: CHG-20260722-999", errors)

    # --- configuration agreement -------------------------------------------

    def test_config_path_disagreement_is_an_error(self) -> None:
        self.write_distribution(
            'targets:\n  cloud:\n    path: "../wt-media-cloud-web"\n    groups:\n      - common\n'
        )

        self.assertIn(
            "repository 'cloud' path disagrees: "
            "repository-map '../wt-media-cloud' != skills-distribution '../wt-media-cloud-web'",
            self.errors(),
        )

    def test_config_without_matching_target_is_an_error(self) -> None:
        self.write_distribution(
            'targets:\n  workspace:\n    path: ".."\n    groups:\n      - common\n'
        )

        errors = self.errors()

        self.assertIn(
            "repository 'cloud' is missing from config/skills-distribution.yaml targets",
            errors,
        )
        self.assertIn(
            "repository 'agent' is missing from config/skills-distribution.yaml targets",
            errors,
        )

    def test_repository_kind_target_missing_from_map_is_an_error(self) -> None:
        self.write_distribution(
            "targets:\n"
            "  cloud:\n"
            '    path: "../wt-media-cloud"\n'
            "    groups:\n"
            "      - common\n"
            "  cloud-web:\n"
            '    path: "../wt-media-cloud-web"\n'
            "    groups:\n"
            "      - common\n"
        )

        self.assertIn(
            "target 'cloud-web' is kind: repository but is missing from "
            "config/repository-map.yaml",
            self.errors(),
        )

    def test_distribution_kind_target_is_exempt_from_the_repository_map(self) -> None:
        self.write_distribution(
            "targets:\n"
            '  root:\n'
            '    path: ".."\n'
            "    kind: distribution\n"
            "    groups:\n"
            "      - common\n"
            "  cloud:\n"
            '    path: "../wt-media-cloud"\n'
            "    groups:\n"
            "      - common\n"
            "  agent:\n"
            '    path: "../wt-media-agent"\n'
            "    groups:\n"
            "      - common\n"
            "  desktop:\n"
            '    path: "../wt-media-desktop"\n'
            "    groups:\n"
            "      - common\n"
        )

        self.assertEqual([error for error in self.errors() if "root" in error], [])

    def test_unclaimed_skill_group_is_an_error(self) -> None:
        (self.workspace / "skills" / "desktop").mkdir()

        self.assertIn(
            "skill group 'skills/desktop' is not claimed by any distribution target",
            self.errors(),
        )

    def test_target_claiming_a_missing_group_is_an_error(self) -> None:
        self.write_distribution(
            'targets:\n  cloud:\n    path: "../wt-media-cloud"\n    groups:\n      - desktop\n'
        )

        self.assertIn(
            "distribution targets claim a missing skill group: skills/desktop",
            self.errors(),
        )

    def test_malformed_config_is_reported_as_an_error(self) -> None:
        self.write_distribution('targets:\n  cloud: ["../wt-media-cloud"]\n')

        errors = self.errors()

        self.assertEqual(len(errors), 1)
        self.assertIn("skills-distribution.yaml:2:", errors[0])

    # --- running repository entry files ------------------------------------

    def test_missing_running_repo_entry_file_is_an_error(self) -> None:
        (self.repos["cloud"] / "DIRECTORY_MAP.md").unlink()

        self.assertEqual(
            self.errors(),
            ["cloud: missing agent entry file: DIRECTORY_MAP.md"],
        )

    def test_empty_running_repo_entry_file_is_an_error(self) -> None:
        (self.repos["agent"] / "AGENTS.md").write_text("", encoding="utf-8")

        # Emptying a pointer breaks it twice over: the file is empty, and the
        # declaration it carries is gone with it. Both must be reported, or
        # fixing the first would silently leave the second.
        self.assertEqual(
            self.errors(),
            [
                "agent: empty agent entry file: AGENTS.md",
                "agent: AGENTS.md declares no rule body: expected `- 正文：`<file>``",
            ],
        )

    def test_absent_repository_is_warned_and_not_errored(self) -> None:
        """A checkout without the siblings must not fail the whole gate."""
        shutil.rmtree(self.repos["desktop"])

        self.assertEqual(self.errors(), [])
        self.assertIn(
            "desktop: repository not present at ../wt-media-desktop, "
            "entry files not checked",
            self.warnings(),
        )

    # --- pointer shape ------------------------------------------------------

    def test_pointer_without_machine_key_is_an_error(self) -> None:
        (self.repos["cloud"] / "CLAUDE.md").write_text(
            "# cloud entry\n\n## 权威源\n\n规则见 [`AGENT-INDEX.md`](AGENT-INDEX.md)。\n",
            encoding="utf-8",
        )

        self.assertEqual(
            self.errors(),
            ["cloud: CLAUDE.md declares no rule body: expected `- 正文：`<file>``"],
        )

    def test_pointer_key_pointing_nowhere_is_an_error(self) -> None:
        write_pointer(
            self.repos["cloud"], "CLAUDE.md", "cloud",
            **{"- 正文：`AGENT-INDEX.md`": "- 正文：`RULES.md`"},
        )
        with (self.repos["cloud"] / "CLAUDE.md").open("a", encoding="utf-8") as handle:
            handle.write("\n- 不创建 `internal/runtime`。\n")

        # The rule line must be judged against the body this file actually
        # declares, not against the one it was supposed to declare: the
        # declaration is what a session would follow.
        self.assertEqual(
            self.errors(),
            [
                "cloud: CLAUDE.md declares an unknown rule body: RULES.md",
                "cloud: CLAUDE.md:9 restates a rule without naming RULES.md: "
                "- 不创建 `internal/runtime`。",
                "cloud: pointer files disagree on the rule body: "
                "AGENTS.md -> AGENT-INDEX.md, CLAUDE.md -> RULES.md",
            ],
        )

    def test_pointer_declaring_itself_is_an_error(self) -> None:
        write_pointer(
            self.repos["agent"], "AGENTS.md", "agent",
            **{"- 正文：`AGENT-INDEX.md`": "- 正文：`AGENTS.md`"},
        )

        self.assertEqual(
            self.errors(),
            [
                "agent: AGENTS.md declares itself as the rule body",
                "agent: pointer files disagree on the rule body: "
                "AGENTS.md -> AGENTS.md, CLAUDE.md -> AGENT-INDEX.md",
                "agent: AGENTS.md declares a pointer as the rule body (AGENTS.md); "
                "the body must not itself be a pointer",
            ],
        )

    def test_pointer_restating_a_rule_is_an_error(self) -> None:
        with (self.repos["cloud"] / "CLAUDE.md").open("a", encoding="utf-8") as handle:
            handle.write("\n- 不创建 `internal/runtime`。\n")

        self.assertEqual(
            self.errors(),
            [
                "cloud: CLAUDE.md:9 restates a rule without naming AGENT-INDEX.md: "
                "- 不创建 `internal/runtime`。"
            ],
        )

    def test_pointer_over_line_budget_is_an_error(self) -> None:
        with (self.repos["cloud"] / "CLAUDE.md").open("a", encoding="utf-8") as handle:
            handle.write(
                "".join(
                    f"- 补充说明 {index}，细节见 `AGENT-INDEX.md`。\n"
                    for index in range(30)
                )
            )

        errors = self.errors()

        self.assertEqual(len(errors), 1)
        self.assertIn("cloud: CLAUDE.md exceeds the pointer budget (lines)", errors[0])
        self.assertIn("37 lines", errors[0])

    def test_pointer_over_heading_budget_is_an_error(self) -> None:
        with (self.repos["desktop"] / "AGENTS.md").open("a", encoding="utf-8") as handle:
            handle.write("".join(f"## 章节 {index}\n\n- 见 `AGENT-INDEX.md`。\n" for index in range(5)))

        errors = self.errors()

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "desktop: AGENTS.md exceeds the pointer budget (H2 headings)", errors[0]
        )
        self.assertIn("6 H2 headings", errors[0])

    def test_pointers_disagreeing_on_the_body_is_an_error(self) -> None:
        write_pointer(
            self.repos["cloud"], "AGENTS.md", "cloud",
            **{"- 正文：`AGENT-INDEX.md`": "- 正文：`AGENTS.md`"},
        )

        errors = self.errors()

        self.assertIn(
            "cloud: pointer files disagree on the rule body: "
            "AGENTS.md -> AGENTS.md, CLAUDE.md -> AGENT-INDEX.md",
            errors,
        )
        self.assertIn(
            "cloud: AGENTS.md declares a pointer as the rule body (AGENTS.md); "
            "the body must not itself be a pointer",
            errors,
        )

    def test_pointer_chain_through_the_body_is_an_error(self) -> None:
        """A body that declares a body is a chain, not a body."""
        (self.repos["agent"] / "AGENT-INDEX.md").write_text(
            "# agent Agent Index\n\n"
            + "".join(f"## {section}\n\n- 内容。\n\n" for section in ORDER_SECTIONS)
            + "- 正文：`CLAUDE.md`\n",
            encoding="utf-8",
        )

        self.assertEqual(
            self.errors(),
            [
                "agent: AGENT-INDEX.md is declared as the rule body but declares one "
                "itself; the chain must end at the body"
            ],
        )

    # --- layer 3 shape ------------------------------------------------------

    def test_layer3_section_count_is_an_error(self) -> None:
        (self.repos["desktop"] / "AGENT-INDEX.md").write_text(
            "# desktop Agent Index\n\n"
            + "".join(f"## {section}\n\n- 内容。\n\n" for section in ORDER_SECTIONS[:-1]),
            encoding="utf-8",
        )

        errors = self.errors()

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "desktop: AGENT-INDEX.md has 7 H2 sections, expected 8", errors[0]
        )

    def test_layer3_sequence_divergence_is_an_error(self) -> None:
        (self.repos["agent"] / "AGENT-INDEX.md").write_text(
            "# agent Agent Index\n\n"
            + "".join(
                f"## {'其他' if section == '禁止' else section}\n\n- 内容。\n\n"
                for section in ORDER_SECTIONS
            ),
            encoding="utf-8",
        )

        errors = self.errors()

        # Repositories are compared in name order, so the reference is `agent`
        # and the stale sequence is the one that now reads wrong.
        self.assertEqual(
            errors,
            [
                "cloud: AGENT-INDEX.md H2 sequence diverges from agent at position 7: "
                "'禁止' != '其他'"
            ],
        )

    # --- WARN heuristics ----------------------------------------------------

    def test_duplicated_rule_sentence_is_warned(self) -> None:
        (self.repos["agent"] / "AGENT-INDEX.md").write_text(
            BODY_TEMPLATE.format(repo="agent").replace(
                "- 内容。\n", "- 不得直连 Cloud 数据库。\n", 1
            ),
            encoding="utf-8",
        )
        (self.repos["agent"] / "README.md").write_text(
            "# agent\n\n- 不得直连 Cloud 数据库。\n", encoding="utf-8"
        )

        warnings = self.warnings()

        self.assertEqual(
            warnings,
            [
                "agent: rule sentence repeated in AGENT-INDEX.md, README.md: "
                "- 不得直连 Cloud 数据库。"
            ],
        )
        self.assertIn("compared 5 rule sentence(s)", self.duplication_note())

    def test_pointer_lines_are_excluded_from_duplication(self) -> None:
        """Both pointers name the body on every rule-ish line; that overlap is by design."""
        self.assertEqual(
            [warning for warning in self.warnings() if "repeated in" in warning], []
        )

    def test_local_order_section_leaking_the_project_order_is_warned(self) -> None:
        body = (self.repos["desktop"] / "AGENT-INDEX.md").read_text(encoding="utf-8")
        (self.repos["desktop"] / "AGENT-INDEX.md").write_text(
            body.replace(
                "## 本仓内加载顺序\n\n- 内容。\n",
                "## 本仓内加载顺序\n\n- 先读 `.ai/CURRENT_CONTEXT.md`。\n",
            ),
            encoding="utf-8",
        )

        warnings = self.warnings()

        self.assertEqual(
            warnings,
            [
                "desktop: AGENT-INDEX.md section '本仓内加载顺序' names "
                "`CURRENT_CONTEXT` - the project-level order belongs to the workspace"
            ],
        )

    # --- loader -------------------------------------------------------------

    def test_config_reader_is_loaded_from_the_workspace_tree(self) -> None:
        """The reader must come from the tree under test, not the caller's path."""
        config = self.module.load_agent_config()

        self.assertEqual(
            Path(config.__file__), self.workspace / "scripts" / "agent_config.py"
        )


if __name__ == "__main__":
    unittest.main()
