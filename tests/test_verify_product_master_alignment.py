from __future__ import annotations

import importlib.util
import re
import shutil
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
            ["M6 contains obsolete publishing baseline 'pending_manual_submit'"],
        )

    def test_rejects_reactivated_interaction_or_analytics_candidates(self) -> None:
        for number in (8, 9):
            with self.subTest(milestone=number):
                self.assert_errors(
                    self.mutate("### M10：", f"### M{number}：旧计划\n\n候选 CHG：\n\n```text\nM{number}-C1 旧实施\n```\n\n### M10："),
                    ["Master milestone set mismatch: expected M0-M7 and M10 (M8/M9 retired), "
                     f"got {', '.join(f'M{i}' for i in sorted([*range(8), number, 10]))}"],
                )

    def test_rejects_unfinished_milestone_without_candidate_block(self) -> None:
        block = self.module.candidate_block(self.module.milestone_sections(self.master)[7])
        self.assertNotEqual(block, "")
        self.assert_errors(
            self.mutate(block, ""),
            ["M7 is 'NOT_STARTED' but carries no candidate CHG block"],
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

    def test_rejects_missing_ui_baseline(self) -> None:
        import shutil
        root = Path(self.tmp.name)
        shutil.copytree(ROOT / "delivery" / "milestones", root / "delivery" / "milestones")
        (root / "docs").symlink_to(ROOT / "docs", target_is_directory=True)
        (root / "delivery" / "completed").symlink_to(ROOT / "delivery" / "completed", target_is_directory=True)
        card = root / "delivery" / "milestones" / "M6-single-publishing.md"
        old = "`/example/operations/publishing/tasks`"
        text = card.read_text(encoding="utf-8")
        self.assertIn(old, text)
        card.write_text(text.replace(old, "`/example/operations/other`"), encoding="utf-8")
        self.assertEqual(self.module.validate_publishing_cards(root), [
            f"M6-single-publishing.md UI baseline missing {old!r}",
        ])

    def publishing_root(self) -> Path:
        self._root_count = getattr(self, "_root_count", 0) + 1
        root = Path(self.tmp.name) / f"publishing-{self._root_count}"
        shutil.copytree(ROOT / "delivery" / "milestones", root / "delivery" / "milestones")
        shutil.copy2(MASTER_PATH, root / "delivery" / MASTER_PATH.name)
        (root / "docs").symlink_to(ROOT / "docs", target_is_directory=True)
        (root / "config").symlink_to(ROOT / "config", target_is_directory=True)
        (root / "delivery" / "LEDGER.md").write_text("# Delivery Ledger\n", encoding="utf-8")
        return root

    def set_stage(self, root, name, status, active="None", evidence=None, retire_candidates=False):
        master_path = root / "delivery" / MASTER_PATH.name
        master = master_path.read_text(encoding="utf-8")
        before = self.module.route_sections(master)[name]
        after = before.replace("| 状态 | `NOT_STARTED` |", f"| 状态 | `{status}` |", 1)
        after = after.replace("| Active CHG | None |", f"| Active CHG | {active} |", 1)
        if evidence is not None:
            after = re.sub(r"^\| Evidence \| .*", f"| Evidence | {evidence} |", after, flags=re.MULTILINE)
        if retire_candidates:
            after = re.sub(r"候选 CHG：\s*```text.*?```\s*", "", after, flags=re.DOTALL)
        master_path.write_text(master.replace(before, after, 1), encoding="utf-8")
        if name in self.module.PUBLISHING_CARDS:
            card = root / "delivery" / "milestones" / self.module.PUBLISHING_CARDS[name]
            text = card.read_text(encoding="utf-8")
            text = text.replace("状态：`NOT_STARTED`", f"状态：`{status}`", 1)
            text = text.replace("Active CHG：None", f"Active CHG：{active}", 1)
            if evidence is not None:
                text += f"\n- Evidence：{evidence}\n"
            if retire_candidates:
                text = re.sub(r"## 候选 CHG.*?(?=\n- Evidence：|\Z)", "", text, flags=re.DOTALL)
            card.write_text(text, encoding="utf-8")

    def stage_change(self, root, name, status):
        filename = self.module.PUBLISHING_CARDS.get(name, "M-first-production-release.md")
        directory = "completed" if status == "DONE" else "active"
        path = root / "delivery" / directory / "CHG-20261118-001" / "change.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            "---\nid: CHG-20261118-001\n"
            f"parent: delivery/milestones/{filename}#验收\nstatus: {status}\n"
            'depends_on: []\naffected_repos: ["wt-media-workspace"]\nrisk: L\n---\n'
            "# CHG-20261118-001: Test\n\n## Change\n\nTest\n\n## Done When\n\nTest\n",
            encoding="utf-8",
        )
        if directory == "active":
            (root / "delivery" / "LEDGER.md").write_text(
                f"| CHG-20261118-001 | Test | {status} | wt-media-workspace |\n", encoding="utf-8")
        return path

    def test_publishing_lifecycle_accepts_activation_verification_and_completion(self) -> None:
        for name in (*self.module.PUBLISHING_CARDS, "M10"):
            for status, chg_status in (("IN_PROGRESS", "IMPLEMENTING"), ("VERIFYING", "VERIFYING"), ("DONE", "DONE")):
                with self.subTest(milestone=name, status=status):
                    root = self.publishing_root()
                    self.stage_change(root, name, chg_status)
                    active = "None" if status == "DONE" else "CHG-20261118-001"
                    # The two documents resolve evidence relative to different directories.
                    self.set_stage(root, name, status, active, retire_candidates=True)
                    if status == "DONE":
                        master = root / "delivery" / MASTER_PATH.name
                        text = master.read_text(encoding="utf-8")
                        section = self.module.route_sections(text)[name]
                        evidence = "[验收通过](completed/CHG-20261118-001/change.md)"
                        changed = re.sub(r"^\| Evidence \| .*", f"| Evidence | {evidence} |", section, flags=re.MULTILINE)
                        master.write_text(text.replace(section, changed, 1), encoding="utf-8")
                        if name in self.module.PUBLISHING_CARDS:
                            card = root / "delivery" / "milestones" / self.module.PUBLISHING_CARDS[name]
                            with card.open("a", encoding="utf-8") as stream:
                                stream.write("\n- Evidence：[验收通过](../completed/CHG-20261118-001/change.md)\n")
                    self.assertEqual(self.module.validate_alignment(root), [])

    def test_candidate_names_are_not_permanent_requirements(self) -> None:
        root = self.publishing_root()
        for path in (root / "delivery").rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            text = re.sub(r"\b(?:M6|M7|PLAN|OPS)-[ABC]\b|PLATFORM-(?:百度|小红书)", "新候选", text)
            path.write_text(text, encoding="utf-8")
        self.assertEqual(self.module.validate_alignment(root), [])

    def test_not_started_card_still_requires_candidate_work(self) -> None:
        root = self.publishing_root()
        path = root / "delivery" / "milestones" / "M6-single-publishing.md"
        text = path.read_text(encoding="utf-8")
        changed, count = re.subn(r"^\| M6-[ABC] .*\n", "", text, flags=re.MULTILINE)
        self.assertEqual(count, 3)
        path.write_text(changed, encoding="utf-8")
        self.assertEqual(self.module.validate_publishing_cards(root), [
            "M6-single-publishing.md carries no candidate CHG rows",
        ])

    def test_rejects_invalid_publishing_statuses_and_master_card_disagreement(self) -> None:
        for name in (*self.module.PUBLISHING_CARDS, "M10"):
            with self.subTest(milestone=name):
                root = self.publishing_root()
                self.set_stage(root, name, "IMPLEMENTING")  # CHG word, not a milestone word.
                master = (root / "delivery" / MASTER_PATH.name).read_text(encoding="utf-8")
                self.assertEqual(self.module.validate_master_text(master), [
                    f"{name} has invalid milestone status 'IMPLEMENTING'",
                ])
        root = self.publishing_root()
        self.stage_change(root, "M6", "IMPLEMENTING")
        self.set_stage(root, "M6", "IN_PROGRESS", "CHG-20261118-001")
        card = root / "delivery" / "milestones" / "M6-single-publishing.md"
        card.write_text(card.read_text().replace("状态：`IN_PROGRESS`", "状态：`VERIFYING`"))
        self.assertEqual(self.module.validate_publishing_lifecycle(root), [
            "M6 Master/card milestone statuses disagree",
        ])

    def test_rejects_missing_or_wrong_parent_active_chg(self) -> None:
        for wrong_parent in (False, True):
            with self.subTest(wrong_parent=wrong_parent):
                root = self.publishing_root()
                if wrong_parent:
                    self.stage_change(root, "M7", "IMPLEMENTING")
                self.set_stage(root, "M6", "IN_PROGRESS", "CHG-20261118-001")
                errors = self.module.validate_publishing_lifecycle(root)
                self.assertIn("M6 MASTER_IMPLEMENTATION_PLAN.md Active CHG does not match delivery/active parent ownership", errors)
                self.assertIn("M6 M6-single-publishing.md Active CHG does not match delivery/active parent ownership", errors)
                if wrong_parent:
                    self.assertIn("M7 is NOT_STARTED but still owns active CHGs", errors)

    def test_rejects_active_pointer_disagreement_and_early_verifying(self) -> None:
        root = self.publishing_root()
        self.stage_change(root, "M6", "IMPLEMENTING")
        self.set_stage(root, "M6", "VERIFYING", "CHG-20261118-001")
        card = root / "delivery" / "milestones" / "M6-single-publishing.md"
        card.write_text(card.read_text().replace("Active CHG：CHG-20261118-001", "Active CHG：None"))
        self.assertEqual(self.module.validate_publishing_lifecycle(root), [
            "M6 M6-single-publishing.md Active CHG does not match delivery/active parent ownership",
            "M6 is VERIFYING but owns an IMPLEMENTING CHG",
        ])

    def test_progress_without_active_chg_requires_delivery_evidence(self) -> None:
        for status in ("IN_PROGRESS", "VERIFYING", "DONE"):
            with self.subTest(status=status):
                root = self.publishing_root()
                self.set_stage(root, "M6", status, retire_candidates=True)
                self.assertEqual(self.module.validate_publishing_lifecycle(root), [
                    f"M6 MASTER_IMPLEMENTATION_PLAN.md requires linked delivery evidence for {status}",
                    f"M6 M6-single-publishing.md requires linked delivery evidence for {status}",
                ])

    def test_progress_between_chgs_accepts_archived_evidence(self) -> None:
        for status in ("IN_PROGRESS", "VERIFYING"):
            with self.subTest(status=status):
                root = self.publishing_root()
                self.stage_change(root, "M6", "DONE")
                self.set_stage(root, "M6", status, evidence="[已完成工作](completed/CHG-20261118-001/change.md)")
                card = root / "delivery" / "milestones" / "M6-single-publishing.md"
                card.write_text(card.read_text().replace("](completed/", "](../completed/"))
                self.assertEqual(self.module.validate_alignment(root), [])

    def test_done_rejects_remaining_active_chgs_and_missing_or_unfinished_evidence(self) -> None:
        root = self.publishing_root()
        self.stage_change(root, "M6", "VERIFYING")
        self.set_stage(root, "M6", "DONE", "CHG-20261118-001", "[验收](active/CHG-20261118-001/change.md)")
        card = root / "delivery" / "milestones" / "M6-single-publishing.md"
        card.write_text(card.read_text().replace("](active/", "](../active/"))
        self.assertEqual(self.module.validate_publishing_lifecycle(root), [
            "M6 MASTER_IMPLEMENTATION_PLAN.md evidence CHG is not DONE: active/CHG-20261118-001/change.md",
            "M6 M6-single-publishing.md evidence CHG is not DONE: ../active/CHG-20261118-001/change.md",
            "M6 is DONE but still owns active CHGs",
        ])
        root = self.publishing_root()
        self.set_stage(root, "M6", "DONE", evidence="[验收](missing.md)")
        self.assertEqual(self.module.validate_publishing_lifecycle(root), [
            "M6 MASTER_IMPLEMENTATION_PLAN.md evidence file is missing: missing.md",
            "M6 M6-single-publishing.md evidence file is missing: missing.md",
        ])

    def test_ui_baseline_accepts_changed_or_absent_preview_host_and_pinned_source(self) -> None:
        for preview in ("https://another-host:9999", None):
            with self.subTest(preview=preview):
                root = self.publishing_root()
                for filename in self.module.PUBLISHING_CARDS.values():
                    path = root / "delivery" / "milestones" / filename
                    text = path.read_text(encoding="utf-8")
                    self.assertNotRegex(text, r"https?://(?:127\.0\.0\.1|localhost)(?::\d+)?/")
                    if preview:
                        route = re.search(r"`(/example/operations/[^`]+)`", text)
                        self.assertIsNotNone(route)
                        text += f"\n[本次启动的预览地址]({preview}{route.group(1)})\n"
                        self.assertIn(preview, text)
                    self.assertIn("/tree/main/web/", text)
                    text = text.replace("/tree/main/web/", "/tree/" + "a" * 40 + "/web/")
                    path.write_text(text, encoding="utf-8")
                self.assertEqual(self.module.validate_alignment(root), [])

    def test_ui_baseline_requires_source_components_and_public_standards(self) -> None:
        changes = (
            ("wt-media-cloud/tree/main/web/example/proto/publishing-design", "wt-media-cloud/tree/main/web/example/other", "Cloud prototype source link"),
            ("QuickPublish.vue", "Missing.vue", "'QuickPublish.vue'"),
            ("../../docs/standards/frontend/AdminUI页面规范.md", "README.md", "'../../docs/standards/frontend/AdminUI页面规范.md'"),
        )
        for before, after, expected in changes:
            with self.subTest(missing=before):
                root = self.publishing_root()
                path = root / "delivery" / "milestones" / "M6-single-publishing.md"
                text = path.read_text(encoding="utf-8")
                self.assertIn(before, text)
                path.write_text(text.replace(before, after, 1), encoding="utf-8")
                self.assertEqual(self.module.validate_publishing_cards(root), [
                    f"M6-single-publishing.md UI baseline missing {expected}",
                ])

    def test_retired_prototype_is_absent_and_not_referenced_by_current_docs(self) -> None:
        root = Path(self.tmp.name)
        milestones = root / "delivery" / "milestones"
        milestones.mkdir(parents=True)
        retired = milestones / "M-publishing-prototype.md"
        retired.write_text("old prototype", encoding="utf-8")
        self.assertEqual(self.module.validate_publishing_retirement(root), [
            "Retired prototype milestone must not exist",
        ])
        retired.unlink()
        current = milestones / "README.md"
        current.write_text("[old](M-publishing-prototype.md)", encoding="utf-8")
        self.assertEqual(self.module.validate_publishing_retirement(root), [
            "Current document references retired prototype: delivery/milestones/README.md",
        ])
        current.unlink()
        archive = root / "delivery" / "completed" / "old"
        archive.mkdir(parents=True)
        (archive / "change.md").write_text("[historical](../../milestones/M-publishing-prototype.md)", encoding="utf-8")
        self.assertEqual(self.module.validate_publishing_retirement(root), [])

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
