from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.release.submit_tag import ReleaseError, submit_tag


TAG = "v0.1.0-rc.99"
MANIFEST = f"""schema_version: 1
product_tag: {TAG}
channel: rc
environment: online
cloud_origin: https://wt.longyanyue.cn
network_smoke: false
components:
  cloud: v0.1.0-rc.12
  agent: v0.2.2-rc.2
  desktop: v0.1.0-rc.3
targets:
  cloud: linux-amd64
  desktop: [windows-x64, macos-x64, macos-arm64]
"""


class SubmitTagTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        self.bare = base / "origin.git"
        self.work = base / "workspace"
        self.bin = base / "bin"
        self.bin.mkdir()
        subprocess.run(["git", "init", "--bare", str(self.bare)], check=True, capture_output=True)
        subprocess.run(["git", "init", "-b", "codex/release-test", str(self.work)], check=True, capture_output=True)
        self.git("config", "user.name", "Release Test")
        self.git("config", "user.email", "release-test@example.invalid")
        self.git("remote", "add", "origin", str(self.bare))
        manifest = self.work / "releases" / "manifests" / f"{TAG}.yaml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(MANIFEST, encoding="utf-8")
        self.git("add", "releases")
        self.git("commit", "-m", "Add release manifest")
        self.git("push", "origin", "HEAD:refs/heads/codex/release-test")
        stub = self.bin / "gh"
        stub.write_text("#!/bin/sh\ncase \"$*\" in\n  *wt-media-cloud*) [ \"${MISSING_CLOUD_TAG:-0}\" != 1 ];;\n  *) exit 0;;\nesac\n", encoding="utf-8")
        stub.chmod(0o755)
        self.environment = patch.dict(os.environ, {"PATH": str(self.bin) + os.pathsep + os.environ["PATH"]})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.work, check=True, capture_output=True, text=True).stdout.strip()

    def remote_tag_commit(self) -> str | None:
        result = subprocess.run(
            ["git", "--git-dir", str(self.bare), "rev-parse", "--verify", f"refs/tags/{TAG}^{{}}"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() if result.returncode == 0 else None

    def test_dry_run_does_not_create_tag_and_explicit_push_does(self) -> None:
        head = self.git("rev-parse", "HEAD")
        submit_tag(TAG, self.work, push=False)
        self.assertIsNone(self.remote_tag_commit())
        submit_tag(TAG, self.work, push=True)
        self.assertEqual(self.remote_tag_commit(), head)

    def test_rejects_unpushed_source_commit(self) -> None:
        (self.work / "notes.txt").write_text("new commit\n", encoding="utf-8")
        self.git("add", "notes.txt")
        self.git("commit", "-m", "Local only")
        with self.assertRaisesRegex(ReleaseError, "push.*branch"):
            submit_tag(TAG, self.work, push=True)
        self.assertIsNone(self.remote_tag_commit())

    def test_rejects_dirty_manifest(self) -> None:
        manifest = self.work / "releases" / "manifests" / f"{TAG}.yaml"
        manifest.write_text(MANIFEST + "# uncommitted\n", encoding="utf-8")
        with self.assertRaisesRegex(ReleaseError, "uncommitted"):
            submit_tag(TAG, self.work, push=True)
        self.assertIsNone(self.remote_tag_commit())

    def test_rejects_missing_component_tag(self) -> None:
        with patch.dict(os.environ, {"MISSING_CLOUD_TAG": "1"}):
            with self.assertRaisesRegex(ReleaseError, "cloud.*Tag"):
                submit_tag(TAG, self.work, push=True)
        self.assertIsNone(self.remote_tag_commit())

    def test_rejects_existing_product_tag(self) -> None:
        submit_tag(TAG, self.work, push=True)
        with self.assertRaisesRegex(ReleaseError, "already exists"):
            submit_tag(TAG, self.work, push=True)
        self.assertEqual(self.remote_tag_commit(), self.git("rev-parse", "HEAD"))


if __name__ == "__main__":
    unittest.main()
