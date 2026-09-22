from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "agent_config.py"
REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("agent_config", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load agent_config.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AgentConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "config.yaml"

    def write(self, text: str) -> Path:
        self.path.write_text(text, encoding="utf-8")
        return self.path

    def test_reads_nested_mappings_sequences_and_scalars(self) -> None:
        self.write(
            "schema_version: 1\n"
            "\n"
            "# a comment\n"
            "targets:\n"
            "  root:\n"
            '    path: ".."\n'
            "    kind: distribution\n"
            "    commit_generated: false\n"
            "    groups:\n"
            "      - common\n"
            "      - workspace\n"
            "  cloud:\n"
            "    path: ../wt-media-cloud\n"
            "    groups:\n"
            "      - cloud\n"
            "tools:\n"
            "  - codex\n"
            "  - claude\n"
        )

        document = self.module.read_document(self.path)

        self.assertEqual(document["schema_version"], "1")
        self.assertEqual(
            document["targets"]["root"],
            {
                "path": "..",
                "kind": "distribution",
                "commit_generated": False,
                "groups": ["common", "workspace"],
            },
        )
        self.assertEqual(self.module.read_sequence(self.path, "tools"), ["codex", "claude"])

    def test_read_section_requires_a_mapping_of_mappings(self) -> None:
        self.write("repositories:\n  cloud:\n    path: ../wt-media-cloud\n")

        self.assertEqual(
            self.module.read_section(self.path, "repositories"),
            {"cloud": {"path": "../wt-media-cloud"}},
        )

        with self.assertRaises(self.module.ConfigError):
            self.module.read_section(self.path, "tools")

    def test_inline_collections_are_rejected(self) -> None:
        self.write('targets:\n  cloud: ["../wt-media-cloud"]\n')

        with self.assertRaises(self.module.ConfigError) as caught:
            self.module.read_document(self.path)

        self.assertIn("inline collections are not supported", str(caught.exception))

    def test_duplicate_keys_are_rejected(self) -> None:
        self.write("targets:\n  cloud:\n    path: a\n    path: b\n")

        with self.assertRaises(self.module.ConfigError) as caught:
            self.module.read_document(self.path)

        self.assertIn("duplicate key: path", str(caught.exception))

    def test_tab_indentation_is_rejected(self) -> None:
        self.write("targets:\n\tcloud:\n\t\tpath: a\n")

        with self.assertRaises(self.module.ConfigError) as caught:
            self.module.read_document(self.path)

        self.assertIn("tabs are not allowed", str(caught.exception))

    def test_errors_name_the_file_and_line(self) -> None:
        self.write("targets:\n  cloud:\n    path: a\n  broken\n")

        with self.assertRaises(self.module.ConfigError) as caught:
            self.module.read_document(self.path)

        self.assertIn(f"{self.path}:4:", str(caught.exception))

    def test_missing_file_is_reported(self) -> None:
        with self.assertRaises(self.module.ConfigError) as caught:
            self.module.read_document(Path(self.tmp.name) / "absent.yaml")

        self.assertIn("missing configuration file", str(caught.exception))

    def test_the_repository_configuration_files_parse(self) -> None:
        """Guard against the reader drifting from the files it exists to read."""
        config = REPO_ROOT / "config"
        repositories = self.module.read_section(
            config / "repository-map.yaml", "repositories"
        )
        targets = self.module.read_section(config / "skills-distribution.yaml", "targets")

        self.assertIn("cloud", repositories)
        self.assertEqual(
            sorted(repositories), sorted(name for name in targets if name != "root")
        )
        self.assertEqual(
            self.module.read_sequence(config / "skills-distribution.yaml", "tools"),
            ["codex", "claude"],
        )


if __name__ == "__main__":
    unittest.main()
