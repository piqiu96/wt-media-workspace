# Evidence: T-06 收尾

- CHG: `CHG-20260925-063`
- Task: `T-06`
- Date: 2026-09-25
- Type: close
- Status: PASS
- 提交：见本文件末「提交边界」

## Purpose

关闭闸门：在**本 CHG 最后一次改动之后**重测全套判据、逐条给 AC 终态、签字 DONE Gate、
`active/` → `completed/` 归档、同步 `LEDGER.md` 与执行快照，并做**两遍**归档后失效指针扫描。

## 1. 关闭读数（最后一次改动之后）

时间 2026-09-25 18:43:12 CST，原始输出 `artifacts/t06-gate-readings.out`。

| 判据 | 读数 |
|---|---|
| `verify_delivery_governance.py` | `exit=0` — `Active CHG: none` |
| `verify_agent_entry.py` | `exit=0` — `0 warning(s)`，快照 1668 字符（预算 8000） |
| `verify_skills.py` | `exit=0` — `verified 10 skill source files` |
| `verify_m0_config.py` | `exit=0` |
| `verify_product_master_alignment.py` | `exit=0` |
| `verify_m2_acceptance.py` | `exit=0`（附注：真实 MySQL 与 BitBrowser 证据须另行记录，与本 CHG 无关） |
| `python3 -m unittest discover -s tests -q` | **`Ran 75 tests` / `OK`**（`exit=0`） |
| 执行快照 | **1668 字符**（无活动 CHG 态） |

**这组读数是关闭值**，不是沿用 T-04/T-05 的读数：它取自归档、`LEDGER` 重写、快照重生成
与 §10 该行更正**之后**。按本 CHG 自己写入 `conventions §10` 的那条硬约束——「报通过 / 0 命中前
必须先证明检查能失败」——本节只报读数；每条判据的**判别力**由各 Task 的变异对照留证，
不在此重复（本 CHG 未改任何判据）。

## 2. 中间态实测：`Status: DONE` 但记录仍在 `active/`

`artifacts/t06-intermediate-done-status.out`。此态**只能靠归档消除**，故先量后归档：

```
verify_delivery_governance.py           exit=0
verify_agent_entry.py                   exit=0
verify_skills.py                        exit=0
verify_m0_config.py                     exit=0
verify_product_master_alignment.py      exit=1
verify_m2_acceptance.py                 exit=0

ERROR: active CHG status must be IN_PROGRESS, IMPLEMENTING or VERIFYING, got 'DONE'
ERROR: Ledger is not aligned with active CHG CHG-20260925-063 status 'DONE'
```

**两条，不是一条。** CHG-062 归档条目登记的是「多出 1 项」。差异成因已查明：除
`active CHG status` 外，本脚本**另有一条** `LEDGER` ↔ active CHG 状态一致性检查，
归档前 `LEDGER.md` 表行仍写 `IMPLEMENTING` 故它同时报错。

**未复现 062 当时的态**（那需要把 062 恢复成中间态），故本文件只登记本轮读数、
不断言 062 记错。处置：按实测登记，不猜。

## 3. AC-12 复测：判据的基线部分有缺口（如实登记）

原始输出 `artifacts/t06-ac12-runtime-worktrees.out`。

| 仓 | `status --porcelain` | 已跟踪文件改动数（`-uno`） |
|---|---|---|
| `wt-media-cloud` | 1 条：`?? dump.rdb` | **0** |
| `wt-media-agent` | 0 条 | **0** |
| `wt-media-desktop` | 0 条 | **0** |

唯一偏离项的归属（以实测取数，不靠印象）：

```
dump.rdb  size=88  mtime=2026-09-24 17:19:16   （本 CHG 于 2026-09-25 立项）
```

- mtime **早于本 CHG 一天**，且是**未跟踪**的 88 字节 Redis 空转储；
- CHG-062 归档条目已登记过它（「cloud `dump.rdb` 的他人在途改动（mtime 全部早于本会话）」）。

**判据缺口如实登记**：AC-12 写的是「与**开工前**一致」，而**开工时没有记录三仓工作区基线**
（本 CHG 自己的记录缺口，不是本轮引入）。因此这一次是**事后推证**（mtime + 既往前例），
不是基线对比。可断言的是「本 CHG 未写三仓」——这一点由 `-uno` 逐仓为 0 直接支持；
「与开工前一致」这一半证据强度较弱，AC 行已按此改写。

