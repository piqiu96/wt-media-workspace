# T-01 — 激活与基线

- CHG: `CHG-20260925-066`（Level S，仅 `wt-media-workspace`）
- Task: T-01 激活
- 日期: 2026-09-25
- 前置: CHG-20260925-065 已归档（`5c1d98c`），工作树干净

## 1. 激活动作与实测

| 动作 | 落点 | 读数 |
|---|---|---|
| 建 active 目录三件 | `delivery/active/CHG-20260925-066/{change.md,checkpoint.md,evidence/}` | 三件齐备 |
| LEDGER 表行 | `delivery/LEDGER.md:9` | `\| CHG-20260925-066 \| 归档边界冻结与纯过程产物清理 \| IMPLEMENTING \| wt-media-workspace \|` |
| 快照 | `.ai/CURRENT_CONTEXT.md` | `Active CHG: \`CHG-20260925-066\`` / `Status: \`IMPLEMENTING\``；1930 字符（预算 8000） |
| `MASTER` §3 读数列刷新 | `:106`／`:114`／`:116`／`:119` | 见 §3 |

## 2. 门禁读数（前后对照）

原始输出：`artifacts/t01-gate-before.out`（激活前，无活动 CHG）、`artifacts/t01-gate-after.out`（激活后）。

| 判据 | 激活前 | 激活后 |
|---|---|---|
| `verify_delivery_governance.py` | `exit=0`, `Active CHG: none` | `exit=0`, `Active CHG: CHG-20260925-066` |
| `verify_product_master_alignment.py` | `exit=0` | `exit=0` |
| `verify_agent_entry.py` | `exit=0`, 0 warning；快照 1668 字符 | `exit=0`, 0 warning；快照 1930 字符 |
| `verify_m0_config.py` | `exit=0` | `exit=0` |
| `verify_skills.py` | `exit=0`, 10 skill 源 | `exit=0` |
| `verify_m2_acceptance.py` | `exit=0` | `exit=0` |
| `unittest discover -s tests -q` | `Ran 94` / `OK` | `Ran 94` / `OK` |
| `sync_skills.py check` | `exit=0`, up to date | `exit=0`, up to date |

**中间态见红并已定位**（不是缺陷）：`change.md` 已建而 `checkpoint.md`／LEDGER 表行未落时，两处报错——
`verify_delivery_governance.py` 报 `active CHG is missing checkpoint.md: CHG-20260925-066`，
`verify_product_master_alignment.py` 报 `Ledger is not aligned with active CHG … status 'IMPLEMENTING'`，
`unittest` 相应 1 条失败（`test_current_product_master_and_governance_are_aligned`）。
三处同源，落齐后全部归 `exit=0` / `OK`。

## 3. `MASTER` §3 读数列刷新（F-05，AC-06）

实测方式：**调门禁自己的 `verify_product_master_alignment.py::status_word()`**，对两种写入形式
（`- Status:` 与 `> 状态：`）各计后相加——量法不弱于门禁。原始输出 `artifacts/t01-status-words.out`。

| 项 | 改前（= 065 归档后未刷新的值） | 实测/改后 | 触发原因 |
|---|---|---|---|
| 归档记录合计 | 39 | **40** | CHG-065 归档（065 未刷新） |
| 归档 `DONE` | 29 | **30** | 同上 |
| 归档列合计 | 31 | **32** | 同上 |
| 活跃 `IMPLEMENTING` | 0 | **1** | 本 CHG 激活 |
| `delivery/active/*/change.md` | 0 篇 | **1** 篇 | 同上 |
| 活记录合计 | 19 | **20** | 同上 |

逐词比对结果：**15 项全部相等**，活列 20 ＝ 20、归档列 40 ＝ 40（`RESULT: ALL EQUAL`）。
其余各项（`DISCUSSION` 7／`PLANNED` 3／`SUPERSEDED` 9／`CLOSED` 2／`HANDOFF` 2／`IN_PROGRESS` 4／
归档 `IMPLEMENTING` 1／归档 `VERIFYING` 1）改前即已相符。

## 4. F-07 实验：门禁是否因 `completed/` 的存在而改变结论

| 臂 | `completed/` | 六门禁 | `unittest` |
|---|---|---|---|
| 对照 | 在树中（698 文件） | 全 `exit=0` | `Ran 94` / `OK` |
| 实验 | 整目录移到 `/tmp` | 全 `exit=0` | `Ran 94` / `OK` |

两臂读数**逐字相同**。实验后目录已还原（698 文件，`git status` 无异常）。
原始输出：对照臂 `artifacts/t01-gate-after.out`，实验臂 `artifacts/t01-f07-completed-moved.out`。

**该实验的结论边界**：它证明**没有任何门禁因 `completed/` 的存在或缺失而改变结论**；
它**不**主张门禁从不读取该目录（那需要系统调用级观测）。

**首次尝试被污染、已作废**：该实验第一次跑在**半激活**的树上（`change.md` 存在而 `checkpoint.md`
与 LEDGER 表行尚未落），两臂各报 2 条与本实验无关的 ERROR。若照读，会把「激活没做完」误判成
「移走 `completed/` 打红了门禁」。故重跑于激活完成、全绿之后。

## 5. 归档体量基线（T-02／T-05 的分母）

698 文件 / **10,736,581 B**。逐类分解与占比见 `change.md` §4 F-01；
逐篇集中度（CHG-052 ＝ 55.4%）见 F-02。本 Task 只落基线读数，**不做删除决策**——
可删量在 T-02 逐类实测。

## 6. 四仓工作树基线

原始输出 `artifacts/t01-repo-baseline.out`（锚在激活前）。

| 仓 | HEAD | `git status --porcelain` |
|---|---|---|
| `wt-media-workspace` | `5c1d98c` | 干净（除本 CHG 新建的 `delivery/active/CHG-20260925-066/`） |
| `wt-media-cloud` | `0db02ab` | `?? dump.rdb`（他人在途产物，不碰不删不提交） |
| `wt-media-agent` | `6d740fc` | 干净 |
| `wt-media-desktop` | `7c1b0ad` | 干净 |

三仓 HEAD 与 CHG-065 收口时一致（cloud `0db02ab`／agent `6d740fc`／desktop `7c1b0ad`），
即 **065 之后三仓无新提交**，本 CHG 的 AC-09 以本表为锚。

## 7. 本 Task 变更文件

新建：`delivery/active/CHG-20260925-066/` 下 `change.md`、`checkpoint.md`、`evidence/task-01-baseline.md`、
`evidence/artifacts/t01-*.out`（5 个）。
修改：`delivery/LEDGER.md`（表行 1 增）、`delivery/MASTER_IMPLEMENTATION_PLAN.md`（4 处数字）、
`.ai/CURRENT_CONTEXT.md`（生成物）。
**未改任何归档记录正文**，未改三仓任何文件。
