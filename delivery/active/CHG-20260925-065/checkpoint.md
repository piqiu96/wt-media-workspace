# Checkpoint: CHG-20260925-065

- CHG: `CHG-20260925-065`（三个运行仓入口文件形态统一——双指针 + 单一正文）
- Level: S
- Updated: 2026-09-25

## 状态

`IMPLEMENTING`（2026-09-25 激活）

## Completed

- **T-01 激活**：建 `delivery/active/CHG-20260925-065/`（`change.md`、`checkpoint.md`、`evidence/`）；§5 范围**封闭**；§7 `Pending Questions` = `None.`；`LEDGER.md` 表行与归档说明；快照以 `--change CHG-20260925-065` 重生成；四仓 `git status --porcelain` 基线记入 `evidence/task-01-baseline.md`（workspace 净、agent 净、desktop 净、cloud `?? dump.rdb`——他人在途产物，88 字节、mtime 2026-09-24 17:19:16，早于本 CHG 一天，不碰不提交不清理，沿用 CHG-063/064 处置）；开工基线 `bd5df2c`。
- **为什么本 CHG 与四条 S 级先例不同**：那四条都写明「三仓只被读、不被写」，**本 CHG 会写三仓的入口文件**（仅四类入口文件，零运行时代码／配置／测试）。已在 `change.md` §1／§4／§5／§9 各落一次，收尾 T-09 逐仓对账。

- **T-03 生成器对齐**：`scripts/init-agent-entry.sh` 全文重写——产出 3 件 → **4 件**（＋ `DIRECTORY_MAP.md`，目录节按生成时磁盘实况列顶层目录）、`AGENT-INDEX.md` 由 `## Workspace`／`## Rule` 改为**八节同序骨架**、两个指针带机读键、新增 `## 本仓内加载顺序` ＋ 作用域句、`:79-85` **停止手写** `.ai/CURRENT_CONTEXT.md`（改为打印 `prepare_ai_workspace.py --no-active`）。**并改正 §3 指针预算的自我矛盾**（`H2 ≤ 1` ＋ 白名单 `权威源` ⟷ 它自己引用的参照件有 3 个 H2；改为 `H2 ≤ 4`、不设白名单，规则词判据只作用于非标题行，补出重复比较集的构造）——**不是放松**：变异 4 在改正前后都被规则词判据抓出，改正后多抓一类。tmpdir 实跑 12/12 形态判据 PASS，阳性对照 7 类变异全报出。读数见 `evidence/task-03-generator.md`。
- **T-02 规范与落点成文**：`conventions §3` 整节改写为「入口文件形态」（角色与边界表／`AGENT-INDEX.md` 同名两角色＋运行仓八节模板／**指针文件的机检定义**三条 ERROR／「重复只在生成物与其生成器之间存在」判别句／显式否决 `@` 导入）＋ §9 耦合表 2→5 行 ＋ §10 已知限制重写 ＋ §11 补两条禁令；`AGENT-INDEX.md` §4 `:62` 作用域句（**两个层级**而非两个落点）、§10 表加 `DIRECTORY_MAP.md` 行＋「两者都不得承载规则正文」段；`..._V1.md:769` 补自洽句、`:1801` 验收话扩写到五文件。节号未变（`verify_m0_config.py:249` 引 §10）。读数见 `evidence/task-02-normative.md`。
- **T-04 门禁实现与退役**（`e663270`）：`verify_agent_entry.py` 新六条检查（`check_repo_entry_files`／`check_pointer_shape`／`check_rule_body_consistency`／`check_layer3_shape`／`check_rule_text_duplication` WARN／`check_local_order_scope` WARN）＋退役 `check_entry_drift` 与 `check_layer3_entries`；`tests/` fixture 重写为「默认合规」。**每条 ERROR 都做变异对照**：禁用逐条 → 3／7／4／2／2／1 条用例失败，`ImportError` **0**。落地即见红 **71 ERROR**——这是设计结果，收口路径见下「预期中间态见红」。
- **T-05 cloud 收口**（`0db02ab`）：四件入口文件改为 §3 形态，正文迁入 `AGENT-INDEX.md` 的 `## 本仓规则`；落实 A（`docs/superpowers/` 判为分析材料）／B（两处事实错误**按代码实况**回写：`internal/infra` 5 项、模块树取含 `router.go` 的那份）／E／F。门禁 cloud **51 → 1**。
- **T-06 agent 收口**（`6d740fc`）：同上四件 ＋ E。门禁 agent **10 → 0**，四仓合计 **71 → 11**；13 行模块树迁入 `DIRECTORY_MAP.md`（**该图本就有更精确版本**）；「文件与 FFmpeg 运行时」按代码回写为「尚无实现」。
- **T-07 desktop 收口**（`7c1b0ad`）：同上四件 ＋ E ＋ D-04 的范围限定句（**只改措辞**，政策冲突另立 CHG）。门禁 desktop **8 → 0**，四仓合计 **11 → 3**；**跨仓八节相等判据自 T-04 起红至此刻转绿**（该红只能由三仓齐备消，设计如此）。
- **T-08 workspace 入口对齐**（`50a2417`）：两件入口文件各加机读键 ＋ `CLAUDE.md:9` 由复述句改为指针句（该事实的唯一落点本就在 `AGENT-INDEX.md` §1，故是**改指针而非搬家**）。门禁 **3 → 0**，**四仓合计 0 ERROR / 0 WARN**——本 CHG 的中心验收条件达成。

