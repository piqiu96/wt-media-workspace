#!/usr/bin/env python3
"""Validate workspace contract map and release matrix invariants."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTER_ROOT = ROOT.parent

# map 条目里承载日期版本的字段。
REVISION_FIELDS = (
    "contract_revision",
    "schema_revision",
    "error_revision",
    "event_revision",
    "enum_revision",
)

# 只匹配定义文件中的日期版本，避开其他名为 version 的字段。
REVISION_LINE = re.compile(r'^revision:\s*"?(\d{4}\.\d{2}\.\d{2}\.\d+)"?\s*$', re.MULTILINE)
OPENAPI_VERSION_LINE = re.compile(r"^ {2,6}version:\s*(\d{4}\.\d{2}\.\d{2}\.\d+)\s*$", re.MULTILINE)

EXPECTED_CONTRACTS = {
    "cloud_api": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-api"),
    "cloud_agent_api": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-agent-api"),
    "business_schemas": ("wt-media-cloud", "../wt-media-cloud/contracts/business-schemas"),
    "business_enums": ("wt-media-cloud", "../wt-media-cloud/contracts/business-enums"),
    "cloud_error_codes": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-error-codes"),
    "local_agent_api": ("wt-media-agent", "../wt-media-agent/contracts/local-agent-api"),
    "local_event_schemas": ("wt-media-agent", "../wt-media-agent/contracts/local-event-schemas"),
    "local_status_enums": ("wt-media-agent", "../wt-media-agent/contracts/local-status-enums"),
    "local_error_codes": ("wt-media-agent", "../wt-media-agent/contracts/local-error-codes"),
}


def revision_order(value: str) -> tuple[int, int, int, int]:
    # 修订序号按数值比较，避免 10 排在 9 前面。
    return tuple(int(part) for part in value.split("."))


def definition_revision_max(provider_path: Path) -> tuple[str | None, str]:
    """定义目录里最新的日期版本值，及它所在的文件名；找不到返回 (None, "")。"""
    best: str | None = None
    best_file = ""
    for found in sorted(provider_path.rglob("*.yaml")) + sorted(provider_path.rglob("*.yml")):
        text = found.read_text(encoding="utf-8")
        for value in REVISION_LINE.findall(text) + OPENAPI_VERSION_LINE.findall(text):
            if best is None or revision_order(value) > revision_order(best):
                best, best_file = value, found.name
    return best, best_file


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

    for name, (owner, rel_path) in EXPECTED_CONTRACTS.items():
        actual = contracts.get(name, {})
        if actual.get("owner") != owner:
            errors.append(f"{name}: expected owner {owner!r}, got {actual.get('owner')!r}")
        if actual.get("path") != rel_path:
            errors.append(f"{name}: expected path {rel_path!r}, got {actual.get('path')!r}")
        if actual.get("state") != "active":
            errors.append(f"{name}: expected state 'active', got {actual.get('state')!r}")
        if actual.get("formal_definition") != "active":
            errors.append(
                f"{name}: expected formal_definition 'active', "
                f"got {actual.get('formal_definition')!r}"
            )
        # 修订值以提供方定义为准，避免在脚本中再维护日期常量。
        provider_path = (ROOT / rel_path).resolve()
        if not provider_path.is_dir() and not allow_missing_repos:
            errors.append(f"{name}: provider path does not exist: {provider_path}")

        # contract-map 记录定义目录中的最新修订值。
        if provider_path.is_dir():
            field = next((k for k in REVISION_FIELDS if k in actual), None)
            if field is None:
                errors.append(f"{name}: contract-map entry has no revision field")
            else:
                def_max, def_file = definition_revision_max(provider_path)
                if def_max is None:
                    errors.append(f"{name}: no dated revision found in {provider_path}")
                elif actual.get(field) != def_max:
                    errors.append(
                        f"{name}: map {field} {actual.get(field)!r} != definition "
                        f"latest {def_max!r} ({def_file})"
                    )

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
        'local_event_schemas: "status@2026.07.14.6"',
        'local_status_enums: "status@2026.07.14.6"',
        'cloud_error_codes: "agent-runtime@2026.07.14.4"',
        'local_event_schemas: "runtime-environment@2026.07.14.9"',
        'local_status_enums: "status@2026.07.14.7"',
        'cloud_error_codes: "profile-guard@2026.07.14.5"',
        "ci_go_version: \"1.26.5\"",
        "ci_python_version: \"3.12\"",
        "ci_node_version: \"26\"",
        "ci_rust_toolchain: stable",
        "M0-R4 verified real Vue/Vite/Tauri Rust test/build/start/health/stop loop",
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

    forbidden = ("cloud_api: v1", "local_agent_api: v1")
    for needle in forbidden:
        if needle in text:
            errors.append(f"release-matrix.yaml must not claim active formal version {needle!r}")

    return errors


def validate_ci_workflows(allow_missing_repos: bool) -> list[str]:
    """Check required workflow entries; text presence does not prove a step ran."""
    errors: list[str] = []
    expected = {
        "wt-media-cloud/.github/workflows/m0-cloud.yml": (
            "services:",
            "mysql:8.4",
            "node-version: \"26\"",
            "scripts/bootstrap.sh",
            "scripts/test.sh",
            "scripts/migrate.sh",
        ),
        "wt-media-agent/.github/workflows/m0-agent.yml": (
            "astral-sh/setup-uv@v5",
            "scripts/bootstrap.sh",
            "scripts/test.sh",
            "scripts/migrate-storage.sh",
            "scripts/build.sh",
        ),
        "wt-media-desktop/.github/workflows/m0-desktop.yml": (
            "runs-on: macos-latest",
            "dtolnay/rust-toolchain@stable",
            "scripts/test.sh",
        ),
    }
    for rel_path, needles in expected.items():
        path = OUTER_ROOT / rel_path
        if not path.is_file():
            if not allow_missing_repos:
                errors.append(f"missing CI workflow: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel_path} missing {needle!r}")

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
    errors.extend(validate_ci_workflows(allow_missing_repos=args.allow_missing_repos))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Workspace config verification ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
