from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (
    ROOT
    / "skills"
    / "workspace"
    / "executing-wt-media-change"
    / "SKILL.md"
)


class ExecutingWtMediaChangeSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_start_gate_requires_synchronized_active_context(self) -> None:
        self.assertIn("CURRENT_CONTEXT", self.text)
        self.assertIn("delivery/LEDGER.md", self.text)
        self.assertIn("delivery/active", self.text)

    def test_start_gate_requires_business_closure_reference(self) -> None:
        self.assertIn("Milestone", self.text)
        self.assertIn("closure", self.text.lower())
        self.assertIn("user-visible vertical result", self.text)

    def test_real_effect_acceptance_cannot_be_replaced_by_code_presence(self) -> None:
        self.assertIn("external side effect", self.text)
        self.assertIn("read-back", self.text)
        self.assertIn("Code presence", self.text)

    def test_design_drift_returns_to_planning_skill(self) -> None:
        self.assertIn("planning-wt-media-delivery", self.text)
        self.assertIn("multiple independent closures", self.text)


if __name__ == "__main__":
    unittest.main()
