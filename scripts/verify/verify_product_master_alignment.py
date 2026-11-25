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


MILESTONE_STATUSES = {"NOT_STARTED", "IN_PROGRESS", "VERIFYING", "DONE"}
PUBLISHING_CARDS = {
    "M6": "M6-single-publishing.md",
    "M7": "M7-batch-publishing.md",
    "M-publishing-plan": "M-publishing-plan.md",
    "M-publishing-operations": "M-publishing-operations.md",
}


def milestone_field(text: str, label: str) -> str | None:
    match = re.search(rf"^\| {re.escape(label)} \| ([^|\n]*)\|", text, re.MULTILINE)
    if not match:
        match = re.search(rf"{re.escape(label)}[：:]\s*([^；;\n]+)", text)
    if not match:
        return None
    value = match.group(1).strip()
    if label == "状态":
        word = re.match(r"`([^`]+)`", value)
        return word.group(1) if word else value
    return value.strip("`")


def route_sections(text: str) -> dict[str, str]:
    headings = list(re.finditer(
        r"^### (M\d+|M-publishing-plan|M-publishing-operations)：.*$",
        text, flags=re.MULTILINE,
    ))
    sections: dict[str, str] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[heading.group(1)] = text[heading.start():end]
    return sections


def milestone_sections(text: str) -> dict[int, str]:
    return {int(name[1:]): section for name, section in route_sections(text).items()
            if re.fullmatch(r"M\d+", name)}


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
    if set(sections) != {*range(8), 10}:
        errors.append(
            "Master milestone set mismatch: expected M0-M7 and M10 (M8/M9 retired), "
            f"got {', '.join(f'M{number}' for number in sorted(sections)) or 'none'}"
        )
        return errors

    route = route_sections(text)
    for name, section in route.items():
        status = milestone_field(section, "状态")
        if name in {f"M{number}" for number in range(6)}:
            if status != "DONE":
                errors.append(f"{name} status expected 'DONE', got {status!r}")
        elif status not in MILESTONE_STATUSES:
            errors.append(f"{name} has invalid milestone status {status!r}")
        # Candidates are a plan, not a permanent list of CHG IDs. Once work
        # starts, lifecycle checks below follow actual CHGs and evidence.
        if status == "NOT_STARTED" and not candidate_block(section).strip():
            errors.append(f"{name} is 'NOT_STARTED' but carries no candidate CHG block")

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

    # Current M2 extension owns its closure in the milestone, not a duplicate
    # frozen list of pre-refactor capabilities in this summary.
    if 'milestones/M2-account-runtime.md#m2-d-社媒账号重构' not in sections[2]:
        errors.append('M2 closure reference missing')

    # M3 has no candidate block: a DONE milestone is covered by its status word
    # plus the common milestone acceptance needles (D-04).

    for name, dependency, reference in (
        ("M6", None, "milestones/M6-single-publishing.md"),
        ("M7", "M6", "milestones/M7-batch-publishing.md"),
        ("M-publishing-plan", "M7", "milestones/M-publishing-plan.md"),
        ("M-publishing-operations", "M-publishing-plan", "milestones/M-publishing-operations.md"),
        ("M10", "M-publishing-operations", "milestones/M-first-production-release.md"),
    ):
        section = route.get(name, "")
        if not section:
            errors.append(f"Missing publishing route stage {name}")
            continue
        errors.extend(require_all(section, (reference,), f"{name} closure reference"))
        if dependency:
            needle = f"| 依赖 | {dependency} `DONE`"
            # Tools may be implemented earlier, but acceptance still depends on plans.
            if name == "M-publishing-operations":
                needle = f"整体验收依赖 {dependency} `DONE`"
            elif name != "M10":
                needle += " |"
            errors.extend(require_all(section, (needle,), f"{name} dependency"))
        dependency_row = re.search(r"^\| 依赖 \| (.+)$", section, re.MULTILINE)
        if dependency_row:
            for excluded in ("M8", "M9"):
                if re.search(rf"\b{excluded}\s+`DONE`", dependency_row.group(1)):
                    errors.append(f"{name} depends on excluded {excluded}")

    errors.extend(require_all(sections[6], ("浏览器自动提交",), "M6 capability"))
    errors.extend(require_all(sections[6], ("审核中不算公开成功", "断网后必须核实且不重复投稿"), "M6 gate"))
    for name in ("M6", "M7", "M-publishing-plan", "M-publishing-operations", "M10"):
        section = route.get(name, "")
        for obsolete in ("pending_manual_submit", "Agent 不点击最终发布按钮", "运营人工提交", "B站辅助发布", "百家号辅助发布"):
            if obsolete in section:
                errors.append(f"{name} contains obsolete publishing baseline {obsolete!r}")

    # Check the actual ordered route, not incidental mentions in explanatory prose.
    flow = re.search(r"采用纵向闭环路线：\s*```text\s*(.*?)```", text, re.DOTALL)
    expected_route = [*(f"M{i}" for i in range(8)),
                      "M-publishing-plan", "M-publishing-operations", "M10"]
    actual_route = re.findall(r"^(?:→ )?(M[\w-]+) ", flow.group(1), re.MULTILINE) if flow else []
    if actual_route != expected_route:
        errors.append("Current milestone route must follow M0-M7, publishing plan, operations, M10")

    if milestone_field(sections[10], "状态") == "NOT_STARTED":
        errors.extend(
            require_all(
                candidate_block(sections[10]),
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


def validate_publishing_cards(root: Path) -> list[str]:
    """Keep publishing closure cards present and linked to their real prerequisites."""
    errors: list[str] = []
    for filename, dependency in (
        ("M6-single-publishing.md", None),
        ("M7-batch-publishing.md", "M6-single-publishing.md"),
        ("M-publishing-plan.md", "M7-batch-publishing.md"),
        ("M-publishing-operations.md", "M-publishing-plan.md"),
    ):
        path = root / "delivery" / "milestones" / filename
        if not path.is_file():
            errors.append(f"Publishing closure card missing: {filename}")
            continue
        card = path.read_text(encoding="utf-8")
        status = milestone_field(card, "状态")
        if status not in MILESTONE_STATUSES:
            errors.append(f"{filename} has invalid milestone status {status!r}")
        if status == "NOT_STARTED":
            errors.extend(require_all(card, (
                "候选 CHG", "工作内容及仓库", "直接依赖", "可独立验证的完成条件",
            ), f"{filename} candidate plan"))
            plan = card.partition("## 候选 CHG")[2]
            if not re.search(r"^\| (?!候选|CHG\s*\||[- :]+\|)[^|]+\|[^|]+\|[^|]+\|[^|]+\|", plan, re.MULTILINE):
                errors.append(f"{filename} carries no candidate CHG rows")
        errors.extend(require_all(card, (
            "用户目标", "前置能力", "用户操作",
            "系统与平台动作", "同时成立才算完成", "必须排除的假成功",
        ), filename))
        ui_routes = {
            "M6-single-publishing.md": ("publishing/tasks", "production/outputs"),
            "M7-batch-publishing.md": ("publishing/batches",),
            "M-publishing-plan.md": ("publishing/plans",),
            "M-publishing-operations.md": ("tools/images", "tools/templates"),
        }
        ui_sources = {
            "M6-single-publishing.md": ("PublishingTaskPage.vue", "QuickPublish.vue", "TaskDetail.vue"),
            "M7-batch-publishing.md": ("BatchManager.vue", "BatchWorkbench.vue", "BatchContentWorkspace.vue", "BatchDetailContent.vue"),
            "M-publishing-plan.md": ("PlanPage.vue", "plan/"),
            "M-publishing-operations.md": ("ImageLibraryDetail.vue", "CoverTemplateManager.vue", "CoverTemplateWorkspace.vue"),
        }
        if not re.search(r"https://github\.com/piqiu96/wt-media-cloud/(?:tree|blob)/[^/\s)]+/web/example/proto/publishing-design(?:[/)#\s]|$)", card):
            errors.append(f"{filename} UI baseline missing Cloud prototype source link")
        errors.extend(require_all(card, (
            "../../docs/standards/frontend/AdminUI页面规范.md",
            "../../docs/standards/frontend/前端交互规范.md",
            "../../docs/standards/frontend/前端架构与视觉规范.md",
            "README.md#页面实施与验收基线", "实际页面与原型的一致性检查", "产品负责人裁定",
            *ui_sources[filename],
            *(f"`/example/operations/{route}`" for route in ui_routes[filename]),
        ), f"{filename} UI baseline"))
        if dependency:
            errors.extend(require_all(card, (f"]({dependency})",), f"{filename} dependency"))
        for target in re.findall(r"\]\(([^)]+)\)", card):
            if re.match(r"[a-z]+://", target):
                continue
            relative = target.partition("#")[0]
            if relative and not (path.parent / relative).is_file():
                errors.append(f"{filename} links missing file: {relative}")
    return errors


def validate_publishing_lifecycle(root: Path) -> list[str]:
    """Compare current milestone pointers with CHG ownership, not an initial snapshot."""
    errors: list[str] = []
    master = (root / "delivery" / "MASTER_IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
    sections = route_sections(master)
    cards = {**PUBLISHING_CARDS, "M10": "M-first-production-release.md"}
    active: dict[str, dict[str, str]] = {name: {} for name in cards}
    for path in sorted((root / "delivery" / "active").glob("*/change.md")):
        try:
            metadata = read_change(path)
        except ValueError:
            continue  # validate_active_change reports malformed records.
        parent = metadata.parent.partition("#")[0]
        for name, filename in cards.items():
            if parent == f"delivery/milestones/{filename}":
                active[name][metadata.change_id] = metadata.status

    for name, filename in cards.items():
        section = sections.get(name, "")
        status = milestone_field(section, "状态")
        documents = [(root / "delivery" / "MASTER_IMPLEMENTATION_PLAN.md", section)]
        # M10 reuses a historical release record, not a second current status.
        if name != "M10":
            path = root / "delivery" / "milestones" / filename
            if not path.is_file():
                continue  # validate_publishing_cards reports the missing card.
            card = path.read_text(encoding="utf-8")
            if milestone_field(card, "状态") != status:
                errors.append(f"{name} Master/card milestone statuses disagree")
            documents.append((path, card))
        for path, document in documents:
            label = f"{name} {path.name}"
            value = milestone_field(document, "Active CHG")
            declared = set(re.findall(r"CHG-\d{8}-\d{3}", value or ""))
            if value != "None" and not declared:
                errors.append(f"{label} must declare Active CHG IDs or None")
            if declared != set(active[name]):
                errors.append(f"{label} Active CHG does not match delivery/active parent ownership")
            if status == "DONE" or (status in {"IN_PROGRESS", "VERIFYING"} and not active[name]):
                evidence = milestone_field(document, "Evidence") or ""
                links = re.findall(r"\]\(([^)]+)\)", evidence)
                if not links:
                    errors.append(f"{label} requires linked delivery evidence for {status}")
                for target in links:
                    if target.startswith("https://"):
                        continue
                    evidence_path = (path.parent / target.partition("#")[0]).resolve()
                    if not evidence_path.is_file():
                        errors.append(f"{label} evidence file is missing: {target}")
                    elif evidence_path.name == "change.md":
                        try:
                            if read_change(evidence_path).status != "DONE":
                                errors.append(f"{label} evidence CHG is not DONE: {target}")
                        except ValueError as exc:
                            errors.append(f"{label} invalid evidence CHG: {exc}")
        if status in {"NOT_STARTED", "DONE"} and active[name]:
            errors.append(f"{name} is {status} but still owns active CHGs")
        if status == "VERIFYING" and "IMPLEMENTING" in active[name].values():
            errors.append(f"{name} is VERIFYING but owns an IMPLEMENTING CHG")
    return errors


def validate_publishing_retirement(root: Path) -> list[str]:
    """Reject retired planning files and current references; leave archives immutable."""
    errors: list[str] = []
    retired = "M-publishing-prototype.md"
    if (root / "delivery" / "milestones" / retired).exists():
        errors.append("Retired prototype milestone must not exist")
    current = {root / "delivery" / "MASTER_IMPLEMENTATION_PLAN.md", root / "AGENT-INDEX.md", root / "README.md"}
    for directory in ("docs", "delivery/milestones", "delivery/active", "delivery/planned"):
        current.update((root / directory).rglob("*.md"))
    for path in sorted(current):
        if path.is_file() and path.name != retired and retired in path.read_text(encoding="utf-8"):
            errors.append(f"Current document references retired prototype: {path.relative_to(root).as_posix()}")
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
    errors.extend(validate_publishing_cards(root))
    errors.extend(validate_publishing_lifecycle(root))
    errors.extend(validate_publishing_retirement(root))
    milestone_index = (root / "delivery" / "milestones" / "README.md").read_text(encoding="utf-8")
    errors.extend(require_all(milestone_index, (
        "## 页面实施与验收基线", "CHG 必须在 References 引用", "实际页面与同一原型基线逐项对照",
        "Cloud 原型 commit SHA", "接口/实现差异由研发在原框架内解决", "仅涉及业务规则", "不得绕开原型重新设计",
    ), "Publishing UI implementation policy"))
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
