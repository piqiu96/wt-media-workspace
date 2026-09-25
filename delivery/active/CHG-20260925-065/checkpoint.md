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

## Current

T-05 已完成（`0db02ab`）；下一项是 T-06（agent）。

## Next

1. **T-06 agent 收口**（分母 10）、**T-07 desktop 收口**（分母 7／8，含 D-04 的范围限定句）。各仓独立提交。两仓都需新增 `## 本仓规则` 节（八节第 6 位）——cloud 已就位，**跨仓序列相等判据要等这两仓落地才转绿**。
2. **T-08**：workspace 入口文件补机读键 ＋ 修 `CLAUDE.md:9` 那行复述（分母 3）。**T-09**：收尾归档与对账（**不得早于 T-07**）。

## Blocked

- None.

## 预期中间态见红（不得静默容忍）

**现状：`verify_agent_entry.py` exit=1，22 条 ERROR**（`evidence/artifacts/t05-gate-after.out`；改前 71 条见 `t04-gate-readings.out`）。这是 T-04 的**设计结果**，不是缺陷：新检查按构造先对现状报错，再由 T-05～T-07（三仓）与 T-08（治理仓）逐个收口。

| 仓／面 | T-04（改前） | 现在（T-05 后，收口目标 0） |
|---|---|---|
| `cloud` | 51 | **1** |
| `agent` | 10 | 10 |
| `desktop` | 7 | 8 |
| `workspace` | 3 | 3 |
| **合计** | **71** | **22** |

分判据（现在）：`restates a rule without naming` 10 ／ `declares no rule body` 6 ／ `exceeds the pointer budget` 2 ／ `H2 sections, expected 8` 2 ／ `H2 sequence diverges` 2。`disagree on the rule body`、`declares itself`、`declares a pointer as the rule body`、`declares an unknown rule body` 均 **0**（只出现在 `tests/` 的变异用例里，属构造性，不是现状）。

**云臂那条的归属必须写清**：cloud 剩的 1 条、desktop 的 8 条里 1 条、都是 `H2 sequence diverges`——**跨仓相等判据**，因为 agent 与 desktop 还没有 `## 本仓规则` 节（位置 6 不同）。cloud 自身文件**零缺陷**。⇒ 这三条只能由 T-06／T-07 消，**T-09 必须在那之后重测**。

必须显式说明：CHG-20260925-063 的教训是「意料外的红会训练读者忽略这个门禁」，**已文档化的红同样会**（`conventions §10` 成文）。故本节的读数是**带收口计划的中间态**，不是「已知红项」：**T-09 不得早于 T-07**；本 CHG 不得在红的状态下归档。**其余五个门禁此时仍全绿**（本次改动未触及它们）。

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
| AC-11 阳性对照 | 同一扫描对未改动的 `HEAD:AGENT-INDEX.md` 命中 **1**（本文件命中 0） |
| 指针链接 | 两个指针各 3 个链接全部 resolve |
| cloud `git status --porcelain` | 仅 4 个 `M` ＋ 既存 `?? dump.rdb` |

**两条如实登记的不足**：①AC-09 的判据**不是门禁**（全仓无脚本读 infra 列表，`change.md` §14 第 11 项）；②cloud 剩余的 1 条跨仓 ERROR 本 Task 无法消（§1 归属说明）。

**一处自纠**：归属表初稿把「总行数」与「非空行数」两个分母混用，且 CLAUDE.md 的三类条数加总（99 行）写成了 112。改用 `HEAD` 版本重测分母后改正；**分母必须当场量**，不能沿用前一稿的读数。

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

**记录成本自纠**：§11 原有的「`change.md` ≤ 25 KB、单 Task evidence ≤ 3 KB」被 T-01～T-04 逐条突破（四篇 4559／4845／6314／6329 B；`change.md` 26477 B）。数字改为按实测定，并把界放在总量——见 `change.md` §11 与 §14 第 9 项。

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