## 4. DONE Gate 与 AC 终态

§13 九项逐项签字；§9 Repository Checklist 三节勾选。AC-01…AC-11、AC-13、AC-14 **全 PASS**；
**AC-12 PASS 但判据基线有缺口**（见第 3 节）。

其中一处判据被主动**收窄**并留痕：AC-12 原表述无法由现有证据完全支撑，故不写成
「与开工前一致 ✅」，而是在 AC 行写明「成立的是哪一半、靠什么推证」。

## 5. 归档与快照

```bash
git mv delivery/active/CHG-20260925-063 delivery/completed/CHG-20260925-063
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/prepare_ai_workspace.py --no-active
```

- `delivery/active/` 归档后只剩 `.gitkeep`；旧路径不再存在（已实测 `ls` 报 No such file）。
- 快照 `Active CHG: none` / `Status: NONE`，**1668 字符**。**注意这与 T-05 记的 1919 不是矛盾**：
  快照体积随「有无活动 CHG」变化，两个数各对应一个态——见第 6 节。
- `LEDGER.md`：表行由 CHG-063 表行改为占位行（沿用 CHG-062 归档时的既有形态），
  并在历史叙述段顶部**前置**本 CHG 的归档条目。

## 6. 收尾时发现的一处文档缺陷（T-05 的漏网，本任务修正）

T-05 把 `conventions §10` 快照行由 `1923` 更正为「实测 **1919**」。收尾时实测**无活动 CHG 态**
为 **1668**，两者都对——**该数字随状态变化，写单一值就是按构造必然过期的读数**，
正是 §10 这一轮要清除的那类东西。

处置：把该行改为**两态并列**（`1919（有活动 CHG）/ 1668（无活动 CHG）`）。**登记为 T-05 的漏网**，
不掩盖——T-05 当时确实量了，只是没意识到它有两个态。这是本 CHG 内同类错的**第二次**
（第一次是 T-05 的 27 条误判 MISS）：**判据选错粒度时，输出看起来同样「像量过的」**。

## 7. 归档后失效指针扫描（两遍，各自带阳性对照）

### 第一遍：字符串扫描

`git grep -n -- 'active/CHG-20260925-063'`，分母 = 本仓全部跟踪文件。

**修前 4 处命中**，逐条按「路径判修、叙述判留」分类：

| 命中 | 形态 | 处置 |
|---|---|---|
| `checkpoint.md:21` | 过去时叙述（「T-01：建 `delivery/active/CHG-.../`」） | **保留** |
| `artifacts/t01-activate.out:14` | 原始输出（脚本当时打印的绝对路径） | **保留**——改写原始输出即伪造证据 |
| `evidence/task-03:66` | **可重放命令** | **修为 `completed/`** |
| `evidence/task-04:60` | **可重放命令** | **修为 `completed/`** |

修后复扫**剩 2 处**，均为应保留的叙述。

**阳性对照**（证明扫描不是空转）：同一模式对已归档的 062 旧路径命中 **8 处**；
`git grep -c 'delivery/active/'` 在 70 个文件中有命中。**对照也暴露了一件事**：
062 归档时它的 3 处命中**全部**是叙述，没有可重放命令，故当时的扫描确实只需保留——
本轮出现 2 处命令是**新情况**，不是 062 漏了。

### 第二遍：相对引用 resolve

**首版把目标集选错，如实登记**：我先按「归档目录下的文件」跑，得到
「10 个文件、**0 条** markdown 链接、0 条失败」——**0 条链接意味着这次 resolve 什么都没证明**，
是典型的分母为零式空转（本 CHG 反复处理的正是这个形状）。

改为按**引用集**跑：全仓提到本 CHG 的跟踪文件，去掉本 CHG 目录自身，得 **7 个**：

```
README.md、delivery/LEDGER.md、docs/engineering/specs/agent-workspace-conventions.md、
scripts/verify_m0_config.py、scripts/verify_m2_acceptance.py、
scripts/verify_product_master_alignment.py、tests/test_verify_product_master_alignment.py
```

