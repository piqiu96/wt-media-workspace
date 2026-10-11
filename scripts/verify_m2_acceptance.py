#!/usr/bin/env python3
"""Static cross-repository M2 acceptance matrix.

Real MySQL and BitBrowser checks are intentionally separate: this verifier
must never turn fixture evidence into a real-integration PASS.

Assertion scope (set by CHG-20260925-063, do not widen without a CHG):

Only DURABLE, contract-layer facts about the runtime repositories are asserted
here: contract revision maps, release-matrix pins, migration files, published
contract YAML, the Desktop contract lock's `consumes` map, and the
secret-persistence invariant. Assertions on the TEXT OF A SOURCE FILE that a
later refactor may legitimately move or rename are deliberately NOT made --
that is what made this script red for months while nothing was actually wrong.
A refactor moving a symbol between files must not be able to turn this gate
red; a contract or schema change must.

Each repository asserts its own implementation in its own test suite. For
example the binding-ticket single-use rule is covered behaviourally by
`wt-media-cloud/internal/modules/runtimebinding/service/service_test.go`
(`TestRegisterConsumesTicketOnceAndIssuesHashedCredential`); this script only
asserts the schema that makes it enforceable, in the applied migration.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# 复用 m0 门禁的锚定抽取器与版本排序，避免两处正则各自漂移。
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_m0_config import REVISION_LINE, definition_revision_max, revision_order


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


def pinned_file_revision(contracts_dir: Path, stem: str) -> str | None:
    """`v1/<stem>.yaml` 自己的 revision——Desktop 锁具体文件时的期望值来源。"""
    path = contracts_dir / "v1" / f"{stem}.yaml"
    if not path.is_file():
        return None
    values = REVISION_LINE.findall(path.read_text(encoding="utf-8"))
    return max(values, key=revision_order) if values else None


def validate_static_matrix() -> list[str]:
    errors: list[str] = []
    for path in required_repository_paths():
        if not path.is_dir():
            errors.append(f"missing repository: {path}")
    if errors:
        return errors

    # contract-map 的日期值不再在此钉字面量：值的一致性由 verify_m0_config 的
    # 「map 对定义文件」活源对比负责，这里只留 M2 范围声明本身。
    require_contains(
        errors,
        WORKSPACE / "config" / "contract-map.yaml",
        ("contract_state: m2_sensitive_profile_guard",),
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
    # Removed by CHG-20260925-063: asserted two Go constants in
    # `cloudagent/compatibility.go`. The file moved to
    # `cloudagent/service/compatibility.go` and both values are unchanged --
    # i.e. the gate went red for a pure file move. The revision values are
    # asserted at the contract layer instead (contract-map.yaml, the published
    # contract YAML, and the Desktop contract lock below).
    for migration in range(1, 6):
        matches = list((CLOUD / "migrations").glob(f"20260714_00{migration}_*.sql"))
        if len(matches) != 1:
            errors.append(f"expected one M2 migration 00{migration}, got {matches}")
    require_contains(
        errors,
        CLOUD / "contracts" / "cloud-agent-api" / "v1" / "sensitive-profile-guard.openapi.yaml",
        ("review_required", "X-Profile-Permit"),
    )
    # Removed by CHG-20260925-063: asserted the literal
    # `REQUIRED_CONTRACT_REVISION = "2026.07.15.1"` in
    # `wt_media_agent/cloud_agent_contract.py`. The constant still exists with
    # that exact value; its definition moved to `clients/cloud/contract.py` and
    # the old module now re-exports it. The revision is asserted at the contract
    # layer instead (contract-map.yaml, and the contract YAML below).
    # Removed by CHG-20261003-075: the agent `pyproject.toml` version snapshot
    # and the two dated-revision literals above. M2 was accepted on 2026-09-14;
    # a released-version snapshot in a standing suite goes red on every honest
    # bump, and the revision linkage is enforced by the derived lock checks
    # below instead.
    require_contains(
        errors,
        AGENT / "contracts" / "local-event-schemas" / "v1" / "profile-guard.yaml",
        ("result_uncertain",),
    )

    # Desktop contract lock 不再对硬编码基线（基线会随每次合约前进过期，
    # CHG-20261003-075 第 1 项），改从定义文件派生期望值：
    # - `v1@` 条目对定义目录的最新版本，与 contract-map 同口径；
    # - `<文件>@<版本>` 条目对被指文件自己的 revision——锁具体文件就意味着
    #   区内其他文件（如 runtime-environment）的前进不强迫消费方跟进。
    lock_path = DESKTOP / "contracts.lock.json"
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"could not parse {lock_path}: {error}")
        lock = {}
    consumes = lock.get("consumes")
    if not isinstance(consumes, dict):
        errors.append(f"{lock_path}: missing consumes map")
    else:
        for name, contracts_dir in (
            ("cloud_agent_api", CLOUD / "contracts" / "cloud-agent-api"),
            ("task_schemas", CLOUD / "contracts" / "task-schemas"),
            ("local_agent_api", AGENT / "contracts" / "local-agent-api"),
        ):
            def_max, def_file = definition_revision_max(contracts_dir)
            if def_max is None:
                errors.append(f"{name}: no dated revision found in {contracts_dir}")
            elif consumes.get(name) != f"v1@{def_max}":
                errors.append(
                    f"{name}: Desktop lock {consumes.get(name)!r} != v1@{def_max} "
                    f"(latest definition: {def_file})"
                )
        for name, contracts_dir in (
            ("local_event_schemas", AGENT / "contracts" / "local-event-schemas"),
            ("local_status_enums", AGENT / "contracts" / "local-status-enums"),
        ):
            pinned = consumes.get(name, "")
            stem, sep, rev = pinned.partition("@")
            if not sep or not stem or not rev:
                errors.append(f"{name}: Desktop lock entry {pinned!r} is not <file>@<revision>")
                continue
            actual = pinned_file_revision(contracts_dir, stem)
            if actual is None:
                errors.append(
                    f"{name}: {stem}.yaml missing or has no dated revision in {contracts_dir}"
                )
            elif actual != rev:
                errors.append(f"{name}: Desktop lock pins {stem}@{rev}, definition says {actual}")
    # Binding-ticket single use, asserted at the layer that can actually stay
    # true. CHG-20260925-063 removed assertions on Desktop source text
    # (`main.rs` carrying "wt-media-agent"; `local_agent/mod.rs` carrying
    # `fn consume_binding_ticket(` and
    # `pub fn bind_session<T: BindingTransport>(`). CHG-056 split `main.rs` into
    # layered modules and the ticket consume path moved to `commands/bind.rs`
    # as a `#[tauri::command]`; the enforcement itself moved ACROSS a repo
    # boundary to Cloud, which consumes the ticket atomically. Desktop source
    # text was the wrong place to assert that. An APPLIED MIGRATION is
    # append-only, so its text is stable in a way a refactorable source file is
    # not: `used_at` (nullable marker, set once on consume) plus a UNIQUE key on
    # `token_hash` is the schema that makes single use enforceable at all.
    require_contains(
        errors,
        CLOUD / "migrations" / "20260714_004_agent_runtime.sql",
        (
            "CREATE TABLE local_agent_binding_tickets",
            "used_at DATETIME(6) NULL",
            "UNIQUE KEY uq_local_agent_binding_ticket_hash (token_hash)",
        ),
    )

    sensitive_files = [
        CLOUD / "migrations" / "20260714_004_agent_runtime.sql",
        CLOUD / "migrations" / "20260714_005_sensitive_profile_locks.sql",
        DESKTOP / "src-tauri" / "src" / "local_agent" / "mod.rs",
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
