# Checkpoint: CHG-20260925-066

- CHG: `CHG-20260925-066`（归档边界冻结与纯过程产物清理）
- Level: S
- Updated: 2026-09-26

## 状态

`DONE`（2026-09-25 激活、2026-09-26 关闭归档；仅 `wt-media-workspace` 一仓，已移入
`delivery/completed/`）

State words come from §3 of `delivery/MASTER_IMPLEMENTATION_PLAN.md`. A record in
`delivery/active/` may only be `IMPLEMENTING` or `VERIFYING`；本记录已不在
`delivery/active/`，故取归档词 `DONE`。

## Completed

- **T-01 激活**：`delivery/active/CHG-20260925-066/` 三件齐备（`change.md`／`checkpoint.md`／`evidence/`）；§5 范围封闭；LEDGER 表行；`MASTER` §3 读数列按 §4 的 F-05 实测刷新（归档记录 39 → **40**、归档 `DONE` 29 → **30**、归档列 31 → **32**、活跃 `IMPLEMENTING` 0 → **1**、`active/` 0 → **1** 篇、活记录 19 → **20**）；快照 `--change`；四仓基线落 `artifacts/t01-repo-baseline.out`。逐词比对 15 项全部相等（`artifacts/t01-status-words.out`，量法调门禁自己的 `status_word()`）。
- **T-01 附带处置两处实测发现**：①**F-07 证毕**——`completed/` 整目录移走后六门禁与套件读数与移走前逐字相同（两臂 `exit=0` / `Ran 94 OK`），故改 `change.md` §4 F-07 的措辞为「没有门禁因它的存在而改变结论」，**不主张**「从不读取」；②**记录成本界第二次越界并如实登记**——T-01 的 `change.md` 增量 **16,605 B** 对界 5,120 B，越界 3.2 倍，成因是激活 Task 一次性写完整份计划（`change.md` 此后只增补），已登记为 §14 第 4 项，**界不改**。

- **T-02 边界成文 ＋ 可删量实测**：`delivery/completed/README.md` 新建（含机读键 `- 归档边界：\`READ-ONLY\``）；`AGENT-INDEX.md` §8／`MASTER:132`／`README.md:51` 三处消歧并各指唯一落点；判据串**先写后实现**（evidence §1）。**可删量实测只有 42 files / 140,556 B ＝ 1.3%**——删除不是本 CHG 的收益，价值全在边界与写入者；用户据此裁定 D-05（删 1.3%、不碰 CHG-052 包）。两处方法学自纠已登记（粗读/细读差 1 文件；F-01 的 74.1% 是拼装的，实测 74.4%）。

- **T-03 修掉唯一的写入者**：`scripts/verify_m3_acceptance.py` 的**读写两侧一并**移出归档（读点逐条核验后全部读的是本轮产物，§5 的条件不成立），产物改落 `.cache/m3-acceptance/`；P10 缺输入即 `BLOCKED` 而不回退读归档。三层判据：字面量 **0/1810**（阳性对照 2/1798）、19 个写点逐个归属**0 处写归档**、运行三读数（699/699、字节全等、`find -newer` **0**）＋ 影子树两臂对照（旧版写进归档 **2** 文件且 `.cache/` 不存在）。附带删掉 `own_artifacts` 里那个**从未存在过**的 `scripts/m3-acceptance.sh`（CHG-055:91 早已登记为未处理）。两处新实测：**归档区 15.6% 的字节不在版本控制内**（F-08）、**P10 从来不是可重跑的阶段**（F-09）。记录成本两处越界（+12%／+9.5%），已照报。

- **T-04 两条 ERROR 门禁**：`verify_delivery_governance.py` 新增 `check_archive_readonly`／`check_completed_has_boundary`，两条分母由 `main()` 无条件打印（`scanned 12 script(s)`／`1 boundary marker(s)`）。判据**锚在字符串字面量**上再从字面量追一跳（不做函数内闭包——那一步会爆炸，§14 第 11 项）。**判据层**阳性对照锚不变的基线 `05c2045`：改前脚本报 **11 处**归档写、现树 **0 处**；这 11 处里有 4 处是函数内局部名，靠那一跳才追得上。**用例层**四条变异（关掉两条判定／改错 `open` 的 mode 位置／摘掉接线）全部红成 `FAIL`，`ImportError` 与 `ERROR` 各 **0**。`write_target` 初版有一处真错（方法形式 `open("rb")` 被读成写，14 处 vs 11 处），由该对照抓出。套件 **94 → 100 OK**，六门禁全 `exit=0`。见 `evidence/task-04-gate-mutation.md`。

