"""The formal Desktop pipeline must never publish a dev/test identity."""
from pathlib import Path
import unittest

import yaml


class DesktopReleaseIdentityTest(unittest.TestCase):
    def test_formal_desktop_job_pins_production_gate(self):
        root = Path(__file__).resolve().parents[1]
        workflow = yaml.safe_load((root / ".github/workflows/release.yml").read_text())
        job = workflow["jobs"]["build-desktop"]
        self.assertEqual(job["env"]["WT_MEDIA_DESKTOP_ENVIRONMENT"], "prod")
        self.assertEqual(job["env"]["WT_MEDIA_DESKTOP_RELEASE_CHANNEL"], "stable")
        build_steps = [step for step in job["steps"] if "build-desktop-environment.py" in step.get("run", "")]
        self.assertTrue(build_steps)
        self.assertTrue(all("--debug" not in step["run"] for step in build_steps))
