import json
import tempfile
import unittest
from pathlib import Path

from scripts.release.update_desktop_downloads import ReleaseDownloadError, build_manifest, write_manifest


TAG = "v0.1.0"


def release(**overrides):
    names = [
        f"WT-Media_{TAG}_windows-x64-setup.exe",
        f"WT-Media_{TAG}_macos-x64.zip",
        f"WT-Media_{TAG}_macos-arm64.zip",
    ]
    data = {
        "tag_name": TAG,
        "draft": False,
        "prerelease": False,
        "assets": [
            {"name": name, "browser_download_url": f"https://github.com/piqiu96/wt-media-workspace/releases/download/{TAG}/{name}"}
            for name in names
        ],
    }
    data.update(overrides)
    return data


class ManifestTests(unittest.TestCase):
    def test_maps_exactly_three_platform_assets(self):
        manifest = build_manifest(TAG, release())
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["version"], TAG)
        self.assertEqual(set(manifest["downloads"]), {"windows-x64", "macos-x64", "macos-arm64"})
        self.assertEqual(manifest["downloads"]["windows-x64"]["file_name"], f"WT-Media_{TAG}_windows-x64-setup.exe")

    def test_rejects_non_stable_or_wrong_release(self):
        for payload in [release(draft=True), release(prerelease=True), release(tag_name="v0.1.1")]:
            with self.subTest(payload=payload):
                with self.assertRaises(ReleaseDownloadError):
                    build_manifest(TAG, payload)
        with self.assertRaises(ReleaseDownloadError):
            build_manifest("v0.1.0-rc.1", release())

    def test_rejects_missing_duplicate_and_foreign_asset(self):
        good = release()["assets"]
        for assets in [good[:-1], good + [good[0]], [*good[:2], {**good[2], "browser_download_url": "https://evil.example/file.zip"}]]:
            with self.subTest(assets=assets):
                with self.assertRaises(ReleaseDownloadError):
                    build_manifest(TAG, release(assets=assets))

    def test_write_replaces_manifest_and_preserves_old_on_invalid_input(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "desktop-downloads.json"
            output.write_text("old", encoding="utf-8")
            with self.assertRaises(ReleaseDownloadError):
                write_manifest("v0.1.0-rc.1", release(), output)
            self.assertEqual(output.read_text(encoding="utf-8"), "old")
            write_manifest(TAG, release(), output)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["version"], TAG)


if __name__ == "__main__":
    unittest.main()
