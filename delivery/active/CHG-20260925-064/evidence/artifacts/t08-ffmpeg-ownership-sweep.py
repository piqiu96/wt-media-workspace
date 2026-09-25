#!/usr/bin/env python3
"""T-08 扫描：活文件里「执行方」与 FFmpeg 同现的地方。

用法：
    python3 -B -X pycache_prefix=/tmp/pyc-none t08-ffmpeg-ownership-sweep.py [root] [--rev <rev>]

    不带 --rev 读工作区；带 --rev 用 `git show <rev>:<path>` 读该提交的内容
    （这样改前 / 改后是同一个扫描器、同一套判据，可直接对拍）。

两列，都不是结论：
  candidate  同一子句内 owner 词与 ffmpeg 词相距 ≤80 字符、且该子句**无**否定词
  negated    同上，但该子句**含**否定词（不 / 禁止 / 无 / 移除 / 撤销 / 排除）

否定列不是「干净」的：`不改变 M2 … FFmpeg … 的 Agent 边界` 这种写法在否定外壳里
仍然断言了「这个边界里含 FFmpeg」——它是真冲突，却落在 negated 列。所以结论只能
来自**逐行判定**，不能来自任一列是否为空。判定结果见同目录 task-08-*.md。
"""
import re
import subprocess
import sys
import pathlib

EXCL = ("delivery/completed/", "delivery/reports/", ".claude/", ".codex/")
OWNER = r"(?:Agent|Desktop|本地|本机|运营电脑)"
FF = r"(?:ffmpeg|FFmpeg|ffprobe|FFprobe)"
NEG = r"[不禁止无移除撤销排除]"
SPLIT = "。；;"
MAX_DIST = 80


def live_files(root: pathlib.Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True
    ).stdout.split("\n")
    return [f for f in out if f and not f.startswith(EXCL)]


def readers(root: pathlib.Path, rev: str | None):
    if rev is None:
        return lambda f: (root / f).read_text(encoding="utf-8", errors="strict")
    def read(f: str) -> str:
        return subprocess.run(
            ["git", "-C", str(root), "show", f"{rev}:{f}"],
            capture_output=True, text=True, check=True,
        ).stdout
    return read


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = pathlib.Path(args[0] if args else ".")
    rev = None
    if "--rev" in sys.argv:
        rev = sys.argv[sys.argv.index("--rev") + 1]
    read = readers(root, rev)

    owner_re = re.compile(OWNER)
    ff_re = re.compile(FF)
    cand: list[tuple[str, str, int]] = []
    neg: list[tuple[str, str, int]] = []
    n_files = n_lines = 0

    for path in live_files(root):
        try:
            text = read(path)
        except (UnicodeDecodeError, FileNotFoundError, subprocess.CalledProcessError):
            continue
        touched = False
        for i, line in enumerate(text.split("\n"), 1):
            if not ff_re.search(line):
                continue
            n_lines += 1
            touched = True
            if not owner_re.search(line):
                continue
            for clause in re.split(f"[{SPLIT}]", line):
                if not (owner_re.search(clause) and ff_re.search(clause)):
                    continue
                dist = min(
                    abs(a.start() - b.start())
                    for a in owner_re.finditer(clause)
                    for b in ff_re.finditer(clause)
                )
                if dist > MAX_DIST:
                    continue
                (neg if re.search(NEG, clause) else cand).append(
                    (f"{path}:{i}", clause.strip(), dist)
                )
        n_files += touched

    where = f"工作区（{root}）" if rev is None else f"提交 {rev}"
    print(f"# T-08 FFmpeg 归属扫描 —— {where}")
    print(f"# 范围：git ls-files，排除 {', '.join(EXCL)}")
    print(f"# 分母：含 ffmpeg 的行 {n_lines} 行，分布在 {n_files} 个文件")
    print()
    for title, rows in (("candidate（子句内无否定词）", cand), ("negated（子句内含否定词）", neg)):
        print(f"### {title} —— {len(rows)} 条")
        for loc, clause, dist in rows:
            print(f"{loc} | 距离 {dist} | {clause[:150]}")
        print()
    print(f"# 候选合计 {len(cand) + len(neg)} 条。两列都不是结论——判定见 task-08-*.md。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
