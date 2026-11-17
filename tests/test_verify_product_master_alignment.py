from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "verify" / "verify_product_master_alignment.py"
MASTER_PATH = ROOT / "delivery" / "MASTER_IMPLEMENTATION_PLAN.md"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_product_master_alignment", SCRIPT_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify_product_master_alignment.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ProductMasterAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.module = load_module()
        self.master = MASTER_PATH.read_text(encoding="utf-8")

    def mutate(self, old: str, new: str) -> str:
        """Return the Master Plan with one occurrence of `old` replaced by `new`.

        Existence is asserted first on purpose. A `str.replace` whose target is
        absent is a silent no-op that leaves the text byte-identical, and an
        assertion shaped "some error mentions label X" is then free to be
        satisfied by errors the UNMUTATED run already produces. That is exactly
        how this file's M3 forbidden-object test used to pass while the
        judgement under test was deliberately never reached (CHG-20260925-063
        §4.4). The `assertNotEqual` also covers the degenerate case where `old`
        is the empty string, which is `in` every string.
        """
        self.assertIn(old, self.master, f"mutation target absent from Master Plan: {old!r}")
        changed = self.master.replace(old, new, 1)
        self.assertNotEqual(changed, self.master, "mutation was a no-op")
        return changed

    def assert_errors(self, changed: str, expected: list[str]) -> None:
        """Assert the FULL error set rather than the presence of a label.

        Matching on a label alone lets any other error of the same family
        satisfy the assertion, so a test written that way stays green while the
        judgement it names is broken.
        """
        errors = self.module.validate_master_text(changed)
        self.assertEqual(sorted(errors), sorted(expected), errors)

    def test_current_product_master_and_governance_are_aligned(self) -> None:
        self.assertEqual(self.module.validate_alignment(ROOT), [])

    def test_done_milestones_need_no_candidate_block(self) -> None:
        """D-04: a closed milestone is asserted on its status word.

        M2 and M3 are DONE and retired their candidate blocks at closure, so
        these two facts must both hold: the blocks are gone, and a clean run is
        still clean. Asserting it here keeps someone from "restoring" a
        candidate-block requirement onto closed milestones.
        """
        sections = self.module.milestone_sections(self.master)
        for number in (2, 3):
            with self.subTest(milestone=number):
                self.assertEqual(self.module.candidate_block(sections[number]), "")
        self.assertEqual(self.module.validate_master_text(self.master), [])

    def test_rejects_reopened_milestone_status_regression(self) -> None:
        changed = self.mutate("| 状态 | `DONE` |", "| 状态 | `VERIFYING` |")

        # The first plain status row is M0's. Exactly one error: M0 keeps its
        # candidate block, so the missing-block check has nothing to add here.
        self.assert_errors(changed, ["M0 status expected 'DONE', got 'VERIFYING'"])

    def test_accepts_approved_browser_assisted_auto_submit_terminology(self) -> None:
        self.assert_errors(
            self.mutate("浏览器自动提交是必须能力", "浏览器辅助发布（自动提交）中浏览器自动提交是必须能力"),
            [],
        )

    def test_rejects_manual_final_submission_baseline(self) -> None:
        self.assert_errors(
            self.mutate("首次浏览器自动提交与真实回执", "首次 pending_manual_submit 与真实回执"),
            ["M6 candidate missing '浏览器自动提交'",
             "M6 contains obsolete publishing baseline 'pending_manual_submit'"],
        )

    def test_rejects_reactivated_interaction_or_analytics_candidates(self) -> None:
        sections = self.module.milestone_sections(self.master)
        for number in (8, 9):
            with self.subTest(milestone=number):
                old = sections[number]
                self.assert_errors(
                    self.mutate(old, old + f"\n候选 CHG：\n\n```text\nM{number}-C1 恢复旧实施\n```\n"),
                    [f"M{number} is outside the current route but carries candidate CHGs"],
                )

    def test_rejects_unfinished_milestone_without_candidate_block(self) -> None:
        block = self.module.candidate_block(self.module.milestone_sections(self.master)[7])
        self.assertNotEqual(block, "")
        self.assert_errors(
            self.mutate(block, ""),
            ["M7 is 'NOT_STARTED' but carries no candidate CHG block; "
             "candidate assertions against an empty block would be vacuous"],
        )

    def test_rejects_missing_named_stage_or_changed_dependency(self) -> None:
        self.assertTrue(self.module.validate_master_text(self.mutate(
            "### M-publishing-plan：", "### missing-plan：")))
        self.assert_errors(
            self.mutate("| 依赖 | M7 `DONE` |", "| 依赖 | M6 `DONE` |"),
            ["M-publishing-plan dependency missing '| 依赖 | M7 `DONE` |'"],
        )

    def test_rejects_m10_dependency_on_excluded_module(self) -> None:
        self.assert_errors(
            self.mutate("| 依赖 | M-publishing-operations `DONE`，继承", "| 依赖 | M9 `DONE`，继承"),
            ["M10 dependency missing '| 依赖 | M-publishing-operations `DONE`'",
             "M10 depends on excluded M9"],
        )

    def test_rejects_missing_publishing_reference_and_safety_gate(self) -> None:
        self.assert_errors(
            self.mutate("milestones/M6-single-publishing.md", "milestones/missing.md"),
            ["M6 closure reference missing 'milestones/M6-single-publishing.md'"],
        )
        self.assert_errors(
            self.mutate("断网后必须核实且不重复投稿", "断网后直接重新执行"),
            ["M6 gate missing '断网后必须核实且不重复投稿'"],
        )

    def test_rejects_missing_m2_closure_reference(self) -> None:
        changed = self.mutate(
            'milestones/M2-account-runtime.md#m2-d-社媒账号重构',
            'milestones/missing-account-closure.md',
        )
        self.assert_errors(changed, ['M2 closure reference missing'])

    def test_rejects_old_route_and_missing_closure_card(self) -> None:
        self.assert_errors(
            self.mutate("→ M-publishing-plan 发布计划推进与结束", "→ M8 互动管理闭环"),
            ["Current milestone route must follow M0-M7, publishing plan, operations, M10"],
        )
        root = Path(self.tmp.name)
        errors = self.module.validate_publishing_cards(root)
        self.assertEqual(len(errors), 4)
        self.assertTrue(all("Publishing closure card missing:" in error for error in errors))

    def test_rejects_missing_card_dependency_or_dangling_link(self) -> None:
        import shutil
        root = Path(self.tmp.name)
        shutil.copytree(ROOT / "delivery" / "milestones", root / "delivery" / "milestones")
        # Preserve formal references in this isolated fixture.
        (root / "docs").symlink_to(ROOT / "docs", target_is_directory=True)
        (root / "delivery" / "completed").symlink_to(ROOT / "delivery" / "completed", target_is_directory=True)
        card = root / "delivery" / "milestones" / "M7-batch-publishing.md"
        text = card.read_text(encoding="utf-8")
        self.assertIn("](M6-single-publishing.md)", text)
        card.write_text(text.replace("](M6-single-publishing.md)", "](missing.md)"), encoding="utf-8")
        self.assertEqual(sorted(self.module.validate_publishing_cards(root)), sorted([
            "M7-batch-publishing.md dependency missing '](M6-single-publishing.md)'",
            "M7-batch-publishing.md links missing file: missing.md",
        ]))

    def _active_root(self, status: str, ledger_status: str | None = None) -> Path:
        """A minimal, otherwise-valid active CHG whose status line is `status`.

        Everything the other checks in `validate_active_change` look at is
        filled in — title, repository, a `None.` Pending Questions section, and
        a matching Ledger row — so the FULL error list under test is the status
        one and nothing else. `status` may carry an annotation; `ledger_status`
        is the bare word the Ledger carries, defaulting to `status` itself.
        """
        # One root per case: a shared root would make the second subTest fail
        # on `mkdir` instead of on the judgement under test.
        self._root_count = getattr(self, "_root_count", 0) + 1
        root = Path(self.tmp.name) / f"case-{self._root_count}" / "wt-media-workspace"
        change = root / "delivery" / "active" / "CHG-20260722-021" / "change.md"
        change.parent.mkdir(parents=True)
        change.write_text(
            "# CHG-20260722-021: Test\n\n"
            f"- Status: {status}\n"
            "- Current repository: `wt-media-workspace`\n\n"
            "## 7. Pending Questions\n\n"
            "None.\n",
            encoding="utf-8",
        )
        (root / "delivery" / "LEDGER.md").write_text(
            "# Delivery Ledger\n\n"
            "| Change | Title | Status | Current Repository |\n"
            "|---|---|---|---|\n"
            f"| CHG-20260722-021 | Test | {ledger_status or status} | wt-media-workspace |\n",
            encoding="utf-8",
        )
        return root

    def test_annotated_status_line_is_read_as_its_word(self) -> None:
        """An annotated status line must be judged on its word, not on `None`.

        Five consecutive CHGs (055–059) annotated the status line — three of
        them while still in `delivery/active/`. A regex demanding the bare word
        fails to match those at all, so the status came back as `None` and the
        gate reported `got None` while the record was legitimately active
        (CHG-20260923-059 own `evidence/task-08-gate.out`). Both directions are
        asserted: the annotation must not manufacture an error on a good word,
        and it must not smuggle a bad word past the accept-set.
        """
        # Verbatim from CHG-20260923-059, the record the gate misread as `None`.
        annotated = "IMPLEMENTING（2026-09-25 由 `delivery/planned/` 激活并改写为十三节执行记录）"
        self.assertEqual(
            self.module.validate_active_change(
                self._active_root(annotated, ledger_status="IMPLEMENTING")
            ),
            [],
        )

        # Verbatim from `CHG-20260923-053` (its `planned/` record was deleted
        # 2026-10-10): bolded.
        bold = "**SUPERSEDED（2026-09-23 并入联合工程优化程序，不再独立激活）**"
        self.assertEqual(
            self.module.validate_active_change(
                self._active_root(bold, ledger_status="SUPERSEDED")
            ),
            ["active CHG status must be IMPLEMENTING or VERIFYING, got 'SUPERSEDED'"],
        )

    def test_status_word_strips_bold_and_annotation(self) -> None:
        """The extraction helper, on every form the records actually use.

        Kept separate from the validate test above so that test's red run is
        a behavioural red (the judgement returns the wrong list) rather than an
        `AttributeError` on a function that does not exist yet — which would
        prove nothing about the behaviour.
        """
        cases = {
            "- Status: IMPLEMENTING": "IMPLEMENTING",
            "> 状态：DONE": "DONE",
            "> 状态：DONE（2026-08-05 窗口收口完成）": "DONE",
            "- Status: **SUPERSEDED（2026-09-23 并入联合工程优化程序，不再独立激活）**": "SUPERSEDED",
            "- Status: DONE (closed at the 2026-08-05 window)": "DONE",
        }
        for line, expected in cases.items():
            with self.subTest(line=line):
                self.assertEqual(self.module.status_word(line), expected)
        self.assertIsNone(self.module.status_word("# CHG-x: Test\n\nNo status line.\n"))
        self.assertIsNone(self.module.status_word("- Status: （only an annotation）"))

    def test_active_change_accepts_only_the_two_execution_words(self) -> None:
        """The accept-set is exactly `IMPLEMENTING` / `VERIFYING`.

        A record sits in `delivery/active/` only while it is being executed.
        `DISCUSSION` and `PLANNED` are pre-activation states, `DONE` and
        `SUPERSEDED` are terminal — accepting any of them accepts the state the
        vocabulary forbids. Both halves are asserted: the two legal words pass
        silently, and each illegal one produces exactly the status error.
        """
        for status in ("IMPLEMENTING", "VERIFYING"):
            with self.subTest(status=status):
                self.assertEqual(
                    self.module.validate_active_change(self._active_root(status)), []
                )

        for status in ("DISCUSSION", "PLANNED", "DONE", "SUPERSEDED", "IN_PROGRESS", "ACTIVE"):
            with self.subTest(status=status):
                self.assertEqual(
                    self.module.validate_active_change(self._active_root(status)),
                    [f"active CHG status must be IMPLEMENTING or VERIFYING, got {status!r}"],
                )

    def test_contract_governance_requires_mixed_state_and_active_task_schema(
        self,
    ) -> None:
        human = (ROOT / "docs" / "contracts" / "contract-map.md").read_text(
            encoding="utf-8"
        )
        machine = (ROOT / "config" / "contract-map.yaml").read_text(encoding="utf-8")

        self.assertIn("Current state is mixed.", human)
        errors = self.module.validate_contract_texts(
            human.replace("Current state is mixed.", "All contracts are active."),
            machine,
        )

        self.assertEqual(
            sorted(errors),
            sorted(["mixed contract state missing 'Current state is mixed.'"]),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
