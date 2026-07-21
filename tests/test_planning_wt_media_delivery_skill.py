from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (
    ROOT
    / "skills"
    / "workspace"
    / "planning-wt-media-delivery"
    / "SKILL.md"
)


class PlanningWtMediaDeliverySkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_small_bug_does_not_force_milestone_rewrite(self) -> None:
        self.assertIn(
            "Do not rewrite a Milestone for a field display Bug.",
            self.text,
        )
        self.assertIn("Create or adjust one small CHG", self.text)

    def test_business_closure_gap_returns_to_milestone(self) -> None:
        self.assertIn(
            "User goal, operation order, success effect, or false-success rule changes",
            self.text,
        )
        self.assertIn("Update the Milestone, then create or adjust CHGs", self.text)

    def test_architecture_change_requires_decision_and_engineering(self) -> None:
        self.assertIn(
            "Record a Decision and update Engineering before Milestone/CHGs",
            self.text,
        )

    def test_new_milestone_stops_before_runtime_implementation(self) -> None:
        self.assertIn("Activate at most one M/L CHG", self.text)
        self.assertIn("Stop before runtime implementation", self.text)
        self.assertIn("executing-wt-media-change", self.text)


if __name__ == "__main__":
    unittest.main()
