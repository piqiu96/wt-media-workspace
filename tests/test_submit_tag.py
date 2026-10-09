from __future__ import annotations

import os
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.release.submit_tag import ReleaseError, submit_tag, verify_publication


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
        stub.write_text(
            "#!/bin/sh\n"
            "case \"$2\" in\n"
            "  repos/piqiu96/wt-media-workspace/git/ref/*)\n"
            "    ref=${2#*/git/ref/}\n"
            "    if git --git-dir \"$FAKE_GH_BARE\" rev-parse --verify \"refs/$ref\" >/dev/null 2>&1; then\n"
            "      git --git-dir \"$FAKE_GH_BARE\" rev-parse \"refs/$ref\"\n"
            "    else\n"
            "      echo 'gh: Not Found (HTTP 404)' >&2\n"
            "      exit 1\n"
            "    fi;;\n"
            "  *wt-media-cloud*) [ \"${MISSING_CLOUD_TAG:-0}\" != 1 ];;\n"
            "  *) exit 0;;\n"
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

    def test_can_retry_matching_local_tag_after_network_failure(self) -> None:
        self.git("tag", "-a", TAG, "-m", "prepared release Tag")
        self.assertIsNone(self.remote_tag_commit())
        submit_tag(TAG, self.work, push=True)
        self.assertEqual(self.remote_tag_commit(), self.git("rev-parse", "HEAD"))

    def test_remote_preflight_works_when_git_ls_remote_is_unavailable(self) -> None:
        real_git = shutil.which("git")
        assert real_git is not None
        wrapper = self.bin / "git"
        wrapper.write_text(
            "#!/bin/sh\n"
            "case \"$*\" in *ls-remote*) exit 88;; esac\n"
            f"exec '{real_git}' \"$@\"\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        self.addCleanup(wrapper.unlink)
        submit_tag(TAG, self.work, push=False)

    def test_verify_publication_checks_exact_release_assets_and_checksums(self) -> None:
        names = [
            f"WT-Media_{TAG}_macos-arm64.zip",
            f"WT-Media_{TAG}_macos-x64.zip",
            f"WT-Media_{TAG}_windows-x64-setup.exe",
            "build-info.json",
            f"{TAG}.yaml",
        ]
        payloads = {name: name.encode() for name in names}
        payloads["build-info.json"] = json.dumps({"product_tag": TAG}).encode()
        payloads["SHA256SUMS"] = "".join(
            f"{hashlib.sha256(payloads[name]).hexdigest()}  {name}\n" for name in names
        ).encode()
        assets = [{"name": name} for name in [*names, "SHA256SUMS"]]
        calls: list[list[str]] = []

        def fake_command(args: list[str], repo_root: Path, *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
            calls.append(args)
            if args[:3] == ["gh", "run", "list"]:
                return subprocess.CompletedProcess(args, 0, json.dumps([{"databaseId": 123, "headBranch": TAG}]), "")
            if args[:3] == ["gh", "run", "watch"]:
                return subprocess.CompletedProcess(args, 0, "", "")
            if args[:3] == ["gh", "release", "view"]:
                return subprocess.CompletedProcess(args, 0, json.dumps({"isPrerelease": True, "assets": assets}), "")
            if args[:3] == ["gh", "release", "download"]:
                directory = Path(args[args.index("--dir") + 1])
                for name, content in payloads.items():
                    (directory / name).write_bytes(content)
                return subprocess.CompletedProcess(args, 0, "", "")
            raise AssertionError(args)

        with patch("scripts.release.submit_tag._command", side_effect=fake_command):
            summary = verify_publication(TAG, self.work)
        self.assertIn("123", summary)
        self.assertIn(hashlib.sha256(payloads[f"WT-Media_{TAG}_windows-x64-setup.exe"]).hexdigest(), summary)
        self.assertTrue(any(args[:3] == ["gh", "run", "watch"] for args in calls))

    def test_verify_publication_rejects_bad_download(self) -> None:
        def fake_command(args: list[str], repo_root: Path, *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
            if args[:3] == ["gh", "run", "list"]:
                return subprocess.CompletedProcess(args, 0, json.dumps([{"databaseId": 123, "headBranch": TAG}]), "")
            if args[:3] == ["gh", "run", "watch"]:
                return subprocess.CompletedProcess(args, 0, "", "")
            if args[:3] == ["gh", "release", "view"]:
                return subprocess.CompletedProcess(args, 0, json.dumps({"isPrerelease": True, "assets": [
                    {"name": f"WT-Media_{TAG}_macos-arm64.zip"},
                    {"name": f"WT-Media_{TAG}_macos-x64.zip"},
                    {"name": f"WT-Media_{TAG}_windows-x64-setup.exe"},
                    {"name": "build-info.json"},
                    {"name": f"{TAG}.yaml"},
                    {"name": "SHA256SUMS"},
                ]}), "")
            if args[:3] == ["gh", "release", "download"]:
                directory = Path(args[args.index("--dir") + 1])
                (directory / "SHA256SUMS").write_text("0" * 64 + "  build-info.json\n")
                (directory / "build-info.json").write_text(json.dumps({"product_tag": TAG}))
                (directory / f"{TAG}.yaml").write_text(MANIFEST)
                for platform, suffix in (("macos-arm64", "zip"), ("macos-x64", "zip"), ("windows-x64-setup", "exe")):
                    (directory / f"WT-Media_{TAG}_{platform}.{suffix}").write_bytes(b"asset")
                return subprocess.CompletedProcess(args, 0, "", "")
            raise AssertionError(args)

        with patch("scripts.release.submit_tag._command", side_effect=fake_command):
            with self.assertRaisesRegex(ReleaseError, "SHA-256"):
                verify_publication(TAG, self.work)


if __name__ == "__main__":
    unittest.main()
