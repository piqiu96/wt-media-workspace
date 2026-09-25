#!/usr/bin/env python3
"""Mutation control for the T-04 test rewrites.

A new test that only fails with an ImportError proves nothing. Each arm here
DISABLES one judgement in a copy of the script and replays the corresponding
test's predicate, requiring it to go red. The last arm is the decisive one: it
shows the OLD M3 test could not detect the removal of the very check it named.

Nothing on disk is modified; every mutant is a temp file loaded as a module.

Usage: python3 t04-mutation-control.py <repo-root>
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile

M8_TARGET = "M8-C1 外部 tracked_object 录入"
M8_INJECT = "M8-C1 interaction_batch 外部 tracked_object 录入"
M9_TAIL_TARGET = "M9-C8 数据统计综合验收"
M9_TAIL_INJECT = "M9-C8 数据统计综合验收 production_signal"
M9_EMPTY_EXPECTED = [
    "M9 is 'NOT_STARTED' but carries no candidate CHG block; "
    "candidate assertions against an empty block would be vacuous",
    "M9 candidate missing 'M9-C1 platform_metric_snapshot'",
    "M9 candidate missing '环境统计与新鲜度'",
    "M9 candidate missing 'Excel 导出'",
]


def load(source: str, name: str):
    path = pathlib.Path(tempfile.mkdtemp()) / f"{name}.py"
    path.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def disable(source: str, old: str, new: str, what: str) -> str:
    if old not in source:
        raise SystemExit(f"could not disable {what}: pattern not found")
    mutated = source.replace(old, new, 1)
    if mutated == source:
        raise SystemExit(f"could not disable {what}: replacement was a no-op")
    return mutated


def main() -> int:
    root = pathlib.Path(sys.argv[1]).resolve()
    script = (root / "scripts" / "verify_product_master_alignment.py").read_text(encoding="utf-8")
    master = (root / "delivery" / "MASTER_IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")

    failures: list[str] = []

    def arm(name: str, passed: bool, must_pass: bool) -> None:
        ok = passed is must_pass
        print(f"{'ok  ' if ok else 'FAIL'} {name}  (expected {'PASS' if must_pass else 'FAIL'})")
        if not ok:
            failures.append(name)

    # --- positive control: the unmutated script passes every predicate -------
    base = load(script, "base")
    m8_errors = base.validate_master_text(master.replace(M8_TARGET, M8_INJECT, 1))
    m9_tail_errors = base.validate_master_text(master.replace(M9_TAIL_TARGET, M9_TAIL_INJECT, 1))
    m9_block = base.candidate_block(base.milestone_sections(master)[9])
    m9_empty_errors = base.validate_master_text(master.replace(m9_block, "", 1))

    arm(
        "control: forbidden-object predicate holds on the real script",
        sorted(m8_errors) == ["M8 candidate contains forbidden operational object 'interaction_batch'"]
        and sorted(m9_tail_errors) == ["M9 candidate contains forbidden operational object 'production_signal'"],
        True,
    )
    arm(
        "control: missing-block predicate holds on the real script",
        sorted(m9_empty_errors) == sorted(M9_EMPTY_EXPECTED),
        True,
    )

    # --- arm 1: does the forbidden-object test die if the check is disabled? --
    silent = load(
        disable(
            script,
            "    if not block.strip():\n        return\n",
            "    return\n    if not block.strip():\n        return\n",
            "forbid_all",
        ),
        "silent_forbid",
    )
    arm(
        "forbid_all() neutralised -> forbidden-object test goes red",
        sorted(silent.validate_master_text(master.replace(M8_TARGET, M8_INJECT, 1))) == ["M8 candidate contains forbidden operational object 'interaction_batch'"],
        False,
    )

    # --- arm 2: does the missing-block test die if the new check is disabled? -
    no_struct = load(
        disable(
            script,
            "        if not candidate_block(sections[number]).strip():",
            "        if False:",
            "the candidate-block requirement",
        ),
        "no_struct",
    )
    arm(
        "structural check disabled -> missing-block test goes red",
        sorted(no_struct.validate_master_text(master.replace(m9_block, "", 1))) == sorted(M9_EMPTY_EXPECTED),
        False,
    )

    # --- arm 3 (decisive): the OLD test could not detect this removal --------
    # Reproduce the old test exactly: mutate a string that is not in the Master
    # Plan, then assert `any("M3 candidate" in error)`. Run it against the OLD
    # script with the M3 forbidden check disabled. If it still passes, it never
    # tested that check.
    old_source = (
        pathlib.Path(__file__).parent / "t04-baseline-verify_product_master_alignment.py"
    ).read_text(encoding="utf-8")
    old_silenced = load(
        disable(
            old_source,
            "        if forbidden in m3_candidates:",
            "        if False:",
            "the old M3 forbidden check",
        ),
        "old_silenced",
    )
    old_mutation = master.replace(
        "M3-C6 source_content 全局去重、状态和最新原始 JSON",
        "M3-C6 crawl_result 和 content_lead 入库",
    )
    arm(
        "no-op mutation + silent M3 forbidden check -> old test STILL passed (hollow)",
        any("M3 candidate" in error for error in old_silenced.validate_master_text(old_mutation)),
        True,
    )

    print()
    if failures:
        print(f"MUTATION CONTROL FAILED: {len(failures)} arm(s) misbehaved: {failures}")
        return 1
    print("MUTATION CONTROL OK: each rewritten test is coupled to the judgement it names.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