| 形态 | 条数 | 解析结果 |
|---|---|---|
| markdown 链接（7 个文件中合计） | 17 | 其中**指向本 CHG 的 1 条**：`LEDGER.md:11` → `completed/CHG-20260925-063/change.md`，**resolve OK** |
| 代码文件中的裸标识（`# Removed by CHG-20260925-063` 等 9 处） | 9 | 非路径，不解析；已单独 `git grep 'active/CHG' -- scripts/ tests/` 确认为**空** |

**阳性对照**：同一解析器对 `completed/CHG-20260925-063/nope.md` 报 `False`、
对 `completed/CHG-20260925-063/change.md` 报 `True` ⇒ 它能报出缺失，也能报出命中。

**覆盖面如实枚举**：本遍只覆盖「本 CHG 目录之外的引用者」共 7 个文件；归档目录**内部**的
相对引用（`artifacts/...` 形态）不在本遍范围内——它们在 `git mv` 整目录搬迁下**基点同移**，
本来就不断，若把它们混进来会虚增分母。

## 8. 提交边界

T-06 的改动与暂存范围：

| 文件 | 是否本 CHG 产物 |
|---|---|
| `delivery/active/CHG-20260925-063/** → delivery/completed/CHG-20260925-063/**` | 是（`git mv`） |
| `delivery/LEDGER.md` | 是 |
| `.ai/CURRENT_CONTEXT.md` | 是（生成物） |
| `docs/engineering/specs/agent-workspace-conventions.md` §10 该行 | 是（第 6 节） |
| 同上文件第 33 行（`/doctor` 编辑） | **否——上一任务的工作区改动，不由本 CHG 提交** |
| `CLAUDE.md`（`/doctor` 瘦身） | **否——同上** |

`conventions §10` 该行与第 33 行同文件，处置沿用 T-05 已登记的做法：**临时把第 33 行还原为
HEAD 文本 → 确认 `git diff` 只剩本任务改动 → 提交 → 改回**，并核对 HEAD 与该模式的工作区计数。
两个 `/doctor` 文件在整个 CHG 内**始终未进入任何提交**（§13 的 out-of-scope 一项）。

### 8.1 部分暂存的实际经过（含一次失败，如实登记）

**首版还原脚本写错了**，把文件改成了 209 行 + 208 行填充的错位结果：**第 136/137 行出现两条
`verify_agent_entry.py`**，且末尾换行丢失（`\ No newline at end of file`）。成因是我按「逐行与 HEAD
顺序对齐」重建，而我的新行占了一个位置却没有对应消费 HEAD 的同位置行，于是后续整体错位一行。

处置：从**提交前留的完整工作副本**还原，改用**精确字符串替换**（取 HEAD 全文，只把那一行 `replace` 成新行），
并加两条断言（HEAD 中旧行恰好 1 次、新行 0 次）。**这条断言是这一步的关键**——前一次失败正是
「替换目标没对上却照样输出得像成功」。

**没有用 `git stash` / `git checkout --` 处理**，因为工作副本里含一处我无权提交的 `/doctor` 编辑，
任何整文件级的回滚都会把它一起丢掉。

### 8.2 最后一次改动之后的复测

撤下 `git diff` 那一层后，**在还原了 `/doctor` 行的工作区上再跑一遍**：六个门禁仍全 `exit=0`、
`Ran 75 tests / OK`。⇒ 第 1 节的关闭读数在**本 CHG 全部改动结束之后**依然成立，两个 `/doctor`
工作区编辑不影响任何判据。

### 8.3 `/doctor` 行的归属核对（两个模式互相验证）

| 模式 | HEAD 计数 | 工作区计数 |
|---|---|---|
| `权威源与最小硬约束`（T-05 记录用的模式） | **2**（`:11`、`:32`） | **3**（多出 `:33`） |
| `项目概览、权威源与最小硬约束`（本任务用的更特异模式） | **0** | **1**（即 `:33`） |

两个模式指向同一结论：**该行只存在于工作区，不在任何提交里**。**如实登记一处口径差**：
本任务第一次核对时误用了后一个（更特异的）模式，首次读数 `0 / 1` 与 T-05 记录的 `2 / 3` 不同，
看着像「文件被改回去了」；改用 T-05 的同一模式后复现 `2 / 3`。**不是不一致，是两次用的模式不同**
——这本身就是「分母/模式不同，读数就不同」的又一个实例。
