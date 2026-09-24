# evidence — T-01 建 CHG 并激活

- CHG: CHG-20260924-060
- Task: T-01
- Date: 2026-09-24
- Type: command
- Status: PASS

## Purpose

把 CHG-056 归档时登记的四项待裁定中的三项纳入一个 Level-S CHG 的授权范围，
并使快照、LEDGER、active 目录三者互指同一变更（治理一致性是执行的前置条件）。

## Method

```
# Start Gate：四仓工作区状态
for r in wt-media-workspace wt-media-desktop wt-media-agent wt-media-cloud; do
  git -C /Users/aqiuye/Develop/workspace/wt-media/$r status --short --branch
done

# 现状
ls -la delivery/active/
cat delivery/LEDGER.md
cat .ai/CURRENT_CONTEXT.md

# 建记录后
python3 scripts/prepare_ai_workspace.py --change CHG-20260924-060
python3 scripts/verify_agent_entry.py
python3 scripts/verify_delivery_governance.py
```

## Expected

1. 四仓工作区干净（无未提交改动）——否则「未解释的脏改动」会污染后续 diff 检查。
2. `delivery/active/` 仅 `.gitkeep`，`LEDGER.md` 无表行，快照为 `none`（即 active 名额为空，可激活）。
3. `prepare_ai_workspace.py` 接受本 CHG 并把 `affected_repositories` 解析为三仓。
4. 两个验证器 exit 0。

## Actual

**Start Gate（实测）**

```
=== wt-media-workspace ===
## main...origin/main [ahead 28]
=== wt-media-desktop ===
## main...origin/main [ahead 26]
=== wt-media-agent ===
## main...origin/main [ahead 37]
=== wt-media-cloud ===
## main...origin/main [ahead 3]
```

四仓均无未提交改动（`--short` 无输出行，只有分支行）。active 目录只有 `.gitkeep`；
LEDGER 表体为空；快照 `- Active CHG: none` / `- Status: NONE` / `- Affected Repositories\n\n- None`。

**一次失败并修正**：首次加 LEDGER 表行时写成 markdown 链接形式
`| [CHG-20260924-060](active/…) | … |`，两个验证器同时报：

```
ERROR execution snapshot and LEDGER disagree: CHG-20260924-060 != none
ERROR current context and ledger disagree: CHG-20260924-060 != none
```

根因是 `verify_delivery_governance.py:37` 的 `LEDGER_ROW_RE = re.compile(r"^\|\s*(CHG-\d{8}-\d{3})\s*\|")`
要求**裸 id 紧跟在竖线之后**，链接形式不匹配 ⇒ `parse_ledger_changes` 返回空 ⇒ 被读成 `none`。
（对照：`git show HEAD~1:delivery/LEDGER.md` 里 CHG-056 当时那行就是裸 id 形式。）
改为 `| CHG-20260924-060 | … |` 后两者同时转绿。这一条是**验证器确实在校验**的正面证据，
不是形式主义：链接形式若被接受，`len(ledger_changes) == 1` 的分支就不会成立。

**修正后的实测输出**

```
$ python3 scripts/prepare_ai_workspace.py --change CHG-20260924-060
  "active_change": "CHG-20260924-060",
  "active_change_status": "IMPLEMENTING",
  "active_milestone": null,
  "affected_repositories": ["wt-media-desktop", "wt-media-agent", "wt-media-workspace"],
  "generated_execution_skill": ".../.agents/skills/executing-wt-media-change/SKILL.md"

$ python3 scripts/verify_agent_entry.py
execution snapshot: 1971 characters (~788 tokens, budget 8000 characters)
Agent entry verification ok. 0 warning(s) need review.
exit=0

$ python3 scripts/verify_delivery_governance.py
Delivery governance verification ok. Active CHG: CHG-20260924-060
exit=0
```

`active_milestone: null` 是 Level S 的预期结果（验证器只对 `M`/`L` 强制 Milestone 引用，
见 `verify_delivery_governance.py:118-122`），与 §3 用散文写「锚点」的写法一致。

## Follow-Up

- 本 Task 未验证的部分：`verify_agent_entry.py` 报 `0 warning(s)`，但未逐条检查它对
  `AGENT-INDEX.md` 的解析内容；归档时会再跑一次（`--no-active`），届时状态将变为 `none`。
- 快照生成时间 `2026-09-24T03:55:56Z`；本文件落盘后不再改快照。
- 未做：`delivery/completed/CHG-20260923-056/change.md` §12 的处置去向标注（属 T-05 收尾，
  须等三项改动的实际结果落定后再回写，否则会写成预测而非事实）。
