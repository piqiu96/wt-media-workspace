# T-01 激活与开工基线

本文件只记事实（命令／动作、期望、实际、结论），不重复需求。原始输出：`artifacts/t01-baseline.out`。

## 1. 激活动作

| 动作 | 期望 | 实际 |
|---|---|---|
| 建 `delivery/active/CHG-20260925-065/`（`change.md`、`checkpoint.md`、`evidence/`） | 记录存在且 §5 封闭、§7 = `None.` | 已建；§5 四小节齐全；§7 为字面 `None.` |
| `LEDGER.md` 表行 | 由占位行换成活动行，且合 `verify_delivery_governance.py:37` 的 `LEDGER_ROW_RE`（行首 `\| CHG-…\|`） | 占位行 `\| — \| 当前没有 active CHG（…） \| — \| — \|` 已替换为活动行——与 `git show bd5df2c~13:delivery/LEDGER.md`（CHG-063 active 期）的表行同形：纯文本、无链接、四列 |
| ↳ 一次失败的尝试（登记） | 表行标题须**逐字**等于 `change.md` H1 的标题 | 第一版把标题缩短为「…——双指针 + 单一正文」，`verify_product_master_alignment.py` 报 `Ledger is not aligned with active CHG CHG-20260925-065`，`unittest` 同时红 1 条。成因是该脚本 `:311` 用 `^# {CHG}[：:] ?(.+)$` 取 H1 全文并在 `:338` 拼 `expected_row` 做整行包含判断。改为 H1 全文 `三个运行仓入口文件形态统一——参考 workspace 的双指针 + 单一正文` 后两条同时转绿 ⇒ **该门禁有判别力** |
| `python3 scripts/prepare_ai_workspace.py --change CHG-20260925-065` | 快照指本 CHG | `Active CHG: \`CHG-20260925-065\``／`Status: \`IMPLEMENTING\``；分列 `mode: workspace-governance-active`、`active_change: CHG-20260925-065`、`active_milestone: null`、`affected_repositories` 四仓齐全 |
| 建 `status/` 目录？ | **不建** | `AGENT-INDEX.md:184` 规定仅同一 CHG **多工程并行**实施时才建；本 CHG 三仓是**顺序**实施，故不建 |

## 2. 四仓 git 基线（收尾 T-09 按此对账）

开工 commit：`bd5df2c26dcb020eebafc9d0aafbdc71ec23586d`

| 仓库 | `git status --porcelain` |
|---|---|
| `wt-media-workspace` | 开工时净；本 Task 后 `?? delivery/active/CHG-20260925-065/`（本 CHG 自己的未跟踪记录，收尾提交） |
| `wt-media-cloud` | `?? dump.rdb` |
| `wt-media-agent` | 净 |
| `wt-media-desktop` | 净 |

`dump.rdb` 是**他人的未跟踪产物**：88 字节、mtime `2026-09-24 17:19:16`，早于本 CHG 一天。不碰、不提交、不清理（沿用 CHG-20260925-063／064 的处置）。

## 3. 入口文件体量（分母：四仓 × 四类 = 16 格）

| 仓 | `CLAUDE.md` | `AGENTS.md` | `AGENT-INDEX.md` | `DIRECTORY_MAP.md` |
|---|---|---|---|---|
| `wt-media-workspace` | 1755 B / 28 行 | 1267 B / 22 行 | 12736 B / 209 行 | **不存在** |
| `wt-media-cloud` | 2715 B / 168 行 | 6046 B / 113 行 | 4357 B / 60 行 | 7449 B / 105 行 |
| `wt-media-agent` | 226 B / 10 行 | 3705 B / 45 行 | 4668 B / 65 行 | 9886 B / 117 行 |
| `wt-media-desktop` | 283 B / 12 行 | 3170 B / 39 行 | 8193 B / 75 行 | 12036 B / 90 行 |

workspace 的 `DIRECTORY_MAP.md` 不存在**不是**缺口：`AGENT-INDEX.md:71`／`:120` 与 `prepare_ai_workspace.py:172` 都只对**目标仓**点名该文件，workspace 自身豁免（见 `change.md` §5）。

## 4. 三仓 `AGENT-INDEX.md` 的 H2 序列

```
cloud   7 节: ## 依赖|## 定位|## 本仓库拥有|## 本仓库不拥有|## 需求路由|## 禁止|## 上下文加载顺序|
agent   7 节: 同上
desktop 7 节: 同上
```

逐字比较：**cloud == agent == desktop : YES**。

⇒ 三仓的一致性是**靠互相模仿得到的，不靠任何规定**（`change.md` F-01）。这同时是 AC-06（新 `check_layer3_shape` 要求长度为 **8**）的**先红读数**：该检查落地时对现状必然报红，因为 `## 本仓规则` 尚未加入；T-05～T-07 逐个补齐后转绿。

## 5. 门禁读数（开工前）

```
verify_agent_entry: exit=0 | Agent entry verification ok. 0 warning(s) need review.
verify_delivery_governance: exit=0 | Delivery governance verification ok. Active CHG: none
```

两条都在**本 CHG 加新检查之前**取，故 `verify_agent_entry` 的 0 warning 只说明旧检查范围不够（`change.md` F-04，已附阳性对照），**不**说明现状合规。第二行取于 LEDGER 改行之前，故 `Active CHG: none`。

## 6. 未覆盖

- 本节未量 `README.md`（不在四类入口文件内；其 `:42-51` 的处置登记 `change.md` §14 第 4 项，归 CHG-20260925-066）。
- 本节未量三仓的 `.claude/skills`／`.codex/skills` 副本（不属本 CHG 范围；T-09 对账时按 AC-14 一并看）。
