# T-12 收尾：归档、两遍失效指针扫描、三仓对账

本文件只记事实（命令／动作、期望、实际、结论），不重复需求。

## 1. 归档

| 动作 | 期望 | 实际 |
|---|---|---|
| `git mv delivery/active/CHG-20260925-064 delivery/completed/CHG-20260925-064` | 记录整体搬迁，`active/` 只剩 `.gitkeep` | 43 个文件全部 `R`（rename），无内容改动；`ls delivery/active/` 只剩 `.gitkeep` |
| `change.md` §1 `Status: IMPLEMENTING` → `DONE` | 归档记录写 `DONE` | 已改。**顺序有意为之**：先搬目录、后改状态，避免「`Status: DONE` 但记录仍在 `active/`」这一中间态（CHG-063 实测该态会让 `verify_product_master_alignment.py` 多报 1 条 `active CHG status must be …`，CHG-063 归档条目已登记） |
| `delivery/LEDGER.md` 表行 | 移除活动行，改成与先例同形的占位行 | 改为 `\| — \| 当前没有 active CHG（权威冲突与重复落点已按单一落点收口，见下） \| — \| — \|`——与 `0de87e8`（063 归档后）、`eae5cca`（062 归档后）的表行同形；并在表下新增本 CHG 的归档说明段 |
| `python3 scripts/prepare_ai_workspace.py --no-active` | 快照指 `none` | `Active CHG: \`none\``／`Status: \`NONE\``／1668 字符（预算 8000）。分列为 `mode: workspace-governance-active`、`active_change: null` |

**归档使 `MASTER` §3 的读数列立即过期**（这是本 Task 现场量到的机制，不是预想）：词表计数随记录从 `active/` 移入 `completed/` 而移动。按归档后口径重测并就地刷新：

| 读数 | 归档前 | 归档后 |
|---|---:|---:|
| 活列合计 | 20 | **19**（`planned` 19 ＋ `active` 0） |
| 归档列合计 | 30 | **31** |
| ＋ 退役 `CLOSED` 2 ＋ `HANDOFF` 2 ＋ `IN_PROGRESS` 4 | 38 | **39** |
| `IMPLEMENTING` 活 | 1 | **0** |
| `DONE` 归档 | 28 | **29** |
| 归档记录分母行 | 38 篇 | **39 篇** |

复算口径：`git ls-files -z -- delivery/{planned,active,completed}` 取 `*/change.md`，用**门禁自己的** `verify_product_master_alignment.py::status_word()` 逐文件取词（避免自写正则与门禁判据不一致）。归档后：活 19 篇＝`SUPERSEDED` 9 ＋ `DISCUSSION` 7 ＋ `PLANNED` 3（**表外词 0、读不出 0**）；归档 39 篇＝`DONE` 29 ＋ `IN_PROGRESS` 4 ＋ `CLOSED` 2 ＋ `HANDOFF` 2 ＋ `VERIFYING` 1 ＋ `IMPLEMENTING` 1。与 `MASTER` §3 成文表逐词逐格相等。

**一处自写脚本的假读数已排除**：第一版复算用 `re.sub(r"[（(].*?[)）]", "", word)` 剥注，读到 `CHG-20260923-058` 的词是 `DONE（2026-09-24 由 …`——因为**该行的注跨了两行**，闭括号在第 7 行（`- Status: DONE（… 关闭并归档；` ＋ `  关闭时的口径见 §12 与末行的归档说明）`）。门禁的写法是 `re.sub(r"[（(].*$", "", word)`（**从首个开括号删到行尾**），对这种跨行注同样读成 `DONE`。故**是我的量法弱，不是记录坏了**，也不是门禁漏了；换用门禁的函数后 39 篇全部读出词。此事登记在此，因为「量法与门禁不一致会凭空造出一个缺陷」。

## 2. 两遍失效指针扫描（AC-14）

脚本 `artifacts/t12-pointer-sweep.py`；原始输出 `t12-pointer-sweep-pre-archive.out`／`t12-pointer-sweep-post-archive.out`。分母：`git ls-files '*.md'` = **466** 个已跟踪 markdown 文件。

