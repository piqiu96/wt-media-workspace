# Checkpoint: CHG-20260925-064

- CHG: `CHG-20260925-064`（权威冲突与重复落点处置——按单一落点收口）
- Level: S ／ 仅 `wt-media-workspace` 一仓
- Updated: 2026-09-25

## 状态

`IMPLEMENTING`（2026-09-25 激活）

## Completed

- **T-01 激活**：建本目录（`change.md`、`checkpoint.md`、`evidence/`）；`delivery/LEDGER.md` 表行由占位行改为本 CHG 行；`python3 scripts/prepare_ai_workspace.py --change CHG-20260925-064` 重生成 `.ai/CURRENT_CONTEXT.md`。两门禁 `exit=0`；LEDGER 表行与 `change.md` 的标题／状态／仓库**逐字一致**（`verify_product_master_alignment.py:306-311`）；§7 为字面 `None.`（`:300`）。开工三仓工作区基线已记入 `change.md` §11。
- **T-02 承接工作区编辑**：`M CLAUDE.md`（`/doctor` 瘦身 1 插入 / 55 删除）与 `M conventions:33` 作为一次独立提交入库（`9e9bf39`，只含这两个文件）。三态量测证明这批改动**不是** CHG-062 承接的那次入口重构。净代价：两条提交约定活落点归零，交 T-04 补回。
- **T-03 `conventions` 精简保留**：按用户 2026-09-25 裁定的**保留清单**（保 §1、§7 配置规则、§8、§9、§10 判据、§11）删掉一次性读数与历史叙述：**208 → 148 行、18541 → 14233 字节、节数 11 → 11**。6 类读数／叙述模式（含 `0/8/0`、`Ran 75 / OK`、`1919 字符`）改前 1–7 命中、改后全 0（阳性对照见 evidence §2）；保留下来的规则句与 §9 的 8 个实现落点逐条在位。两处活引用者逐个复核：`AGENT-INDEX.md:198` 改（「校验读数不作文档落点」），`verify_m0_config.py:249` **不改**（节号未变、其断言仍成立）。

- **T-04 读取顺序单一化**：读取顺序由 **5 处手写清单 + 1 个代码常量**（其中 3 处内容互不相同，`MASTER` 那版整份不含 `AGENT-INDEX.md`、第 1 项指向已删的执行根 `AGENTS.md`）收敛为 **1 处手写（`AGENT-INDEX.md` §4）＋ 1 处生成物**。§4 补齐第 6–8 项（T-03 发现的两版「第二层」不一致按 `AGENT-INDEX.md` 为准）；`AGENTS.md` 30→22 行、`CLAUDE.md` 37→28 行（删各自复述的红线与清单，只留指针）；`MASTER:791-796` 6 项清单删为 1 行；`MASTER:66` 的退休词「渐进式加载」就地改写；生成器常量加注释登记为「§4 的生成物镜像」。**变异对照**：常量第 1 项改探针 → 快照正好 2 行不同（时间戳＋第 1 项），还原后只剩时间戳且生成器逐字节相同。**入口红线 9/9 逐条归属**（删掉的 4+5 条全部在 `AGENT-INDEX.md` §2／§9 有落点，阳性对照：`HEAD` 两文件对应小节各命中 1–2）。**两条提交约定回迁**至 `AGENT-INDEX.md` §9「提交纪律」（改前活落点 0，阳性对照 `0de87e8:CLAUDE.md` 各命中 1）。

- **T-05 状态词汇成文**：`MASTER` §3 由「两套词 ＋ 状态定义表」就地覆盖为 `### 状态词汇`——CHG 六词（`DISCUSSION`／`PLANNED`／`IMPLEMENTING`／`VERIFYING`／`DONE`／`SUPERSEDED`）与里程碑四词，读数列逐词给分母（活 20 篇／归档 38 篇／里程碑 6 篇）。**改前的实况是两套都不准**：`TODO`／`IMPLEMENTED`／状态值 `VERIFIED` **零记录使用**，而真在用的 `DISCUSSION`（7）／`PLANNED`（3）／`SUPERSEDED`（8）在文档里**无定义**；校验脚本的接受集与文档词表**交集为零**。阳性对照：同一扫描对 `CLOSED`／`HANDOFF` 各报 2。`MASTER` §6 的 `### CHG 门禁 — CLOSED` 及 `:289`／`:336` 两处一并改 `DONE`（`CLOSED` 退役后 §6 是它的第二落点）。实施中词取 `IMPLEMENTING`（模板／夹具／脚本接受集／056～064 全链在用），退 `IN_PROGRESS`（仅旧归档 4 处 ＋ 1 篇 `planned`），里程碑层不变——依据记在 evidence §3。

