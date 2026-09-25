#!/usr/bin/env python3
"""T-11: v2 -> merged 逐行留存量核对（否决式报告，不静默算通过）。

对 `前端框架视觉规范v2.md` 的每一行非空、非标题行，做归一化后在合并件里找。
报出分母与逐条 MISS，由人来判每一条 MISS 是「功能删除」还是「真丢失」。
阳性对照：把源文件换成一份合并件里必然没有的行，确认脚本会报 MISS。
"""
import re, subprocess, sys

# 源文件已被合并删除，从 git 里读合并前那一版（REF 必须是合并前的提交）
REF = "HEAD"
V2_PATH = "docs/engineering/specs/前端框架视觉规范v2.md"
V2 = f"{REF}:{V2_PATH}"
MERGED = "docs/engineering/specs/web-desktop-visual-system.md"

# 归一化：去空白 + 去 markdown 强调标记 + 引号/斜杠变体统一
FOLD = {"\u201c": "\u300c", "\u201d": "\u300d", "\uff0f": "/", "\uff1a": ":", "\uff1b": ";"}

def canon(s):
    s = s.strip()
    for a, b in FOLD.items():
        s = s.replace(a, b)
    s = s.replace("*", "").replace("`", "").replace("_", "")
    s = re.sub(r"[\u3002\uff1b;.,\u3001]+$", "", s)
    s = re.sub(r"\s+", "", s)
    return s

def norm(s):
    return re.sub(r"\s+", " ", s.strip())

def load(path):
    """path 为 "<ref>:<file>" 时从 git 读；否则读工作区。"""
    if ":" in path and not path.startswith("."):
        out = subprocess.run(["git", "show", path], capture_output=True, text=True, check=True)
        return out.stdout.split("\n")
    return open(path, encoding="utf-8").read().split("\n")

def main():
    inject = "--inject" in sys.argv
    v2, merged = load(V2), load(MERGED)
    hay = norm("\n".join(merged)).replace("\n", " ")
    # 归一化后的合并件全文（去掉所有空白差异）
    flat = canon("\n".join(merged))
    total = miss = 0
    misses = []
    for i, raw in enumerate(v2, 1):
        s = norm(raw)
        if not s or s.startswith("#") or s in ("---",) or s.startswith("> 文档"):
            continue
        total += 1
        key = canon(s)
        if key in flat:
            continue
        miss += 1
        misses.append((i, s))
    if inject:
        for probe in ["这一整行是 T-11 阳性对照，合并件里必然没有它", "TDesign Starter 永远直接加载线上 Web 地址"]:
            total += 1
            if canon(probe) not in flat:
                miss += 1
                misses.append((-1, probe))
    print(f"注入模式: {'开（阳性对照）' if inject else '关（实测）'}")
    print(f"分母: v2 非空非标题行 {total} 行；未在合并件中找到 {miss} 行\n")
    for ln, s in misses:
        print(f"  MISS  v2:{ln if ln > 0 else '(注入)'}  {s}")
    print(f"\n合计：分母 {total}，MISS {miss}，命中 {total - miss}")

main()
