from __future__ import annotations

import tempfile
import tomllib
import unittest
from pathlib import Path

from scripts.release.stage_config import stage_config


DESKTOP = '''environment = "production"
[agent]
host = "127.0.0.1"
port = 8765
[cloud]
base_url = "http://127.0.0.1:8188"
[browser]
csp_connect_src = "ipc: http://ipc.localhost http://127.0.0.1:8188"
'''
AGENT = '''environment = "production"
[cloud]
base_url = "http://127.0.0.1:8188"
[local_api]
host = "127.0.0.1"
port = 8765
'''


class ReleaseStageConfigTest(unittest.TestCase):
    def test_stages_same_cloud_origin_without_changing_local_api(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            desktop = Path(temporary) / "desktop.toml"
            agent = Path(temporary) / "agent.toml"
            desktop.write_text(DESKTOP, encoding="utf-8")
            agent.write_text(AGENT, encoding="utf-8")
            stage_config(desktop, agent, "https://wt.longyanyue.cn")
            d = tomllib.loads(desktop.read_text(encoding="utf-8"))
            a = tomllib.loads(agent.read_text(encoding="utf-8"))
            self.assertEqual(d["cloud"]["base_url"], "https://wt.longyanyue.cn")
            self.assertEqual(a["cloud"]["base_url"], "https://wt.longyanyue.cn")
            self.assertIn("https://wt.longyanyue.cn", d["browser"]["csp_connect_src"])
            self.assertEqual(d["agent"], {"host": "127.0.0.1", "port": 8765})
            self.assertEqual(a["local_api"], {"host": "127.0.0.1", "port": 8765})

    def test_refuses_missing_cloud_setting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            desktop = Path(temporary) / "desktop.toml"
            agent = Path(temporary) / "agent.toml"
            desktop.write_text(DESKTOP.replace('base_url = "http://127.0.0.1:8188"', ''), encoding="utf-8")
            agent.write_text(AGENT, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cloud.base_url"):
                stage_config(desktop, agent, "https://wt.longyanyue.cn")


if __name__ == "__main__":
    unittest.main()