- **T-05 删纯过程产物（复检后清单）**：T-02 的「42 files / 140,556 B ＝ 1.3%」是**高估**——它的入站引用仪器只认「精确文件名」一种写法，漏掉同 CHG 记录里的**带星 glob** 与**裸前缀**（`` `t01-` `` 这种一个 `*` 都没有的写法，任何基于 `*` 的扫描都够不着）。三形态复检：**37/42 其实被点名**，可删集 42 → 5。5 个里 3 个是 `probe-*.json`（**测量**，不是任何已跟踪源的确定性函数，且 M3 里程碑有活指针指向那个目录）判不删；**实删 2 个 `__pycache__/*.pyc`／54,810 B（0.51%）**。读数：699→697 文件、10,740,897→10,686,087 B、`.pyc` 分母 2→0；**git 侧零痕迹**（两个 `.pyc` 被 gitignore），唯一记录是 evidence ＋ `artifacts/t05-*`（§4 F-08 首次实际发生）。AC-07 两条读数已完成：净删除 **0**（阳性对照 `63092e8`）。删后六门禁 `exit=0` ＋ `Ran 100 OK`。见 `evidence/task-05-deletion-list.md`。

- **T-06 收尾**：`git mv` 归档（**27 条 rename**）→ `delivery/completed/CHG-20260925-066/`；`LEDGER.md` 表行移除并补关闭段；`.ai/CURRENT_CONTEXT.md` 以 `--no-active` 重生成（`Active CHG: none`／`Status: NONE`）；`MASTER` §3 读数列按 D-04 **刷新一次**并**调门禁自己的 `status_word()`** 逐词复测（活列 20→**19**、归档列 32→**33**、归档 `DONE` 30→**31**、`IMPLEMENTING` 活 1→**0**、活记录 20→**19**、归档记录 40→**41**，闭合式 33＋退役 8＝41）；两遍扫描各带阳性对照与分母（字符串：分母 887 已跟踪文件，活跃面命中 **0**；相对链接 resolve：分母 474 篇 `*.md`／118 条链接，未解析 **6** 条全在 CHG-052 且与 CHG-065 读数逐条相同）；四仓对账（36 条改动路径逐条落在 §5 内、越界 **0**、运行时代码 **0**，三仓 HEAD 与基线逐字相同）。六门禁 `exit=0` ＋ `Ran 100 OK`，取在最后一次改动之后。见 `evidence/task-06-close-out.md`。

## Current

无。T-01…T-06 全部完成，本 CHG 已归档为 `DONE`，`delivery/active/` 与
`delivery/LEDGER.md` 均无本记录。

## Next

1. **本 CHG 无后续 Task**。§13 DONE Gate 九项逐项签字；AC-01…AC-10 全 PASS。
2. **收尾口径（照 §14 第 17／18 项写）**：AC-05 的实删量 **0.51%** 低于 D-05 裁定的
   上限 1.3%——**这不是「放宽了排除换更小删除量」，而是 T-05 复检发现上限那个数本身
   是高估**（T-02 的入站引用仪器只认三种写法里的一种，42 个候选里 37 个其实被点名）。
   下一轮若有人重提「归档区有多少可删」，**先读 `artifacts/t05-reference-forms.out`
   的三形态口径**，不要从 T-02 的 42/140,556 起算。