- **T-06 脚本／模板与 `checkpoint.md` 落点对齐**：**「active 目录必须有 `checkpoint.md`」这条规则早已写在 `AGENT-INDEX.md` §8、却无人执行**——`git grep -i checkpoint -- scripts tests` 命中 **0** 个文件（阳性对照 `change.md` 9 个）。新增结构检查（`verify_delivery_governance.py`），**变异对照**：`if not (…)` 改 `if False and not (…)` → 新用例复红、其余 4 条仍绿；**活树阳性对照**：把本 CHG 的 `checkpoint.md` 改名 → 真门禁 `exit=1` 报 `active CHG is missing checkpoint.md: CHG-20260925-064`，还原后 `sha256` 相同。接受集由 `{IN_PROGRESS, IMPLEMENTING, VERIFYING, ACTIVE}` 收为 **`{IMPLEMENTING, VERIFYING}`**（记录落在 `active/` 即意味着在执行；`DISCUSSION`／`PLANNED` 属 `planned/`，`DONE`／`SUPERSEDED` 是终态），加 6 非法词 × 2 合法词的用例，`HEAD` 版上 **6/6 非法 subTest 全红**（其中 `IN_PROGRESS`／`ACTIVE` 是被旧集**收下**）。**实测另发现一处既有误诊**：`:288` 的 `(\S+)\s*$` 要求状态行恰好只是那个词，58 篇里 **9 篇**带注 ⇒ `status=None`；`CHG-20260923-059` active 期正是带注形式，它自己的门禁输出里留着 `… got None`——**点了一个该记录从未有过的状态**。抽出 `status_word()` 先剥 `**`／`（…）`／`(…)`，新用例的红**是行为性的**（在测试里复现出 059 那条报文）。附带的收紧：剥注后 LEDGER 表行比对由**被跳过**变为**真的执行**。新增 `templates/delivery/checkpoint.md`、`change.md` §12 改指针、skill `:95` 与 `AGENT-INDEX.md:141` 点名 `checkpoint.md`、`sync_skills.py` 重生成并 `check` 通过、`conventions` §9 加两行耦合。**一次自我更正**：带注用例初稿同时断言 `status_word()`，红成了 `AttributeError`（**这种红什么都证明不了**），已拆成两个用例；夹具也修过一处（初版把带注串写进了 LEDGER 值）。

- **T-07 活记录状态词就地改写**：改前活记录 20 篇里不在 `MASTER` §3 表中的词**恰有 1 个**（`023` 的 `IN_PROGRESS`），改后 **20/20 全部落表**（阳性对照：同一脚本对归档记录仍报出 8 处表外词 ⇒ 扫描能咬住）。`023` 判 `SUPERSEDED` 是**内容判断**，两个互相独立的依据：`CHG-20260723-025` 的标题本身就是「M2-B1 浏览器窗口扫描与 Diff 只读闭环」（与 023 同标签），且 `CHG-20260725-031` 的收口矩阵把 B1 归给 025；023 的三项 Task 分别由 025／`026`／`022` 交付，它自己从未进过 `active/`、无 `evidence/`。`planned/README.md` 两处：023 那条已过期的旧理由就地覆盖；M3 表加列说明——该列写**程序进度**，不是记录的**状态词**，故 `045` 的「已实施…由 CHG-052 承载」与它自己的 `DISCUSSION` 不矛盾（**只让两轴可分辨，不改判任何草案**，七份草案的终态词归 §14 第 8 项）。`MASTER` §3 的实测读数列连带更新：`SUPERSEDED` 活列 8→9、`IN_PROGRESS` 活记录 1→0，并改掉被本 Task 直接证伪的「`planned` 记录保持原样」这半句。

- **T-08 FFmpeg 归属：就地改写 ＋ 全仓复扫**：按用户裁定把 `ADR-0015:6`／`:27` **整句重写**（不删词、不留取代注记），并从 M2 的 Agent 边界清单里去掉 FFmpeg、就地补明它属 Cloud Compose Worker（ADR-0017）。**复扫又咬出两处**计划没点名的活落点——`skills/common/common-architecture-review/SKILL.md:13` 与 `skills/desktop/desktop-sidecar-update/SKILL.md:3` 都直白断言 Agent 拥有 FFmpeg，只改 ADR 则 AC-08 当场不成立，故一并改。判给 Agent 的活落点 **4 → 0**（改后 20 条候选逐条判定：Cloud-owned／排除句／清单／历史引述／本记录自述，无一条判给 Agent）。扫描口径与分母：`git ls-files` 排除 `completed|reports` 与生成副本目录，同子句（`。；;`）内「执行方词」与「ffmpeg 词」相距 ≤80 字符即入候选，**两列都不是结论**（`0015:6` 的真冲突恰恰藏在否定列里）。阳性对照：把 `MASTER:454` 注入成「视频合成由 Local Agent 执行 FFmpeg」→ candidate **9→10** 且新条目正是该行，`git restore` 后 `sha256` 与注入前相同。**两处记录更正**：§4.2 C2 原写「全仓其余落点一致判给 Cloud」**过宽**（漏了两个 skill），就地更正；§4.4／§9／AC-15 的「三仓零写」按分发机制改写为「不改运行时代码，只收 `skills/` 的分发副本」。`sync_skills.py check` → `skill outputs are up to date`；三仓各自收到生成副本并随各自仓库单独提交（`commit_generated: true`，`AGENT-INDEX.md` §9）。

