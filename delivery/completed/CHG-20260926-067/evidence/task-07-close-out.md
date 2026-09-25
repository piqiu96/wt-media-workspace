# T-07 证据：收尾（AC 矩阵签字、归档、台账、快照、两遍指针扫描、四仓对账、DONE Gate）

- CHG: `CHG-20260926-067`
- Task: T-07（`change.md` §8）
- 日期: 2026-09-26
- 锚: `9cef13b`（T-06 的记录提交）

## 1. AC 矩阵签字（11 条，全 PASS）

逐条读数与判读落 `artifacts/t07-ac-matrix.out`。三条**缩减了结论范围**，如实登在这里：

- **AC-07 的字面判据不成立**。判据写的是「旧启停路径在 workspace＋cloud 零命中」，实测 workspace **活跃面 3 行**，
  全在 `config/release-matrix.yaml:114/117/120`。这 3 行是 §5 **Explicitly Not Doing** 明令不改的**历史证据行**
  （该文件 `:2 planning_note` 声明 verified releases 是历史证据，写下时是真的；改写＝伪造历史）
  ⇒ 登记为「**3 行判留 ＋ 可解析／可执行的活指针 0**」，不写成「零命中」。cloud 侧 2 行同理（新文件表头的过去时叙述）。
- **AC-08 目前没有真实被扫对象**。本 CHG 按用户裁定**不往 `scripts/verify/` 放任何脚本**，
  所以「扫描面覆盖子目录」的**唯一**证据是 T-01 的两臂实验（`glob` 分母 12 未点名 / `rglob` 分母 13 点名）。
  判据已改而尚无真实对象——记下来，免得日后被读成「已验证过有子目录的情况」。
- **AC-05／AC-06 的变异红由 T-02 提供**，本 Task 未重跑（重跑要改文件再还原），只由 AC-10 的门禁绿**复证结论态**。

## 2. 归档

`git mv delivery/active/CHG-20260926-067 delivery/completed/CHG-20260926-067`，**49 条 rename ＋ 1 个新 artifact**
（`t07-ac-matrix.out`，其在本 Task 新建）。移后 `delivery/active/` 只剩被跟踪的 `.gitkeep`。

`LEDGER.md`：表行移除（表只剩表头与分隔行，与 CHG-065／066 收尾后同形），表下补本 CHG 的关闭段。

`.ai/CURRENT_CONTEXT.md`：以 `scripts/prepare_ai_workspace.py --no-active` 重生成，`Active CHG: none`／`Status: NONE`。

**归档与记录改动在同一次 commit 里落地**：`change.md` 的 `Status: IMPLEMENTING → DONE`、§9 勾选、§13 九项签字，
都是在 `git mv` **之后**、**提交之前**做的。这样 git 历史里不存在「先归档、再回改」的中间态
（`delivery/completed/README.md` 的「不回改」约束的是归档之后的改动；收口这一次的写入属归档动作本身，
与 CHG-066 把 `task-06-close-out.md` 落在归档目录内是同一形态）。

## 3. `MASTER` §3 读数列（D-04：本 CHG 只刷新一次）

量法**直接 import 门禁自己的 `status_word()`**（`verify_product_master_alignment.py`），不另写等价正则。
读数与分母落 `artifacts/t07-status-words.out`。

| 量 | 归档前 | 归档后 |
| --- | --- | --- |
| 活 `IMPLEMENTING` | 1 | **0** |
| 活记录合计（planned 19 ＋ active） | 20 | **19** |
| 归档 `DONE` | 31 | **32** |
| 归档列 | 33 | **34** |
| 归档记录合计 | 41 | **42** |

闭合式：归档列 34 ＋ 退役 `CLOSED` 2 ＋ `HANDOFF` 2 ＋ `IN_PROGRESS` 4 ＝ **42** ✓；总分母 19 ＋ 42 ＝ 61。

**§3 里那句指向旧 active 路径的话已改指 `delivery/completed/`**——这是第一遍指针扫描**自己找出来的**，
不在任何 Task 的清单里。**残余（登记，不设对策）**：该数列每次归档即过期，通用机制留独立 CHG
（沿用 CHG-064 §14 第 7 项、CHG-066 §14 第 2 项）。

## 4. 两遍失效指针扫描（各带对照与分母）

落 `artifacts/t07-sweep.out`。分母 **944** 个已跟踪文件 ＋ 1 个未跟踪；取数在 `git add` **之后**
（`git grep` 只看得见已跟踪／已暂存文件——§14 第 24 项）。

### 第一遍 字符串

活跃面（排除 `delivery/completed/`）**3 行**：`release-matrix.yaml:117`（判留）、
`docs/superpowers/plans/…:75`（判留，§14 第 9 项）、`MASTER:119`（**真失效指针，已修**）。