**遍一（字符串）**：查本 CHG 动过的落点——删掉的 `docs/engineering/specs/前端框架视觉规范v2.md`、挪走的 `delivery/active/CHG-20260925-064`（两个位置都查）。

| | 命中 |
|---|---:|
| 归档前 | 13 |
| 归档后 | **10** |
| 阳性对照（各遍各注入 1 条） | 报出 ✓ |

消失的 3 条是 `.ai/CURRENT_CONTEXT.md` 里指向 active 目录的行——随快照以 `--no-active` 重生成而消失。余 10 条的落点**全在本记录自己的 `completed/CHG-20260925-064/` 之内**（8 条 active 路径 ＋ 2 条 v2 文件名）：

| 落点 | 内容性质 | 判定 |
|---|---|---|
| `change.md:85` | §5 Add 的范围声明（`- \`delivery/active/CHG-20260925-064/\`（change.md、checkpoint.md、evidence/）`） | 该记录**撰写当时**的范围，判留 |
| `task-01-activate.md:19`／`:88` | 启动动作与范围表 | 启动命令的过去时记录，判留 |
| `task-03-conventions-slim.md:148` | 范围表 | 同上，判留 |
| `task-06-script-template-checkpoint.md:28` | 阳性对照记录（把 active 下的 `checkpoint.md` 临时改名） | 必须写成当时的路径，否则该对照不可重放，判留 |
| `task-08-ffmpeg-ownership.md:60` | 逐字引用被判定的原句及其出处 | 同上，判留 |
| `task-11-spec-merge.md:124-125`／`:150` | T-11 判定 A 的原始输出与逐节对照表 | 扫描产物**必须**逐字含被查的串，判留 |
| `change.md:108` | §5 Delete 里的被删文件名 | 描述「删了什么」必须写出它，判留 |

**先例**：CHG-062、CHG-063 归档后同样保留其 `delivery/active/…` 自述——`completed/CHG-20260925-062/evidence/artifacts/t05-postarchive-sweep.out` 把这些命中**逐条记录后原样留下**。本 CHG 沿用同一处置（路径判修、叙述判留）。

**遍二（相对链接 resolve）**：站内相对链接 **122** 条，不可达 **10** 条，**归档前后集合逐条相同**。

| 不可达链接 | 落点 | 是否本 CHG 引入 |
|---|---|---|
| `../../../../../wt-media-cloud/internal/modules/contentpool/{repository/discovery_store_mysql.go#L27,#L167,#L278,#L280, service/operations.go#L49}`、`.../web/src/modules/contentpool/pages/ContentPoolPage.vue#L251`（6 条） | `completed/CHG-20260916-052/evidence/m3-e3-acceptance-20260923/12-defects-and-security.md` | 否（既有归档记录） |
| `CHG-20260923-059/change.md` | `completed/CHG-20260923-057/evidence/task-18-writeback-and-archive.md` | 否 |
| `../completed/CHG-20260923-057/change.md` | `completed/CHG-20260923-058/evidence/task-09-writeback-and-archive.md` | 否 |
| `active/…`（带省略号，非真路径） | `completed/CHG-20260923-058/…`、`completed/CHG-20260924-060/…` | 否 |

新增的 1 条链接（121 → 122）是 `LEDGER.md` 里指向本记录的 `[CHG-20260925-064](completed/CHG-20260925-064/change.md)`，**可 resolve**，不在失败列表里。

**两遍的阳性对照都成立**（各注入 1 条必然失效的，均被报出），故那两个 0／10 不是空转。**本 CHG 未新增任何一条不可达链接**——这正是 AC-14 的判据。

## 3. 归档后复测两条早期判据

**判据 A（前端源码根与六个旧名）**——脚本 `artifacts/t12-frontend-path-resweep.py`，输出 `t12-frontend-path-resweep.out`。

归档后工作区全仓 45 行，**`docs/` 下 0**（口径不变）；落点分布：本记录 **44** 行（`task-11-spec-merge.md` 18 ＋ `change.md` 10 ＋ `t11-frontend-path-sweep.out` 8 ＋ `checkpoint.md` 4 ＋ `t11-probe-check.py` 3 ＋ `t11-source-root-check.out` 1）＋ `delivery/LEDGER.md` 1 行（本次归档说明里写了「前端源码根 `wt-media-cloud/frontend` 实测不存在」）。

