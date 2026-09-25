# T-00 证据：激活

- CHG: `CHG-20260926-067`
- Task: T-00（`change.md` §8）
- 日期: 2026-09-26
- 锚: 开工前 workspace HEAD `71fd32f`（本 Task 尚无提交）

## 1. 激活前的四仓基线

命令与逐仓输出：`artifacts/t00-repo-baseline.out`。

| 仓 | HEAD | 工作树 |
|---|---|---|
| `wt-media-workspace` | `71fd32f` | 仅本 CHG 新建的 `delivery/active/CHG-20260926-067/` |
| `wt-media-cloud` | `0db02ab` | 仅未跟踪的 `dump.rdb` |
| `wt-media-agent` | `6d740fc` | ` M AGENT-INDEX.md` |
| `wt-media-desktop` | `7c1b0ad` | 干净 |

**后两条先于本 CHG 存在**（`change.md` §4 F-06），全程**不触碰**；它们的后果是收尾时 agent 仓的读数**失去归因**，已在 §14 第 1 项登记。

## 2. 脚本层清点与 `bin/` 忽略探针

命令与逐仓输出：`artifacts/t00-script-inventory.out`。

| 仓 | `git ls-files scripts` 分母 | `bin/` 磁盘 | `check-ignore bin/control.sh` |
|---|---|---|---|
| `wt-media-workspace` | 18 | 不存在 | **不被忽略** |
| `wt-media-cloud` | 10 | 不存在 | **被 `.gitignore:3` 忽略** |
| `wt-media-agent` | 10 | 不存在 | 不被忽略 |
| `wt-media-desktop` | 20 | 不存在 | 不被忽略 |

**探针有判别力**：它在 cloud 报出「被忽略」这一相反结论，故另外三仓的三个否定读数不是空转。因四仓 `bin/` 均不存在，放开 cloud 的忽略**不会**让任何既有产物突然变成待跟踪。

## 3. 六门禁与套件

| 臂 | 读数 | 文件 |
|---|---|---|
| 激活前（无活动 CHG） | 六门禁全 `exit=0`；`sync_skills.py check` `exit=0`；`Ran 100 / OK` | `artifacts/t00-gate-before.out` |
| 激活后 | 同上，六门禁全 `exit=0`；`Ran 100 / OK` | `artifacts/t00-gate-after.out` |

`MASTER` §3 状态词读数：`artifacts/t00-status-words.out`（激活前）与 `t00-status-words-after.out`（激活后），量法**直接 import 门禁自己的 `verify_product_master_alignment.status_word()`**，不另写等价正则。

| 量 | 激活前 | 激活后 | `MASTER` §3 现文 |
|---|---|---|---|
| 活列 | 19 | **20** | 20 |
| 活 `IMPLEMENTING` | 0 | **1** | 1 |
| `active/*/change.md` | 0 | **1** | 1 |
| 归档列 | 33 | 33（不变） | 33 |
| 归档记录 | 41 | 41（不变） | 41 |

激活前实测与 §3 现文**逐词相等**（含闭合式 33＋2＋2＋4＝41）⇒ 当前**无漂移**，本次刷新只反映本 CHG 激活带来的三项。

## 4. 里程碑覆盖（`Level` 取 `S` 的判据）

分母 **5** 篇（`delivery/milestones/*.md`，排除 `README.md`）。对
`bin/|control\.sh|scripts/dev|scripts/verify|脚本目录|启停脚本|scripts/README` 实测 **0 命中**。
其中 `M-launch-engineering` 已于 2026-09-25 关闭为 `DONE`，`M2`／`M3` 亦然，`M4`／`M5` 为 `NOT_STARTED`。
`scripts/verify_delivery_governance.py:293` 只对 `Level: M/L` 强制 `- Milestone:` ⇒ 按实测取 `S`
（与 CHG-065 同级同形）。**这一条推翻了本 CHG 计划里的 `Level M`**，登记为 §14 第 2 项。

## 5. 一处自己造成的红：LEDGER 表行的形态有两个硬约束

首轮激活后复跑，`verify_delivery_governance.py`、`verify_agent_entry.py`、
`verify_product_master_alignment.py` **三条红**，套件 **1 failure**。三条红的措辞互相矛盾
（前两条说 `CHG-20260926-067 != none`，即**根本没看见表行**；第三条说 Ledger **未对齐**）。
根因是我把表行写成了 `| [CHG-20260926-067](active/…) | … | \`IMPLEMENTING\` | … |`：

1. `verify_delivery_governance.py:205` 的 `LEDGER_ROW_RE` 是 `^\|\s*(CHG-\d{8}-\d{3})\s*\|`——
   后接 `[` 而不是 `|`，**表行不被识别**，于是「台账里没有活动 CHG」，前两条红由此而来。
2. `verify_product_master_alignment.py:338` 的 `expected_row` 是
   `f"| {active_change} | {title} | {status} | {current_repository} |"`，其中 `title` 取自 H1
   （`^# <CHG-ID>[：:] ?(.+)$`）。我的 H1 里写了 `scripts/dev|verify`——那个 `|` 会让**表行被劈成 5 个单元格**。
   子串比对因此不中，第三条红由此而来。

⇒ **教训（对后续 Task 直接适用）**：`change.md` 的 H1 标题里**不得出现 `|`**；LEDGER 表行必须是
`| CHG-… | 标题 | 状态 | 仓库 |` 四格**无反引号、无链接**的形态（历史形态见 `7e3c8c4` 等提交）。
两条都是**表渲染**与**门禁比对**各自的硬约束，且第一条的报错措辞（"!= none"）指向的是「台账为空」，
与真实成因（表行不被识别）**不是同一个说法**。

改 H1 与表行后重跑：**六门禁全 `exit=0`、`Ran 100 / OK`**（`artifacts/t00-gate-after.out`）。

## 6. 本 Task 的改动文件

| 文件 | 改动 |
|---|---|
| `delivery/active/CHG-20260926-067/change.md` | 新建 |
| `delivery/active/CHG-20260926-067/checkpoint.md` | 新建 |
| `delivery/active/CHG-20260926-067/evidence/task-00-activation.md` | 新建（本文件） |
| `delivery/active/CHG-20260926-067/evidence/artifacts/t00-*.out` | 新建 7 个读数文件 |
| `delivery/LEDGER.md` | 表行 |
| `delivery/MASTER_IMPLEMENTATION_PLAN.md` | §3 读数列：活列 19→**20**、活 `IMPLEMENTING` 0→**1**、分母 `active` 0→**1** 篇 |
| `.ai/CURRENT_CONTEXT.md` | `--change CHG-20260926-067` 重生成 |
