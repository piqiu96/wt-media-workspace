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
        package_root = payload / f"wt-media-cloud_{TAG}_linux-amd64"
        files = {
            "web/index.cloud.html": "cloud-web",
            "ffmpeg-source.json": "{}",
            "release-info.json": json.dumps({
                "product_tag": TAG,
                "source_commit": SOURCES["cloud"],
                "configuration": "template-state config/ rendered by deploy/init-config.sh",
            }),
            "deploy/DEPLOYMENT.md": "# Deployment\n",
            "deploy/prepare-database.sql.example": "-- prepare\n",
            "config/app.toml.tpl": "password = {{WT_INITIAL_ADMIN_PASSWORD}}\n",
            "config/database/primary.toml.tpl": "password = {{WT_DB_PASSWORD}}\n",
            "config/credentials/agent.toml.tpl": "auth_token = {{WT_AGENT_AUTH_TOKEN}}\n",
            "config/credentials/douyin.toml.tpl": "api_key = {{WT_DOUYIN_API_KEY}}\n",
            "config/credentials/object_storage.toml.tpl": "secret_key = {{WT_OBJECT_STORAGE_SECRET_KEY}}\n",
            "config/storage/object_storage.toml.tpl": "endpoint = {{WT_OBJECT_STORAGE_ENDPOINT}}\n",
            "migrations/001_identity.sql": "CREATE TABLE users (id INT);\n",
        }
        for relative, content in files.items():
            file = package_root / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content, encoding="utf-8")
        for binary in ("server", "discovery-scheduler", "discovery-worker", "migrate", "config-check", "ffmpeg", "ffprobe"):
            file = package_root / "bin" / binary
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("#!/bin/sh\n", encoding="utf-8")
            file.chmod(0o755)
        for script in ("render-config.py", "install.sh", "init-config.sh", "migrate.sh", "activate.sh", "verify-package.sh", "verify-database.sh", "verify-runtime.sh", "rollback.sh"):
            file = package_root / "deploy" / script
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("#!/bin/sh\n", encoding="utf-8")
            file.chmod(0o755)
        cloud_archive = cloud / f"wt-media-cloud_{TAG}_linux-amd64.tar.gz"
        with tarfile.open(cloud_archive, "w:gz") as archive:
            archive.add(package_root, arcname=package_root.name)
        web_archive = cloud / f"desktop-web_{TAG}.tar.gz"
        web_archive.write_bytes(b"web")
        (cloud / "SHA256SUMS").write_text(
            f"{hashlib.sha256(cloud_archive.read_bytes()).hexdigest()}  {cloud_archive.name}\n"
            f"{hashlib.sha256(web_archive.read_bytes()).hexdigest()}  {web_archive.name}\n",
            encoding="utf-8",
        )
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
