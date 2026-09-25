"""Cross-repository arms for the four `bin/control.sh` entries.

What this adds over the per-repository checks (desktop `tests/control.test.sh`,
cloud `scripts/verify/test-control.sh`, agent `tests/test_control_sh.py`,
workspace `scripts/test-control.sh`): one place that sees all four entries at
once, so the defect class that CHG-20260926-067 missed cannot be visible in one
repository and invisible in the rest. A sibling repository whose directory is not
next to this one is **skipped, with the denominator printed**, following
`scripts/verify_agent_entry.py`'s precedent -- otherwise a single-repository
checkout would go red for a reason that has nothing to do with the entries.

This file asserts **behaviour and modes only**: does the file exist, is it
tracked, what mode is in the git index, is it executable on disk, does invoking
it directly work, does an unknown verb exit 2. It never matches the entry's
source text across repositories. `AGENT-INDEX.md` §12 / D-01 keep cross-repo
source literals out of gates, and the entries legitimately differ: the workspace
dispatches five verbs (it also has `verify`), the other three dispatch four, and
each spells its own usage lines. A cross-repo check that pinned those strings
would be a second landing point for each repository's own contract.

Why direct invocation, not `bash bin/control.sh ...`: invoking through `bash`
succeeds even when the execute bit is missing, so a check written that way
cannot see the very defect it is meant to catch -- that is exactly how the
desktop entry shipped 100644 while every arm that tested it passed.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXECUTION_ROOT = ROOT.parent

#: name -> directory next to this checkout. `workspace` is this repository.
REPOSITORIES = {
    "workspace": ROOT,
    "cloud": EXECUTION_ROOT / "wt-media-cloud",
    "agent": EXECUTION_ROOT / "wt-media-agent",
    "desktop": EXECUTION_ROOT / "wt-media-desktop",
}


def entry_for(repo: Path) -> Path:
    return repo / "bin" / "control.sh"


class EntryNotInvocable(Exception):
    """The entry could not be executed at all -- the defect this file checks for."""


class BinControlEntryTest(unittest.TestCase):
    maxDiff = None

    # Every arm walks this list and wraps each repository in its own subTest, so
    # one repository's failure is reported as that repository's cell and the
    # remaining ones are still evaluated. An absent sibling is a skip *inside*
    # the subTest (never a failure): a single-repository checkout must not go red
    # for a reason that has nothing to do with the entries.
    @staticmethod
    def repository_items() -> list[tuple[str, Path]]:
        return [(name, repo) for name, repo in REPOSITORIES.items()]

    @staticmethod
    def present() -> list[str]:
        return sorted(n for n, p in REPOSITORIES.items() if p.is_dir())

    def require_present(self, name: str, repo: Path) -> None:
        if not repo.is_dir():
            self.skipTest(
                f"{name}: no sibling checkout at {repo} -- this arm covers "
                f"{len(self.present())}/{len(REPOSITORIES)} repositories"
            )

    def run_entry(self, entry: Path, *args: str) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                [str(entry), *args],
                capture_output=True,
                text=True,
                cwd=str(entry.parent.parent),
            )
        except OSError as exc:  # EACCES on a non-executable entry lands here
            raise EntryNotInvocable(exc) from exc

    # criterion 1 -- the file is there and git knows about it
    def test_entry_exists_and_is_tracked(self) -> None:
        git = shutil.which("git")
        self.assertIsNotNone(git, "git is required to read the index mode")
        for name, repo in self.repository_items():
            with self.subTest(repository=name):
                self.require_present(name, repo)
                entry = entry_for(repo)
                self.assertTrue(entry.is_file(), f"{name}: not a regular file: {entry}")
                result = subprocess.run(
                    [str(git), "-C", str(repo), "ls-files", "--error-unmatch", "bin/control.sh"],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    result.returncode, 0, f"{name}: bin/control.sh is not tracked"
                )

    # criterion 2 -- what a fresh clone and CI materialise
    def test_index_mode_is_100755(self) -> None:
        git = shutil.which("git")
        self.assertIsNotNone(git, "git is required to read the index mode")
        for name, repo in self.repository_items():
            with self.subTest(repository=name):
                self.require_present(name, repo)
                result = subprocess.run(
                    [str(git), "-C", str(repo), "ls-files", "-s", "--", "bin/control.sh"],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, f"{name}: {result.stderr.strip()}")
                mode = result.stdout.split()[0]
                self.assertEqual(
                    mode,
                    "100755",
                    f"{name}: git index mode is {mode}; a fresh checkout would not be "
                    "executable even though this machine may run it fine",
                )

    # criterion 3 -- what this machine runs
    def test_working_tree_mode_is_executable(self) -> None:
        for name, repo in self.repository_items():
            with self.subTest(repository=name):
                self.require_present(name, repo)
                entry = entry_for(repo)
                self.assertTrue(
                    os.access(entry, os.X_OK), f"{name}: not executable: {entry}"
                )

    # criterion 4 -- direct invocation
    def test_direct_invocation_help_exits_zero(self) -> None:
        for name, repo in self.repository_items():
            with self.subTest(repository=name):
                self.require_present(name, repo)
                entry = entry_for(repo)
                try:
                    result = self.run_entry(entry, "help")
                except EntryNotInvocable as exc:
                    self.fail(
                        f"{name}: could not invoke {entry} directly: {exc}. A "
                        "non-executable entry is the point of this arm -- run "
                        f"`chmod +x {entry}`."
                    )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"{name}: 'control.sh help' exit={result.returncode}; "
                    f"stderr: {result.stderr.strip()[:200]}",
                )

    # criterion 6 -- the dispatch table's failure path
    def test_unknown_verb_exits_two_with_usage_on_stderr(self) -> None:
        for name, repo in self.repository_items():
            with self.subTest(repository=name):
                self.require_present(name, repo)
                entry = entry_for(repo)
                try:
                    result = self.run_entry(entry, "no-such-verb")
                except EntryNotInvocable as exc:
                    self.fail(f"{name}: could not invoke {entry} directly: {exc}")
                self.assertEqual(result.returncode, 2, f"{name}: exit={result.returncode}")
                self.assertEqual(
                    result.stdout,
                    "",
                    f"{name}: unknown verb must write nothing to stdout",
                )
                self.assertIn("Usage:", result.stderr, f"{name}: no usage on stderr")


if __name__ == "__main__":
    unittest.main()
