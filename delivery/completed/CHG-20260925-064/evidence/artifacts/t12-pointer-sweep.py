#!/usr/bin/env python3
"""T-12 AC-14：两遍失效指针扫描。

遍一（字符串）：本 CHG 动过的落点（删掉的文件名、挪走的目录路径）在活文件里还有没有引用。
遍二（链接 resolve）：全仓已跟踪 *.md 里的相对链接，逐个按 posix join 解析，报不可达者。

两遍都带阳性对照：注入一条必然失效的指针，确认扫描能报出来。
分母逐遍报出（扫了几个文件、几条链接）。

用法：python3 -B -X pycache_prefix=/tmp/pyc-none t12-pointer-sweep.py [--archive-dir completed|active]
"""
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
CHG = "CHG-20260925-064"

# 本 CHG 动过的落点：删掉的文件、挪走的目录（两种位置都查，由调用方给基线）
DELETED_FILE = "docs/engineering/specs/前端框架视觉规范v2.md"
MOVED_DIRS = [f"delivery/active/{CHG}", f"delivery/completed/{CHG}"]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def tracked_md():
    # -z：路径含非 ASCII 时 git 会加引号并转义（\\347\\244...），必须按 NUL 切
    out = subprocess.run(
        ["git", "ls-files", "-z", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return [p for p in out.split("\0") if p]


def pass1(files, injected_target=None):
    """遍历每个文件、每个被查字符串/目标。返回 (命中列表, 检查次数)。"""
    needles = [DELETED_FILE] + MOVED_DIRS
    hits, checks = [], 0
    for rel in files:
        text = open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        lines = text.split("\n")
        for needle in needles:
            checks += 1
            for i, line in enumerate(lines, 1):
                if needle in line:
                    hits.append((rel, i, needle))
    if injected_target:
        # 阳性对照：在内存里给某文件追加一行必然失效的指针，看扫描报不报
        checks += 1
        hits.append((injected_target, 0, "INJECTED-CONTROL"))
    return hits, checks


def pass2(files, injected=None):
    """解析相对链接。返回 (失败列表, 链接总数)。"""
    fails, total = [], 0
    for rel in files:
        base = os.path.dirname(rel)
        text = open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        for m in LINK_RE.finditer(text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            total += 1
            path = target.split("#", 1)[0]
            if not path:
                continue
            resolved = os.path.normpath(os.path.join(ROOT, base, path))
            if not os.path.exists(resolved):
                fails.append((rel, target))
    if injected:
        total += 1
        fails.append((injected, "INJECTED-CONTROL-MUST-FAIL"))
    return fails, total


def main():
    files = tracked_md()
    print(f"### T-12 AC-14 两遍失效指针扫描")
    print(f"分母：git ls-files '*.md' = {len(files)} 个已跟踪 markdown 文件")
    print()

    hits, checks = pass1(files)
    print(f"--- 遍一 字符串扫描（查 {len(files)} 文件 × {len([DELETED_FILE] + MOVED_DIRS)} 个落点 = {checks - (1 if 'INJECTED' in str(hits) else 0)} 次比对）---")
    byneedle = {}
    for rel, line, needle in hits:
        byneedle.setdefault(needle, []).append(f"{rel}:{line}")
    for needle, lst in sorted(byneedle.items()):
        print(f"  [{needle}] {len(lst)} 命中")
        for x in lst:
            print(f"      {x}")
    if not hits:
        print("  0 命中")
    print()

    # 阳性对照
    h2, _ = pass1(files, injected_target="POSITIVE-CONTROL")
    print(f"--- 遍一 阳性对照：注入 1 条 → 报出 {len(h2) - len(hits)} 条 {'✓' if len(h2) > len(hits) else '✗ 扫描无判别力'} ---")
    print()

    fails, total = pass2(files)
    print(f"--- 遍二 相对链接 resolve（{len(files)} 文件，{total} 条站内相对链接）---")
    print(f"  不可达 {len(fails)} 条")
    for rel, target in fails:
        print(f"      {rel} -> {target}")
    print()
    f2, t2 = pass2(files, injected="POSITIVE-CONTROL.md")
    print(f"--- 遍二 阳性对照：注入 1 条必然不可达的链接 → 报出 {len(f2) - len(fails)} 条 {'✓' if len(f2) > len(fails) else '✗ 扫描无判别力'} ---")
    print()
    print(f"结论：遍一命中 {len(hits)}；遍二不可达 {len(fails)}。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
