from __future__ import annotations

import hashlib
import json
import plistlib
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.release.package_assets import PLATFORMS, package


TAG = "v0.1.0-rc.1"
ORIGIN = "https://wt.longyanyue.cn"
DESKTOP_TAG = "v0.1.0-rc.9"
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
                "configuration": "template-state config/ rendered by wtmctl",
            }),
            "deploy/DEPLOYMENT.md": "# Deployment\n",
            "deploy/config-variable-schema.toml": "schema_version = 1\n",
            "deploy/prepare-database.sql.example": "-- prepare\n",
            "deploy/examples/online.toml.example": "# online\n",
            "deploy/examples/online-deploy.toml.example": "# profile\n",
            "config/app.toml": "password = 'admin123'\n",
            "config/clients/http/agent.toml": "host = '127.0.0.1'\n",
            "config/clients/http/douyin.toml": "host = 'api.itfaba.com'\n",
            "config/database/primary.toml.tpl": "password = {{WT_PRIMARY_DB_PASSWORD}}\n",
            "config/credentials/agent.toml.tpl": "auth_token = {{WT_AGENT_AUTH_TOKEN}}\n",
            "config/credentials/douyin.toml.tpl": "api_key = {{WT_DOUYIN_API_KEY}}\n",
            "config/credentials/object_storage.toml.tpl": "secret_key = {{WT_OBJECT_STORAGE_SECRET_KEY}}\n",
            "config/storage/object_storage.toml.tpl": "prefix = {{WT_OBJECT_STORAGE_PREFIX}}\n",
            "migrations/001_identity.sql": "CREATE TABLE users (id INT);\n",
        }
        for relative, content in files.items():
            file = package_root / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content, encoding="utf-8")
        for binary in ("wt-media-cloud", "discovery-scheduler", "discovery-worker", "migrate", "config-check", "wtmctl", "ffmpeg", "ffprobe"):
            file = package_root / "bin" / binary
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
                build = {"product_tag": TAG, "desktop_version": TAG[1:], "desktop_source_tag": DESKTOP_TAG, "desktop_source_commit": SOURCES["desktop"]}
                archive.writestr(prefix + "desktop-build.json", json.dumps(build))
                archive.writestr(prefix + "versions.json", json.dumps({"desktop_version": TAG[1:], "desktop_build": build}))
                archive.writestr("release/app.app/Contents/Info.plist", plistlib.dumps({"CFBundleShortVersionString": TAG[1:]}))
                archive.writestr("release/app.dmg", "dmg")
        return manifest, assets, cloud, agent

    def test_accepts_complete_candidate_and_records_all_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest, assets, cloud, agent = self.fixture(Path(temporary))
            package(TAG, ORIGIN, manifest, assets, cloud, agent, SOURCES, DESKTOP_TAG)
            info = json.loads((assets / "build-info.json").read_text(encoding="utf-8"))
            self.assertEqual(info["source_commits"], SOURCES)
            self.assertEqual(len(info["desktop_assets"]), 3)
            self.assertIn("WT-Media_v0.1.0-rc.1_windows-x64-setup.exe", (assets / "SHA256SUMS").read_text(encoding="utf-8"))
            self.assertFalse(list(assets.glob("起飞_*")), "non-ASCII artifact names must not reach GitHub")

    def test_package_cli_accepts_separate_product_and_component_tags(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest, assets, cloud, agent=self.fixture(Path(temporary))
            command=[sys.executable,"scripts/release/package_assets.py","--tag",TAG,"--desktop-source-tag",DESKTOP_TAG,"--cloud-origin",ORIGIN,"--manifest",str(manifest),"--assets",str(assets),"--cloud-artifact",str(cloud),"--agent-artifacts",str(agent)]
            for component, commit in SOURCES.items(): command.extend(["--source-commit",f"{component}={commit}"])
            subprocess.run(command,check=True,capture_output=True,text=True)
            self.assertTrue((assets/"build-info.json").is_file())

    def test_rejects_macos_with_wrong_native_version_or_source(self):
        from scripts.release.package_assets import verify_mac
        for key, value in [("desktop_version", "0.1.0"), ("desktop_source_commit", "b"*40), ("desktop_source_tag", "v9.0.0"), ("product_tag", "v0.1.1")]:
            with self.subTest(key=key), tempfile.TemporaryDirectory() as temporary:
                _, assets, _, _ = self.fixture(Path(temporary))
                source = next(assets.glob("*x64.zip"))
                changed = Path(temporary)/"changed.zip"
                with zipfile.ZipFile(source) as old, zipfile.ZipFile(changed, "w") as new:
                    for name in old.namelist():
                        data = old.read(name)
                        if name.endswith("/desktop-build.json"):
                            record=json.loads(data); record[key]=value; data=json.dumps(record).encode()
                        new.writestr(name,data)
                with self.assertRaisesRegex(ValueError, "version|source|Tag"):
                    verify_mac(changed, ORIGIN, TAG, SOURCES["desktop"], DESKTOP_TAG)

    def test_rejects_macos_package_with_different_cloud_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest, assets, cloud, agent = self.fixture(Path(temporary), "https://wrong.example")
            with self.assertRaisesRegex(ValueError, "wrong Cloud origin"):
                package(TAG, ORIGIN, manifest, assets, cloud, agent, SOURCES, DESKTOP_TAG)


if __name__ == "__main__":
    unittest.main()
