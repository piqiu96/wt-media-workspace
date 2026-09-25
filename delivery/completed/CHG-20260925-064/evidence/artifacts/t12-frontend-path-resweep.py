#!/usr/bin/env python3
"""T-12 归档后复测：判据 A（前端源码根与六个旧名清空）。

T-11 时的阳性对照读的是 `HEAD`——那时 `HEAD` 还是合并**前**那一版，读数有效。
T-11 的提交一落，`HEAD` 就变成合并**后**，同一个对照再读 `HEAD` 得到的是
「docs/ 下 0」，对照失去判别力。故这里把对照锚改成本 CHG 的**开工基线**
（`0148c34~1`，即 T-01 激活提交的父提交），并同时打印 `HEAD` 以免误读。

判据口径：`docs/` 下为 0。全仓余命中一律逐个文件报出，看它落在哪。
"""
import re
import subprocess
import sys
from collections import Counter

BASE = "0148c34~1"  # 本 CHG 开工基线（T-01 激活提交的父提交）
PATS = [
    "wt-media-cloud/frontend",
    "cloud/frontend",
    "pnpm",
    "dist-web",
    "build:web",
    "dev:web",
    "frontendCommit",
    "localhost:5173",
]
MERGED = "|".join(re.escape(p) for p in PATS)


def grep(pattern, *revs, path=None):
    cmd = ["git", "grep", "-nE", "-e", pattern] + list(revs) + ["--", path or "."]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode not in (0, 1):  # 0 = 有命中, 1 = 无命中, 其他 = 出错
        sys.exit(f"git grep failed ({r.returncode}): {r.stderr}")
    return [ln for ln in r.stdout.split("\n") if ln]


def counts(pattern, rev=None):
    ws = grep(pattern)
    docs = grep(pattern, path="docs")
    base = grep(pattern, BASE)
    return len(ws), len(docs), len(base)


def main():
    print("### T-12 归档后复测：判据 A（前端源码根 `wt-media-cloud/frontend` 与六个旧名）")
    print("口径：git grep -nE（只扫已跟踪文件）；对照 = 开工基线 " + BASE)
    print()
    print(f"{'模式':<28}{'ws全仓':>8}{'ws/docs':>9}{'基线全仓':>10}")
    for p in PATS:
        w, d, b = counts(p)
        print(f"{p:<28}{w:>8}{d:>9}{b:>10}")
    print()

    def breakdown(label, revs):
        # `git grep <rev>` 的行是 `<rev>:<path>:<lineno>:<content>`，
        # 带 rev 时必须先剥掉一段，否则「文件」那列会全是 rev 名。
        print(f"--- {label} ---")
        skip = 1 if revs else 0
        out = Counter(":".join(ln.split(":")[skip:skip + 1]) for ln in grep(MERGED, *revs))
        for f, n in out.most_common():
            print(f"  {n:>3}  {f}")
        print(f"  合计行数: {sum(out.values())}；其中 docs/ 下: {len(grep(MERGED, *revs, path='docs'))}")

    breakdown("工作区全仓，七模式合并（记录落点）", ())
    breakdown("开工基线 " + BASE + " 全仓（阳性对照）", (BASE,))
    print()

    # 阳性对照必须有判别力：基线在 docs/ 下必须非 0，否则这个模式对目标无鉴别力
    base_docs = len(grep(MERGED, BASE, path="docs"))
    ws_docs = len(grep(MERGED, path="docs"))
    ok = base_docs > 0 and ws_docs == 0
    print(f"对照判别力：基线 docs/ {base_docs} 行 > 0 且工作区 docs/ {ws_docs} 行 == 0 → "
          f"{'✓ 有判别力' if ok else '✗ 无判别力'}")
    print()
    print("口径提醒：`HEAD` 现在已是 T-11 之后，读 `HEAD` 会得到 docs/ 0 —— 那是**结果**不是对照。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