- **阳性对照的第一版选错了**：最初拿归档后的新路径 `delivery/completed/CHG-20260926-067` 作对照，读数 **0**——
  因为**当时确实还没有任何文件引用它**（LEDGER 那段是这次才写的）。0 是真的，但**它证明不了检查能看见目录**。
  换成前一个已归档的 CHG（`CHG-20260925-066`，4 文件／154 行）后才有判别力。反向对照（不存在的归档目录）0。
- **反向对照的一条污染（如实登记）**：`scripts/never-existed.sh` **全仓 4 行而非 0**——本 CHG 自己的
  `t05`／`t06-pointer-sweep.out` 把这个对照名写进了正文（「反向对照（证明扫的不是空转）」小节）。
  排除 `delivery/completed/` 后为 0。**与 §14 第 24 项同源**：只要产物里写了一个被扫的串，它就会进别人的分母。

### 第二遍 相对链接 resolve

检查器写在 `/private/tmp`（**不入库**——本 CHG 不往 `scripts/` 加任何脚本，加了就要满足分类规则）。
剔除围栏代码块与行内代码后取 `](target)`。

分母 **496** 篇已跟踪 `*.md`、站内相对链接 **127** 条，**未解析 6 条**——**同一批、同一成因**：相对路径少一级 `..`，
全部落在 `delivery/completed/CHG-20260916-052/…/12-defects-and-security.md`，目标是跨仓的 `wt-media-cloud/…`。
CHG-066 的 T-06 与 CHG-065 的 T-09 各独立量到**同一批 6 条**，三次读数逐条相同 ⇒ **稳定状态而非抖动**，
按 `MASTER:132` 只登记不改。**指向本 CHG 的未解析链接 0 条。**

三条对照全过：①存在的目标被看见 ＋ 坏链接被报出 ＋ **代码块／行内代码里的链接形状不被看见**
（证明剥离是选择性的，不是把检查器弄瞎）；②指向归档后 CHG-067 的链接 **1 条 resolve OK**
（`delivery/LEDGER.md -> completed/CHG-20260926-067/change.md`）⇒ 检查器确实看见了归档后的目录，
否则「0 条未解析」可能只是没扫到；③不存在的归档目录 0 条。

## 5. 四仓对账

落 `artifacts/t07-repo-reconcile.out`。锚是 T-00 的基线（workspace `71fd32f`／cloud `0db02ab`／agent `6d740fc`／
desktop `7c1b0ad`）。四仓改动路径逐条归属 §5，**越界 0**；三仓各**恰一个**提交
（cloud `e2ba4d8`／agent `aa95332`／desktop `9ba5486`），符合「跨仓各自提交」。

**两条脏项先于本 CHG 存在、全程未触碰**：cloud 未跟踪的 `dump.rdb`、agent 的 ` M AGENT-INDEX.md`。
⇒ **归因声明**：agent 仓的 `Ran 409 / OK` 是**脏工作树上的绿**，不是干净提交上的绿；此处不据此拔高结论。

## 6. 收尾读数

六门禁 ＋ `sync_skills.py check` ＋ workspace 套件，取在**最后一次改动之后**，落 `artifacts/t07-gate-final.out`。

**如实记**：§6 的三组读数是 workspace 侧的量，**不代替** agent 侧的 `Ran 409 / OK`（两者不互相代表）。

## 7. 记录体量（本 Task **越界**，如实登记）

判据（沿用 CHG-065／066 的 v5）：**每 Task 增量**——`change.md` ≤ 5,120 B、`checkpoint.md` ≤ 4,096 B、evidence md ≤ 9,216 B。
锚取**上一 Task 提交后的 blob**（`9cef13b:delivery/active/…`），非 HEAD。读数落 `artifacts/t07-record-size.out`。

| 量 | 读数 | 界 | 判 |
| --- | --- | --- | --- |
| `change.md` | 44516 → 51555，**+7039（＋36%）** | 5120 | **越界** |
| `checkpoint.md` | 18751 → 22802，**+4051** | 4096 | 界内 |
| `evidence/task-07-close-out.md` | 新增 **8123** | 9216 | 界内 |

首测为 **+7935**；做了一轮**只删复述、不删读数**的压缩（DONE Gate 九项与 AC 各格的解释性措辞改指 §10／§5 的对应读数）后为 +7039，**未删任何一条读数、路径或 commit id**。
**残留越界如实上报、不强压**，同 CHG-066 `t03-record-size.out` 的先例（那次 +5740、越界 +12%）。与 T-00 的越界不同类：T-00 是「一次写完整份计划」，本项是**收尾 Task 的签字手续本身**（11 条 AC 读数 ＋ 9 项 DONE Gate ＋ 归档动作）；**CHG-066 的收尾 Task 未量自身增量，故本项是该量法的首次实测**。