## Current

T-08 已完成（workspace 入口两件；**四仓 0 ERROR / 0 WARN**）；下一项是 T-09（收尾）。

## Next

1. **T-09**：收尾归档与对账。**T-08 已完成，T-09 的前置条件满足**（T-09 不得早于 T-07，且不得在红的状态下归档——**此刻已无红**）：两遍失效指针扫描（字符串 ＋ 相对链接 resolve，各带阳性对照与分母，**锚取具体提交不取 `HEAD`**）、归档 → `completed/`、LEDGER 同步、快照 `--no-active`、四仓对账、六门禁 ＋ 套件在最后一次改动之后重测。

## Blocked

- None.

## 预期中间态见红（不得静默容忍）

**现状：`verify_agent_entry.py` exit=0，0 ERROR / 0 WARN —— 本节所述的中间态已全部关闭**（T-08 后；`evidence/artifacts/t08-gate-after.out`）。T-04 落地时的 71 条是**设计结果**，不是缺陷：新检查按构造先对现状报错，再由 T-05～T-07（三仓）与 T-08（治理仓）逐个收口。

| 仓／面 | T-04（改前） | T-05 后 | T-06 后 | T-07 后 | **现在（T-08 后）** |
|---|---|---|---|---|---|
| `cloud` | 51 | 1 | 0 | 0 | **0** |
| `agent` | 10 | 10 | 0 | 0 | **0** |
| `desktop` | 7 | 8 | 8 | 0 | **0** |
| `workspace` | 3 | 3 | 3 | 3 | **0** |
| **合计** | **71** | 22 | 11 | 3 | **0** |

分判据（T-08 后，分母＝0）：`declares no rule body`、`restates a rule without naming`、`H2 sections, expected 8`、`H2 sequence diverges`、`exceeds the pointer budget`、`disagree on the rule body`、`declares itself`、`declares a pointer as the rule body`、`declares an unknown rule body` **均 0**。跨仓八节相等判据在 T-07 转绿——它自 T-04 起一直是红的，且**只能**由三仓齐备消（设计如此，不是缺陷）。

必须显式说明（**本节的自述也在被检验**）：CHG-20260925-063 的教训是「意料外的红会训练读者忽略这个门禁」，**已文档化的红同样会**（`conventions §10` 成文）。故本节的读数是**带收口计划的中间态**，不是「已知红项」——每一步都有对应的 Task 与「收口后应转绿」的可证伪预期，且每个 Task 都在**收口前后各量一次**（T-08 的两次读数见 `t08-gate-before.out`／`t08-gate-after.out`）。**红转绿不是靠收窄判据换来的**：T-08 另在真树上做活体阳性对照（删键 → 报出），证明这个 0 不是门禁变瞎。**其余五个门禁全程全绿**（本 CHG 未触及它们，T-09 重测）。

