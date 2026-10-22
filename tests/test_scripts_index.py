from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
INDEX = SCRIPTS / "README.md"


def script_files() -> list[str]:
    return sorted(
        path.relative_to(ROOT).as_posix()
        for path in SCRIPTS.rglob("*")
        if path.is_file()
        and path.suffix in {".py", ".sh", ".ps1"}
        and path.name != "__init__.py"
    )


def missing_entries(index_text: str) -> list[str]:
    return [path for path in script_files() if path not in index_text]


class ScriptsIndexTests(unittest.TestCase):
    def test_every_script_is_registered(self) -> None:
        self.assertEqual(missing_entries(INDEX.read_text(encoding="utf-8")), [])

    def test_new_script_without_an_entry_is_detected(self) -> None:
        text = INDEX.read_text(encoding="utf-8")
        removed = "scripts/docs/check.py"
        self.assertIn(removed, text)
        self.assertIn(removed, missing_entries(text.replace(removed, "")))

    def test_required_entries_are_present(self) -> None:
        text = INDEX.read_text(encoding="utf-8")
        for relative in (
            "scripts/wt.py",
            "scripts/chg/start.py",
            "scripts/chg/resume.py",
            "scripts/chg/verify.py",
            "scripts/docs/check.py",
            "scripts/dev/local_env.py",
            "scripts/lib/change_metadata.py",
            "scripts/lib/workspace_config.py",
            "scripts/verify/verify-control.sh",
            "scripts/verify/verify_m0_local.sh",
        ):
            self.assertIn(relative, text)


if __name__ == "__main__":
    unittest.main()
