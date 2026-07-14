#!/usr/bin/env python3
"""Validate workspace contract map and release matrix invariants."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTER_ROOT = ROOT.parent

EXPECTED_CONTRACTS = {
    "cloud_api": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-api", "active", "active"),
    "cloud_agent_api": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-agent-api", "active", "active"),
    "business_schemas": ("wt-media-cloud", "../wt-media-cloud/contracts/business-schemas", "active", "active"),
    "task_schemas": ("wt-media-cloud", "../wt-media-cloud/contracts/task-schemas", "placeholder_only", "inactive"),
    "business_enums": ("wt-media-cloud", "../wt-media-cloud/contracts/business-enums", "active", "active"),
    "cloud_error_codes": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-error-codes", "active", "active"),
    "local_agent_api": ("wt-media-agent", "../wt-media-agent/contracts/local-agent-api", "active", "active"),
    "local_event_schemas": ("wt-media-agent", "../wt-media-agent/contracts/local-event-schemas", "active", "active"),
    "local_status_enums": ("wt-media-agent", "../wt-media-agent/contracts/local-status-enums", "active", "active"),
    "local_error_codes": ("wt-media-agent", "../wt-media-agent/contracts/local-error-codes", "active", "active"),
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
        "contract_state: m2_sensitive_profile_guard",
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
                ("contract_revision", "2026.07.14.7"),
                ("minimum_agent_contract_revision", "2026.07.14.7"),
                ("compatibility_endpoint", "/api/v1/cloud-agent/compatibility"),
            ):
                if actual.get(key) != value:
                    errors.append(f"{name}: expected {key} {value!r}, got {actual.get(key)!r}")
        if name == "cloud_api":
            if actual.get("api_major_version") != "v1":
                errors.append("cloud_api: expected api_major_version 'v1'")
            if actual.get("contract_revision") != "2026.07.14.4":
                errors.append("cloud_api: expected contract_revision '2026.07.14.4'")
        if name == "business_schemas" and actual.get("schema_revision") != "2026.07.14.4":
            errors.append("business_schemas: expected schema_revision '2026.07.14.4'")
        if name == "business_enums" and actual.get("enum_revision") != "2026.07.14.3":
            errors.append("business_enums: expected enum_revision '2026.07.14.3'")
        if name == "cloud_error_codes" and actual.get("error_revision") != "2026.07.14.5":
            errors.append("cloud_error_codes: expected error_revision '2026.07.14.5'")
        if name == "local_agent_api":
            if actual.get("api_major_version") != "v1":
                errors.append("local_agent_api: expected api_major_version 'v1'")
            if actual.get("contract_revision") != "2026.07.14.7":
                errors.append("local_agent_api: expected contract_revision '2026.07.14.7'")
        if name == "local_event_schemas":
            if actual.get("event_revision") != "2026.07.14.9":
                errors.append("local_event_schemas: expected event_revision '2026.07.14.9'")
        if name == "local_status_enums" and actual.get("enum_revision") != "2026.07.14.8":
            errors.append("local_status_enums: expected enum_revision '2026.07.14.8'")
        if name == "local_error_codes" and actual.get("error_revision") != "2026.07.14.6":
            errors.append("local_error_codes: expected error_revision '2026.07.14.6'")

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
        'release: "0.1.0-m1-noop-status"',
        'release: "0.1.0-m1-local-agent-observability"',
        'release: "0.1.0-m1-desktop-local-agent-controls"',
        'release: "0.1.0-m1-three-end-integration"',
        'release: "0.2.0-m2-identity-access"',
        'release: "0.2.1-m2-media-accounts"',
        'release: "0.2.2-m2-bitbrowser-profile-binding"',
        'release: "0.2.3-m2-agent-runtime-binding"',
        'release: "0.2.4-m2-sensitive-profile-guard"',
        "status: verified",
        "scope: m0_scaffold_health",
        "scope: m1_cloud_agent_contract_compatibility",
        "scope: m1_agent_registration_heartbeat",
        "scope: m1_task_creation_claim_lease",
        "scope: m1_noop_executor_status_reporting",
        "scope: m1_local_agent_http_sse_offline_queue",
        "scope: m1_desktop_local_agent_controls",
        "scope: m1_three_end_integration",
        "scope: m2_user_auth_single_session_fixed_roles",
        "scope: m2_media_account_model_assignment_tags",
        "scope: m2_bitbrowser_user_profile_binding",
        "scope: m2_agent_node_profile_runtime_environment",
        "scope: m2_profile_concurrency_sensitive_preflight",
        "contract_state: placeholder_only",
        "contract_state: m1_cloud_agent_compatibility",
        "contract_state: m1_agent_registration_heartbeat",
        "contract_state: m1_task_claim_lease",
        "contract_state: m1_noop_status_reporting",
        "contract_state: m1_local_agent_observability",
        "contract_state: m1_desktop_local_agent_controls",
        "contract_state: m1_three_end_integration",
        "contract_state: m2_identity_access",
        "contract_state: m2_media_accounts",
        "contract_state: m2_bitbrowser_profile_binding",
        "contract_state: m2_agent_runtime_binding",
        "contract_state: m2_sensitive_profile_guard",
        "formal_contract_versions_active: false",
        "formal_contract_versions_active: true",
        'cloud_agent_api: "v1@2026.07.14.1"',
        'cloud_agent_api: "v1@2026.07.14.2"',
        'cloud_agent_api: "v1@2026.07.14.3"',
        'cloud_agent_api: "v1@2026.07.14.4"',
        'local_agent_api: "v1@2026.07.14.5"',
        'local_event_schemas: "status@2026.07.14.5"',
        'cloud_api: "v1@2026.07.14.1"',
        'business_schemas: "identity@2026.07.14.1"',
        'business_enums: "identity@2026.07.14.1"',
        'cloud_error_codes: "identity@2026.07.14.1"',
        'cloud_api: "v1@2026.07.14.2"',
        'business_schemas: "media-account@2026.07.14.2"',
        'business_enums: "media-account@2026.07.14.2"',
        'cloud_error_codes: "media-account@2026.07.14.2"',
        'cloud_api: "v1@2026.07.14.4"',
        'business_schemas: "browser-profile@2026.07.14.4"',
        'business_enums: "browser-profile@2026.07.14.3"',
        'cloud_error_codes: "browser-profile@2026.07.14.3"',
        'local_agent_api: "v1@2026.07.14.7"',
        'local_event_schemas: "status@2026.07.14.6"',
        'local_status_enums: "status@2026.07.14.6"',
        'local_error_codes: "bitbrowser@2026.07.14.6"',
        'cloud_agent_api: "v1@2026.07.14.7"',
        'cloud_error_codes: "agent-runtime@2026.07.14.4"',
        'local_event_schemas: "runtime-environment@2026.07.14.9"',
        'local_status_enums: "status@2026.07.14.7"',
        'cloud_agent_api: "v1@2026.07.14.7"',
        'cloud_error_codes: "profile-guard@2026.07.14.5"',
        'local_event_schemas: "profile-guard@2026.07.14.8"',
        'local_status_enums: "status@2026.07.14.8"',
        "ci_go_version: \"1.26.5\"",
        "ci_python_version: \"3.12\"",
        "ci_node_version: \"25\"",
    )
    for needle in required:
        if needle not in text:
            errors.append(f"release-matrix.yaml missing {needle!r}")

    active_revisions = {
        "cloud_agent_api": 'cloud_agent_api: "v1@2026.07.14.7"',
        "local_agent_api": 'local_agent_api: "v1@2026.07.14.7"',
        "local_event_schemas": 'local_event_schemas: "profile-guard@2026.07.14.8"',
        "local_status_enums": 'local_status_enums: "status@2026.07.14.8"',
        "local_error_codes": 'local_error_codes: "bitbrowser@2026.07.14.6"',
    }
    for name in EXPECTED_CONTRACTS:
        if name in active_revisions:
            if active_revisions[name] not in text:
                errors.append(
                    f"release-matrix.yaml must mark {name} with {active_revisions[name]!r}"
                )
            continue
        if f"{name}: m0-placeholder" not in text:
            errors.append(f"release-matrix.yaml must retain the historical {name} m0 placeholder")

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