3. **建议的下一项**（按 `MASTER_IMPLEMENTATION_PLAN.md` §2 完成清单与当前真实代码状态，
   **不自动开工**）：`MASTER` §4 没有为归档区留下未完成的条目，本 CHG 也未打开新的
   范围；`delivery/planned/` 下 3 篇 `PLANNED`（`CHG-20260924-061` 等）与 7 篇
   `DISCUSSION` 是现成的候选，**取哪一篇需用户裁定**。本 CHG 只登记两条供选型参考的
   现存事实：①`MASTER` §3 读数列**每次归档即过期**的机制仍无通用对策（§14 第 2 项，
   下一任 Active CHG 归档时必须再刷一次）；②归档区现有 **6 条**少一级 `..` 的死链
   （§14 第 23 项，可复现，按 `MASTER:132` 只登记不改）。

## Blocked

- None.

## Recent verification

| 判据 | 读数 |
|---|---|
| 六门禁（激活前，无活动 CHG） | 全部 `exit=0`；见 `artifacts/t01-gate-before.out` |
| 六门禁（激活后） | 全部 `exit=0`，`Active CHG: CHG-20260925-066`；见 `artifacts/t01-gate-after.out` |
| `unittest discover -s tests -q`（激活前／后） | 两臂皆 `Ran 94 tests` / `OK` |
| `sync_skills.py check`（激活前／后） | 两臂皆 `exit=0` |
| `MASTER` §3 读数列 vs 实测 | 15 项逐词全等；活列 20＝20、归档列 40＝40（`artifacts/t01-status-words.out`） |
| F-07：`completed/` 移走 vs 在树 | 两臂六门禁与套件读数逐字相同（`artifacts/t01-f07-completed-moved.out`） |
| 四仓工作树（激活前） | workspace／agent／desktop 干净；cloud 只有未跟踪的 `dump.rdb`（他人在途产物，不碰） |
| 归档体量（删除决策的分母） | 698 文件 / `10,736,581 B`；按类分解见 `change.md` §4 F-01 |
| `completed/` 曾被删除的提交数 | `0`（同一命令对 `docs/` 为 `3`，阳性对照） |
| 本 Task 记录体量 | **`change.md` 越界**（界 5,120 B／Task）；三个量的收尾读数见 `artifacts/t01-record-size.out`——**不在此内联**，本表的字节数会随写入而改变 |
| T-02 可删量（分母 698 文件 / 10,736,581 B） | **42 files / 140,556 B ＝ 1.3%**；有引用须保留 158 files / 630,808 B（`artifacts/t02-deletable-measure.out`） |
| T-02 边界落点 | `completed/README.md` 机读键 1 处（阳性对照 0）；`AGENT-INDEX.md`／`MASTER` 各 1 处指针 |
| T-02 六门禁 ＋ 套件 | 全 `exit=0`／`Ran 94 OK`（`artifacts/t02-gate-readings.out`） |
| T-03 归档区写向判据 | 字面量 **0/1810**（阳性对照 2/1798）；19 个写点 **0 处**写归档 |
| T-03 跑前跑后三读数 | 文件数 699→699、字节 10740897→10740897、`find -newer` **0 个**（`artifacts/t03-write-surface.out`） |
| T-03 阳性对照（旧版，基线 `05c2045`） | 影子树归档 0→**2** 文件、`find -newer` **2 个**、`.cache/` 不存在 ⇒ 判据有判别力且**缺陷真实存在过** |
| T-03 归档区跟踪面 | 已跟踪 **687** ＋ 被忽略 **12** ＝ 文件系统 **699**（三个分母闭合，F-08） |
| T-03 记录体量 | `change.md` ＋5,740 B（界 5,120，**越界 +12%**）；本 Task evidence ＋10,095 B（界 9,216，**越界 +9.5%**）；见 `artifacts/t03-record-size.out` |
| T-03 六门禁 ＋ 套件 | 全 `exit=0`／`Ran 94 OK`（`artifacts/t03-gate-readings.out`） |
| T-04 判据层阳性对照（锚 `05c2045`） | 改前脚本 **11 处**归档写、现树 **0 处**（`artifacts/t04-readonly-oracle.out`） |
| T-04 用例层变异对照 | 四条变异全红成 `FAIL`；`ImportError` **0**、`ERROR` **0**（`artifacts/t04-gate-mutation.out`） |
| T-04 两条判据的分母 | `scanned 12 script(s)`／`0 write(s)`；`1 boundary marker(s)`（`artifacts/t04-gate-readings.out`） |
| T-04 六门禁 ＋ 套件 | 全 `exit=0`／`Ran 100 OK`（同上文件；与 T-03 的 94 对照） |
| T-04 修掉第二处 fixture | `test_prepare_ai_workspace.py` 的临时树补合规归档区；不是放宽判据（§14 第 13 项） |
| T-04 记录体量 | 见 `artifacts/t04-record-size.out`——**不在此内联**，本表的字节数会随写入而改变 |
| T-05 入站引用三形态复检 | 形态 1＋2：21/42 被引用；加形态 3（裸前缀）：**37/42**；三形态皆无引用 **5/42**（`artifacts/t05-reference-forms.out`，三条对照全过） |
| T-05 删除读数 | **2 files / 54,810 B**：699→697 文件、10,740,897→10,686,087 B、`.pyc` 2→0；仪器对照含「不存在的路径报不存在」（`artifacts/t05-deletion-list.out`） |
| T-05 git 侧痕迹 | `git status --porcelain` **无删除项**——两个 `.pyc` 本在 `.gitignore` 内 |
| AC-07 归档净删除 | **0**（分母：归档区被删除的已跟踪文件）；阳性对照同命令对 `delivery/active/CHG-20260714-001/change.md` 报出 `63092e8` |
| T-05 六门禁 ＋ 套件 | 全 `exit=0`／`Ran 100 OK`（`artifacts/t05-gate-readings.out`） |
| T-05 归档区新基线 | 697 文件 / 10,686,087 B |
| T-05 记录体量 | 见 `artifacts/t05-record-size.out`——**不在此内联** |
| T-06 `MASTER` §3 读数复测 | 归档后 活列 **19**／归档列 **33**／归档 `DONE` **31**／`IMPLEMENTING` 活 **0**／活记录 **19**／归档记录 **41**；闭合式 33＋退役 8＝41（`artifacts/t06-status-words.out`） |
| T-06 第一遍扫描（字符串） | 分母 **891** 已跟踪／已暂存文件（**须 stage 之后取数**：未跟踪的产物不在分母里，第一版 887 对不上提交后的树）；**活跃面命中 0**；全仓命中数**不在此内联**，它有两个不稳定来源（本节复述的串、产物自指），确切读数与分解见 `artifacts/t06-sweep.out`——自指已实测 **43 → 87**（真实 43／自指 44／活跃面 0）。命中全在本 CHG 自己的已归档记录里，性质是**过去时叙述**＋**原始捕获回读**，按 `MASTER:132` 保留；**归档前**同一命令在本 CHG 目录外为 **3** 处（全在 `.ai/CURRENT_CONTEXT.md`，已由快照重生成归零） |
| T-06 第二遍扫描（链接 resolve） | 分母 **474** 篇 `*.md`／**118** 条站内相对链接；未解析 **6** 条全在 `CHG-20260916-052`（少一级 `..`）；**指向本 CHG 的 0 条**；与 CHG-065 T-09 读数逐条相同 ⇒ 稳定状态（`artifacts/t06-sweep.out`） |
| T-06 扫描的阳性对照 | 三条全过（存在/不存在/另一存在）；「跳过代码块与行内代码」**双向**验证（散文里的报出、围栏与行内代码里的不报） |
| T-06 四仓对账 | workspace 36 条改动路径**越界 0**、运行时代码 **0**；三仓 HEAD ＝ 基线（`0db02ab`／`6d740fc`／`7c1b0ad`）、工作树仅 cloud 的既有 `dump.rdb`（`artifacts/t06-repo-reconcile.out`） |
| T-06 六门禁 ＋ 套件 | 全 `exit=0`／`Ran 100 OK`／`sync_skills exit=0`，取在最后一次改动之后（`artifacts/t06-gate-readings.out`） |
| 归档后本 CHG 体量 | 27 文件（归档前 27，逐条 rename） |

读数取在**最后一次内容改动之后**；原始输出在 `evidence/artifacts/`。