⇒ **T-09 不得早于 T-07**（已满足）；本 CHG 不得在红的状态下归档（**此刻已无红**）。

## Recent verification

T-01 收尾读数（`evidence/artifacts/t01-gate-readings.out`，@ 2026-09-25T14:36:35Z）：

| 判据 | 读数 |
|---|---|
| `verify_m0_config` | `exit=0` |
| `verify_delivery_governance` | `exit=0`，`Active CHG: CHG-20260925-065` |
| `verify_agent_entry` | `exit=0`，0 warning（**尚未加新检查**，故此处 0 warning 只说明旧范围不够，见 `change.md` F-04） |
| `verify_skills` | `exit=0`，verified 10 skill source files |
| `verify_product_master_alignment` | `exit=0` |
| `verify_m2_acceptance` | `exit=0` |
| `unittest discover -s tests -q` | `Ran 79 tests` / `OK` |
| `sync_skills.py check` | `exit=0` |
| 四仓 `git status --porcelain` | workspace 净（＋本 CHG 未跟踪记录）/ cloud `?? dump.rdb` / agent 净 / desktop 净 |
| 开工基线 commit | `bd5df2c` |

**一处激活期实测（登记，不追责）**：第一版 LEDGER 表行的标题被我**缩短**为「…——双指针 + 单一正文」，而 `verify_product_master_alignment.py:311,338` 要求表行逐字等于 `change.md` H1 的标题（`expected_row = f"\| {active_change} \| {title} \| {status} \| {current_repository} \|"`）。实测报 `Ledger is not aligned with active CHG CHG-20260925-065 status 'IMPLEMENTING'`，**且 `unittest` 同时红 1 条**——即该门禁有判别力，不是装饰。改为 H1 全文后两条同时转绿。

T-02 收尾读数（`evidence/artifacts/t02-normative-strings.out`，@ 2026-09-25T14:38:16Z，锚 `bd5df2c`）：

| 判据 | 读数 |
|---|---|
| 判据串落地（分母 15） | `正文：` 0→1；六条新检查名 **0→1 或 0→2**；`## 本仓规则` 0→2；`本仓内加载顺序` 0→2；`check_entry_drift` 1→2 |
| 阳性对照（把判据串注入 fixture） | **10/10 命中 ✓** |
| 「先写后实现」（`verify_agent_entry.py`） | 六条新检查名 **6/6 命中 0**；对照 `check_entry_drift` 命中 2 |
| 六门禁 | 全 `exit=0` |
| `unittest discover -s tests -q` | `Ran 79 tests` / `OK` |
| `sync_skills.py check` | `exit=0` |

六门禁全绿是**预期**：T-02 只写规范与文档、未动脚本，而新判据尚未实现——故此刻的绿**不**说明现状合规（与 T-01 的 0 warning 同理）。**行号漂移**：T-02 给 `AGENT-INDEX.md` §10 加 3 行后，§12 里那句旧描述由 `:193` 漂到 **`:198`**；本 CHG 的记录自此**按内容定位、不按行号**（已登记 `change.md` §14 第 7 项）。

T-05 收尾读数（cloud，@ 2026-09-25T23:0xZ；`artifacts/t05-gate-after.out`）：

| 判据 | 读数 |
|---|---|
| `verify_agent_entry` | `exit=1`，**22 ERROR / 0 WARN**（cloud 51 → **1**，见上表） |
| `check_rule_text_duplication` | WARN 0；**分母** `compared 95 rule sentence(s) across 11 file(s) in 4 repositories` |
| 其余五个门禁 | 全 `exit=0` |
| `unittest discover -s tests -q` | `Ran 94` / OK |
| 形态（`wc -l`） | `AGENT-INDEX` 60→205、`AGENTS` 113→11、`CLAUDE` 168→11、`DIRECTORY_MAP` 105→106 |
| 逐条归属表 | 分母＝改前非空行数 86／99／45／75，各类加总等于分母（`task-05-cloud.md` §2） |
| AC-09 阳性对照 | 注入 `cache` → infra 扫描报 `missing -> ['cache']` |
| AC-11 阳性对照 | 同一扫描对**改前提交** `0346edf:AGENT-INDEX.md` 命中 **1**（`:60`；本文件命中 0）——**锚是提交，不是 `HEAD`**（理由见下） |
| 指针链接 | 两个指针各 3 个链接全部 resolve |
| cloud `git status --porcelain` | 仅 4 个 `M` ＋ 既存 `?? dump.rdb` |

