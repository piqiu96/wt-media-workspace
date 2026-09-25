"""Skill paths must resolve, not merely be present as strings.

A skill file is read by an agent that then goes looking for the paths it names.
Asserting that a string appears in `SKILL.md` therefore proves nothing about
whether the agent will find anything at the other end: the string can survive a
file move, a rename, or a deletion for months. This module resolves them
instead, and it is the check that would have caught `agent-platform-adapter-
change` still pointing at `src/wt_media_agent/platforms` after the platform
code moved under `clients/`.

What counts as a path here is deliberately narrow, because a skill also quotes
commands, HTTP routes and prose. A backticked token is treated as a path when
all of these hold:

- it contains no whitespace (so `GET /api/v1/health` is out),
- it contains a `/`,
- it contains none of `<`, `>` or `*` (placeholders and globs name a shape,
  not a file),
- it does not start with `/` and contains no `:` (absolute paths and URLs),
- and its first segment names a real top-level entry of one of the roots below.

That last rule is the honest boundary of this check: it catches a path that
moved *under a known top-level directory*. A skill that misspells the first
segment outright (`serc/...`) is not caught here, because "does this look like a
path at all" and "does this path exist" cannot both be answered by the same
filesystem lookup.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXECUTION_ROOT = ROOT.parent

#: The repository a group's skills are written against. `common` skills are
#: distributed everywhere but written against the governance repository, which
#: is also where every skill file actually lives.
GROUP_ROOTS = {
    "common": ROOT,
    "workspace": ROOT,
    "agent": EXECUTION_ROOT / "wt-media-agent",
    "cloud": EXECUTION_ROOT / "wt-media-cloud",
    "desktop": EXECUTION_ROOT / "wt-media-desktop",
}

BACKTICKED = re.compile(r"`([^`\n]+)`")


def skill_files() -> list[Path]:
    return sorted((ROOT / "skills").glob("*/*/SKILL.md"))


def roots_for(group: str) -> list[Path]:
    """Where a token may legitimately resolve, most specific first."""
    roots = [ROOT]
    group_root = GROUP_ROOTS.get(group)
    if group_root is not None and group_root not in roots:
        roots.append(group_root)
    if EXECUTION_ROOT not in roots:
        roots.append(EXECUTION_ROOT)
    return roots


def known_first_segments() -> set[str]:
    """Top-level entry names across every root this check resolves against."""
    names: set[str] = set()
    for root in {ROOT, EXECUTION_ROOT, *GROUP_ROOTS.values()}:
        if root.is_dir():
            names.update(entry.name for entry in root.iterdir())
    return names


def path_tokens(text: str, known: set[str]) -> list[str]:
    tokens: list[str] = []
    for raw in BACKTICKED.findall(text):
        token = raw.strip()
        if any(character.isspace() for character in token):
            continue
        if "/" not in token or token.startswith("/") or ":" in token:
            continue
        if any(character in token for character in "<>*"):
            continue
        if token.split("/", 1)[0] not in known:
            continue
        tokens.append(token)
    return tokens


def unresolved(token: str, group: str) -> str | None:
    """The token if nothing is there, else `None`."""
    for root in roots_for(group):
        if (root / token).exists():
            return None
    return token


class SkillPathsResolveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.known = known_first_segments()
        cls.skills = skill_files()
        missing = sorted(
            root.name for root in GROUP_ROOTS.values() if not root.is_dir()
        )
        if missing:
            raise unittest.SkipTest(
                "runtime sibling repositories are not present in this checkout: "
                + ", ".join(missing)
            )
        cls.tokens = {
            path: path_tokens(path.read_text(encoding="utf-8"), cls.known)
            for path in cls.skills
        }

    def test_the_denominator_is_worth_reporting(self) -> None:
        """Guard against a vacuous pass: say how many tokens were even looked at.

        A path check whose extraction rules silently match nothing reports
        success forever. The floor is set well below today's count so that
        ordinary skill edits do not trip it.
        """
        found = sum(len(tokens) for tokens in self.tokens.values())

        self.assertGreaterEqual(len(self.skills), 8)
        self.assertGreaterEqual(
            found,
            20,
            f"only {found} path-like tokens found across {len(self.skills)} skills; "
            "the extraction rules are probably not matching",
        )

    def test_every_skill_path_resolves(self) -> None:
        missing: list[str] = []
        for path, tokens in self.tokens.items():
            group = path.parent.parent.name
            for token in tokens:
                if unresolved(token, group) is not None:
                    missing.append(f"{path.relative_to(ROOT)}: {token}")

        self.assertEqual(missing, [])

    def test_the_check_reports_a_path_that_is_not_there(self) -> None:
        """Positive control for the resolution step itself.

        Without this, `test_every_skill_path_resolves` passing is also what a
        broken `unresolved()` would produce.
        """
        known = self.known
        self.assertIn("skills", known)
        real = "skills/__definitely-not-here__/x"
        text = f"See `{real}` for details."

        self.assertEqual(path_tokens(text, known), [real])
        self.assertEqual(unresolved(real, "workspace"), real)

    def test_placeholders_and_globs_are_not_paths(self) -> None:
        text = "Write `delivery/active/<CHG>/change.md` and read `delivery/milestones/M*.md`."

        self.assertEqual(path_tokens(text, self.known), [])


if __name__ == "__main__":
    unittest.main()
