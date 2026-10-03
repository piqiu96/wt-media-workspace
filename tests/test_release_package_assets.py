from __future__ import annotations

import hashlib
import json
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.release.package_assets import PLATFORMS, package


TAG = "v0.1.0-rc.1"
ORIGIN = "https://wt.longyanyue.cn"
SOURCES = {name: "a" * 40 for name in ("workspace", "cloud", "agent", "desktop")}


class ReleasePackageAssetsTest(unittest.TestCase):
    def fixture(self, root: Path, mac_origin: str = ORIGIN) -> tuple[Path, Path, Path, Path]:
        assets = root / "assets"
        cloud = root / "cloud"
        agent = root / "agent"
        for folder in (assets, cloud, agent):
            folder.mkdir()
        manifest = root / f"{TAG}.yaml"
        manifest.write_text("product_tag: " + TAG + "\n", encoding="utf-8")
        payload = root / "content"
        for relative in ("bin/server", "bin/discovery-scheduler", "bin/discovery-worker", "bin/migrate", "bin/ffmpeg", "bin/ffprobe", "web/index.cloud.html", "ffmpeg-source.json"):
            file = payload / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(relative, encoding="utf-8")
        with tarfile.open(cloud / f"wt-media-cloud_{TAG}_linux-amd64.tar.gz", "w:gz") as archive:
            archive.add(payload, arcname="cloud")
        (cloud / f"desktop-web_{TAG}.tar.gz").write_bytes(b"web")
        for platform, target in PLATFORMS.items():
            folder = agent / f"agent-{platform}"
            folder.mkdir()
            binary = folder / "wt-media-agent"
            binary.write_bytes(target.encode())
            (folder / "sidecar-manifest.json").write_text(json.dumps({
                "component": "wt-media-agent", "version": "0.2.2", "target": target,
                "filename": binary.name, "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            }), encoding="utf-8")
        (assets / "起飞_0.1.0_x64-setup.exe").write_bytes(b"nsis")
        for arch in ("x64", "aarch64"):
            with zipfile.ZipFile(assets / f"起飞_0.1.0_macos-{arch}.zip", "w") as archive:
                prefix = "release/app.app/Contents/Resources/"
                archive.writestr(prefix + "config/agent.toml", f'[cloud]\nbase_url = "{mac_origin}"')
                archive.writestr(prefix + "resources/desktop.production.toml", f'[cloud]\nbase_url = "{mac_origin}"')
                archive.writestr(prefix + "sidecar-manifest.json", "{}")
                archive.writestr(prefix + "versions.json", "{}")
                archive.writestr("release/app.dmg", "dmg")
        return manifest, assets, cloud, agent

    def test_accepts_complete_candidate_and_records_all_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest, assets, cloud, agent = self.fixture(Path(temporary))
            package(TAG, ORIGIN, manifest, assets, cloud, agent, SOURCES)
            info = json.loads((assets / "build-info.json").read_text(encoding="utf-8"))
            self.assertEqual(info["source_commits"], SOURCES)
            self.assertEqual(len(info["desktop_assets"]), 3)
            self.assertIn("WT-Media_v0.1.0-rc.1_windows-x64-setup.exe", (assets / "SHA256SUMS").read_text(encoding="utf-8"))
            self.assertFalse(list(assets.glob("起飞_*")), "non-ASCII artifact names must not reach GitHub")

    def test_rejects_macos_package_with_different_cloud_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest, assets, cloud, agent = self.fixture(Path(temporary), "https://wrong.example")
            with self.assertRaisesRegex(ValueError, "wrong Cloud origin"):
                package(TAG, ORIGIN, manifest, assets, cloud, agent, SOURCES)


if __name__ == "__main__":
    unittest.main()
