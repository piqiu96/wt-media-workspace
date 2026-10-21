from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.change_metadata import read_change


class ChangeMetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def change(self, body: str, change_id: str = "CHG-20261022-099") -> Path:
        path = self.root / change_id / "change.md"
        path.parent.mkdir()
        path.write_text(body, encoding="utf-8")
        return path

    def test_minimal_new_change(self) -> None:
        path = self.change("""---
id: CHG-20261022-099
parent: none
status: IMPLEMENTING
depends_on: []
affected_repos: ["wt-media-workspace"]
risk: M
---
# CHG-20261022-099: Governance
## Change
Do work.
## Done When
Verified.
""")
        parsed = read_change(path)
        self.assertEqual(parsed.title, "Governance")
        self.assertEqual(parsed.affected_repos, ("wt-media-workspace",))
        self.assertEqual(parsed.depends_on, ())
        self.assertFalse(parsed.legacy)

    def test_new_change_rejects_missing_metadata(self) -> None:
        path = self.change("""---
id: CHG-20261022-099
parent: none
status: IMPLEMENTING
depends_on: []
affected_repos: ["wt-media-workspace"]
---
## Change
x
## Done When
y
""")
        with self.assertRaisesRegex(ValueError, "risk"):
            read_change(path)

    def test_legacy_change_remains_readable(self) -> None:
        path = self.change("""# CHG-20261022-099: Existing
- Status: IMPLEMENTING
- Milestone: `delivery/milestones/M5-automatic-production.md`
- Affected repositories: `wt-media-cloud`, `wt-media-agent`
""")
        parsed = read_change(path)
        self.assertTrue(parsed.legacy)
        self.assertEqual(parsed.parent, "delivery/milestones/M5-automatic-production.md")
        self.assertEqual(parsed.affected_repos, ("wt-media-cloud", "wt-media-agent"))


if __name__ == "__main__":
    unittest.main()