**两条如实登记的不足**：①AC-09 的判据**不是门禁**（全仓无脚本读 infra 列表，`change.md` §14 第 11 项）；②cloud 剩余的 1 条跨仓 ERROR 本 Task 无法消（§1 归属说明）。

**一处自纠**：归属表初稿把「总行数」与「非空行数」两个分母混用，且 CLAUDE.md 的三类条数加总（99 行）写成了 112。改用改前版本重测分母后改正；**分母必须当场量**，不能沿用前一稿的读数。

**一处事后修正（T-06 时发现）**：本表原来记的对照是 `HEAD:AGENT-INDEX.md`。取证当时 `HEAD` **确实**指向改前提交，读数正确；但 `0db02ab` 一落，`HEAD` 就是修复后的文件，**同一条命令读数也是 0——与「扫描无判别力」形状完全相同**。故此表的对照改记 `0346edf`（＝ `0db02ab^`），`artifacts/t05-cloud-checks.sh` 里钉为常量 `BASE`。**凡以改前状态为对照的可重放命令，一律指向具体提交。**（T-06 的 agent 臂在同一处犯了同样的错，两次已登记 `change.md` §14 第 14 项。）

T-06 收尾读数（agent，@ 2026-09-25；`artifacts/t06-gate-after.out`）：

| 判据 | 读数 |
|---|---|
| `verify_agent_entry` | `exit=1`，**11 ERROR / 0 WARN**（agent 10 → **0**，见上表） |
| `check_rule_text_duplication` | WARN 0；**分母** `compared 96 rule sentence(s) across 11 file(s) in 4 repositories`（改前 62） |
| 其余五个门禁 | 全 `exit=0` |
| `unittest discover -s tests -q` | `Ran 94 tests` / `OK` |
| 形态（总行数） | `AGENT-INDEX` 65→92、`AGENTS` 45→11、`CLAUDE` 10→11、`DIRECTORY_MAP` 117→118 |
| 逐条归属表 | 分母＝改前非空行数 34／6／48／88，四列加总等于分母；`DIRECTORY_MAP.md` diff 为纯增量（2 insertions／1 deletion，那 1 处是同行的句尾替换） |
| AC-09′ 点名路径 | 分母 25 条反引号路径，**25/25 存在**（22 直接 resolve ＋ 3 条同句内已点名目录的简写）；注入假路径 → missing 3→4 ⇒ 有判别力 |
| AC-11 阳性对照 | 对 `24da21b:AGENT-INDEX.md` 命中 **1**（`:65`）；**未改动的 desktop 仍命中 1**（`:75`）＝第三方对照 |
| 指针链接 | 两个指针各 4 个链接（8/8 resolve）；注入 `[dead](NO-SUCH-FILE.md)` → 报出 |
| agent `git status --porcelain` | 仅 4 个 `M`（提交后净） |

**两条如实登记的不足**：①AC-09′ 与 AC-11 的判据**不是门禁**（全仓无脚本读 infra 列表或排除清单，`change.md` §14 第 11 项）；②判据里的**路径词表是承重构件**——松判据（只查 `扫描`）在**已修好的**文件上仍报 agent 2 行／cloud 3 行，**全为假阳性**（两条指针行含「禁止扫描区」四字、一条是 `go vet` 行）。去掉词表，「0 命中」会被假阳性污染成噪声（`change.md` §14 第 15 项）。

T-07 收尾读数（desktop，@ 2026-09-25；`artifacts/t07-gate-after.out`）：

