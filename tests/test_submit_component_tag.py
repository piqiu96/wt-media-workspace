from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.release.submit_component_tag import ComponentTagError, submit_component_tag


class SubmitComponentTagTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        self.bare = base / "origin.git"
        self.work = base / "agent"
        self.bin = base / "bin"
        self.bin.mkdir()
        subprocess.run(["git", "init", "--bare", str(self.bare)], check=True, capture_output=True)
        subprocess.run(["git", "init", "-b", "main", str(self.work)], check=True, capture_output=True)
        self.git("config", "user.name", "Release Test")
        self.git("config", "user.email", "release-test@example.invalid")
        self.git("remote", "add", "origin", str(self.bare))
        (self.work / "source.txt").write_text("source\n")
        self.git("add", "source.txt")
        self.git("commit", "-m", "Release source")
        self.commit = self.git("rev-parse", "HEAD")
        self.git("push", "origin", "HEAD:refs/heads/main")
        stub = self.bin / "gh"
        stub.write_text(
            "#!/bin/sh\n"
            "case \"$2\" in\n"
            "  repos/piqiu96/wt-media-agent/git/commits/*)\n"
            "    commit=${2##*/}\n"
            "    git --git-dir \"$FAKE_GH_BARE\" cat-file -e \"$commit^{commit}\";;\n"
            "  repos/piqiu96/wt-media-agent/git/ref/tags/*)\n"
            "    tag=${2##*/}\n"
            "    if git --git-dir \"$FAKE_GH_BARE\" rev-parse --verify \"refs/tags/$tag\" >/dev/null 2>&1; then\n"
            "      git --git-dir \"$FAKE_GH_BARE\" rev-parse \"refs/tags/$tag\"\n"
            "    else\n"
            "      echo 'gh: Not Found (HTTP 404)' >&2\n"
            "      exit 1\n"
            "    fi;;\n"
            "  *) exit 1;;\n"
            "esac\n",
            encoding="utf-8",
        )
        stub.chmod(0o755)
        self.environment = patch.dict(os.environ, {
            "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
            "FAKE_GH_BARE": str(self.bare),
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.work, check=True, capture_output=True, text=True).stdout.strip()

    def test_preflight_is_read_only_and_push_creates_exact_annotated_tag(self) -> None:
        tag = "v0.2.2-rc.99"
        submit_component_tag("agent", tag, self.commit, self.work, push=False)
        local = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/tags/{tag}"], cwd=self.work)
        self.assertNotEqual(local.returncode, 0)
        submit_component_tag("agent", tag, self.commit, self.work, push=True)
        self.assertEqual(self.git("cat-file", "-t", f"refs/tags/{tag}"), "tag")
        self.assertEqual(self.git("rev-parse", f"refs/tags/{tag}^{{}}"), self.commit)
        remote = subprocess.run(["git", "--git-dir", str(self.bare), "rev-parse", f"refs/tags/{tag}^{{}}"], check=True, capture_output=True, text=True)
        self.assertEqual(remote.stdout.strip(), self.commit)

    def test_rejects_commit_not_pushed_to_github(self) -> None:
        (self.work / "source.txt").write_text("new source\n")
        self.git("commit", "-am", "Local only")
        local_commit = self.git("rev-parse", "HEAD")
        with self.assertRaisesRegex(ComponentTagError, "not present on GitHub"):
            submit_component_tag("agent", "v0.2.2-rc.99", local_commit, self.work, push=True)

    def test_rejects_existing_local_tag_at_other_commit(self) -> None:
        self.git("tag", "-a", "v0.2.2-rc.99", "-m", "old", self.commit)
        (self.work / "source.txt").write_text("new source\n")
        self.git("commit", "-am", "New source")
        new_commit = self.git("rev-parse", "HEAD")
        self.git("push", "origin", "HEAD:refs/heads/main")
        with self.assertRaisesRegex(ComponentTagError, "different commit"):
            submit_component_tag("agent", "v0.2.2-rc.99", new_commit, self.work, push=True)


if __name__ == "__main__":
    unittest.main()
