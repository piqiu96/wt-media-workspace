from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (
    ROOT
    / "skills"
    / "common"
    / "environment-bring-up"
    / "SKILL.md"
)


class EnvironmentBringUpSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_force_restart_required(self) -> None:
        self.assertIn("Force-stop stale processes", self.text)
        self.assertIn("Kill any running Cloud", self.text)
        self.assertIn("NOT fresh just because", self.text)

    def test_rebuild_from_latest_source(self) -> None:
        self.assertIn("Rebuild from latest source", self.text)
        self.assertIn("migrations", self.text)
        self.assertIn("cargo tauri build --bundles dmg", self.text)

    def test_freshness_gate(self) -> None:
        self.assertIn("Freshness gate", self.text)
        self.assertIn("Do not proceed with a stale Cloud or Agent", self.text)

    def test_login_smoke_gate(self) -> None:
        self.assertIn("Login smoke", self.text)
        self.assertIn("replace_existing: true", self.text)
        self.assertIn("errcode 0", self.text)

    def test_no_partial_pass(self) -> None:
        self.assertIn("no partial-pass shortcut", self.text)
        self.assertIn("Never declare the environment ready", self.text)

    def test_evidence_and_boundaries(self) -> None:
        self.assertIn("Record the bring-up run", self.text)
        self.assertIn("does not perform product acceptance", self.text)


if __name__ == "__main__":
    unittest.main()
