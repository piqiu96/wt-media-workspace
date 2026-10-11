from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "verify_m0_config.py"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_m0_config", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify_m0_config.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class VerifyM0ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_contract_map_matches_m1_cloud_agent_compatibility(self) -> None:
        errors = self.module.validate_contract_map(allow_missing_repos=True)
        self.assertEqual(errors, [])

    def test_contract_map_provider_paths_exist_in_full_workspace(self) -> None:
        errors = self.module.validate_contract_map(allow_missing_repos=False)
        missing_provider_errors = [
            error for error in errors if "provider path does not exist" in error
        ]
        if missing_provider_errors:
            self.skipTest("runtime sibling repositories are not present in this checkout")
        self.assertEqual(errors, [])

    def test_release_matrix_matches_m0_and_m1_c1_releases(self) -> None:
        errors = self.module.validate_release_matrix()
        self.assertEqual(errors, [])

    def test_release_matrix_allows_local_toolchain_observations_to_change(self) -> None:
        source = (self.module.ROOT / "config" / "release-matrix.yaml").read_text(
            encoding="utf-8"
        )
        updated, count = re.subn(
            r'(?m)^(    local_observed_(?:node|npm|rustc|cargo): ).*$',
            r'\g<1>"99.0.0"',
            source,
        )
        self.assertEqual(count, 4)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "config").mkdir()
            (root / "config" / "release-matrix.yaml").write_text(
                updated, encoding="utf-8"
            )
            with patch.object(self.module, "ROOT", root):
                self.assertEqual(self.module.validate_release_matrix(), [])

    def test_ci_workflows_cover_revised_m0_gates(self) -> None:
        errors = self.module.validate_ci_workflows(allow_missing_repos=True)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
