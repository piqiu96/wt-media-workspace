from __future__ import annotations

import tempfile
import unittest
import subprocess
import sys
from pathlib import Path

from scripts.release.manifest import validate_manifest


RC = """schema_version: 1
product_tag: v0.1.0-rc.1
channel: rc
environment: online
cloud_origin: https://rc.wt-media.invalid
network_smoke: false
components:
  cloud: v0.1.0-rc.1
  agent: v0.2.2-rc.1
  desktop: v0.1.0-rc.1
targets:
  cloud: linux-amd64
  desktop: [windows-x64, macos-x64, macos-arm64]
"""


class ReleaseManifestTest(unittest.TestCase):
    def validate(self, content: str, tag: str = "v0.1.0-rc.1") -> dict:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / f"{tag}.yaml"
            path.write_text(content, encoding="utf-8")
            return validate_manifest(path, tag)

    def test_ci_receives_validated_product_tag_independent_of_component_tag(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            manifest=root/"v0.1.0-rc.1.yaml"
            manifest.write_text(RC.replace("desktop: v0.1.0-rc.1", "desktop: v0.1.0-rc.9"))
            output=root/"output"
            subprocess.run([sys.executable,"scripts/release/manifest.py","--file",str(manifest),"--tag","v0.1.0-rc.1","--github-output",str(output)], check=True, capture_output=True)
            values=dict(line.split("=",1) for line in output.read_text().splitlines())
            self.assertEqual(values["product_tag"],"v0.1.0-rc.1")
            self.assertEqual(values["desktop_tag"],"v0.1.0-rc.9")

    def test_rc_requires_matching_tag_and_fixed_target_matrix(self) -> None:
        result = self.validate(RC)
        self.assertEqual(result["channel"], "rc")
        self.assertEqual(result["components"]["agent"], "v0.2.2-rc.1")
        with self.assertRaisesRegex(ValueError, "product Tag"):
            self.validate(RC, "v0.1.0-rc.2")

    def test_rejects_credentials_in_cloud_origin(self) -> None:
        with self.assertRaisesRegex(ValueError, "Cloud origin"):
            self.validate(RC.replace("https://rc.wt-media.invalid", "https://user:pass@rc.wt-media.invalid"))

    def test_stable_tag_cannot_select_rc_channel(self) -> None:
        content = RC.replace("v0.1.0-rc.1", "v0.1.0").replace("environment: online", "environment: pre")
        with self.assertRaisesRegex(ValueError, "channel"):
            self.validate(content, "v0.1.0")

    def test_rejects_unknown_environment(self) -> None:
        with self.assertRaisesRegex(ValueError, "environment"):
            self.validate(RC.replace("environment: online", "environment: staging"))

    def test_pre_and_online_are_both_valid(self) -> None:
        pre = self.validate(RC.replace("environment: online", "environment: pre"))
        online = self.validate(RC)
        self.assertEqual(pre["environment"], "pre")
        self.assertEqual(online["environment"], "online")


if __name__ == "__main__":
    unittest.main()
