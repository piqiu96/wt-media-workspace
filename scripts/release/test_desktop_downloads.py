"""Tests for the tag-derived desktop download manifest writer."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.release import desktop_downloads
from scripts.release.desktop_downloads import (
    ReleaseDownloadError,
    build_manifest_from_tag,
    write_manifest,
)

GOLDEN_V010 = """{
  "schema_version": 1,
  "version": "v0.1.0",
  "downloads": {
    "windows-x64": {
      "file_name": "WT-Media_v0.1.0_windows-x64-setup.exe",
      "url": "https://github.com/piqiu96/wt-media-workspace/releases/download/v0.1.0/WT-Media_v0.1.0_windows-x64-setup.exe"
    },
    "macos-x64": {
      "file_name": "WT-Media_v0.1.0_macos-x64.zip",
      "url": "https://github.com/piqiu96/wt-media-workspace/releases/download/v0.1.0/WT-Media_v0.1.0_macos-x64.zip"
    },
    "macos-arm64": {
      "file_name": "WT-Media_v0.1.0_macos-arm64.zip",
      "url": "https://github.com/piqiu96/wt-media-workspace/releases/download/v0.1.0/WT-Media_v0.1.0_macos-arm64.zip"
    }
  }
}
"""


class BuildManifestFromTagTest(unittest.TestCase):
    def test_v0_1_0_matches_published_manifest_bytes(self):
        manifest = build_manifest_from_tag("v0.1.0")
        encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        self.assertEqual(encoded.decode("utf-8"), GOLDEN_V010)

    def test_rejects_non_stable_tag(self):
        for tag in ("v0.1.0-rc.1", "0.1.0", "latest"):
            with self.subTest(tag=tag):
                with self.assertRaises(ReleaseDownloadError):
                    build_manifest_from_tag(tag)


class WriteManifestTest(unittest.TestCase):
    def test_writes_published_bytes_atomically(self):
        with tempfile_directory() as output_dir:
            target = output_dir / "desktop-downloads.json"
            write_manifest("v0.1.0", target)
            self.assertEqual(target.read_text(encoding="utf-8"), GOLDEN_V010)
            self.assertEqual(
                sorted(path.name for path in output_dir.iterdir()), ["desktop-downloads.json"]
            )

    def test_missing_output_directory_reports_and_writes_nothing(self):
        with tempfile_directory() as output_dir:
            target = output_dir / "absent" / "desktop-downloads.json"
            with self.assertRaises(ReleaseDownloadError):
                write_manifest("v0.1.0", target)
            self.assertFalse((output_dir / "absent").exists())

    def test_failed_replace_leaves_no_temporary_and_keeps_old_file(self):
        with tempfile_directory() as output_dir:
            target = output_dir / "desktop-downloads.json"
            target.write_text("old manifest", encoding="utf-8")
            with mock.patch.object(os, "replace", side_effect=OSError("replace failed")):
                with self.assertRaises(OSError):
                    write_manifest("v0.1.0", target)
            self.assertEqual(target.read_text(encoding="utf-8"), "old manifest")
            self.assertEqual(
                sorted(path.name for path in output_dir.iterdir()), ["desktop-downloads.json"]
            )


class tempfile_directory:
    def __enter__(self) -> Path:
        self._temporary = tempfile.TemporaryDirectory()
        return Path(self._temporary.name)

    def __exit__(self, *_args) -> None:
        self._temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
