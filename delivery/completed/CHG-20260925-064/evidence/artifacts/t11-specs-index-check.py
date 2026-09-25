#!/usr/bin/env python3
"""T-11 / AC-12: specs 索引与目录实况双向一致，链接可 resolve。

双向：索引里每个链接都能 resolve 到存在的文件；目录里每个（非 README 的）.md 都被索引列到。
阳性对照 --inject：注入一条不存在的链接、并造一个未索引的文件名，两个方向各报一次 FAIL。
"""
import os, re, sys

D = "docs/engineering/specs"
IDX = os.path.join(D, "README.md")


def main():
    inject = "--inject" in sys.argv
    text = open(IDX, encoding="utf-8").read()
    links = re.findall(r"\]\(([^)]+)\)", text)
    links = [l for l in links if not l.startswith(("http://", "https://", "#"))]

    actual = sorted(f for f in os.listdir(D) if f.endswith(".md") and f != "README.md")

    fail = 0
    print(f"注入模式: {'开（阳性对照）' if inject else '关（实测）'}")
    print(f"\n索引链接 {len(links)} 条；目录内 .md（不含本索引）{len(actual)} 篇")

    print("\n[方向一] 索引里的每条链接都能 resolve")
    for l in links:
        p = os.path.join(D, l)
        if not os.path.exists(p):
            fail += 1
            print(f"  FAIL  链接不可达: {l}")
    if inject:
        l = "__t11_index_positive_control__.md"
        if not os.path.exists(os.path.join(D, l)):
            fail += 1
            print(f"  FAIL  链接不可达（注入）: {l}")
    print(f"  失败 {fail}")

    before = fail
    print("\n[方向二] 目录里的每篇都被索引列到")
    for f in actual:
        if f not in links:
            fail += 1
            print(f"  FAIL  未被索引: {f}")
    if inject:
        f = "__t11_unindexed_positive_control__.md"
        if f not in links:
            fail += 1
            print(f"  FAIL  未被索引（注入）: {f}")
    print(f"  失败 {fail - before}")

    print(f"\n合计失败 {fail}")
    print(f"分母：索引链接 {len(links)} ＋ 目录 .md {len(actual)} ＝ {len(links) + len(actual)} 次判断")


main()