| 判据 | 读数 |
|---|---|
| `verify_agent_entry` | `exit=1`，**3 ERROR / 0 WARN**（desktop 8 → **0**，见上表） |
| `check_rule_text_duplication` | WARN 0；**分母** `compared 97 rule sentence(s) across 11 file(s) in 4 repositories` |
| 其余五个门禁 | 全 `exit=0` |
| `unittest discover -s tests -q` | `Ran 94 tests` / `OK` |
| 形态（总行数） | `AGENT-INDEX` 75→99、`AGENTS` 39→11、`CLAUDE` 12→11、`DIRECTORY_MAP` 90→92 |
| 逐条归属表 | 分母＝改前非空行数 28／7／59／68，四列加总等于分母 |
| AC-11 阳性对照 | 对 `623583d:AGENT-INDEX.md` 命中 **1**（`:75`）；本文件命中 **0** |
| 指针链接 | 两个指针各 4 个链接（8/8 resolve） |
| desktop `git status --porcelain` | 仅 4 个 `M`（提交后净） |

**一处按磁盘复核**：`DIRECTORY_MAP.md:42` 的「四个占位模块目前是 3 行空壳」——实测四个 `mod.rs` 各 3 行、共 12 行，与地图一致，**不是陈旧断言**。**一处按代码回写**：排除清单里的 `../generated`（无点）全仓仅该行提到过，`frontendDist` 实为 `../.generated/frontend`，按实况删除（`change.md` §14 第 16 项）。

T-08 收尾读数（workspace 入口；@ 2026-09-25T15:06:23Z，**在最后一次改动之后**重测 —— `artifacts/t08-gate-readings.out`）：

| 判据 | 读数 |
|---|---|
| `verify_agent_entry` | **`exit=0`，0 ERROR / 0 WARN**（workspace 3 → **0**，见上表） |
| `check_rule_text_duplication` | WARN 0；**分母** `compared 97 rule sentence(s) across 11 file(s) in 4 repositories`（与 T-07 同分母——本 Task 未增删可比较的规则句） |
| 其余五个门禁 | 全 `exit=0` |
| `unittest discover -s tests -q` | `Ran 94 tests` / `OK`；`sync_skills.py check` `exit=0` |
| 形态（`wc -l`／字节／H2） | `CLAUDE.md` 30／1796／3、`AGENTS.md` 24／1296／2；机读键各在 `:3` |
| 改动面 | **5 增 1 删**：两文件各 1 行机读键（`AGENTS.md` 只增不减）＋ `CLAUDE.md:9` 由规则句改为指针句 |
| 阳性对照 ①（活体真树） | 删 `AGENTS.md` 的机读键 → 报 `declares no rule body`、`exit=1`；还原后 `cmp` 逐字节相同 → 回 0（`t08-live-control.out`） |
| 阳性对照 ②（锚改前提交 `23eeaa6`） | 两文件还原成改前版本 → **恰报出那 3 条**、`exit=1`；还原 → `exit=0`（`t08-gate-before.out`） |
| workspace `git status --porcelain` | 2 个 `M`（两件入口文件），**无新增文件**（记录另提交） |

**一处性质判定**：`CLAUDE.md:9` 不是「搬家」而是「改指针」——该事实的唯一落点本就在 `AGENT-INDEX.md:23` §1 第 6 行（`- **不拥有**：运行时代码、服务运行代码、构建产物、临时文件。`），第 9 行即三仓路径。删掉的是**第二份**，不是唯一一份。

**一条被上一轮读法否掉的推断**（如实登记）：T-07 时我从「三仓指针各 11 行 / 656 B」推断 workspace 的指针**也应**同量级，据此以为 workspace 只需加两行键。实测 workspace 的两个指针**本就更大**（30／24 行，各 2–3 个 H2），因为它们承载一件运行仓不存在的事实——**同名两角色**（`AGENT-INDEX.md` 在 workspace 是治理正文、在运行仓是三层索引）。⇒ 三仓的形态不是 workspace 的标尺，**形态约束的是角色，不是章节结构**（与本 CHG §Risk 1 同一句）。

T-04 收尾读数（@ 2026-09-25T22:47Z 前后）：

| 判据 | 读数 |
|---|---|
| `verify_agent_entry` | **`exit=1`，71 ERROR / 0 WARN**（见上「预期中间态见红」） |
| 其余五个门禁 | 全 `exit=0` |
| `unittest discover -s tests -q` | `Ran 94 tests` / `OK`（原 79：−16 旧用例 ＋31 新用例） |
| 变异对照（分母＝6 条新检查） | 禁用逐条 → 3／7／4／2／2／1 条用例失败；**`ImportError` 6 次全为 0** |
| 生成器产出 vs **门禁自己的函数** | 六函数 0／0／0／0／`WARN 0`（分母 1 条规则句）／0；阳性对照 **3/3 命中**（`artifacts/t04-generator-vs-gate.out`） |
| `sync_skills.py check` | `exit=0` |

