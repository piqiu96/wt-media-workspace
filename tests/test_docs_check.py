from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


CHECKER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "docs" / "check.py"
STABLE = "<!-- governance: class=stable default_load=task -->"
INDEX = "<!-- governance: class=index default_load=task -->"
ALWAYS = "<!-- governance: class=index default_load=always -->"
HISTORICAL = "<!-- governance: class=historical default_load=never -->"


def load_checker():
    spec = importlib.util.spec_from_file_location("docs_check", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load scripts/docs/check.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DocsCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.checker = load_checker()
        self.build_compliant_tree()

    def write(self, relative: str, body: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def build_compliant_tree(self) -> None:
        for directory in ("bin", "config", "skills", "scripts"):
            (self.root / directory).mkdir()
        self.write("docs/README.md", ALWAYS + """
# Documents

- [Product](product/README.md)
- [Engineering](engineering/README.md)
- [Standards](standards/README.md)
- [Contracts](contracts/README.md)
- [Decisions](decisions/README.md)
- [DevOps](devops/README.md)
- [Reference](reference/README.md)
- [History](superpowers/README.md)
""")
        for directory in (
            "docs/product", "docs/engineering", "docs/standards",
            "docs/contracts", "docs/decisions", "docs/devops", "docs/reference",
        ):
            self.write(f"{directory}/README.md", STABLE + "\n# Index\n")
        self.write("docs/engineering/specs/README.md", INDEX + """
# Specs

- [Alpha](alpha.md)
""")
        self.write("docs/engineering/specs/alpha.md", "# Alpha\n")
        self.write("docs/standards/frontend/README.md", INDEX + "\n# Frontend\n")
        self.write("docs/reference/state-models/README.md", STABLE + "\n# State models\n")
        self.write("docs/superpowers/README.md", HISTORICAL + "\n# History\n")
        for directory in ("delivery/milestones", "delivery/planned"):
            self.write(f"{directory}/README.md", INDEX + "\n# Index\n")
        self.write("delivery/reports/README.md", HISTORICAL + "\n# Reports\n")
        self.write("delivery/completed/README.md", "# Archive\n\n- 归档边界：`READ-ONLY`\n")
        self.write("AGENT-INDEX.md", """
# Index

## 3. 系统事实来源

- `docs/`
- `delivery/`
- `config/`
- `skills/`
- `scripts/`
- `bin/`

## 4. 上下文加载

### 默认不加载

- `docs/superpowers/`
- `delivery/reports/`
""")

    def check(self) -> list[str]:
        return self.checker.check(self.root)

    def test_compliant_tree_has_no_errors(self) -> None:
        self.assertEqual(self.check(), [])

    def test_missing_index_is_reported(self) -> None:
        (self.root / "docs/contracts/README.md").unlink()
        errors = self.check()
        self.assertIn("missing documentation index: docs/contracts/README.md", errors)

    def test_missing_marker_is_reported(self) -> None:
        self.write("docs/contracts/README.md", "# Contracts\n")
        errors = self.check()
        self.assertIn(
            "expected exactly one governance marker in docs/contracts/README.md, found 0",
            errors,
        )

    def test_historical_marker_requires_never(self) -> None:
        self.write(
            "docs/superpowers/README.md",
            "<!-- governance: class=historical default_load=task -->\n# History\n",
        )
        self.assertIn(
            "docs/superpowers/README.md: historical documents must use default_load=never",
            self.check(),
        )

    def test_unregistered_top_level_directory_is_reported(self) -> None:
        self.write("docs/extra/README.md", STABLE + "\n# Extra\n")
        self.assertIn(
            "docs/extra/ is not registered in docs/README.md",
            self.check(),
        )

    def test_registered_directory_must_exist(self) -> None:
        self.write(
            "docs/README.md",
            ALWAYS + "\n- [Ghost](ghost/README.md)\n",
        )
        errors = self.check()
        self.assertIn(
            "docs/README.md registers a missing directory: docs/ghost/",
            errors,
        )

    def test_missing_agent_index_path_is_reported(self) -> None:
        self.write("AGENT-INDEX.md", """
# Index

## 3. 系统事实来源

- `docs/missing/`
- `delivery/`

## 4. 上下文加载

### 默认不加载

- `docs/superpowers/`
- `delivery/reports/`
""")
        self.assertIn(
            "AGENT-INDEX.md section 3 path does not exist: docs/missing/",
            self.check(),
        )

    def test_history_must_be_excluded_from_default_load(self) -> None:
        self.write("AGENT-INDEX.md", """
# Index

## 3. 系统事实来源

- `docs/`

## 4. 上下文加载

### 默认不加载

- `delivery/completed/`
""")
        errors = self.check()
        self.assertIn(
            "AGENT-INDEX.md section 4 must list docs/superpowers/ as not loaded by default",
            errors,
        )
        self.assertIn(
            "AGENT-INDEX.md section 4 must list delivery/reports/ as not loaded by default",
            errors,
        )

    def test_broken_relative_link_is_reported(self) -> None:
        self.write("docs/product/README.md", STABLE + "\n[Missing](../missing.md)\n")
        self.assertIn(
            "broken relative link: docs/product/README.md -> ../missing.md",
            self.check(),
        )

    def test_links_with_anchors_and_web_urls_are_valid(self) -> None:
        self.write(
            "docs/product/README.md",
            STABLE + "\n[Alpha](../engineering/specs/alpha.md#alpha)\n[Web](https://example.test/a)\n",
        )
        self.assertEqual(self.check(), [])

    def test_code_is_not_scanned_for_markers_or_links(self) -> None:
        self.write(
            "docs/product/README.md",
            STABLE + "\n```markdown\n[Missing](missing.md)\n"
            "<!-- governance: class=historical default_load=task -->\n```\n"
            "`[Missing](also-missing.md)`\n",
        )
        self.assertEqual(self.check(), [])

    def test_unlisted_spec_is_reported(self) -> None:
        self.write("docs/engineering/specs/beta.md", "# Beta\n")
        self.assertIn(
            "spec is not listed in docs/engineering/specs/README.md: beta.md",
            self.check(),
        )

    def test_completed_boundary_marker_is_required(self) -> None:
        self.write("delivery/completed/README.md", "# Archive\n")
        self.assertIn(
            "delivery/completed/README.md is missing the archive boundary marker "
            "(- 归档边界：`READ-ONLY`)",
            self.check(),
        )


if __name__ == "__main__":
    unittest.main()