**阳性对照换了锚，这件事本身要记**：T-11 时对照读 `HEAD`（那时 `HEAD` 还是合并**前**那一版，报全仓 11／`docs/` 8，有效）。T-11 的提交一落，`HEAD` 就变成合并**后**，再读 `HEAD` 得到 `docs/` **0**——那是**结果**，对照失去判别力。故 T-12 把对照锚改成**开工基线 `0148c34~1`**：读它在 `docs/` 下报 **22 行，且全部落在同一个文件** `docs/engineering/specs/web-desktop-visual-system.md` 里。判别力检验：基线 `docs/` 22 > 0 且工作区 `docs/` 0 == 0 → ✓。

**FFmpeg 归属（T-08）**——脚本 `artifacts/t08-ffmpeg-ownership-sweep.py`，输出 `t12-ffmpeg-resweep.out`。归档后候选 **20** 条（9 candidate ＋ 11 negated），与 T-08 收盘的 20 条同量；分母：含 `ffmpeg` 的行 **95 行／22 文件**（T-08 改前 102／26，T-08 后 100／24——本轮再降是因为记录搬进 `completed/` 后被排除）。逐条看：判给 Agent／Desktop 的落点仍是 **0**；新增的 1 条 candidate 是 `LEDGER.md:11` 本次归档说明里的「判给 Agent 的活落点 **4 → 0**」——是叙述，非归属。

## 4. 三仓对账（AC-15）

| 仓库 | 开工基线（T-01） | 收尾实测 | 本 CHG 期间的提交 |
|---|---|---|---|
| `wt-media-cloud` | `?? dump.rdb` | `?? dump.rdb`（已跟踪改动 **0**） | `0346edf` 2 文件各 1 行 |
| `wt-media-agent` | 空 | 空（已跟踪改动 **0**） | `24da21b` 2 文件各 1 行 |
| `wt-media-desktop` | 空 | 空（已跟踪改动 **0**） | `623583d` 4 文件各 1 行 |

三个提交的文件清单**全部落在 `.claude/skills/` 与 `.codex/skills/` 之下**（`common-architecture-review` 三仓各有，`desktop-sidecar-update` 只有 desktop），无一处运行时代码、配置或测试。desktop 那个提交的改动内容逐行看过：就是删掉 `description` 里的 `FFmpeg, `。`sync_skills.py check` → `skill outputs are up to date`。

`dump.rdb` 是**他人的未跟踪产物**：88 字节、mtime `2026-09-24 17:19:16`，早于本 CHG 一天，与本 CHG 无关，不碰不提交不清理（沿用 CHG-063 的处置）。

## 5. 收尾读数

`artifacts/t12-gate-readings.out`（归档之后取）：

```
verify_m0_config: exit=0 | Workspace config verification ok
verify_delivery_governance: exit=0 | Delivery governance verification ok. Active CHG: none
verify_agent_entry: exit=0 | Agent entry verification ok. 0 warning(s) need review.
verify_skills: exit=0 | verified 10 skill source files
verify_product_master_alignment: exit=0 | Product and Master Plan alignment verification ok
verify_m2_acceptance: exit=0 | NOTE: real MySQL and BitBrowser evidence must be recorded separately
unittest: exit=0 | Ran 79 tests in 0.286s OK
sync_skills check: exit=0 | skill outputs are up to date
snapshot: 1668 字符 | Active CHG: `none`
```

时序见 `change.md` §12：该段读数取自记录正文定稿之后；此后只写入了本记录自身的措辞（门禁不读 `delivery/completed/` 与 `evidence/`），收尾复跑一次，两次逐行相同。

## 6. 未覆盖与明确不改

- **不为归档记录回改历史路径叙述**：见 §2；先例 CHG-062／CHG-063。
- **不修那 10 条既有的不可达链接**：全部落在 CHG-052／057／058／060 的归档记录里（跨仓源码指针与相对路径写法），属他人归档记录的既有内容，不在本 CHG 范围；在此登记。
- **不改三个运行仓**：见 §4。
- **`MASTER` §3 的读数列仍会随每次归档漂移**：本 Task 只把它刷新到当下，并把分母行写成可复算的形式。机制无对策，登记 `change.md` §14 第 7 项。
