from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.release.tag_transport import TagTransportError, push_annotated_tag_by_api


class TagTransportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        subprocess.run(["git", "init", "-b", "main", str(self.repo)], check=True, capture_output=True)
        self.git("config", "user.name", "Release Test")
        self.git("config", "user.email", "release-test@example.invalid")
        (self.repo / "source.txt").write_text("source\n")
        self.git("add", "source.txt")
        self.git("commit", "-m", "source")
        self.commit = self.git("rev-parse", "HEAD")
        self.tag = "v0.1.0-rc.99"
        self.git("tag", "-a", self.tag, "-m", "WT Media test")
        self.tag_object = self.git("rev-parse", f"refs/tags/{self.tag}")

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True, check=True, text=True).stdout.strip()

    def test_api_payload_recreates_exact_local_tag_object(self) -> None:
        calls: list[tuple[str, dict]] = []

        def fake_api(endpoint: str, payload: dict, repo_root: Path) -> dict:
            calls.append((endpoint, payload))
            return {"sha": self.tag_object}

        with patch("scripts.release.tag_transport._api", side_effect=fake_api):
            push_annotated_tag_by_api("wt-media-workspace", self.tag, self.repo)
        self.assertEqual(calls[0][0], "repos/piqiu96/wt-media-workspace/git/tags")
        self.assertEqual(calls[0][1]["object"], self.commit)
        self.assertEqual(calls[0][1]["message"], "WT Media test\n")
        self.assertEqual(calls[1][1], {"ref": f"refs/tags/{self.tag}", "sha": self.tag_object})

    def test_rejects_api_tag_object_that_differs_from_local_tag(self) -> None:
        with patch("scripts.release.tag_transport._api", return_value={"sha": "0" * 40}):
            with self.assertRaisesRegex(TagTransportError, "differs"):
                push_annotated_tag_by_api("wt-media-workspace", self.tag, self.repo)


if __name__ == "__main__":
    unittest.main()
