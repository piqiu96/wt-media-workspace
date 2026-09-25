# T-05 evidence — 状态词汇成文（`MASTER` §3 就地覆盖）

日期：2026-09-25
Task：T-05（依赖 T-04）

## 1. 改前：文档定义的两套词汇与实况的关系

`MASTER` §3 改前只定义了两套：

```text
里程碑：NOT_STARTED / IN_PROGRESS / VERIFYING / DONE
CHG   ：TODO → IMPLEMENTED → VERIFIED → CLOSED
```

实测（分母见 §2）：**没有任何记录用过 `TODO`／`IMPLEMENTED`／作为状态值的 `VERIFIED`**，
而记录真正在用的 `DISCUSSION`／`PLANNED`／`SUPERSEDED` 在本节里**一个字都没有**。
另有一套零重叠的词出现在校验脚本里：`verify_product_master_alignment.py:290` 只接受
`{IN_PROGRESS, IMPLEMENTING, VERIFYING, ACTIVE}`——它与本文档的 CHG 四词**交集为零**。
模板则教第三个词：`templates/delivery/change.md:6` 写 `DISCUSSION`、`:130` 写 `IMPLEMENTING`。

## 2. 实测（分母逐一报出）

**CHG 状态值**，分母＝`delivery/planned/*/change.md` 19 篇 ＋ `delivery/active/*/change.md` 1 篇 ＋
`delivery/completed/*/change.md` 38 篇：

| 词 | 活记录 | 归档记录 | 判据 |
|---|---|---|---|
| `DISCUSSION` | 7 | 0 | `^- Status:` 逐文件提取（含 `CHG-20260923-053` 的加粗带注形式） |
| `PLANNED` | 3 | 0 | 2 篇 `- Status:` ＋ `CHG-20260903-034` 的 `> 状态：` 形式 |
| `IMPLEMENTING` | 1 | 1 | |
| `VERIFYING` | 0 | 1 | |
| `DONE` | 0 | 28 | 活记录不得取此词，由 `validate_active_change` 强制；17 篇 `- Status:` ＋ 11 篇 `> 状态：` |
| `SUPERSEDED` | 8 | 0 | |

**已退役词**：`TODO` 0、`IMPLEMENTED` 0、`Status: VERIFIED` 0、`ACTIVE` 0、`CLOSED` 2、`HANDOFF` 2、
`IN_PROGRESS`（作为 CHG 词）活 1 ＋ 归档 4。
阳性对照：同一模式对 `CLOSED` 报 2、对 `HANDOFF` 报 2 ⇒ 扫描确实能咬住状态值，`TODO` 的 0 是真 0。

`VERIFIED` 的措辞必须精确：它**作为状态值**零处使用，但作为**散文**出现过 2 次
（`completed/CHG-20260723-025:144` 的「才能进入 VERIFIED」、`completed/CHG-20260913-035:71` 的「转入 VERIFIED」）。
故 §3 的历史词汇句写的是「与**作为状态值的** `VERIFIED`」，不是「零处使用」。

**写入形式**：12 篇记录（11 篇归档 ＋ `CHG-20260903-034`）用更早的块引用形式 `> 状态：` 代替 `- Status:`，
取值仍是上表中的词（11 篇全 `DONE`、1 篇 `PLANNED`）。
`verify_product_master_alignment.py:283` 两种形式都认，故这不是缺陷、只是形态差异，如实登记在表下。

**一次自捕的计数口径错**：上表初稿的归档列只数了 `- Status:` 形式，于是 `DONE` 写 17，
而分母写的是 38 篇——**17 与分母对不上，因为 11 篇块引用记录没被计入**。
改为两种形式各自计数后相加（`DONE` = 17 ＋ 11 = 28）。写进这里是因为
「同句里的两个数字自相矛盾」正是这类错唯一会自己暴露的地方。

**对账（脚本逐文件提取，可复算）**：`LIVE 20 篇 → {IN_PROGRESS:1, PLANNED:3, SUPERSEDED:8, DISCUSSION:7, IMPLEMENTING:1}`；
`ARCHIVED 38 篇 → {DONE:28, IN_PROGRESS:4, HANDOFF:2, CLOSED:2, VERIFYING:1, IMPLEMENTING:1}`。
两列各自求和等于分母 ⇒ 表列 ＋ 退役词能凑齐，没有未登记的词。

