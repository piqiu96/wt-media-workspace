#!/usr/bin/env python3
"""Validate workspace contract map and release matrix invariants."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTER_ROOT = ROOT.parent

# map 条目里承载日期版本的字段（每个契约恰有其一）。
REVISION_FIELDS = (
    "contract_revision",
    "schema_revision",
    "error_revision",
    "event_revision",
    "enum_revision",
)

# 定义文件里日期版本的两种行形状：agent 侧 YAML 的行首 `revision: "…"` 与
# openapi `info:` 下缩进的 `version: …`。两处都锚定行首/缩进并要求数值恰为
# 日期形（YYYY.MM.DD.N），避免子串误命中（`app_version:`、schema 里的
# `version: {type: string}`、`const:` 行都不匹配）。
REVISION_LINE = re.compile(r'^revision:\s*"?(\d{4}\.\d{2}\.\d{2}\.\d+)"?\s*$', re.MULTILINE)
OPENAPI_VERSION_LINE = re.compile(r"^ {2,6}version:\s*(\d{4}\.\d{2}\.\d{2}\.\d+)\s*$", re.MULTILINE)

EXPECTED_CONTRACTS = {
    "cloud_api": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-api", "active", "active"),
    "cloud_agent_api": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-agent-api", "active", "active"),
    "business_schemas": ("wt-media-cloud", "../wt-media-cloud/contracts/business-schemas", "active", "active"),
    "task_schemas": ("wt-media-cloud", "../wt-media-cloud/contracts/task-schemas", "active", "active"),
    "business_enums": ("wt-media-cloud", "../wt-media-cloud/contracts/business-enums", "active", "active"),
    "cloud_error_codes": ("wt-media-cloud", "../wt-media-cloud/contracts/cloud-error-codes", "active", "active"),
    "local_agent_api": ("wt-media-agent", "../wt-media-agent/contracts/local-agent-api", "active", "active"),
    "local_event_schemas": ("wt-media-agent", "../wt-media-agent/contracts/local-event-schemas", "active", "active"),
    "local_status_enums": ("wt-media-agent", "../wt-media-agent/contracts/local-status-enums", "active", "active"),
    "local_error_codes": ("wt-media-agent", "../wt-media-agent/contracts/local-error-codes", "active", "active"),
}


def revision_order(value: str) -> tuple[int, int, int, int]:
    # 末段不受零填充保护（9 > 10 会按字典序排错），按数值比较。
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
        # 日期值走活源对比，字段与日期钉子全部退役：硬编码钉子每次合约前进都
        # 要人肉挪，挪漏了就是红灯（CHG-20261003-075 第 2/12 项即两次实例），
        # 而钉子与 map 停在同一个过期值上时会双双通过、看不见真漂移。改为
        # 「map 对定义文件」后，正常演进不再红，map 忘了跟定义一起动反而会被抓。
        # cloud_agent_api 的 minimum_agent_contract_revision 的活源是 cloud 的
        # compatibility.go 常量，由 cloud 自身测试守住，不在本脚本重复。

        provider_path = (ROOT / rel_path).resolve()
        if not provider_path.is_dir() and not allow_missing_repos:
            errors.append(f"{name}: provider path does not exist: {provider_path}")

        # 约定沿用既有口径：map 记该区**最新**的定义版本，各文件自带的 revision
        # 是它自己的；Desktop 的 contracts.lock.json 钉具体文件（profile-guard@…）
        # 而非区最新，两处口径各自正确，由 verify_m2_acceptance.py 派生比对。
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
        "ci_node_version: \"26\"",
        "local_observed_node: \"26.5.0\"",
        "local_observed_npm: \"11.17.0\"",
        "ci_rust_toolchain: stable",
        "local_observed_rustc: \"1.97.0\"",
        "local_observed_cargo: \"1.97.0\"",
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
    """Validate the CI workflows of the three runtime repositories.

    `wt-media-workspace` is deliberately NOT in this list. It carried an entry
    requiring `.github/workflows/m0-workspace.yml` until CHG-20260925-063 removed
    it: that repository has no `.github/` directory and both `AGENT-INDEX.md` §12
    and `agent-workspace-conventions.md` §10 state that it intentionally runs
    these checks locally instead of in CI. The assertion therefore contradicted
    the governance authority and could never pass. Do not re-add it without first
    changing those two governance statements.

    The desktop entry is deliberately Rust-only (CHG-20260926-067 T-02). Until
    then it also required `node-version: "26"`, `scripts/bootstrap.sh`,
    `npm run lint`, and `scripts/build.sh`; none of those describe that
    repository any more — it has no `package.json`, and those three scripts are
    deleted in the same CHG. A needle tuple that cannot be satisfied is not a
    stronger gate, it is an unreachable one.

    Two caveats worth keeping in view before anyone narrows this further. These
    needles are **string checks against the workflow text**: they never proved a
    step actually ran. `npm run lint` had been broken since `7aabb1a` (the file
    pinning it was deleted there) while the needle stayed green. And "Rust-only"
    here means *no Node package toolchain*, not *no Node*: the two shell suites
    under `wt-media-desktop/tests/` still call `node` to read JSON, so the
    workflow keeps `setup-node` — it just no longer caches an npm lockfile.
    """
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
        # Rust-only terminal state (CHG-20260926-067 T-02). Kept minimal on
        # purpose: every needle here must hold under any reasonable desktop
        # workflow, so the entry stays a subset of the text T-03 lands. See the
        # docstring for what was dropped and why.
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
