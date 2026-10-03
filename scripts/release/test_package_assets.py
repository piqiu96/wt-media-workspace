"""The product release accepts the deployable Cloud payload without accepting secrets."""

from __future__ import annotations

import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts.release.package_assets import sha256, verify_cloud, verify_cloud_artifact_checksums


TAG = "v0.1.0-rc.7"
COMMIT = "a" * 40


class CloudPayloadTest(unittest.TestCase):
    def make_archive(self, credential: str = "", commit: str = COMMIT) -> Path:
        root = f"wt-media-cloud_{TAG}_linux-amd64/"
        files = {
            "bin/server": b"ELF", "bin/discovery-scheduler": b"ELF",
            "bin/discovery-worker": b"ELF", "bin/migrate": b"ELF",
            "bin/ffmpeg": b"ELF", "bin/ffprobe": b"ELF",
            "web/index.cloud.html": b"<html></html>",
            "ffmpeg-source.json": b"{}",
            "migrations/001_identity.sql": b"CREATE TABLE users (id INT);",
            "deploy/DEPLOYMENT.md": b"# Deployment",
            "deploy/prepare-database.sql.example": b"CREATE DATABASE example;",
            "deploy/nginx-site-locations.conf.example": b"root /example/web;\n",
            "deploy/install.sh": b"#!/bin/bash\n",
            "deploy/init-config.sh": b"#!/bin/bash\n",
            "deploy/migrate.sh": b"#!/bin/bash\n",
            "deploy/activate.sh": b"#!/bin/bash\n",
            "deploy/verify-package.sh": b"#!/bin/bash\n",
            "deploy/verify-database.sh": b"#!/bin/bash\n",
            "deploy/verify-runtime.sh": b"#!/bin/bash\n",
            "deploy/rollback.sh": b"#!/bin/bash\n",
            "deploy/systemd/wt-media-cloud-server.service": b"[Service]\n",
            "deploy/systemd/wt-media-cloud-scheduler.service": b"[Service]\n",
            "deploy/systemd/wt-media-cloud-worker.service": b"[Service]\n",
            "deploy/config-template/app.toml": b"[initial_admin]\npassword = ''\n",
            "deploy/config-template/database/primary.toml": b"password = ''\n",
            "deploy/config-template/credentials/agent.toml": f"auth_token = '{credential}'\n".encode(),
            "deploy/config-template/credentials/douyin.toml": b"api_key = ''\ncookie = ''\n",
            "deploy/config-template/credentials/object_storage.toml.example": b"access_key = ''\nsecret_key = ''\n",
            "release-info.json": json.dumps({"product_tag": TAG, "source_commit": commit}).encode(),
        }
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        archive_path = Path(tmp.name) / "cloud.tar.gz"
        with tarfile.open(archive_path, "w:gz") as archive:
            for relative, content in files.items():
                header = tarfile.TarInfo(root + relative)
                header.size = len(content)
                archive.addfile(header, io.BytesIO(content))
        return archive_path

    def test_accepts_blank_deployment_template(self) -> None:
        verify_cloud(self.make_archive(), TAG, COMMIT)

    def test_rejects_populated_credential(self) -> None:
        with self.assertRaisesRegex(ValueError, "nonempty credential"):
            verify_cloud(self.make_archive(credential="secret"), TAG, COMMIT)

    def test_rejects_source_commit_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "source Commit"):
            verify_cloud(self.make_archive(commit="b" * 40), TAG, COMMIT)

    def test_checks_both_cloud_artifact_digests(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        directory = Path(tmp.name)
        cloud = directory / "cloud.tar.gz"
        web = directory / "desktop-web.tar.gz"
        cloud.write_bytes(b"cloud")
        web.write_bytes(b"web")
        (directory / "SHA256SUMS").write_text(
            f"{sha256(cloud)}  {cloud.name}\n{sha256(web)}  {web.name}\n",
            encoding="utf-8",
        )
        verify_cloud_artifact_checksums(directory, cloud, web)
        web.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            verify_cloud_artifact_checksums(directory, cloud, web)


if __name__ == "__main__":
    unittest.main()
