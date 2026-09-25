# T-03 证据：agent `tests/test_control_sh.py`

- CHG: `CHG-20260926-068`
- Task: T-03（`change.md` §8）
- 日期: 2026-09-26

## 1. 新建 `tests/test_control_sh.py`（unittest，7 个用例）

被 `scripts/test.sh:24` 的 `unittest discover -s tests` 自动拾取。判据与 desktop／cloud 同类，按 Python 的粒度拆成 7 个用例：

| 用例 | 判据 |
| --- | --- |
| `test_entry_exists` | 是常规文件 |
| `test_entry_is_tracked_by_git` | `git ls-files --error-unmatch bin/control.sh` 退 0 |
| `test_index_mode_is_100755` | `git ls-files -s` 首字段 = `100755` |
| `test_working_tree_mode_is_executable` | `os.access(…, os.X_OK)` |
| `test_direct_invocation_help_exits_zero` | **直接调用**（`subprocess`，路径作 argv[0]）`help` 退 0 |
| `test_help_lists_every_verb` | 四个动词各按 `^  <verb>\b` 多行锚定出现 |
| `test_unknown_verb_exits_two_with_usage_on_stderr` | 未知动词退 2、stdout 空、stderr 含 `Usage:` |

**两条刻意不做的**（写在模块 docstring 里）：

- **不断言非可执行入口的字面退出码**——那个读数随调用方 shell 选项变化（实测 126／1），
  而 Python 的 `subprocess` 在**任何**退出码之前就抛 `PermissionError`。故断言属性（退 0），
  并把 `OSError` 原文报出来（`EntryNotInvocable` → `self.fail`，不是 `error`）。
- **git 缺席时 `fail` 不 `skip`**：index 模式是工作树检查**看不见**的那一半，静默跳过会让套件在只查一半的情况下报绿。

## 2. 两处变异（`artifacts/t03-agent-mutations.out`，各还原并复跑取绿）

| 变异 | 手法 | 读数 |
| --- | --- | --- |
| ① 磁盘执行位 | `chmod -x bin/control.sh` | **3 passed／4 failed**（磁盘执行位、直接调用、help 列动词、未知动词四格） |
| ② 只关 index | `git update-index --chmod=-x`（磁盘仍 `-rwxr-xr-x`） | **6 passed／恰 1 failed = `test_index_mode_is_100755`** |

⇒ 与 desktop／cloud 的分布**同形**：磁盘变异连带 4 项红，index 变异只红一项
（`-rwxr-xr-x` 复读 + `git ls-files -s` 复读 `100755` 各留档）。
**如实记**：agent 入口本来就带执行位，此处没有「真实缺陷先红」可报，判别力的证据只有这两处变异。

## 3. `scripts/test.sh` 全跑（取在最后一次改动之后，`artifacts/t03-agent-test-sh.out`）

`exit=0`，**`Ran 416 tests` / `OK`**。T-03 前的基线是 **`Ran 409`**（CHG-067 的收尾读数），
差 **+7** = 本文件新增的 7 个用例——分母对得上，没有别的用例被顺带改动。

**`.local/` 污染护栏**（`scripts/test.sh:15-37`）：本检出**有** `.local/`，故护栏的 BEFORE 快照非空、
处于生效状态；本次运行**没有**出现 `ERROR: the test suite created paths`，即套件未在检出内新建路径。
对照：该字符串在 `scripts/test.sh` 里能命中 **1** 处（needle 是真的，缺席不是空转）。

## 4. 如实记

- 本检查断言**入口属性**，不覆盖四动词的**行为**——那是 T-05 的 16 格真跑。
- agent 仓里 ` M AGENT-INDEX.md` 是**先于本 CHG 存在的未提交改动**，全程未触碰、未暂存（T-00 §3 已登记）。
- `tests/__pycache__/` 被忽略（`git check-ignore -q` 退出 0），未进索引。
- 本仓的 `scripts/test.sh` 日志**不**被任何门禁按正则解析（该约束只对 cloud 成立，见 §14 第 2 项）。
