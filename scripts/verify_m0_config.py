#!/usr/bin/env python3
"""Validate workspace contract map and release matrix invariants."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTER_ROOT = ROOT.parent

EXPECTED_CONTRACTS = {
    "cloud_api": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-api", "placeholder_only", "inactive"),
    "cloud_agent_api": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-agent-api", "active", "active"),
    "business_schemas": ("wt-media-cloud", "../wt-media-cloud/contracts/business-schemas", "placeholder_only", "inactive"),
    "task_schemas": ("wt-media-cloud", "../wt-media-cloud/contracts/task-schemas", "placeholder_only", "inactive"),
    "business_enums": ("wt-media-cloud", "../wt-media-cloud/contracts/business-enums", "placeholder_only", "inactive"),
    "cloud_error_codes": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-error-codes", "placeholder_only", "inactive"),
    "local_agent_api": ("wt-media-agent", "../wt-media-agent/contracts/local-agent-api", "placeholder_only", "inactive"),
    "local_event_schemas": ("wt-media-agent", "../wt-media-agent/contracts/local-event-schemas", "placeholder_only", "inactive"),
    "local_status_enums": ("wt-media-agent", "../wt-media-agent/contracts/local-status-enums", "placeholder_only", "inactive"),
    "local_error_codes": ("wt-media-agent", "../wt-media-agent/contracts/local-error-codes", "placeholder_only", "inactive"),
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
        "contract_state: m1_task_claim_lease",
        "formal_definitions_active: true",
    ):
        if required not in text:
            errors.append(f"contract-map.yaml missing {required!r}")

    contracts = parse_contract_map(text)
    if set(contracts) != set(EXPECTED_CONTRACTS):
        errors.append(
            "contract-map.yaml contract keys mismatch: "
            f"expected {sorted(EXPECTED_CONTRACTS)}, got {sorted(contracts)}"
        )

    for name, (owner, rel_path, state, formal_definition) in EXPECTED_CONTRACTS.items():
        actual = contracts.get(name, {})
        if actual.get("owner") != owner:
            errors.append(f"{name}: expected owner {owner!r}, got {actual.get('owner')!r}")
        if actual.get("path") != rel_path:
            errors.append(f"{name}: expected path {rel_path!r}, got {actual.get('path')!r}")
        if actual.get("state") != state:
            errors.append(f"{name}: expected state {state!r}, got {actual.get('state')!r}")
        if actual.get("formal_definition") != formal_definition:
            errors.append(
                f"{name}: expected formal_definition {formal_definition!r}, "
                f"got {actual.get('formal_definition')!r}"
            )
        if name == "cloud_agent_api":
            for key, value in (
                ("api_major_version", "v1"),
                ("contract_revision", "2026.07.14.3"),
                ("minimum_agent_contract_revision", "2026.07.14.3"),
                ("compatibility_endpoint", "/api/v1/cloud-agent/compatibility"),
            ):
                if actual.get(key) != value:
                    errors.append(f"{name}: expected {key} {value!r}, got {actual.get(key)!r}")

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
        'release: "0.1.0-m1-cloud-agent-compatibility"',
        'release: "0.1.0-m1-agent-heartbeat"',
        'release: "0.1.0-m1-task-lease"',
        "status: verified",
        "scope: m0_scaffold_health",
        "scope: m1_cloud_agent_contract_compatibility",
        "scope: m1_agent_registration_heartbeat",
        "scope: m1_task_creation_claim_lease",
        "contract_state: placeholder_only",
        "contract_state: m1_cloud_agent_compatibility",
        "contract_state: m1_agent_registration_heartbeat",
        "contract_state: m1_task_claim_lease",
        "formal_contract_versions_active: false",
        "formal_contract_versions_active: true",
        'cloud_agent_api: "v1@2026.07.14.1"',
        'cloud_agent_api: "v1@2026.07.14.2"',
        'cloud_agent_api: "v1@2026.07.14.3"',
        "ci_go_version: \"1.26.5\"",
        "ci_python_version: \"3.12\"",
        "ci_node_version: \"25\"",
    )
    for needle in required:
        if needle not in text:
            errors.append(f"release-matrix.yaml missing {needle!r}")

    for name in EXPECTED_CONTRACTS:
        if name == "cloud_agent_api":
            if 'cloud_agent_api: "v1@2026.07.14.3"' not in text:
                errors.append("release-matrix.yaml must mark cloud_agent_api as v1@2026.07.14.3")
            continue
        if f"{name}: m0-placeholder" not in text:
            errors.append(f"release-matrix.yaml must keep {name} as m0-placeholder")

    forbidden = ("cloud_api: v1", "local_agent_api: v1", "task_schemas: v1")
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

    print("Workspace config verification ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