- **T-09 里程碑与交付事实：三处陈旧结论就地改写**：判据串 `E3 未开始`／`仍为 IN_PROGRESS`／`` 不标 `DONE` `` 在**活文件（分母 174）改前 3 → 改后 0**；放宽关键词的补充扫（`未开始`／`进行中`／`尚未验收`／`待验收`／`待签收`／`签收前`／`IN_PROGRESS`／`NOT_STARTED`／`实施中` 与 `M3` 同现）剩 **1** 条，是 `MASTER:162` 里引述旧行标的**过去时叙述**，判留。三处：`milestones/README.md:7`（「实施中…E3 未开始」→ 写明 2026-09-23 通过 E3 并由用户签收、`DONE`）、`M3-content-discovery-v2.md:35`（把「暂时通过」的口径钉在时间上＋写明整体已 `DONE`；**表内 5 处读数不改**，同 T-07 先例）、`MASTER:162`（**删断言、留缘由**——只记「为什么 `M3-M10` 拆两行」，明写「不重复断言任何状态」）。**计划落点与实况不符并如实登记**：计划写 `MASTER:158`，那行（今 `:159`）本来就是 `DONE`，真正陈旧的是紧邻下方 `:162` 的 2026-09-23 拆分注。**为什么漂移（本轮新量的机制读数）**：同一事实当时 2 个有门禁落点、3 个无门禁落点——`verify_product_master_alignment.py:64` 硬编码期望并读 `MASTER` §3 的 `| 状态 |` 字段（**变异对照**：改成 `IN_PROGRESS` → `exit=1` 报 `M3 status expected 'DONE', got 'IN_PROGRESS'`，连带触发候选块结构检查共 2 条；还原后 `sha256` 相同），而 `milestones/README.md`、`M3-*.md` 的散文、`MASTER` §2 表行**没有任何门禁**（分母 `scripts/`＋`tests/` 共 30 文件：对判据串 0 命中，对 `milestones/` 路径的 7 处命中全是测试夹具的字面量）。**对账**：三处改写与四处权威源（`M3-*.md:3-4`／§2.2、`MASTER:159`／`:362`、`LEDGER:27`）在状态词／签收日期／验收矩阵三项事实上无一处相反。**不新增任何机检点**（为里程碑散文加判据会把措辞冻成契约）。§14 第 2 项就地补上「双落点里只有一处被盯着」这一实测事实与今日行号。

## Current

- T-09 已落。下一个是 T-10／T-11（相互独立，可换序）。

## Next

1. **T-10／T-11**（相互独立，可换序）：目录树与死指针／前端源码根与视觉规范合并。
2. **T-12**：归档、LEDGER 同步、快照重生成、两遍失效指针扫描；并按 AC-15 与开工基线对账三仓（只应多出 `skills/` 分发副本）。

## Blocked

- None.

## Recent verification

| 判据 | 读数 |
|---|---|
| `verify_delivery_governance.py` | `exit=0`，`Active CHG: CHG-20260925-064` |
| `verify_agent_entry.py` | `exit=0`，`0 warning(s)`，快照 **1936 字符**（预算 8000；`wc -c` 是 1978 字节——门禁按**字符**判） |
| `verify_skills.py` | `exit=0`，`verified 10 skill source files` |
| `verify_m0_config.py` | `exit=0` |
| `verify_product_master_alignment.py` | `exit=0` |
| `verify_m2_acceptance.py` | `exit=0` |
| `python3 -m unittest discover -s tests -q` | `Ran 79 tests` / `OK`，`exit=0`（T-05 收盘为 75；T-06 新增 4；T-08 不新增用例） |
| `sync_skills.py check` | `skill outputs are up to date`，`exit=0`（`sync` 之后复测） |
| 退役流水线串 `TODO → IMPLEMENTED`（活文件，排除本 CHG 自身记录） | 0 命中 |
| 三仓工作区基线（AC-15） | `cloud` `?? dump.rdb`；`agent`、`desktop` 空——**T-08 起三仓各自多出 `skills/` 的分发副本**（不改代码），随各自仓库单独提交；逐份明细见 `evidence/task-08-ffmpeg-ownership.md` §6／§8 |

