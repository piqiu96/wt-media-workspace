#!/usr/bin/env python3
"""把 run-manifest.json 渲染成各阶段证据文件，确保每条结论都能回溯到具体步骤。"""
import json, collections, pathlib

EV = pathlib.Path(__file__).resolve().parent.parent
M = json.loads((EV / "run-manifest.json").read_text(encoding="utf-8"))

FILES = [
    ("G0",  "01-freeze-and-preconditions.md", "阶段 G0-G3：静态冻结与前置门禁"),
    ("G1",  None, None), ("G2", None, None), ("G3", None, None),
    ("G4",  "03-external-reachability.md",   "阶段 G4：外部可达性决策"),
    ("5",   "04-entries-and-import.md",      "阶段 5：内容池入口与导入"),
    ("5.5", "05-strategy-config.md",         "阶段 5.5：挖掘策略配置矩阵"),
    ("6",   "06-scheduling.md",              "阶段 6：周期触发与双层防重"),
    ("7",   "07-auto-material.md",           "阶段 7：自动转素材规则矩阵"),
    ("8",   "08-five-states-retry.md",       "阶段 8：五态、重试与确认"),
    ("9",   "09-permissions-idempotency.md", "阶段 9：权限与幂等"),
    ("10",  "10-regression-walkthrough.md",  "阶段 10：回归与视觉走查"),
    ("11",  "11-residue-teardown.md",        "阶段 11：残留登记与收尾"),
]
GROUPS = [("G0", ["G0", "G1", "G2", "G3"]), ("G4", ["G4"]), ("5", ["5"]), ("5.5", ["5.5"]),
          ("6", ["6"]), ("7", ["7"]), ("8", ["8"]), ("9", ["9"]), ("10", ["10"]), ("11", ["11"])]
META = {k: (f, t) for k, f, t in FILES if f}

for key, phases in GROUPS:
    name, title = META[key]
    rows = [e for e in M if e["phase"] in phases]
    c = collections.Counter(e["verdict"] for e in rows)
    out = ["# %s" % title, "",
           "> 由 `tools/render-evidence.py` 从 `run-manifest.json` 渲染，每一步可回溯。",
           "> 判定分布：%s。" % "，".join("%s=%d" % kv for kv in sorted(c.items())), "",
           "| 步骤 | 判定 | 请求 | 期望 | 实际 |", "| --- | --- | --- | --- | --- |"]
    for e in rows:
        cell = lambda s: str(s).replace("|", "\\|").replace("\n", " ")[:400]
        out.append("| %s | %s | %s | %s | %s |" % (
            e["step_id"], e["verdict"], cell(e["request"]), cell(e["expected"]), cell(e["actual"])))
    notes = [e for e in rows if e.get("note")]
    if notes:
        out += ["", "## 备注", ""]
        for e in notes:
            out.append("- **%s**：%s" % (e["step_id"], e["note"]))
    (EV / name).write_text("\n".join(out) + "\n", encoding="utf-8")
    print("wrote", name, "(%d steps)" % len(rows))
