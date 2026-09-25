# CHG-20260925-066: 归档边界冻结与纯过程产物清理

## 1. Basic Information

- Level: S
- Status: IMPLEMENTING
- Created: 2026-09-25
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`

**锚点（Level S，按 CHG-060 §3、CHG-062 §3、CHG-063 §1、CHG-064 §1、CHG-065 §1 先例写散文，不引 Milestone）**：`delivery/milestones/` 下 6 篇无一篇覆盖归档卫生或治理边界（与 CHG-063／064／065 同一读数）；`scripts/verify_delivery_governance.py:125` 只对 `Level: M/L` 强制 `- Milestone:`。

**本 CHG 只写 `wt-media-workspace` 一仓**，且**不写任何已归档记录的正文**——它给归档区**加边界**、给唯一的写入者**改写入目标**、删**可再生**的过程产物。与 CHG-065 的差别在于：065 会写三个运行仓的入口文件，本 CHG 对三仓**零读写**。

## 2. Change Goal

把 `delivery/completed/` 从「一份事实上的活目录」变成**被声明、被强制、被证明的只读归档**，并把其中**可再生的过程产物**按实测清单清掉。

单一可验收结果：`scripts/verify_delivery_governance.py` 新增的两条 ERROR 各**被证明能失败**；重跑 `scripts/verify_m3_acceptance.py` 的读写路径**不再写 `completed/` 下任何文件**；归档区**无一份手写记录、无一张截图被删**，而原始捕获类产物按逐条留痕的清单减少。

## 3. Baseline References

- 治理规范正文：`AGENT-INDEX.md`（§2 红线、§3 知识地图与默认不加载、§8 交付治理、§12 校验）
- 交付与归档规则：`delivery/MASTER_IMPLEMENTATION_PLAN.md` §2（完成 CHG 后第 7／8 项）、§3（状态词汇与读数列）、§4、§6
- 台账与归档现状：`delivery/LEDGER.md`（首段「removed after …」的定义）、`delivery/completed/CHG-20260916-052/`、`.../CHG-20260923-055/`
- 上一轮同类处置（先例与边界）：`delivery/completed/CHG-20260925-065/change.md`（§14 第 20 项、第 14 项）、`.../CHG-20260925-064/change.md`（§14 第 7 项）
- 用户裁定：2026-09-25 `/doctor` 追加指令 ① 的裁定「**边界 + 删纯过程产物**」（见 §6 D-01）

## 4. Current Facts

以下全部为本 CHG 开工前实测读数，命令与分母见 `evidence/task-01-baseline.md` 与 `evidence/task-02-*.md`。

**F-01 归档体量（T-01 实测，作为一切删除决策的分母）。** 698 文件 / **10,736,581 B**。按扩展类：`.png` 24 篇 **4,566,847 B（42.5%）**、`.md` 341 篇 2,496,962（23.3%）、`.log` 11 篇 1,630,884（15.2%）、`.json` 79 篇 1,064,738（9.9%）、`.out` 188 篇 633,413（5.9%）、`.py` 24 篇 199,170（1.9%）、`.pyc` 2 篇 54,810（0.5%）、`.txt` 7 篇 38,862（0.4%）、`.sh` 11 篇 27,708（0.3%）、`.patch` 3 篇 16,216（0.2%）、其余 <7 KB。**原始机器捕获（`.png`＋`.json`＋`.out`＋`.txt`＋`.log`＋`.pyc`）合计 7,989,554 B ＝ 74.4%**；手写的 `change.md` ＋ `checkpoint.md` 合计 **981,058 B ＝ 9.1%**。

**F-01b 删除这一步的结构性上限只有 1.3%——本条推翻了本 CHG 的初始前提。** 逐文件按「是否被归档 `.md` 以同 CHG 路径或文件名引用」判定后（扫 341 篇 `.md`，分母 ＝ F-01 的 698 文件）：

| 分类 | 体量 | 占归档 |
|---|---|---|
| **可删**（无任何入站引用） | **42 files / 140,556 B** | **1.3%** |
| 有真引用（同 CHG 内命中）→ 必须保留 | 158 files / 630,808 B | 5.9% |
| 硬排除：CHG-052 的 `m3-e3` 包 | 127 files / 5,922,113 B | 55.2% |
| 硬排除：`.png` 截图 | 24 files / 4,566,847 B | 42.5% |

⇒ 归档的体量**几乎全部落在三类政策明确保护的地方**：截图（视觉缺陷的唯一判据）、CHG-052 的包（M3 已签收验收的唯一证据）、手写记录。**清理不是本 CHG 能带来的收益**；真正值钱的是边界与写入者。用户 2026-09-25 就此裁定：**删 1.3%，不碰 CHG-052 包**（D-05）。

**T-03 后的更正**：上表把 CHG-052 的包硬排除，当时的理由里含「脚本读取面仍是活依赖」。T-03 把读写两侧一并移出归档后，**该理由已不成立**——保留理由**只剩证据性**（M3 签收的唯一证据）。⇒ 该包从此是「政策上不删」，不是「机制上删不动」；`completed/README.md` 已同步改写，**别把活依赖那条理由写回去**（§14 第 10 项）。

**F-02 体量高度集中在单篇。** `CHG-20260916-052` 一篇 **5,945,638 B ＝ 55.4%**，其中 `evidence/m3-e3-acceptance-20260923/` 一个包 **5,922,113 B / 127 文件 ＝ 55.2%**。次高 `CHG-20260923-055` 1,599,776（14.9%），其余各篇 <7%。

**F-03 唯一活着的写入者，而且写入面比预想宽。** `scripts/verify_m3_acceptance.py:47` 把 `EVIDENCE` 常量钉在归档包内，**既读又写**：

| 面 | 位置 | 动作 |
|---|---|---|
| `EVIDENCE.mkdir` | `:304`／`:310`／`:1739` | 写 |
| `state.json`／`run-manifest.json` | `:306`／`:311`／`:1742-1745` | 读写 |
| `proc-<component>.log` | `:376` | **写**——归档区最大文件 `proc-discovery-worker.log`（1,587,838 B）即此路径产出 |
| 基线快照 `02-baseline-snapshot*.md` | `:522-523` | 写 |
| `proc-discovery-scheduler.log` | `:1059` | 写 |
| `raw/p10-*.log`、`raw/p10-flowview-grep.txt`、`screenshots/*.png` | `:1596`／`:1615`／`:1624`／`:1656`／`:1645` | 只读 |
| `EVIDENCE` 传给 `own_artifacts`（G0 过滤用） | `:406-407` | 字符串常量 |

⇒ 「已归档」在事实层面**并非只读**：重跑该脚本会往归档包里重新生成日志与快照。该脚本不属门禁表（`AGENT-INDEX.md:206`），但它是活的。

**T-03 后的实况**：读写两侧已一并移出（读点逐条核验**全部读的是本轮产物**，没有一处需要归档里的东西——见 `evidence/task-03-writer-moved.md` §1）。该脚本现在**既不读也不写** `delivery/completed/`，产物改落 `.cache/m3-acceptance/`。上表的行号是 T-03 改动**前**的编号。

**F-04 归档区从未被删除过——这一条有判别力。** `git log --diff-filter=D -- delivery/completed` 返回 **0** 个提交；同一命令对 `docs/` 返回 **3** 个（阳性对照）。⇒ 「不回改」不只是文案，是既成事实。

**F-05 `MASTER` §3 的读数列与实测差 1，成因是 CHG-065 归档时未刷新。** 实测（两种写入形式 `- Status:` 与 `> 状态：` 各计后相加）：

| | `MASTER` §3 现文 | 实测 | 差 |
|---|---|---|---|
| 活记录合计 | 19 | 19（`planned` 19 ＋ `active` 0） | 0 |
| 归档记录合计 | 39 | **40** | **-1** |
| 其中归档 `DONE` | 29 | **30** | **-1** |
| 归档列合计 | 31 | **32** | **-1** |

逐词其余各项（`DISCUSSION` 7／`PLANNED` 3／`SUPERSEDED` 9／`CLOSED` 2／`HANDOFF` 2／`IN_PROGRESS` 4／活 `IMPLEMENTING` 0／归档 `IMPLEMENTING` 1／归档 `VERIFYING` 1）**全部相等**。激活本 CHG 还会另改三项（活跃 `IMPLEMENTING` 0→1、`active/` 0→1 篇、活记录 19→20）。该节自述「对不上就说明有词没被登记」，故这是**活的**不一致，不是文风问题。

**F-06 `README.md:51` 的措辞有两种读法，而只有一种是对的。** `README.md:51` 在 `## Rules` 下写 `Remove completed delivery records after final outcomes are reflected in stable baselines and Git.`——可读作「把记录**移出** `active/` 与 `LEDGER`」（= `MASTER:97`）或「把记录**文件删掉**」（= 被 `MASTER:132`「归档记录保持原样、不回改」禁止）。两者语义相反、**都无门禁**。`LEDGER.md:5` 与 `MASTER:97-98` 支持前者。

**F-07 「干扰」的范围已被三个既有结论界定，本 CHG 不重开。** `AGENT-INDEX.md:83` 已写 `delivery/completed` **默认不加载**；**没有任何门禁因它的存在与否而改变结论**——把 `completed/` 整目录临时移走后重跑六门禁与套件，读数与移走前**逐字相同**（两臂皆 `exit=0` / `Ran 94 OK`；对照臂 `artifacts/t01-gate-after.out`，实验臂 `artifacts/t01-f07-completed-moved.out`）。该实验证的是「门禁不因它的存在而失败」，**不主张**它们从不读取该目录。CHG-059 Q-08 已判此类历史叙述「登记不改」，CHG-065 已把「路径判修、叙述判留」成文。⇒ 它干扰的是 **grep 噪声与字节数**，不是上下文或门禁。

**F-08 归档区 15.6% 的字节不在版本控制内（T-03 实测）。** 699 文件 / 10,739,451 B 中，**687 文件 / 9,062,732 B** 已跟踪，**12 文件 / 1,676,719 B（15.6%）** 被 `.gitignore` 的 `*.log` 与 `__pycache__/` 排除——含归档区**最大的单个文件** `proc-discovery-worker.log`（1,587,838 B，正是 F-03 里 `:376` 的产出）。⇒ 对这 12 个文件「不回改」**不由 git 保证**：改写它们时 `git status` 与 `git diff` 都是空的（CHG-055 曾登记过同一现象的两个 `.log`，此处量出了全量）。三个分母互相闭合：687 ＋ 12 ＝ 文件系统实测的 699。

**F-09 P10 从来不是可重跑的阶段，它只是**转录**。** 它自己不跑任何测试，只把 `raw/*.log` 与截图转成清单行；而那些日志由**逐条手敲的 shell 命令**（`scripts/test.sh`、`npm test --prefix web`、`scripts/m2b-local-acceptance.sh`、一个无头 Chrome 截图代理）产生，无驱动脚本。旧版把产物目录钉在归档包内，故「重跑 P10」既不重跑也不报错，只是把上次的结论重新盖一个**今天的日期**。⇒ T-03 给 P10 加了输入前置行：缺任一输入即整段 `BLOCKED`，**不**回退读归档顶替。

## 5. Scope

范围在 T-01 **封闭**；后续新发现只登记 §14，除非落在已列举项内。

### Add

- `delivery/completed/README.md`：归档区**只读边界**的唯一落点（不默认加载、不回改、不作为当前状态依据、扫描可整目录排除、新增原始捕获超阈值不入库）。
- `scripts/verify_delivery_governance.py` 两条新判据：`check_archive_readonly`（**ERROR**，AST 扫描已跟踪脚本对 `completed/` 前缀的**写**操作，白名单外即报）、`check_completed_has_boundary`（**ERROR**，`completed/README.md` 存在且含边界标记串）。

### Modify

- `AGENT-INDEX.md` §8：补归档只读边界一句，并把 `completed/README.md` 指为唯一落点。
- `delivery/MASTER_IMPLEMENTATION_PLAN.md`：`:132` 就地补边界语句使其与 `README.md:51` 的**正确读法**自洽；§3 状态词读数列按 F-05 的实测**逐词刷新**（含本 CHG 激活带来的三项变化）。
- `README.md:51`：措辞消歧——写成「移出 `active/` 与 `LEDGER.md`；记录本身归档于 `delivery/completed/`，不删除、不回改」。
- `scripts/verify_m3_acceptance.py`：`EVIDENCE` 的**写入面**移出归档（写入目标改指该脚本自己的工作目录）；若读取面必须继续读归档，则**只读**并以常量声明路径与「只读」字样。**T-03 判定该条件不成立**——六处读点逐条核验后全部读的是本轮产物，故**读写两侧一并移出**（产物落 `WS_ROOT/.cache/m3-acceptance/`），该脚本不再含归档路径常量；P10 缺输入时记 `BLOCKED` 而不回退读归档（见 §4 F-09）。
- `delivery/completed/README.md`：T-03 增补「已知例外」——①15.6% 的字节不在版本控制内（§4 F-08）；②CHG-052 包的保留理由由「活依赖」改为「证据性」；③本文件是**边界落点**而非归档记录，随边界演进就地更新（否则 T-02 定的「不回改」会与 T-03 改它自相矛盾）。

### Delete

- **只删可再生过程产物**，且**只删无任何入站引用的**。清单已由 T-02 逐类实测（见 §4 F-01b 与 `evidence/artifacts/t02-deletable-measure.out`）：**42 files / 140,556 B**，主要是 `__pycache__`／`.pyc` 与未被本 CHG 记录引用的 `.out`／`.log`／中间 `.json`。T-05 按该清单逐条执行并留痕（先例 `CHG-20260923-063:140`：即使 S 级也要逐条删除清单）。
- **明确排除**（用户裁定 D-05）：全部 `.png` 截图（视觉缺陷的唯一判据——删了 `CHG-20260923-055` 的 CSP 布局结论无法复验）、CHG-052 的 `m3-e3-acceptance-20260923/` 证据包（占归档 55.2%，且 T-03 之后读取面仍是活依赖）、全部 `change.md`／`checkpoint.md`／手写证据、以及**任何被归档 `.md` 引用的产物**。
- **删除规模的上限是 1.3%**（F-01b）。本 CHG **不**通过放宽上述排除来换取更大的删除量——用户在知悉该读数后明确选择不动 CHG-052 的包。

### Explicitly Not Doing

- **不做「内容整合清除」**——不合并、不改写、不重排任何归档记录的正文。用户裁定 D-01。
- 不把归档记录移出仓库、不新建第二处归档。
- 不动 `arch:478`／`arch:1801`／`build-desktop.sh` 的归属（CHG-065 已裁定另立 CHG）。
- 不并进「三仓 skill 分发」（独立 closure，CHG-065 §14 已登记）。
- 不给「里程碑文件头的状态声明」新增一致性判据（与 CHG-063 的判据分层结论相悖）。
- 不修已归档记录的正文，**包括** CHG-065 §14 第 20 项登记的 6 条 off-by-one 死链——那条登记本身就裁定「只登记不改」。

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | `delivery/completed/` 的处置层次＝**声明只读边界 ＋ 冻结 ＋ 修掉唯一的写入者 ＋ 只删可再生的纯过程产物**；不做内容整合清除。 | CONFIRMED（用户 2026-09-25 裁定） |
| D-02 | 顺序：**先入口文件（CHG-065）、后归档边界（本 CHG）**。 | CONFIRMED（用户 2026-09-25 裁定） |
| D-03 | 门禁新增判据一律 **ERROR 只判存在／声明／计数／相等**；判文字的只到 WARN。 | CONFIRMED（沿用 CHG-063 D-01） |
| D-04 | `MASTER` §3 的读数列是**易失读数**，其漂移机制（每次归档即过期）在本 CHG **只登记、不设通用对策**（CHG-064 §14 第 7 项同结论）；本 CHG 只做**一次**按实测的刷新。 | CONFIRMED（本 CHG） |
| D-05 | 在知悉「可删量上限仅 1.3%（F-01b）」后：**按实测清单删这 1.3%，不碰 CHG-052 的 `m3-e3` 包**，也不通过放宽排除来换取更大删除量。 | CONFIRMED（用户 2026-09-25 裁定） |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | 激活：`change.md`／`checkpoint.md`／`evidence/`；§5 封闭；LEDGER 表行；快照 `--change`；四仓 `git status` 基线；`MASTER` §3 读数列按 F-05 刷新 | DONE | 六门禁 `exit=0`；LEDGER 表行逐字合 `validate_active_change`；§7 为 `None.` |
| T-02 | 边界成文 ＋ 实测可删量：`completed/README.md`；`AGENT-INDEX.md` §8；`MASTER:132`；`README.md:51` 消歧；逐类实测可删量并落痕 | DONE | 判据串**先写后实现**（已写定，见 evidence §1）；可删量**42 files / 140,556 B ＝ 1.3%**，分母 ＝ F-01 的 698 文件 |
| T-03 | 修掉唯一的写入者：`verify_m3_acceptance.py` 写入面移出归档；读取面只读且常量声明 | DONE | 判读为**读写两侧一并移出**（读点全是本轮产物）。三层判据：字面量 **0/1810**（阳性对照 2/1798）、19 个写点逐个归属 0 处写归档、运行三读数 ＋ 影子树两臂对照（臂 B 旧版写进归档 2 文件）。见 `evidence/task-03-writer-moved.md` |
| T-04 | 门禁：`check_archive_readonly` ＋ `check_completed_has_boundary` | TODO | 两条各做**变异对照**（关掉判定则用例失败，`ImportError` 计数须为 0）；六门禁 ＋ unittest |
| T-05 | 删纯过程产物：按 T-02 清单执行；排除 PNG 与 CHG-052 的 m3-e3 包 | TODO | 逐条删除清单 ＋ 删前删后总字节读数；删后六门禁 ＋ unittest 全绿 |
| T-06 | 收尾：归档 → `completed/`；LEDGER 同步；快照 `--no-active`；两遍失效指针扫描 | TODO | 六门禁 `exit=0` ＋ unittest，**在最后一次改动之后**重测；四仓 `git status --porcelain` 对账 |

## 9. Repository Checklist

### wt-media-workspace

- [ ] `delivery/active/CHG-20260925-066/` 三件齐备；LEDGER 表行；快照 `--change`（T-01）
- [ ] `completed/README.md` ＋ `AGENT-INDEX.md` §8 ＋ `MASTER:132` ＋ `README.md:51`（T-02）
- [ ] `verify_m3_acceptance.py` 写入面移出归档（T-03）
- [ ] `verify_delivery_governance.py` 两条新判据 ＋ 用例（T-04）
- [ ] 删除清单执行并留痕（T-05）
- [ ] 归档、LEDGER 同步、快照 `--no-active`、指针扫描（T-06）

### wt-media-cloud

- [ ] Not affected（本 CHG 对三仓零读写，收尾时逐仓对账）

### wt-media-agent

- [ ] Not affected

### wt-media-desktop

- [ ] Not affected

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | 归档只读边界**落在唯一落点**且三处措辞不互相矛盾 | `completed/README.md` 存在且含标记串；`AGENT-INDEX.md` §8 与 `MASTER:132` 各指它；`README.md:51` 只剩一种读法 | **PASS**（T-02：标记串 1 处、阳性对照 0；两处指针各 1；`README.md:51` 已改写） |
| AC-02 | `check_archive_readonly` **能失败** | 变异对照：把 T-03 的写入目标指回归档 → 报出；关掉判定 → 用例失败且非 `ImportError` | TODO |
| AC-03 | `check_completed_has_boundary` **能失败** | 变异对照：删 `README.md` → 报出；去掉标记串 → 报出 | TODO |
| AC-04 | 重跑 `verify_m3_acceptance.py` 的读写路径**不再写 `completed/`** | 跑前跑后对 `completed/` 做文件数 ＋ 字节数 ＋ `find -newer` 三读数；**阳性对照**：修改前的版本必须报出写入 | **PASS**（T-03：699/699、字节全等、`find -newer` **0** 个；对照臂旧版 `find -newer` **2** 个且 `.cache/` 不存在——全部写进归档；`artifacts/t03-write-surface.out`） |
| AC-05 | 删除**只**落在可再生过程产物上，且逐条留痕 | 逐条删除清单（路径 ＋ 字节）；删前删后总字节读数；**PNG 与 CHG-052 m3-e3 包零删除**逐类枚举确认 | TODO |
| AC-06 | `MASTER` §3 读数列与实测**逐词相等**（含本 CHG 激活后的分母） | 用与 `verify_product_master_alignment.py::status_word()` 同源的量法重测（先例：`re-measure-with-the-gates-own-function`） | TODO |
| AC-07 | 归档区**从未被删过**这一事实在本 CHG 之后仍成立 | `git log --diff-filter=D -- delivery/completed` 的**净删除文件数**为 0（T-05 的删除须落在可再生的过程产物上，故本条按「记录文件」为分母重述） | TODO |
| AC-08 | 六个静态门禁 `exit=0` ＋ `unittest` OK | 在**最后一次改动之后**重测，读数落 `evidence/artifacts/` | TODO |
| AC-09 | 四仓零越界：workspace 只得治理文件改动，三仓零改动 | 逐仓 `git status --porcelain` ＋ `git diff --stat` 对账，锚 T-01 基线提交 | TODO |
| AC-10 | 门禁**报出分母**，且读数不是空转 | `check_archive_readonly` 打印被扫描脚本数与前缀匹配数；`check_completed_has_boundary` 打印被检查的标记串数 | TODO |

## 11. Evidence

证据在 `evidence/`，只记事实、不复述需求。原始输出进 `evidence/artifacts/`。

- `evidence/task-01-baseline.md` ＋ `artifacts/t01-repo-baseline.out`／`t01-gate-before.out`／`t01-status-words.out`
- `evidence/task-02-archive-inventory.md` ＋ `artifacts/t02-deletable-measure.out`
- `evidence/task-03-writer-moved.md` ＋ `artifacts/t03-*.out`
- `evidence/task-04-gate-mutation.md` ＋ `artifacts/t04-*.out`
- `evidence/task-05-deletion-list.md` ＋ `artifacts/t05-*.out`
- `evidence/task-06-close-out.md` ＋ `artifacts/t06-*.out`

每条记录含：命令或手工动作、期望、实测、通过与否、相关 commit。

## 12. Current Checkpoint

进度写在同目录的 `checkpoint.md`，**不在本文件内联**。`scripts/verify_delivery_governance.py` 强制这一对：有 `change.md` 而无 `checkpoint.md` 的 active CHG 是一个无人能恢复的变更。

## 13. DONE Gate

- [ ] Scope completed.
- [ ] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Manual verification evidence recorded where required.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories touched only if listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.

## 14. 实测推翻或补齐预想（本 CHG 登记，逐项在对应 Task 落地）

1. **F-03 的写入面比计划宽。** 计划只记「`:47` 既读又写（`:304`／`:310`／`:1739` 及 `STATE_FILE`／`MANIFEST_FILE`）」；T-01 逐行实测发现还有 `:376` 的 `proc-<component>.log`、`:522-523` 的基线快照、`:1059` 的 scheduler 日志——**归档区最大的那个 1,587,838 B 文件正是 `:376` 的产出路径**。⇒ T-03 的移出范围以本表为准，不只移 `state.json`。
2. **`MASTER` §3 的漂移是第二次**（CHG-064 §14 第 7 项登记的机制）。064 归档时刷新过，065 归档时没刷，于是归档 `DONE` 少 1、分母少 1。本 CHG 按 D-04 只刷新一次并再登记该机制。
3. **`README.md:51` 与 `MASTER:132` 并非「相反行为」，而是同一句可作两种读法**——正确的读法与 `MASTER:97-98`／`LEDGER.md:5` 一致（移出 `active/` 与 `LEDGER`）。故 T-02 做的是**消歧**，不是二选一，也不改归档政策本身。
4. **记录成本界的第二个盲区：激活 Task 一次性付掉整份计划的钱。** 写本节**之前**量得 T-01 的 `change.md` 增量 ＝ **16,605 B**，而同一条 v5 判据的界是 **5,120 B／Task**——**越界约 3.2 倍**（三个量的收尾读数见 `evidence/artifacts/t01-record-size.out`，**不在此内联**：本节自身一写，它引用的数就变了，同 CHG-065 §14 第 14 项与第 20 项）。成因不是写作啰嗦，是判据的假设不成立：`change.md` **只在 T-01 被完整写一次**，其后只有任务表状态、AC 状态与 §14 逐条增补，所以「每 Task 增量」这个量在 T-01 上等于「整份计划的体量」。**界不改、越界就报越界**（同 CHG-065 §14 第 19 项对补写型 Task 的处置）：真正的判别量应是**每 Task 对既有文本的增补量**（本 CHG 其余 5 个 Task 适用），而「计划总长」是另一个量——16,605 B 相对 CHG-065 收尾时的 47,422 B 为 35%。参考基线照报，**不当作上限**。
5. **实验跑在「半完成」的树上，会把过渡态的错误归因给被实验的变量。** F-07 首次执行时 `change.md` 已建而 `checkpoint.md` 与 LEDGER 表行未落，两臂各报 2 条与本实验无关的 ERROR；照读就会得出「移走 `completed/` 打红了门禁」这一**错误结论**。重跑于激活完成、全绿之后方得到两臂逐字相同的干净读数。⇒ **实验的前置状态与被实验变量无关**这一条必须显式核验，不能假定「先跑一跑再说」。
6. **删除这一步的上限只有 1.3%，推翻了本 CHG 的初始前提。** T-02 逐文件判定（分母 ＝ 698 文件 / 10,736,581 B）后，无任何入站引用的只有 **42 files / 140,556 B**。本 CHG 立项时与计划中都假定「历史调试内容」有可观体量可清，**实测没有**：归档的体量全在 `.png`（42.5%）、CHG-052 的包（55.2%）与手写记录（9.1%）里，而这三类政策各自明确保护。⇒ 本 CHG 的价值因此**全部落在边界与写入者上**，删除只是顺带的卫生动作；已按 D-05 定案（删 1.3%、不碰 CHG-052 包），并在 §5 写明**不**通过放宽排除换取更大删除量。
7. **两处方法学自纠**（详见 `evidence/task-02-archive-inventory.md` §3.1 与 §4）：①入站引用检查的**粗读（全局 basename）与细读（同 CHG 限定）只差 1 个文件**——我一度据粗读推断「同名碰撞普遍」，实测碰撞仅 1 例，量级被我高估，如实记下；②F-01 初稿的「原始机器捕获合计 7,958,694 B ＝ 74.1%」是**拼装的不是量的**，实测 7,989,554 B ＝ 74.4%，已就地更正——与 CHG-065 §14 第 14 项同源（凭印象写数）。

8. **边界是承诺，但归档区有 15.6% 的字节从来不归 git 管**（§4 F-08，T-03 实测）。12 文件 / 1,676,719 B 被 `.gitignore` 的 `*.log` 与 `__pycache__/` 吃掉，含归档区最大的单个文件。⇒ 「不回改」对它们**没有强制手段**：改写时 `git status`／`git diff` 全空。**不**把它们纳入仓库（1.6 MB 原始日志正落在新增捕获的入库阈值反面），改为在 `completed/README.md` 里**明写这一条边界对谁不成立**——边界写清楚自己在哪里失效，比写成一个绝对承诺更有用。

9. **P10 不是可重跑的阶段**（§4 F-09）。它只转录，输入靠手敲的 shell 命令；旧版把产物目录钉在归档里，于是「重跑 P10」既不重跑也不报错，只把上次结论盖上新日期——这正是「归档被当作当前状态依据」的活样本。⇒ 已改为输入缺失即整段 `BLOCKED`。**登记遗留**：本轮**没有**为 P10 补一个驱动脚本（那会把本 CHG 扩成「重写 M3 验收执行链」），故 P10 此后在缺输入时**如实报 BLOCKED**，而不是假装通过。

10. **CHG-052 证据包的保留理由变了**（§4 F-01b 的 T-03 更正）。T-01/T-02 时它被硬排除，理由是「有活脚本依赖」；T-03 把读写两侧移出后该理由消失，只剩证据性（M3 签收的唯一证据）。⇒ 处置结论不变（不删），但**理由必须跟着改**：两处旧文本（§4 F-01b 与 `completed/README.md`）已改写，并留了一句「别把活依赖那条理由写回去」——理由不清的记录会让人在下次评估时按一个不成立的机制做决定。

11. **AST 判据要锚在字符串字面量上，不能锚在接收者变量名上**（T-03 实测，供 T-04 用）。名字式判据对修改前的版本只报 **3/6** 处归档写（漏掉经 `EVIDENCE / "state.json"` 一跳间接的 `STATE_FILE`／`MANIFEST_FILE`／基线快照）；改成定点传播后又因名字空间跨函数共用而把污染集爆到约 180 个名字、命中数**高于**真值。⇒ 两头都不准，且**看不出来**。同时 T-04 须处理的负例：旧版 `own_artifacts` 里那个归档串是**过滤器**不是写目标，只判「字面量出现」会误报，故判据必须真的做「流向写操作」这一步。

12. **T-03 的记录成本两处越界，照报不改界**：`change.md` ＋5,740 B（界 5,120，＋12%）、本 Task 的 evidence ＋10,095 B（界 9,216，＋9.5%）；`checkpoint.md` 0 B 增（本 Task 尚未更新）。读数见 `evidence/artifacts/t03-record-size.out`（**不内联**——本条自身的增补就会改变该读数，同第 4 项）。与第 4 项的区别：T-01 的越界 3.2 倍且**起因为结构性**（激活 Task 一次性写完整份计划），本 Task 的两处各约 10% 且内容全是实测新增——按「界不改、越界就报越界」照记，不调界也不删内容。
