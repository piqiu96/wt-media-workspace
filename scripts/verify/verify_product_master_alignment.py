#!/usr/bin/env python3
"""Verify the reviewed product, governance, and M0-M10 planning invariants."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.lib.change_metadata import read_change


def milestone_sections(text: str) -> dict[int, str]:
    headings = list(re.finditer(r"^### M(\d+)：.*$", text, flags=re.MULTILINE))
    sections: dict[int, str] = {}
    for index, heading in enumerate(headings):
        number = int(heading.group(1))
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[number] = text[heading.start() : end]
    return sections


def candidate_block(section: str) -> str:
    match = re.search(r"候选 CHG：\s*```text\s*(.*?)\s*```", section, flags=re.DOTALL)
    return match.group(1) if match else ""


def require_all(text: str, needles: tuple[str, ...], label: str) -> list[str]:
    return [f"{label} missing {needle!r}" for needle in needles if needle not in text]


def forbid_all(errors: list[str], block: str, label: str, needles: tuple[str, ...]) -> None:
    """Report forbidden operational objects inside a candidate block.

    Guarded on a non-empty block deliberately. `needle in ""` is false for every
    needle, so an empty or malformed block would make this check PASS
    unconditionally -- silently certifying a milestone it never read. The
    missing block is reported once by the required-block check in
    `validate_master_text`; this guard only suppresses a check that cannot run.
    """
    if not block.strip():
        return
    for needle in needles:
        if needle in block:
            errors.append(f"{label} contains forbidden operational object {needle!r}")


def validate_master_text(text: str) -> list[str]:
    errors: list[str] = []
    sections = milestone_sections(text)
    if set(sections) != set(range(11)):
        errors.append(
            "Master milestone set mismatch: expected M0-M10, "
            f"got {', '.join(f'M{number}' for number in sorted(sections)) or 'none'}"
        )
        return errors

    # Status words track the CURRENT Master Plan. Move an entry here in the same
    # change that moves the milestone; a milestone that closed earlier is not an
    # exemption.
    expected_statuses = {
        0: "DONE",
        1: "DONE",
        2: "DONE",
        3: "DONE",
        4: "DONE",
        5: "DONE",
        **{number: "NOT_STARTED" for number in range(6, 11)},
    }
    statuses: dict[int, str | None] = {}
    for number, expected in expected_statuses.items():
        status_match = re.search(r"\| 状态 \| `([^`]+)`", sections[number])
        actual = status_match.group(1) if status_match else None
        statuses[number] = actual
        if actual != expected:
            errors.append(f"M{number} status expected {expected!r}, got {actual!r}")

    # A candidate block belongs to a milestone that is still open. A DONE
    # milestone has retired its candidates into its closure record, so it is not
    # required to carry one; an unfinished milestone MUST, because
    # `candidate_block()` returns "" for an absent or malformed block, and every
    # assertion made against "" is vacuous in one of two ways --
    # `require_all("")` reports all of its needles missing (permanent noise that
    # trains readers to ignore this gate), while `needle in ""` is never true (a
    # silent PASS that certifies a milestone the check never read). Reporting
    # the missing block is what turns that second silence into an error.
    for number in sorted(sections):
        if statuses[number] == "DONE":
            continue
        if not candidate_block(sections[number]).strip():
            errors.append(
                f"M{number} is {statuses[number]!r} but carries no candidate CHG block; "
                "candidate assertions against an empty block would be vacuous"
            )

    # M0 and M1 are DONE but kept their candidate blocks as the closure record,
    # so these assert the retired candidate list itself.
    m0_candidates = candidate_block(sections[0])
    errors.extend(
        require_all(
            m0_candidates,
            tuple(f"M0-R{number} " for number in range(1, 7)),
            "M0 candidate",
        )
    )
    errors.extend(
        require_all(
            sections[0],
            ("Cloud 和 Web 使用真实依赖", "Agent 使用正式包入口", "真实 Vue/Tauri Rust", "空 MySQL 数据库", "echo 脚本", "Mock-only"),
            "M0 gate",
        )
    )

    m1_candidates = candidate_block(sections[1])
    errors.extend(
        require_all(
            m1_candidates,
            tuple(f"M1-R{number} " for number in range(1, 9)),
            "M1 candidate",
        )
    )
    errors.extend(
        require_all(
            sections[1],
            ("MySQL", "task_schemas", "SQLite", "真实 Tauri", "HTTP/SSE", "重启恢复", "无 Mock"),
            "M1 gate",
        )
    )

    # A DONE milestone has no candidate block, so its record is asserted against
    # the section itself. Do not fall back to `candidate_block(...) or section`:
    # a missing block would silently redirect the assertions and report stale
    # needles instead of a structural error.
    m2_record = sections[2]
    errors.extend(
        require_all(
            m2_record,
            ("M2-A：", "M2-B：", "M2-C：", "M2-D：", "M2-E："),
            "M2 candidate",
        )
    )
    errors.extend(
        require_all(
            m2_record,
            (
                "四条业务闭环顺序补齐",
                "M2-A：用户与权限闭环",
                "M2-B：媒体账号与 Profile 闭环",
                "M2-C：代理与 Profile 闭环",
                "M2-D：Cookie 与开户闭环",
                "M2-E：Desktop 与安全闭环",
                "真实 MySQL",
                "BitBrowser",
                "Cookie",
                "Desktop",
            ),
            "M2 capability",
        )
    )

    # M3 has no candidate block: a DONE milestone is covered by its status word
    # plus the common milestone acceptance needles (D-04).

    m8_candidates = candidate_block(sections[8])
    forbid_all(errors, m8_candidates, "M8 candidate", ("interaction_batch", "interaction_item"))
    errors.extend(
        require_all(
            m8_candidates,
            ("外部 tracked_object", "interaction_task", "账号级 task", "验证码接管"),
            "M8 candidate",
        )
    )

    m9_candidates = candidate_block(sections[9])
    forbid_all(errors, m9_candidates, "M9 candidate", ("production_signal",))
    errors.extend(
        require_all(
            m9_candidates,
            ("M9-C1 platform_metric_snapshot", "环境统计与新鲜度", "Excel 导出"),
            "M9 candidate",
        )
    )

    errors.extend(
        require_all(
            sections[6],
            ("pending_manual_submit", "cancelled", "published", "tracked_object"),
            "M6 tracked-object provider",
        )
    )
    errors.extend(
        require_all(
            sections[9],
            ("`tracked_object` 已由 M6/M8 创建", "不可变快照"),
            "M9 dependency",
        )
    )

    m10_candidates = candidate_block(sections[10])
    errors.extend(
        require_all(
            m10_candidates,
            (
                "HTTPS",
                "MySQL/Object Storage 备份、恢复和回滚",
                "Agent 正式打包",
                "FFmpeg/FFprobe 镜像",
                "Sidecar 生命周期",
                "签名和公证",
                "升级、回滚和用户数据保留",
                "日志脱敏和诊断包",
                "故障演练",
            ),
            "M10 capability",
        )
    )

    errors.extend(
        require_all(
            text,
            (
                "自动单元、Contract、集成和回归测试",
                "真实依赖证据",
                "角色/UI/人工链路验收",
                "中断、重启、幂等、恢复和敏感信息安全验收",
                "各仓库独立提交",
            ),
            "common milestone acceptance",
        )
    )
    return errors


def validate_contract_texts(human: str, machine: str) -> list[str]:
    errors: list[str] = []
    errors.extend(
        require_all(
            human,
            ("Current state is mixed.", "`task_schemas` retired"),
            "mixed contract state",
        )
    )
    errors.extend(
        require_all(
            machine,
            ("formal_definitions_active: true",),
            "machine contract state",
        )
    )
    if "  task_schemas:" in machine:
        errors.append("task_schemas machine state must be retired")
    return errors


STATUS_LINE_RE = re.compile(
    r"^(?:- Status:|> 状态[：:])\s*(.+?)\s*$", flags=re.MULTILINE
)


def status_word(change_text: str) -> str | None:
    """The bare status word of a `change.md`, with any annotation stripped.

    Records may annotate the word — `- Status: IMPLEMENTING（说明）`,
    `- Status: **SUPERSEDED（...）**`. The annotation is a note about the word,
    not part of it. A regex that demands the word alone does not merely reject
    those records: it fails to match at all, so the status reads as `None` and
    the gate names a status the record never had. Strip first, then judge.
    """
    match = STATUS_LINE_RE.search(change_text)
    if not match:
        return None
    word = match.group(1).strip().strip("*").strip()
    word = re.sub(r"[（(].*$", "", word).strip()
    return word or None


def validate_active_change(root: Path) -> list[str]:
    errors: list[str] = []
    active_paths = sorted((root / "delivery" / "active").glob("*/change.md"))
    for active_path in active_paths:
        errors.extend(_validate_one_active_change(root, active_path))
    return errors


def _validate_one_active_change(root: Path, active_path: Path) -> list[str]:
    errors: list[str] = []
    active_change = active_path.parent.name
    change_text = active_path.read_text(encoding="utf-8")
    try:
        metadata = read_change(active_path)
    except ValueError as exc:
        return [f"invalid CHG metadata {active_change}: {exc}"]
    # Canonical change.md records use the dash form (`- Status:`, `- Current
    # repository:`); older records use a blockquote header (`> 状态：`,
    # `> 当前仓库：`).  Accept both.  The status word itself must be one the
    # vocabulary in `MASTER_IMPLEMENTATION_PLAN.md` §3 defines.
    title_match = re.search(rf"^# {re.escape(active_change)}[：:] ?(.+)$", change_text, flags=re.MULTILINE)
    title = title_match.group(1) if title_match else None
    status = status_word(change_text) if metadata.legacy else metadata.status
    repo_match = re.search(r"^(?:- Current repository:|> 当前仓库[：:])\s*`([^`]+)`\s*$", change_text, flags=re.MULTILINE)
    current_repository = (repo_match.group(1) if repo_match else None) if metadata.legacy else metadata.affected_repos[0]
    # A CHG sits in `delivery/active/` only while it is being executed, so only
    # the two non-terminal execution words are legal here.  `DISCUSSION` and
    # `PLANNED` are pre-activation states (their home is `delivery/planned/`),
    # and `DONE` / `SUPERSEDED` are terminal — accepting any of them would
    # accept exactly the state §3 forbids.
    if status not in {"IMPLEMENTING", "VERIFYING"}:
        errors.append(
            "active CHG status must be IMPLEMENTING or VERIFYING, "
            f"got {status!r}"
        )
    if not title:
        errors.append(f"active CHG title is missing or does not match {active_change}")
    if not current_repository:
        errors.append("active CHG current repository is missing")
    if metadata.legacy and not re.search(
        r"^## (?:\d+\. )?Pending Questions\s+None\.\s*$",
        change_text,
        flags=re.MULTILINE,
    ):
        errors.append("active CHG must have no pending questions")

    ledger = (root / "delivery" / "LEDGER.md").read_text(encoding="utf-8")
    expected_row = f"| {active_change} | {title} | {status} | {current_repository} |"
    if title and status and current_repository and expected_row not in ledger:
        errors.append(
            f"Ledger is not aligned with active CHG {active_change} status {status!r}"
        )
    return errors


def validate_product_identity(root: Path) -> list[str]:
    errors: list[str] = []
    consolidated = (
        root / "docs" / "product" / "prd" / "社媒运营平台_产品需求说明书_V1.md"
    ).read_text(encoding="utf-8")
    chapter3 = (
        root
        / "docs"
        / "product"
        / "prd"
        / "详细文档"
        / "第三章_用户与账号管理.md"
    ).read_text(encoding="utf-8")
    for label, text in (("consolidated PRD", consolidated), ("Chapter 3", chapter3)):
        errors.extend(
            require_all(
                text,
                ("同一个 `main_user_id` 可以绑定多个系统用户", "Cloud 分配", "profile_user_id"),
                f"{label} BitBrowser identity",
            )
        )
    return errors


def validate_alignment(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    master = (root / "delivery" / "MASTER_IMPLEMENTATION_PLAN.md").read_text(
        encoding="utf-8"
    )
    errors.extend(validate_master_text(master))
    errors.extend(validate_active_change(root))
    errors.extend(validate_product_identity(root))

    human_contract = (root / "docs" / "contracts" / "contract-map.md").read_text(
        encoding="utf-8"
    )
    machine_contract = (root / "config" / "contract-map.yaml").read_text(
        encoding="utf-8"
    )
    errors.extend(validate_contract_texts(human_contract, machine_contract))

    release_matrix = (root / "config" / "release-matrix.yaml").read_text(
        encoding="utf-8"
    )
    errors.extend(
        require_all(
            release_matrix,
            (
                "Verified releases are historical scope evidence",
                "revised milestone completion is determined by the current Master Plan",
                "M0-R4 verified real Vue/Vite/Tauri Rust",
            ),
            "release matrix planning state",
        )
    )
    return errors


def main() -> int:
    errors = validate_alignment()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Product and Master Plan alignment verification ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