| 词汇对账（逐文件提取，可复算；T-07 后） | 活 20 篇 `{SUPERSEDED:9, PLANNED:3, DISCUSSION:7, IMPLEMENTING:1}`——**表外词 0**；归档 38 篇 `{DONE:28, IN_PROGRESS:4, HANDOFF:2, CLOSED:2, VERIFYING:1, IMPLEMENTING:1}`——表外 8（T-05 已声明归档不动） |
| 带注状态行（T-06 新量，分母 58 篇 `change.md`） | **9 篇**用旧正则（`(\S+)\s*$`）匹配不上 ⇒ 旧代码把它们的 `status` 读成 `None`；新 `status_word()` 全部读出词 |
| 现在解析 `checkpoint.md` 的门禁（分母 `scripts/` ＋ `tests/`） | 2 个文件：`scripts/verify_delivery_governance.py`、`tests/test_verify_delivery_governance.py`（T-06 之前是 0 个） |

| FFmpeg 归属（T-08，活文件） | 判给 Agent／Desktop 的落点 **4 → 0**；改后 20 条候选逐条判定；分母：含 `ffmpeg` 的 **100 行／24 文件**（改前 102／26） |
| 同一扫描器可失败（T-08 阳性对照） | 注入 Agent-owned 句子 → candidate **9 → 10**，新条目即被注入的 `MASTER:454`；`git restore` 后 `sha256` 与注入前相同 |

| 陈旧 M3 结论（T-09，判据串，活文件） | 改前 **3** → 改后 **0**（分母 174 个活文件）；放宽关键词补充扫剩 1 条，判为过去时叙述 |
| 同一判据串扫描器可失败（T-09 阳性对照） | 对**本 CHG 自身记录**报出 2 处（`change.md:54`／`:283`，逐字引用的原句） |
| `MASTER` §3 状态字段有门禁（T-09 新量，阳性对照） | 改成 `IN_PROGRESS` → `exit=1` 报 `M3 status expected 'DONE', got 'IN_PROGRESS'`（＋候选块结构检查共 2 条）；还原后 `sha256` 与变异前相同（`54cdbb5f…`） |
| 里程碑散文是否有门禁（T-09，分母 `scripts/`＋`tests/` 共 30 文件） | 判据串 **0 命中**；`milestones/` 路径 7 命中**全是测试夹具字面量**，无一处读取 ⇒ `milestones/README.md` 与 `M3-*.md` 的散文**无门禁** |
| 与四处权威源对账（T-09） | `M3-*.md:3-4`／§2.2、`MASTER:159`／`:362`、`LEDGER:27` 与三处改写，在状态词／签收日期／验收矩阵三项事实上**无一处相反** |

取数时间与逐次读数见 `evidence/artifacts/t09-gate-readings.out`——该文件**逐段追加，每段段首都有取数时间**（T-09 的初遍跑在该文件建立之前、未同时写时间戳，已在该文件开头如实注明、**不列为独立一段**）；各段读数除 `unittest` 耗时外**逐行相同**。为什么本行不写死一个时间：本记录与 `checkpoint.md` 本身是门禁读入的对象，每改一次记录就得重跑一次，写死的时间必然追不上最后一次改动。纪律的实质由两件事保证：①初遍记在本记录更新之前，**不作关闭值**；②末段在本记录最后一次改动之后。门禁对 `checkpoint.md` 只查**存在性**（`git grep -i checkpoint -- scripts/` 唯一命中 `verify_delivery_governance.py` 的 `is_file()`），故末段正文的措辞不影响任何判据。T-09 的扫描与对账原始输出见 `evidence/artifacts/t09-stale-m3-sweep.out`／`t09-canonical-alignment.out`；逐条明细见 `evidence/task-09-milestone-delivery-facts.md`。T-08 的对应产物为 `t08-gate-readings.out`／`t08-sweep-*.out` 与 `task-08-ffmpeg-ownership.md`。

上一版读数（`t06-gate-readings.out`，19:57）已被**覆盖**：T-07 改了 `planned/` 的记录与 `MASTER` §3 的读数列，那些数字不再是关闭值。T-06 那一版同理覆盖了 T-05 的 19:51 读数。`t08-gate-readings.out`（20:06–20:08）同理被 **T-09** 覆盖：T-09 改了 `MASTER:162`、两个里程碑文件，那些数字不再是关闭值——但两版的**判据行仍逐行相同**（T-09 只改文档文本，不碰任何判据的输入面，`unittest` 仍 79）。
