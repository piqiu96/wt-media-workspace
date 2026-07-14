#!/usr/bin/env python3
"""Static cross-repository M2 acceptance matrix.

Real MySQL and BitBrowser checks are intentionally separate: this verifier
must never turn fixture evidence into a real-integration PASS.
"""

from __future__ import annotations

import json
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
ROOT = WORKSPACE.parent
CLOUD = ROOT / "wt-media-cloud"
AGENT = ROOT / "wt-media-agent"
DESKTOP = ROOT / "wt-media-desktop"


def required_repository_paths() -> list[Path]:
    return [WORKSPACE, CLOUD, AGENT, DESKTOP]


def require_contains(errors: list[str], path: Path, needles: tuple[str, ...]) -> None:
    if not path.is_file():
        errors.append(f"missing file: {path}")
        return
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            errors.append(f"{path}: missing {needle!r}")


def validate_static_matrix() -> list[str]:
    errors: list[str] = []
    for path in required_repository_paths():
        if not path.is_dir():
            errors.append(f"missing repository: {path}")
    if errors:
        return errors

    require_contains(
        errors,
        WORKSPACE / "config" / "contract-map.yaml",
        (
            "contract_state: m2_sensitive_profile_guard",
            'cloud_agent_api:',
            'contract_revision: "2026.07.14.6"',
            'error_revision: "2026.07.14.5"',
            'event_revision: "2026.07.14.8"',
            'enum_revision: "2026.07.14.8"',
        ),
    )
    require_contains(
        errors,
        WORKSPACE / "config" / "release-matrix.yaml",
        tuple(
            f'release: "{release}"'
            for release in (
                "0.2.0-m2-identity-access",
                "0.2.1-m2-media-accounts",
                "0.2.2-m2-bitbrowser-profile-binding",
                "0.2.3-m2-agent-runtime-binding",
                "0.2.4-m2-sensitive-profile-guard",
            )
        ),
    )
    require_contains(
        errors,
        CLOUD / "internal" / "modules" / "cloudagent" / "compatibility.go",
        ('ContractRevision             = "2026.07.14.6"', 'MinimumAgentContractRevision = "2026.07.14.6"'),
    )
    for migration in range(1, 6):
        matches = list((CLOUD / "migrations").glob(f"20260714_00{migration}_*.sql"))
        if len(matches) != 1:
            errors.append(f"expected one M2 migration 00{migration}, got {matches}")
    require_contains(
        errors,
        CLOUD / "contracts" / "cloud-agent-api" / "v1" / "sensitive-profile-guard.openapi.yaml",
        ("version: 2026.07.14.6", "review_required", "X-Profile-Permit"),
    )
    require_contains(
        errors,
        AGENT / "src" / "wt_media_agent" / "cloud_agent_contract.py",
        ('REQUIRED_CONTRACT_REVISION = "2026.07.14.6"',),
    )
    require_contains(errors, AGENT / "pyproject.toml", ('version = "0.2.2"',))
    require_contains(
        errors,
        AGENT / "contracts" / "local-event-schemas" / "v1" / "profile-guard.yaml",
        ('revision: "2026.07.14.8"', "result_uncertain"),
    )

    lock_path = DESKTOP / "contracts.lock.json"
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"could not parse {lock_path}: {error}")
    else:
        expected = {
            "cloud_agent_api": "v1@2026.07.14.6",
            "local_agent_api": "v1@2026.07.14.6",
            "local_event_schemas": "profile-guard@2026.07.14.8",
            "local_status_enums": "status@2026.07.14.8",
        }
        if lock.get("consumes") != expected:
            errors.append(f"Desktop contract lock mismatch: {lock.get('consumes')!r}")
    require_contains(
        errors,
        DESKTOP / "src" / "services" / "local-agent.js",
        ('bindSession: "local_agent_bind_session"', "async bindSession(bindingTicket)"),
    )

    sensitive_files = [
        CLOUD / "migrations" / "20260714_004_agent_runtime.sql",
        CLOUD / "migrations" / "20260714_005_sensitive_profile_locks.sql",
        DESKTOP / "src" / "services" / "local-agent.js",
    ]
    forbidden = ("binding_token varchar", "node_credential varchar", "permit_credential varchar", "localstorage", "sessionstorage")
    for path in sensitive_files:
        text = path.read_text(encoding="utf-8").lower()
        for needle in forbidden:
            if needle in text:
                errors.append(f"{path}: forbidden secret persistence marker {needle!r}")

    return errors


def main() -> int:
    errors = validate_static_matrix()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("M2 static cross-repository acceptance matrix ok")
    print("NOTE: real MySQL and BitBrowser evidence must be recorded separately")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
