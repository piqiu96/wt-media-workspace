# T-00 证据：激活（记录三件、LEDGER 表行、快照、四仓基线、`MASTER` §3 刷新、门禁两臂）

- CHG: `CHG-20260926-068`
- Task: T-00（`change.md` §8）
- 日期: 2026-09-26

## 1. 记录三件

`delivery/active/CHG-20260926-068/` 新建：`change.md`（§5 范围封闭：4 Add／4 Modify／0 Delete／8 Explicitly Not Doing；
§7 字面 `None.`）、`checkpoint.md`、`evidence/`（本文件 ＋ `artifacts/` 三件）。

**LEDGER 表行**：`| CHG-20260926-068 | 四仓 bin/control.sh 入口——修 desktop 执行位、补四动词实跑、加机检 | IMPLEMENTING | wt-media-workspace |`。
约束（CHG-067 §14 第 8 项留下的）：H1 标题取自 `# <id>: <title>`，**标题里不得有 `|`**；表行四格、无反引号、无链接。
本 CHG 的标题含中文破折号与顿号，**不含 `|`**，逐字比对通过。

## 2. 快照

`python3 -B -X pycache_prefix=/tmp/pyc-none scripts/prepare_ai_workspace.py --change CHG-20260926-068` → `exit=0`。
`.ai/CURRENT_CONTEXT.md` 读到 `Active CHG: \`CHG-20260926-068\``／`Status: \`IMPLEMENTING\``。
本 CHG **不锚 Milestone**，故生成物 `active_milestone` 为 `null`。

## 3. 四仓基线与监听面（`artifacts/t00-baseline.out`）

锚（开工前 HEAD）：workspace `5622622`／cloud `e2ba4d8`／agent `aa95332`／desktop `9ba5486`。

| 仓 | `git status --porcelain` | 归属 |
| --- | --- | --- |
| workspace | `?? delivery/active/CHG-20260926-068/` | 本 CHG 自己的新目录 |
| cloud | ` D internal/architecture/boundary_test.go` | **用户操作**（D-03），不追 |
| agent | ` M AGENT-INDEX.md` | 先于 CHG-067 存在，未触碰 |
| desktop | 干净 | — |

**`bin/control.sh` 形态（缺陷读数）**：

| 仓 | index | 磁盘 | 大小 | `./bin/control.sh help` | `./bin/control.sh bogus` |
| --- | --- | --- | --- | --- | --- |
| workspace | `100755` | `-rwxr-xr-x` | 1734 | `exit=0` | `exit=2`，stdout 0 B／stderr 503 B |
| cloud | `100755` | `-rwxr-xr-x` | 3669 | `exit=0` | `exit=2`，stdout 0 B／stderr 354 B |
| agent | `100755` | `-rwxr-xr-x` | 4445 | `exit=0` | `exit=2`，stdout 0 B／stderr 467 B |
| desktop | **`100644`** | **`-rw-r--r--`** | 5233 | **`exit=126`** | **`exit=126`**，stderr 47 B |

desktop 的 `bash bin/control.sh help` → `exit=0`：缺口正是「**直接调用**」这一形态，与 F-01 一致。

监听面：18080＝pid 54420（`server`）、8765＝pid 54456（python）、54345＝pid 13947（`/Applications/比特浏览器.app`，
**第三方，本 CHG 不杀**）。cloud `.cache/wt-media-cloud.pid` 不存在；agent `.cache/wt-media-agent-health.pid` 内是
`75067`（`kill -0` 失败 ⇒ 已死）。

## 4. `MASTER` §3 读数列刷新（仅激活带来的三项）

量法：**直接 import 门禁自己的 `status_word()`**（`scripts/verify_product_master_alignment.py:275`），不另写等价正则。
读数落 `artifacts/t00-status-words.out`（激活前／后各一段）。

| 量 | 激活前 | 激活后 |
| --- | --- | --- |
| `active/` 篇数（分母） | 0 | **1** |
| 活列合计（planned 19 ＋ active） | 19 | **20** |
| 活 `IMPLEMENTING` | 0 | **1** |
| 归档列（`DONE` 32＋`VERIFYING` 1＋`IMPLEMENTING` 1） | 34 | 34（不变） |
| 归档分母 | 42 | 42（不变） |

闭合式复算：归档列 34 ＋ 退役 `CLOSED` 2 ＋ `HANDOFF` 2 ＋ `IN_PROGRESS` 4 ＝ **42** ✓。
`MASTER` 三处文本按上表改写，并把这行读数的刷新来源补上「**CHG-20260926-068 的 T-00**」。

## 5. 门禁（激活后一次）

六个静态门禁 ＋ `sync_skills.py check` ＋ workspace 套件，取在激活写入**之后**：六个 `exit=0`（`verify_delivery_governance.py`
打印 `archive readonly: scanned 12 script(s) … 0 write(s)`）、`sync_skills.py check` `exit=0`、`Ran 101 tests` / `OK`；
分母 951 已跟踪／6 未跟踪。读数落 `artifacts/t00-gate-activation.out`。

**如实记：激活前没有另取一次读数。** 「激活前」的读数**继承** `5622622` 上 CHG-067 收尾的最后一次读数
（`delivery/completed/CHG-20260926-067/evidence/artifacts/t07-gate-final.out`，同为 `exit=0`／`Ran 101 / OK`）——
该 commit 是本 CHG 的开工锚且未被打断，故这份读数成立；但它是**继承**的，不是本 Task 现场量的。
之所以不另取「前臂」：六个门禁读工作树，要复原激活前的工作树得另建同级检出（`verify_m2_acceptance.py` 依赖兄弟仓），
代价高于收益——本 Task 只改记录与 `MASTER` §3 文本，**不碰任何被门禁断言的文件**。

**本 CHG 无红窗**：不改 workflow、不改 `AGENT-INDEX.md` §12 口径、不改端口值。

## 6. 记录体量（本 Task **越界**，如实登记）

`change.md` **14149 B**、`checkpoint.md` 3530 B（artifacts 不参与判据）。**本文件自身的体量自指**——写在文件里的数字会因为
这次写入而变，故按 CHG-066 §14 第 4 项的处置**只报方向、指产物**：读数落 `artifacts/t00-record-size.out`。
`change.md` 与 `checkpoint.md` 均**本 Task 新建**，增量即全量；锚取 `5622622` 下的同名路径（不存在 ⇒ 0 B，
`git cat-file -s` 报 `exists on disk, but not in '5622622'`）。判据沿用 CHG-065/066/067 的 v5：每 Task 增量
`change.md` ≤ 5120 B、`checkpoint.md` ≤ 4096 B、evidence md ≤ 9216 B。

⇒ `change.md` **越界 +176%**、`checkpoint.md` 界内。同类先例实测：CHG-067 的 T-00 是 24095 B（越界 +370%）——
**本 Task 是它的 58.7%，读数小一档，但同属「T-00 一次写完整份记录」的结构性越界**，照报、不强压
（CHG-066 §14 第 4 项、CHG-067 T-00 同一处置）。读数落 `artifacts/t00-record-size.out`。
