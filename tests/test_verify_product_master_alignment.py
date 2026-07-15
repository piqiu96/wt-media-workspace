from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "verify_product_master_alignment.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_product_master_alignment", SCRIPT_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify_product_master_alignment.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ProductMasterAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()
        self.master = (ROOT / "delivery" / "MASTER_IMPLEMENTATION_PLAN.md").read_text(
            encoding="utf-8"
        )

    def test_current_product_master_and_governance_are_aligned(self) -> None:
        self.assertEqual(self.module.validate_alignment(ROOT), [])

    def test_rejects_reopened_milestone_status_regression(self) -> None:
        changed = self.master.replace(
            "| 状态 | `VERIFYING` |", "| 状态 | `DONE` |", 1
        )

        errors = self.module.validate_master_text(changed)

        self.assertTrue(any("M0 status" in error for error in errors), errors)

    def test_rejects_stale_operational_object_in_candidate_chg(self) -> None:
        changed = self.master.replace(
            "M3-C6 source_content 全局去重、状态和最新原始 JSON",
            "M3-C6 crawl_result 和 content_lead 入库",
        )

        errors = self.module.validate_master_text(changed)

        self.assertTrue(any("M3 candidate" in error for error in errors), errors)

    def test_rejects_missing_m2_product_capability(self) -> None:
        changed = self.master.replace("代理导入、解析、检测、配额、分配与回读", "网络配置")

        errors = self.module.validate_master_text(changed)

        self.assertTrue(any("M2 capability" in error for error in errors), errors)

    def test_contract_governance_requires_mixed_state_and_placeholder_task_schema(
        self,
    ) -> None:
        human = (ROOT / "docs" / "contracts" / "contract-map.md").read_text(
            encoding="utf-8"
        )
        machine = (ROOT / "config" / "contract-map.yaml").read_text(encoding="utf-8")

        errors = self.module.validate_contract_texts(
            human.replace("Current state is mixed.", "All contracts are active."),
            machine,
        )

        self.assertTrue(any("mixed contract state" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
