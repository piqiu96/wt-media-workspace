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
        agent_template = (
            b"auth_token = {{WT_AGENT_AUTH_TOKEN}}\n"
            if not credential
            else f"auth_token = '{credential}'\n".encode()
        )
        config_templates = {
            "config/app.toml": b"password = 'admin123'\n",
            "config/clients/http/agent.toml": b"host = '127.0.0.1'\n",
            "config/clients/http/douyin.toml": b"host = 'api.itfaba.com'\n",
            "config/database/primary.toml.tpl": b"password = {{WT_PRIMARY_DB_PASSWORD}}\n",
            "config/credentials/agent.toml.tpl": agent_template,
            "config/credentials/douyin.toml.tpl": b"api_key = {{WT_DOUYIN_API_KEY}}\n",
            "config/credentials/object_storage.toml.tpl": b"secret_key = {{WT_OBJECT_STORAGE_SECRET_KEY}}\n",
            "config/storage/object_storage.toml.tpl": b"prefix = {{WT_OBJECT_STORAGE_PREFIX}}\n",
        }
        files = {
            "bin/wt-media-cloud": b"ELF", "bin/discovery-scheduler": b"ELF",
            "bin/discovery-worker": b"ELF", "bin/migrate": b"ELF",
            "bin/config-check": b"ELF", "bin/wtmctl": b"ELF", "bin/ffmpeg": b"ELF", "bin/ffprobe": b"ELF",
            "web/index.cloud.html": b"<html></html>",
            "ffmpeg-source.json": b"{}",
            "migrations/001_identity.sql": b"CREATE TABLE users (id INT);",
            "deploy/DEPLOYMENT.md": b"# Deployment",
            "deploy/prepare-database.sql.example": b"CREATE DATABASE example;",
            "deploy/config-variable-schema.toml": b"schema_version = 1\n",
            "deploy/examples/online.toml.example": b"# online\n",
            "deploy/examples/online-deploy.toml.example": b"# profile\n",
            "release-info.json": json.dumps({
                "product_tag": TAG,
                "source_commit": commit,
                "configuration": "template-state config/ rendered by wtmctl",
            }).encode(),
            **config_templates,
        }
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        archive_path = Path(tmp.name) / "cloud.tar.gz"
        with tarfile.open(archive_path, "w:gz") as archive:
            for relative, content in files.items():
                header = tarfile.TarInfo(root + relative)
                header.size = len(content)
                if relative.startswith("bin/"):
                    header.mode = 0o755
                archive.addfile(header, io.BytesIO(content))
        return archive_path

    def test_accepts_blank_deployment_template(self) -> None:
        verify_cloud(self.make_archive(), TAG, COMMIT)

    def test_rejects_populated_credential(self) -> None:
        with self.assertRaisesRegex(ValueError, "WT_AGENT_AUTH_TOKEN"):
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