**两处不读成「全绿」**：`check_layer3_shape` 的跨仓比较在单仓树上分母为 1（未覆盖，交 T-05～T-07）；`check_rule_text_duplication` 的分母只有 1 条规则句（骨架无规则句）。另：`check_local_order_scope` 报 0 只因三仓小节**仍叫旧名**，**T-07 后必须重测**。

**记录成本自纠（第五版）**：§11 的界改过四次——①`change.md` ≤ 25 KB／单 Task ≤ 3 KB → 被 T-01～T-04 逐条突破；②`change.md` ≤ 30 KB／单 Task ≤ 8 KB → 被 T-05 再次突破；③合计 ≤ 80 KB → **T-06 时证明从一开始就不成立**（9 个 Task、16 条 AC、4 个仓，证据随 Task 数线性长，一个与任务数无关的常数界必然被突破）。④改为 35 KB／15 KB／9 KB ——**这一版仍是存量界**，只在单位上像速率，故 **T-07 收尾时前两条就被突破**（`change.md` 37701＞35840、`checkpoint.md` 15418＞15360）；我不但没换对被限制的量，还在同一节里把它称作「速率」。⑤改为**真速率：每个 Task 的增量**（`change.md` ≤ 5 KB、`checkpoint.md` ≤ 4 KB、单 Task evidence ≤ 9 KB），**存量只报不设顶**，以 CHG-064 实测的 213739 B 作对照基准。**第五版的界也不是无条件成立的**：T-06／T-07 四段在界内，但 **T-08 的 `checkpoint.md` 增量越了 4 KB 界**。原因不是这一版又选错了量——是我在 T-08 收尾时补上了 `Completed` 里 T-04～T-07 五行**早该由那四个 Task 各自写下**的条目，于是替前四个 Task 付了它们的记录成本。**界不改**（§14 第 17 项：该调的是被限制的量，不是界的值），越界就报越界。**真正的错在四节记录没在各自的 Task 里写完**，T-08 只是把它暴露出来；修法是每个 Task 收尾把 `Completed` 写全。⇒ 登记为 §14 第 19 项。逐次读数见 `artifacts/t0{6,7,8}-record-size.out`，**此处不内联数字**——我曾把 T-08 的增量写进这一段，两次改稿就把它变成旧值，与 §14 第 14 项同一错法。**前四版错在同一件事——限存量**，而存量由任务数决定，不由我决定；本 CHG 连错四次，记在此以对照「多落点同一事实必有一个静默过期」是同一个错法。见 `change.md` §11 与 §14 第 9、17 项。

T-03 收尾读数（`evidence/artifacts/t03-conformance.out`，@ 2026-09-25T14:41:53Z）：

| 判据 | 读数 |
|---|---|
| tmpdir 实跑产出 | `AGENT-INDEX.md` 41 行/854 B/H2=8；`CLAUDE.md` 9/567/1；`AGENTS.md` 9/583/1；`DIRECTORY_MAP.md` 15/465/2 |
| 形态对账（分母 12 项） | **PASS 12 / FAIL 0**（**注意：这是我写的临时对账脚本，不是门禁**；T-04 后须调门禁自己的函数复测，不得沿用此读数） |
| 阳性对照（分母 7 类变异） | 变异 1–6 → 12 项里 **FAIL 6**；变异 7（灌水 38 行/2211 B）→ **只**预算 FAIL。⇒ 前 6 类从未让预算变红，故补做变异 7 证明预算确有判别力 |
| `workspace --dry-run` | 三件 `exists:`；快照 `exists:`——**不再** `would create:`（手写路径已消失） |
| 六门禁 | 全 `exit=0` |
| `unittest discover -s tests -q` | `Ran 79 tests` / `OK` |
| `sync_skills.py check` / `bash -n` | `exit=0` / ok |
