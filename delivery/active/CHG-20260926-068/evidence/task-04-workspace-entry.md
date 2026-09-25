# T-04 证据：workspace 侧两件（强化 `scripts/test-control.sh` ＋ 跨仓 `tests/test_bin_control_entry.py`）

- CHG: `CHG-20260926-068`
- Task: T-04（`change.md` §8）
- 日期: 2026-09-26

## 1. 强化 `scripts/test-control.sh`（判据 4 → 6 条）

原文件只有「usage 逐字／未知动词／`status` 端到端／无端口字面量」四条，**五处调用全写成 `bash "$CONTROL"`**
（`:22`／`:33`／`:35`／`:44`）——与 CHG-067 漏掉 desktop 执行位是**同一格错误**。本次：

- 四条 `bash "$CONTROL"` → **直接调用**（判据 1／2 的臂）；
- 补判据 1（存在／被跟踪／index `100755`／磁盘执行位）与判据 2（直接调用退 0），
  失败信息逐条自陈（`die`），不再依赖 `set -e` 的静默非零码；
- 只在 workspace 出现的第 5 个动词（`verify`）的 usage 逐字断言**原样保留**；
- 判据 6（无端口字面量）原样保留。

读数：`bash -n` 通过；全跑 `exit=0`，`PASS: bin/control.sh entry (tracked, index 100755, executable, directly invocable), usage, dispatch, status wiring, and no-port-literal`。

## 2. 新建 `tests/test_bin_control_entry.py`（跨仓，5 个用例）

被 `unittest discover -s tests` 自动拾取。对**四仓**各自的 `bin/control.sh` 断言判据 **1-4 与 6**：

| 用例 | 判据 |
| --- | --- |
| `test_entry_exists_and_is_tracked` | 存在 ＋ `ls-files --error-unmatch` |
| `test_index_mode_is_100755` | `git ls-files -s` 首字段 |
| `test_working_tree_mode_is_executable` | `os.access(…, os.X_OK)` |
| `test_direct_invocation_help_exits_zero` | **直接调用**（`subprocess`，路径作 argv[0]）`help` 退 0 |
| `test_unknown_verb_exits_two_with_usage_on_stderr` | 未知动词退 2、stdout 空、stderr 含 `Usage:` |

**不做的（写在模块 docstring 里）**：

- **不比对跨仓源码文本**：`AGENT-INDEX.md` §12／D-01 把跨仓源码字面量排除在门禁之外；
  且四仓本来就不同——workspace 分派**五个**动词（多一个 `verify`），另三仓四个，
  各自的 usage 行也各不相同。判据 5（动词逐行锚定）因此是**各仓自查**，不进跨仓这条。
- **兄弟仓缺席 → `skip` 并打印分母**（照 `verify_agent_entry.py:286` 的先例）：单仓检出不得因与入口无关的原因变红。
  缺席是 subTest **内部**的 skip，不是 fail。

## 3. 两处变异（`artifacts/t04-workspace-mutations.out`，各还原并复跑取绿）

| 变异 | 手法 | 读数 |
| --- | --- | --- |
| ① 兄弟仓 | `chmod -x wt-media-desktop/bin/control.sh` | 跨仓用例 **恰 3 failed，全部标 `repository='desktop'`**：磁盘执行位／直接调用／未知动词；**workspace 自己的 `scripts/test-control.sh` 仍 `exit=0`**（它只查本仓）；另三仓的格在同一轮内照常求值且全绿 |
| ② 本仓 | `chmod -x bin/control.sh` | 跨仓用例 **恰 3 failed，全部标 `repository='workspace'`**，且 `scripts/test-control.sh` **`exit=1`** 并打印 `FAIL: bin/control.sh is not executable on disk` |

①**就是 CHG-067 漏掉的那个缺陷类别**（本地能跑、新克隆跑不了），现由跨仓用例在 desktop 那一格独立抓住。

**缺席路径的对照**：把第 4 仓指向 `/nonexistent/wt-media-desktop` 后重跑，
`ran=5 skipped=5 failures=0 errors=0`，skip 文案逐字为
`desktop: no sibling checkout at /nonexistent/wt-media-desktop -- this arm covers 3/4 repositories`
⇒ 分母真的印出来了，「缺席」与「通过」在读数上分得开。

## 4. 一处自造缺陷（第一版，已修，如实记）

第一版的 `each_repository()` 写成**生成器**，`self.fail()` 在生成器里抛出会让 `GeneratorExit`
连带触发、**循环就此中断**——变异 ②（workspace 第一格）时 cloud／agent／desktop 从未被求值，
却被记成 `GeneratorExit` ERROR。改成「先取列表、再逐个 `with self.subTest(...)`」后，
每格独立求值：一格红不遮蔽其余格。这正是本 CHG 主题的反面（判据与缺陷错开一格）。
登记 `change.md` §14 第 5 项。

## 5. 六门禁 ＋ 套件（取在最后一次改动之后，`artifacts/t04-workspace-gate.out`）

六个静态门禁**全 `exit=0`**、`sync_skills.py check` `exit=0`（`skill outputs are up to date`）、
`unittest discover -s tests -q` **`Ran 106` / `OK`**（T-04 基线 `Ran 101`，差 **+5** = 新增的 5 个用例）。
分母（实测非回忆）：`tracked=974 / untracked=3`，并与 `e4e1587..HEAD` 的 `16 A / 2 M` 对账闭合（产物内分步列出）。

## 6. 如实记

- 跨仓用例覆盖的是**入口属性与分派失败路径**，**不覆盖**四动词的行为——那是 T-05 的 16 格真跑。
- 四条机检（desktop／cloud／agent／workspace）**都没有**"端口值班"之类的跨仓文本判据，
  与 §5 Explicitly Not Doing 一致。
- 变异②曾把 workspace 入口短暂置为不可执行；已 `chmod +x` 还原，`git ls-files -s` 复读 `100755`（见产物）。
