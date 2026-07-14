from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "verify_m2_acceptance.py"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_m2_acceptance", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify_m2_acceptance.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class VerifyM2AcceptanceTests(unittest.TestCase):
    def test_static_cross_repo_contract_and_security_matrix(self) -> None:
        module = load_module()
        missing = [path for path in module.required_repository_paths() if not path.exists()]
        if missing:
            self.skipTest(f"runtime sibling repositories unavailable: {missing}")
        self.assertEqual(module.validate_static_matrix(), [])


if __name__ == "__main__":
    unittest.main()
