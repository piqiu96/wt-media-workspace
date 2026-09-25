#!/usr/bin/env python3
"""Mutation control for the T-03 judgements in verify_product_master_alignment.py.

Replays `validate_master_text` on the real Master Plan text with one targeted
mutation per judgement, and requires each mutation to produce EXACTLY ONE error
carrying that judgement's label. Text is mutated in memory; no file is written.

Usage: python3 t03-mutation-control.py <repo-root>
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module(root: Path):
    spec = importlib.util.spec_from_file_location(
        "alignment", root / "scripts" / "verify_product_master_alignment.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    module = load_module(root)
    original = (root / "delivery" / "MASTER_IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")

    failures: list[str] = []

    def check(name: str, text: str, expected: list[str]) -> None:
        actual = module.validate_master_text(text)
        ok = actual == expected
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        for error in actual:
            print(f"        {error}")
        if not ok:
            failures.append(name)

    # Positive control for the ARGUMENT: the function must read the text it is
    # handed, not the file on disk. Empty text has no milestone headings at all.
    check(
        "control: empty text -> milestone set mismatch",
        "",
        ["Master milestone set mismatch: expected M0-M10, got none"],
    )

    # Positive control for the BASELINE: the unmutated real text is clean.
    check("control: unmutated real text -> 0 errors", original, [])

    def mutated(old: str, new: str) -> str:
        if old not in original:
            raise SystemExit(f"mutation target absent from Master Plan: {old!r}")
        return original.replace(old, new, 1)

    # 1. M2 status word. Reopening a DONE milestone trips two checks, and that
    #    is intended: its status word is now wrong, AND it is again an
    #    unfinished milestone with no candidate block to plan against.
    check(
        "M2 status DONE -> IN_PROGRESS",
        mutated("| 状态 | `DONE` |\n| 目标 | 在 M1 真实端到端环境上", "| 状态 | `IN_PROGRESS` |\n| 目标 | 在 M1 真实端到端环境上"),
        [
            "M2 status expected 'DONE', got 'IN_PROGRESS'",
            "M2 is 'IN_PROGRESS' but carries no candidate CHG block; "
            "candidate assertions against an empty block would be vacuous",
        ],
    )

    # 2. M2 closure-record needle (four business closures; M2-D is DEFERRED).
    check(
        "M2 record '四条业务闭环顺序补齐' -> '五条...'",
        mutated("四条业务闭环顺序补齐", "五条业务闭环顺序补齐"),
        ["M2 capability missing '四条业务闭环顺序补齐'"],
    )

    # 3. New structural check: a milestone that is NOT DONE must carry a
    #    candidate block. M3 is DONE and has none, so flipping its status to
    #    NOT_STARTED makes the absent block an error -- proving both that the
    #    structural check is live and that M3's old candidate assertions are
    #    really gone (no phantom "M3 candidate" lines reappear).
    check(
        "M3 status DONE -> NOT_STARTED with no candidate block",
        mutated(
            "| 状态 | `DONE`（2026-09-23 用户签收",
            "| 状态 | `NOT_STARTED`（2026-09-23 用户签收",
        ),
        [
            "M3 status expected 'DONE', got 'NOT_STARTED'",
            "M3 is 'NOT_STARTED' but carries no candidate CHG block; "
            "candidate assertions against an empty block would be vacuous",
        ],
    )

    # 4. Forbidden-object check on a NON-EMPTY block must still fire.
    check(
        "M8 block gains forbidden 'interaction_batch'",
        mutated(
            "M8-C1 外部 tracked_object 录入",
            "M8-C1 interaction_batch 外部 tracked_object 录入",
        ),
        ["M8 candidate contains forbidden operational object 'interaction_batch'"],
    )

    # 5. The guard in `forbid_all`: an EMPTY block on an unfinished milestone is
    #    now loud instead of silent. Note what each family contributes here --
    #    `require_all` produces three noise errors, the forbidden loop produces
    #    NOTHING (it cannot run), and the new structural check is the only thing
    #    that names the real problem. That asymmetry is the reason the
    #    structural check exists.
    m9 = module.milestone_sections(original)[9]
    m9_block = module.candidate_block(m9)
    check(
        "M9 candidate block emptied (still NOT_STARTED)",
        mutated(m9_block, ""),
        [
            "M9 is 'NOT_STARTED' but carries no candidate CHG block; "
            "candidate assertions against an empty block would be vacuous",
            "M9 candidate missing 'M9-C1 platform_metric_snapshot'",
            "M9 candidate missing '环境统计与新鲜度'",
            "M9 candidate missing 'Excel 导出'",
        ],
    )

    # 6. M10 needle realigned to ADR-0017 (FFmpeg belongs to the Cloud Compose
    #    Worker image, not to a per-endpoint distribution).
    check(
        "M10 'FFmpeg/FFprobe 镜像' -> '分发'",
        mutated("FFmpeg/FFprobe 镜像", "FFmpeg/FFprobe 分发"),
        ["M10 capability missing 'FFmpeg/FFprobe 镜像'"],
    )

    # 7. Control on an untouched judgement: M0's gate wording. Nothing in this
    #    CHG changed it, and it must still be able to fail.
    check(
        "M0 gate wording 'Cloud 和 Web 使用真实依赖' -> mutated",
        mutated("Cloud 和 Web 使用真实依赖", "Cloud 和 Web 使用模拟依赖"),
        ["M0 gate missing 'Cloud 和 Web 使用真实依赖'"],
    )

    print()
    if failures:
        print(f"MUTATION CONTROL FAILED: {len(failures)} arm(s) did not behave as expected: {failures}")
        return 1
    print("MUTATION CONTROL OK: every arm produced exactly its expected error set.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
