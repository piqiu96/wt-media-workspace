#!/usr/bin/env python3
"""Verify that WT Media delivery pointers and milestone references agree."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


CHANGE_ID_RE = re.compile(r"CHG-\d{8}-\d{3}")
CONTEXT_RE = re.compile(r"Active CHG:\s*`([^`]+)`", re.IGNORECASE)
LEVEL_RE = re.compile(r"^- Level:\s*([A-Z])\s*$", re.MULTILINE)
MILESTONE_RE = re.compile(r"^- Milestone:\s*`([^`]+)`\s*$", re.MULTILINE)

# --------------------------------------------------------------------------
# 归档边界（`delivery/completed/` 只读）
# --------------------------------------------------------------------------
# 边界的正文与理由唯一落点是 `delivery/completed/README.md`；本节只实现强制。
# 两条判据都是 ERROR：一条判「脚本不写归档」，一条判「归档声明了自己的边界」。

ARCHIVE_PREFIX = "delivery/completed"
ARCHIVE_SEGMENT = "completed"
ARCHIVE_MARKER_RE = re.compile(r"^-\s*归档边界：\s*`READ-ONLY`\s*$", re.MULTILINE)

# 判据锚在**字符串字面量**上，不锚在接收者变量名上。名字式判据两头都不准且看不出来：
# 对改前的 verify_m3_acceptance.py 只报 3/6 处归档写（漏掉 `EVIDENCE / "state.json"`
# 这种一跳间接），改成定点传播后又因名字空间跨函数共用而把污染集爆到约 180 个名字。
# 详见 CHG-20260925-066 §14 第 11 项与 evidence/task-03-writer-moved.md §4。
ARCHIVE_WRITE_METHODS = frozenset({
    "write_text", "write_bytes", "mkdir", "unlink", "rmdir", "touch",
    "chmod", "rename", "replace", "remove",
})
ARCHIVE_WRITE_FUNCTIONS = frozenset({"rmtree", "copy", "copy2", "copyfile", "move"})
# 白名单：确需对归档做写操作的脚本（仓库相对路径）-> 理由。当前为空。
ARCHIVE_WRITE_ALLOWLIST: dict[str, str] = {}


def is_archive_literal(text: str) -> bool:
    """一个字符串字面量是否在指归档区。

    接受三种写法：`delivery/completed/...`、`completed/...`、以及单独一段
    `completed`（路径用 `/` 逐段拼出来时的形态）。
    """
    return (
        ARCHIVE_PREFIX in text
        or text.startswith(ARCHIVE_SEGMENT + "/")
        or text.rstrip("/") == ARCHIVE_SEGMENT
    )


def _mentions_archive(node: ast.AST, tainted: set[str]) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            if is_archive_literal(sub.value):
                return True
        elif isinstance(sub, ast.Name) and sub.id in tainted:
            return True
    return False


def _is_write_mode(call: ast.Call, mode_index: int) -> bool:
    """`open` 的 mode 是不是写。

    mode 取不到常量时**按写处理**（宁可报出）——这条判据的代价是不报则已、报则误报，
    比漏报安全。
    """
    modes = list(call.args[mode_index:mode_index + 1])
    modes += [keyword.value for keyword in call.keywords if keyword.arg == "mode"]
    for mode in modes:
        if isinstance(mode, ast.Constant):
            return bool(set(str(mode.value)) & set("wax+"))
    return True


def write_target(call: ast.Call) -> ast.AST | None:
    """写操作的目标表达式；返回 None 表示这不是一次写。

    `x.open(mode)`（方法形式，mode 是第 0 个实参）与 `open(path, mode)`（内建，
    mode 是第 1 个实参）的 mode 位置不同。两者混用会把手读的 `path.open("rb")`
    读成写——T-04 的阳性对照就是这么抓出这一处错的。
    """
    func = call.func
    if isinstance(func, ast.Attribute):
        if func.attr in ARCHIVE_WRITE_METHODS:
            return func.value
        if func.attr == "open":
            return func.value if _is_write_mode(call, 0) else None
        return None
    if isinstance(func, ast.Name):
        if func.id == "open" and call.args:
            return call.args[0] if _is_write_mode(call, 1) else None
        if func.id in ARCHIVE_WRITE_FUNCTIONS and call.args:
            return call.args[0]
    return None


def archive_tainted_names(tree: ast.AST) -> set[str]:
    """被赋值为归档路径的名字。

    模块级的赋值做传递闭包；函数内的赋值只从模块级已污染的名字再走一跳
    （`target = (EVIDENCE / "x.md") if first else (EVIDENCE / "y.md")` 这一跳必须能追上，
    而**不**做函数内的闭包——那正是会爆炸的那一步）。
    """
    tainted: set[str] = set()
    changed = True
    while changed:
        changed = False
        for stmt in tree.body:
            if not isinstance(stmt, ast.Assign) or not _mentions_archive(stmt.value, tainted):
                continue
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id not in tainted:
                    tainted.add(target.id)
                    changed = True
    local: set[str] = set()
    for stmt in ast.walk(tree):
        if not isinstance(stmt, ast.Assign) or not _mentions_archive(stmt.value, tainted):
            continue
        for target in stmt.targets:
            if isinstance(target, ast.Name):
                local.add(target.id)
    return tainted | local


def check_archive_readonly(workspace: Path) -> tuple[list[str], str]:
    """归档区不得被 `scripts/` 下的脚本写入。

    扫描面是**递归**的（`rglob`）：`scripts/verify/` 与 `scripts/dev/` 是
    CHG-20260926-067 新设的落点，非递归的 glob 会让落在其中的脚本**静默滑出**
    这条判据——门禁照绿、分母缩小，而报告里看不出来。同一份写归档的探针
    放在 `scripts/verify/` 下的两臂对照见该 CHG 的
    `evidence/artifacts/t01-scan-surface-arm-{a,b}.out`（臂 A 报 0 处、臂 B 点名）。

    覆盖面仍然只到 `*.py`：`scripts/` 下的 shell 脚本与 `tests/` 不在判据内
    （CHG-20260925-066 §14 第 15 项）。
    """
    scripts_dir = workspace / "scripts"
    scripts = sorted(scripts_dir.rglob("*.py")) if scripts_dir.is_dir() else []
    errors: list[str] = []
    sites = 0
    for script in scripts:
        relative = script.relative_to(workspace).as_posix()
        if relative in ARCHIVE_WRITE_ALLOWLIST:
            continue
        try:
            tree = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except SyntaxError as exc:
            errors.append(f"archive readonly: cannot parse {relative}: {exc}")
            continue
        tainted = archive_tainted_names(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            target = write_target(node)
            if target is None or not _mentions_archive(target, tainted):
                continue
            sites += 1
            errors.append(
                f"archive readonly: {relative}:{node.lineno} writes under "
                f"{ARCHIVE_PREFIX}/ ({ast.unparse(target)})"
            )
    summary = (
        f"archive readonly: scanned {len(scripts)} script(s) under scripts/, "
        f"{sites} write(s) reaching {ARCHIVE_PREFIX}/"
    )
    return errors, summary


def check_completed_has_boundary(workspace: Path) -> tuple[list[str], str]:
    """归档区必须存在，且其 `README.md` 必须声明只读边界。"""
    archive = workspace / "delivery" / ARCHIVE_SEGMENT
    boundary = archive / "README.md"
    errors: list[str] = []
    markers = 0
    if not archive.is_dir():
        errors.append(f"archive boundary: {ARCHIVE_PREFIX}/ is missing")
    elif not boundary.is_file():
        errors.append(f"archive boundary: {ARCHIVE_PREFIX}/README.md is missing")
    else:
        markers = len(ARCHIVE_MARKER_RE.findall(boundary.read_text(encoding="utf-8")))
        if markers == 0:
            errors.append(
                f"archive boundary: {ARCHIVE_PREFIX}/README.md has no "
                "machine-readable boundary marker"
            )
    summary = (
        f"archive boundary: checked {ARCHIVE_PREFIX}/README.md, "
        f"{markers} boundary marker(s)"
    )
    return errors, summary


def current_context_path(workspace: Path) -> Path:
    """Return the single execution snapshot owned by the workspace repository.

    The snapshot lives inside the workspace repository so that a worktree
    checkout carries it, and so that no second copy can drift in the outer
    execution root.
    """
    return workspace / ".ai" / "CURRENT_CONTEXT.md"


def parse_context_change(context: Path) -> str | None:
    if not context.is_file():
        return None
    match = CONTEXT_RE.search(context.read_text(encoding="utf-8"))
    if match is None:
        return None
    value = match.group(1).strip()
    return None if value.lower() == "none" else value


LEDGER_ROW_RE = re.compile(r"^\|\s*(CHG-\d{8}-\d{3})\s*\|")


def parse_ledger_changes(ledger: Path) -> list[str]:
    """Return the CHG ids listed in the LEDGER table.

    Only table rows count. Prose in the LEDGER body may mention a CHG id
    (for example to point at where earlier work was folded in), and that
    mention must not be read as a second active change.
    """
    if not ledger.is_file():
        return []
    changes: list[str] = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        match = LEDGER_ROW_RE.match(line)
        if match is not None:
            changes.append(match.group(1))
    return changes


def heading_anchors(markdown: str) -> set[str]:
    anchors: set[str] = set()
    for line in markdown.splitlines():
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip().lower()
        heading = re.sub(r"[^a-z0-9\u4e00-\u9fff -]", "", heading)
        anchors.add(re.sub(r"[\s-]+", "-", heading).strip("-"))
    return anchors


def validate_milestone_reference(
    workspace: Path, change_id: str, change_text: str
) -> list[str]:
    match = MILESTONE_RE.search(change_text)
    if match is None:
        return [f"active CHG has no milestone reference: {change_id}"]

    reference = match.group(1)
    path_text, separator, anchor = reference.partition("#")
    milestone = workspace / path_text
    if not milestone.is_file():
        return [f"active CHG references missing milestone: {reference}"]
    if separator and anchor.lower() not in heading_anchors(
        milestone.read_text(encoding="utf-8")
    ):
        return [f"active CHG references missing milestone anchor: {reference}"]
    return []


def validate_delivery_governance(workspace: Path) -> list[str]:
    workspace = workspace.resolve()
    context = current_context_path(workspace)
    ledger = workspace / "delivery" / "LEDGER.md"
    active_root = workspace / "delivery" / "active"

    errors: list[str] = []
    context_change = parse_context_change(context)
    ledger_changes = parse_ledger_changes(ledger)
    active_changes = sorted(active_root.glob("CHG-*/change.md"))
    active_ids = [path.parent.name for path in active_changes]

    if context_change and context_change not in active_ids:
        errors.append(f"current context references missing CHG: {context_change}")
    if len(ledger_changes) > 1:
        errors.append("ledger lists more than one active CHG: " + ", ".join(ledger_changes))
    if len(active_ids) > 1:
        errors.append("delivery/active contains more than one CHG: " + ", ".join(active_ids))

    ledger_change = ledger_changes[0] if len(ledger_changes) == 1 else None
    if context_change != ledger_change:
        errors.append(
            "current context and ledger disagree: "
            f"{context_change or 'none'} != {ledger_change or 'none'}"
        )
    if ledger_change and ledger_change not in active_ids:
        errors.append(f"ledger references missing active CHG: {ledger_change}")

    for change_path in active_changes:
        change_id = change_path.parent.name
        # An active CHG directory is a pair: `change.md` is the plan, and
        # `checkpoint.md` is where progress is recorded.  A CHG with only the
        # first still passes the milestone checks, so without this check an
        # unresumable active change is silently accepted.
        if not (change_path.parent / "checkpoint.md").is_file():
            errors.append(f"active CHG is missing checkpoint.md: {change_id}")
        change_text = change_path.read_text(encoding="utf-8")
        level_match = LEVEL_RE.search(change_text)
        if level_match and level_match.group(1) in {"M", "L"}:
            errors.extend(
                validate_milestone_reference(workspace, change_id, change_text)
            )

    errors.extend(check_archive_readonly(workspace)[0])
    errors.extend(check_completed_has_boundary(workspace)[0])
    return errors


def main() -> int:
    workspace = Path(__file__).resolve().parents[1]
    errors = validate_delivery_governance(workspace)
    # 两条归档判据各自报出分母，好让「0 命中」不是一句空话。
    for _, summary in (check_archive_readonly(workspace),
                       check_completed_has_boundary(workspace)):
        print(summary)
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1

    ledger_changes = parse_ledger_changes(workspace / "delivery" / "LEDGER.md")
    active = ledger_changes[0] if ledger_changes else "none"
    print(f"Delivery governance verification ok. Active CHG: {active}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
