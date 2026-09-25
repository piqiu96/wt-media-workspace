#!/usr/bin/env python3
"""T-10 / AC-07: 逐个目录树条目做存在性核对（带阳性对照）。

用法: python3 -B -X pycache_prefix=/tmp/pyc-none /tmp/t10/treels.py [--inject]
  --inject  在每棵树末尾注入一个必然不存在的条目，用于证明脚本能报缺。
"""
import os
import sys

REPO = "/Users/aqiuye/Develop/workspace/wt-media/wt-media-workspace"
EXEC = os.path.dirname(REPO)          # wt-media/
MASTER = os.path.join(REPO, "delivery/MASTER_IMPLEMENTATION_PLAN.md")
ARCH = os.path.join(REPO, "docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md")

TREES = [
    (MASTER, "## 2. 文档和事实源", "MASTER §2"),
    (ARCH, "### 3.1 工程目录与仓库结构", "arch §3.1"),
    (ARCH, "## A.1 跨仓库执行根目录", "arch A.1"),
    (ARCH, "## A.2 Workspace", "arch A.2"),
]

BASE = {"wt-media": EXEC, "wt-media-workspace": REPO}


def read_block(path, marker):
    lines = open(path, encoding="utf-8").read().split("\n")
    i = next(n for n, l in enumerate(lines) if l.strip() == marker)
    j = next(n for n in range(i, len(lines)) if lines[n].strip() == "```text")
    k = next(n for n in range(j + 1, len(lines)) if lines[n].strip() == "```")
    return lines[j + 1:k]


def entries(block, inject):
    """产出 (leaf, is_dir, rel)。depth = 名称起始列 // 4。"""
    stack, out = [], []
    body = list(block) + (["└── __t10_injected_absent__/"] if inject else [])
    for line in body:
        if not line.strip():
            continue
        core = line.split(" #")[0].rstrip()
        if core.endswith("/"):
            core = core.rstrip(" ")
        name = core.lstrip("│├└─ ").rstrip()
        if not name or set(name) <= {"│", "├", "└", "─", " "}:
            continue
        depth = (len(core) - len(core.lstrip("│├└─ "))) // 4
        leaf, is_dir = name.rstrip("/"), name.endswith("/")
        stack = stack[:depth]
        stack.append(leaf)
        out.append((leaf, is_dir, "/".join(stack)))
    return out


def main():
    inject = "--inject" in sys.argv
    total = missing = skipped = 0
    print(f"注入模式: {'开（阳性对照）' if inject else '关（实测）'}")
    for path, marker, label in TREES:
        rows = entries(read_block(path, marker), inject)
        root = rows[0][2]
        base = BASE.get(root)
        print(f"\n=== {label}  root={root}/  声明条目 {len(rows)} ===")
        if base is None:
            print(f"  !! 未知根 {root}，跳过整棵树（不静默算作通过）")
            continue
        for i, (leaf, is_dir, rel) in enumerate(rows):
            if i == 0:
                continue                       # 树根自身即 base
            total += 1
            if "YYYY" in rel or "NNN" in rel:
                skipped += 1
                print(f"  SKIP  {rel}   （模板占位符）")
                continue
            full = os.path.join(base, *rel.split("/")[1:])   # 去掉树根名再看 base 相对路径
            ok = os.path.isdir(full) if is_dir else os.path.exists(full)
            if not ok:
                missing += 1
                print(f"  MISS  {rel}")
    print(f"\n合计：声明条目 {total}（其中模板占位 {skipped}，实际核对 {total - skipped}），缺失 {missing}")


if __name__ == "__main__":
    main()
