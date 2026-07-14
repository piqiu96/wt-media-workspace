from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


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

    def test_contract_map_is_m0_placeholder_only(self) -> None:
        errors = self.module.validate_contract_map(allow_missing_repos=False)
        self.assertEqual(errors, [])

    def test_release_matrix_matches_m0_health_release(self) -> None:
        errors = self.module.validate_release_matrix()
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
