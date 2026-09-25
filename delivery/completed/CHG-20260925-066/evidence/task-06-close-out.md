# T-06 证据：收尾（归档、台账、快照、两遍指针扫描、四仓对账）

- CHG: `CHG-20260925-066`
- Task: T-06（`change.md` §8）
- 日期: 2026-09-26
- 锚: 提交 `e730956`（T-05 的提交）

## 1. 归档

`git mv` 把本 CHG 目录从 `delivery/active/` 移到 `delivery/completed/`，**27 条 rename**。
`delivery/active/` 移后只剩被跟踪的 `.gitkeep`。

`LEDGER.md`：表行移除（表只剩表头与分隔行，与 CHG-065 收尾后的形态一致），并在
关闭段补一段本 CHG 的条目。

`.ai/CURRENT_CONTEXT.md`：以 `scripts/prepare_ai_workspace.py --no-active` 重生成，
`Active CHG: none`／`Status: NONE`。

## 2. `MASTER` §3 读数列（D-04：本 CHG 只刷新一次）

量法**直接 import 门禁自己的 `status_word()`**（`verify_product_master_alignment.py`），
不另写等价正则——先例：本仓成文的「复核门禁管辖的量要调门禁自己的函数」。

| 量 | 归档前 | 归档后 |
| --- | --- | --- |
| 活列（退役词已归零） | 20 | **19** |
| 归档列 | 32 | **33** |
| 归档 `DONE` | 30 | **31** |
| `IMPLEMENTING` 活 | 1 | **0** |
| 活记录（planned ＋ active） | 19 ＋ 1 ＝ 20 | 19 ＋ 0 ＝ **19** |
| 归档记录 | 40 | **41** |

闭合式：归档列 33 ＋ 退役 `CLOSED` 2 ＋ `HANDOFF` 2 ＋ `IN_PROGRESS` 4 ＝ **41** ✓。
前后两轮逐词读数与分母见 `artifacts/t06-status-words.out`。

**残余（登记，不设对策）**：该数列**每次归档即过期**。本 CHG 按 D-04 只做一次刷新，
机制本身留给独立 CHG（`change.md` §14 第 2 项）。

## 3. 两遍失效指针扫描（各带阳性对照与分母）

### 第一遍 字符串

分母 **891** 个已跟踪／已暂存文件。**取数必须在 `git add` 之后**：`git grep` 与
`git ls-files` 只看得见已跟踪与已暂存的文件，未跟踪的产物不在分母里——第一版在
stage 之前量到的是 **887**，对不上提交后的树。

- **活跃面命中 0**（活跃面＝不在 `delivery/completed/` 之下）——**这是稳定读数**。
- 全仓命中数**本文件不内联**：它有两个不稳定的来源。①会被记录自己复述的那个串
  改变（写这一节就要写出那个串）；②**本扫描的产物文件一旦入库就落进自己的分母，
  而它逐条列出命中行**。后者已实测：同一命令连跑两轮 **43 → 87**，逐文件分解给出
  **自指 44 处、真实 43 处、活跃面 0 处**。确切读数与分解以 `artifacts/t06-sweep.out` 为准。
- 命中**全部**落在本 CHG 自己已归档的记录里，逐条判性质后是两类：
  **过去时叙述**（T-01「建 active 目录三件」）与**原始捕获回读**
  （`git status --porcelain` 的读数原样留档）。按「路径判修、叙述判留」与
  `MASTER:132`「归档记录保持原样、不回改」**一律保留**。
- **归档前**同一命令在本 CHG 目录之外只有 **3 处**，**全在 `.ai/CURRENT_CONTEXT.md`**
  （生成物，第 1 节重生成后归零）。

阳性对照：同一命令在同一棵树上搜**归档后的新路径**、搜**上一 CHG 的 id** 均命中，
搜一个**故意拼错的路径**为 0 ⇒ 该 0 是判据的读数，不是命令空转。

### 第二遍 相对链接 resolve

分母 **474** 篇已跟踪 `*.md`、**118** 条站内相对链接；**未解析 6 条**，成因是相对
路径少一级 `..`，全部落在 `delivery/completed/CHG-20260916-052/evidence/
m3-e3-acceptance-20260923/12-defects-and-security.md`。**指向本 CHG 的未解析链接 0 条。**

CHG-065 的 T-09 独立量到**同一批 6 条、同一成因**（该记录 §14 第 20 项），两次读数
逐条相同 ⇒ 这是**稳定状态而非抖动**，按 `MASTER:132` 只登记不改（本 CHG §14 第 23 项）。

阳性对照三条全过（存在的目标、不存在、另一个存在的目标）。另做**双向对照**证明
「跳过代码块与行内代码」不是在弄瞎扫描器：散文里的链接形状被看见、围栏代码块里的
不被看见、行内代码里的不被看见。

## 4. 四仓对账（AC-09）

锚：`artifacts/t01-repo-baseline.out` 记的四仓 HEAD。判据是 **§5 声明的范围**，
不是「路径前缀像不像治理文件」——本脚本第一版按后者写，把五类在范围内的路径报成
越界（§14 第 21 项）。

- workspace：自基线 `5c1d98c` 起 **36 条改动路径**逐条落在 §5 范围内，**越界 0**；
  **运行时代码／配置改动 0**。
- cloud／agent／desktop：HEAD 与基线**逐字相同**（`0db02ab`／`6d740fc`／`7c1b0ad`）；
  工作树只有 cloud 一个**开工时就存在**的未跟踪 `dump.rdb`（他人在途产物，不碰）。

`artifacts/t06-repo-reconcile.out`。

## 5. 收尾判据

- 六个静态门禁全 `exit=0`；`sync_skills.py check` `exit=0`；
  `python3 -m unittest discover -s tests -q` **Ran 100 / OK**。
  读数取在归档、台账、`MASTER` §3、快照与**全部记录改动之后**（`artifacts/t06-gate-readings.out`）。
- `change.md` §13 DONE Gate 九项逐项签字；AC-01…AC-10 全 **PASS**。

## 6. 判据的自限（不宣称覆盖更多）

- 第一遍只扫**已跟踪**文件；`.gitignore` 覆盖的内容不参与（同 T-05 §5）。
- 第二遍只解析**站内相对** markdown 链接；绝对 URL、`#` 锚点、纯字符串式路径
  （不带 `[]()` 形状的）不在分母内——那些由第一遍的字符串扫描覆盖。
- 「两个文件互为指针」这类**语义**问题不在此判据内。
- 扫描的**时间点会改变读数**（第 3 节）：所有读数都标了取数时刻。

## 7. 本 Task 改动的文件

| 文件 | 改动 |
| --- | --- |
| `delivery/active/CHG-20260925-066/` → `delivery/completed/CHG-20260925-066/` | `git mv`（27 条 rename） |
| `delivery/LEDGER.md` | 表行移除；补本 CHG 关闭段 |
| `delivery/MASTER_IMPLEMENTATION_PLAN.md` | §3 读数列就地刷新（六个量） |
| `.ai/CURRENT_CONTEXT.md` | `--no-active` 重生成 |
| `delivery/completed/CHG-20260925-066/change.md` | §1 状态 → `DONE`；§8／§9／§10（AC-06/08/09）／§13／§14（21–24） |
| `delivery/completed/CHG-20260925-066/checkpoint.md` | 状态 → `DONE`；Completed 补 T-06；Current／Next 改写；Recent verification 补 7 行 |