**里程碑状态**，分母＝`delivery/milestones/*.md`（6 篇）＋ `delivery/planned/README.md`：
`NOT_STARTED`（M4、M5）、`DONE`（M2、M3、M-launch-engineering）；`IN_PROGRESS`／`VERIFYING` 当前**无**里程碑处于该态，
但两者保留在表里——它们是有定义的后续状态，不是死词。

## 3. 处置

- `MASTER` §3 由「两套词 + 状态定义表」就地覆盖为 `### 状态词汇`：CHG 表（含变迁箭头与读数列）、
  里程碑表（读数列写成「当前处于该态的里程碑」名）、子项状态说明、一行历史词汇。**不保留旧的两套词表**。
- `MASTER` §6 的 `### CHG 门禁 — CLOSED` 与正文「才能标记为 `CLOSED`」改为 `DONE`（§3 已把
  `CLOSED` 列为退役词，改动前它是该词的**第二个落点**）。
- 另两处 `CLOSED`（`:289` 的 M2 各闭环、`:336` 的历史 C1-C6）同样改为 `DONE`——实测 M2 各闭环的词就是
  `DONE`／`DEFERRED`（见 `M2-account-runtime.md` 最终验收段）。

**为什么选 `IMPLEMENTING` 而不是 `IN_PROGRESS` 作 CHG 的实施中词**（这是一次取舍，记下依据）：
`IN_PROGRESS` 在旧归档里 4 处、在 1 篇 `planned` 记录里 1 处；`IMPLEMENTING` 则是**模板教的词**
（`templates/delivery/change.md:130`）、**测试夹具的默认值**（`tests/test_prepare_ai_workspace.py:64`）、
校验脚本接受集里的正式成员，且 056～064 这一整条最近的 CHG 链都用它。选前者要改模板、夹具、脚本文案
再加本 CHG 自己的记录；选后者只需退役一个旧词。**里程碑层的 `IN_PROGRESS` 不受影响**——两层的词各自
指向不同对象，同名才是问题，不同名不是。

## 4. 判据的边界（本 Task 不覆盖的）

- **脚本接受集与文案尚未与 §3 对齐**：`verify_product_master_alignment.py:290` 仍接受 `ACTIVE`、
  `:292` 的文案仍写「IN_PROGRESS, IMPLEMENTING or VERIFYING」（漏 `ACTIVE`）——**T-06 的落点**。
- `templates/delivery/change.md` 的状态字段与 §12、以及**缺失的 `templates/delivery/checkpoint.md`**——**T-06**。
- `delivery/planned/README.md` 表格里的状态列散文（`HANDOFF（并入 M3 综合变更，已归档）`、
  `已实施，真实证据，由 CHG-052 承载`…）——**T-07**。
- `delivery/milestones/README.md:7` 的 M3 状态叙述——**T-09**。
- `delivery/reports/*` 里的历史状态词（`2026-07-21-current-system-assessment.md` 的 `IN_PROGRESS` 等）
  是**过去时叙述**，按 `AGENT-INDEX.md` §3「历史文档不作新开发依据」保留不改。
- `scripts/verify_m3_acceptance.py:44` 的注释提到 `HANDOFF` 归档——描述已发生的事实，保留。
- **里程碑文件头的状态写法不统一**（M4/M5 用 `- Milestone status:`、M2 用散文、M3 用 `> 实施状态：`、
  M-launch 用 `- 状态：**已完成**`）。本 CHG §5 Explicitly Not Doing 已声明**不为里程碑文件头的状态声明
  新增一致性判据**（会把四种既有格式冻成契约），故只登记不统一 ⇒ §14 第 11 项。

## 5. 未覆盖 / 未决

- `CHG-20260723-023` 是 `planned/` 下唯一带 `IN_PROGRESS` 的活记录（Level M、`Milestone: M2-account-runtime.md#m2-b-…`、
  `planned/CHG-20260723-023/` 下只有 `change.md`、无 `evidence/`）。它的词在 T-07 里要落到上表；
  它究竟该是 `PLANNED` 还是 `DONE`，**是内容判断，不是词汇判断**，留 T-07 逐篇处置并登记（该篇属
  §14 第 8 项登记的「已实施却仍挂 planned」一类）。
- `CHG-044`／`CHG-052` 的 `HANDOFF` 是否改判 `DONE`：`LEDGER.md:31` 早有专段登记此事并写明
  「属治理口径决定，本次不动」。本 Task 只把它们列进历史词汇，**不改写归档记录**，该裁定仍在 `LEDGER` 原地。
