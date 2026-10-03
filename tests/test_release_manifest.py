from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.release.manifest import validate_manifest


RC = """schema_version: 1
product_tag: v0.1.0-rc.1
channel: rc
environment: staging
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
        content = RC.replace("v0.1.0-rc.1", "v0.1.0")
        with self.assertRaisesRegex(ValueError, "channel"):
            self.validate(content, "v0.1.0")


if __name__ == "__main__":
    unittest.main()
