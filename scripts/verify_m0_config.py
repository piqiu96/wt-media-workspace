#!/usr/bin/env python3
"""Validate M0 contract map and release matrix invariants."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTER_ROOT = ROOT.parent

EXPECTED_CONTRACTS = {
    "cloud_api": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-api"),
    "cloud_agent_api": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-agent-api"),
    "business_schemas": ("wt-media-cloud", "../wt-media-cloud/contracts/business-schemas"),
    "task_schemas": ("wt-media-cloud", "../wt-media-cloud/contracts/task-schemas"),
    "business_enums": ("wt-media-cloud", "../wt-media-cloud/contracts/business-enums"),
    "cloud_error_codes": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-error-codes"),
    "local_agent_api": ("wt-media-agent", "../wt-media-agent/contracts/local-agent-api"),
    "local_event_schemas": ("wt-media-agent", "../wt-media-agent/contracts/local-event-schemas"),
    "local_status_enums": ("wt-media-agent", "../wt-media-agent/contracts/local-status-enums"),
    "local_error_codes": ("wt-media-agent", "../wt-media-agent/contracts/local-error-codes"),
}


def parse_contract_map(text: str) -> dict[str, dict[str, str]]:
    contracts: dict[str, dict[str, str]] = {}
    current: str | None = None
    in_contracts = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line == "contracts:":
            in_contracts = True
            continue
        if not in_contracts:
            continue
        if line.startswith("  ") and line.endswith(":") and not line.startswith("    "):
            current = line.strip().removesuffix(":")
            contracts[current] = {}
            continue
        if current and line.startswith("    ") and ": " in line:
            key, value = line.strip().split(": ", 1)
            contracts[current][key] = value.strip('"')
    return contracts


def validate_contract_map(allow_missing_repos: bool) -> list[str]:
    path = ROOT / "config" / "contract-map.yaml"
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    for required in (
        "schema_version: 1",
        "contract_state: placeholder_only",
        "formal_definitions_active: false",
    ):
        if required not in text:
            errors.append(f"contract-map.yaml missing {required!r}")

    contracts = parse_contract_map(text)
    if set(contracts) != set(EXPECTED_CONTRACTS):
        errors.append(
            "contract-map.yaml contract keys mismatch: "
            f"expected {sorted(EXPECTED_CONTRACTS)}, got {sorted(contracts)}"
        )

    for name, (owner, rel_path) in EXPECTED_CONTRACTS.items():
        actual = contracts.get(name, {})
        if actual.get("owner") != owner:
            errors.append(f"{name}: expected owner {owner!r}, got {actual.get('owner')!r}")
        if actual.get("path") != rel_path:
            errors.append(f"{name}: expected path {rel_path!r}, got {actual.get('path')!r}")
        if actual.get("state") != "placeholder_only":
            errors.append(f"{name}: state must be placeholder_only")
        if actual.get("formal_definition") != "inactive":
            errors.append(f"{name}: formal_definition must be inactive")

        provider_path = (ROOT / rel_path).resolve()
        if not provider_path.is_dir() and not allow_missing_repos:
            errors.append(f"{name}: provider path does not exist: {provider_path}")

    return errors


def validate_release_matrix() -> list[str]:
    path = ROOT / "config" / "release-matrix.yaml"
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    required = (
        'release: "0.1.0-m0-health"',
        "status: verified",
        "scope: m0_scaffold_health",
        "contract_state: placeholder_only",
        "formal_contract_versions_active: false",
        "ci_go_version: \"1.26.5\"",
        "ci_python_version: \"3.12\"",
        "ci_node_version: \"25\"",
    )
    for needle in required:
        if needle not in text:
            errors.append(f"release-matrix.yaml missing {needle!r}")

    for name in EXPECTED_CONTRACTS:
        if f"{name}: m0-placeholder" not in text:
            errors.append(f"release-matrix.yaml must mark {name} as m0-placeholder")

    forbidden = ("cloud_api: v1", "cloud_agent_api: v1", "local_agent_api: v1")
    for needle in forbidden:
        if needle in text:
            errors.append(f"release-matrix.yaml must not claim active formal version {needle!r}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-missing-repos",
        action="store_true",
        help="skip provider path existence checks for single-repo CI checkouts",
    )
    args = parser.parse_args()

    errors = []
    errors.extend(validate_contract_map(allow_missing_repos=args.allow_missing_repos))
    errors.extend(validate_release_matrix())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("M0 config verification ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
