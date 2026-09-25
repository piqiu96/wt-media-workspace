# Evidence: T-03 `verify_product_master_alignment.py` 转绿

- CHG: `CHG-20260925-063`
- Task: `T-03`
- Date: 2026-09-25
- Type: command
- Status: PASS
- 未完成项：`tests/test_verify_product_master_alignment.py` 仍 **1 条红**，由 **T-04** 处理（见本文件末节）。

## Purpose

消除 `verify_product_master_alignment.py` 的 8 条红项，并按 D-04 把「已关闭里程碑」的判据
**降到状态词那一层**，同时把两处空转变成**会报错的结构检查**。改前 8 红，改后 `exit=0`。

改前读数（`artifacts/t03-baseline-verify_product_master_alignment.out`）：

```
M2 status expected 'IN_PROGRESS', got 'DONE'
M3 status expected 'NOT_STARTED', got 'DONE'
M2 capability missing '按五条业务闭环顺序补齐'
M3 candidate missing 'source_content' / 'Scheduler' / '正式任务 Schema' / '真实抖音接口'
M10 capability missing 'FFmpeg/FFprobe 分发'
exit=1
```

## 根因：判据编码的是「决策之前」的世界

八条红不是同一类，逐条落到具体决策：

| # | 红项 | 根因（可核对的具体记录） |
|---|---|---|
| 1 | M2 状态期望 `IN_PROGRESS` | M2 于 2026-09-14 用户签收（`MASTER:154`） |
| 2 | M3 状态期望 `NOT_STARTED` | M3 于 2026-09-23 用户签收（`MASTER` M3 段、`milestones/M3-content-discovery-v2.md:3`） |
| 3 | M2 缺 `按五条业务闭环顺序补齐` | **该 needle 编码的是 M2-D 暂缓之前的那版计划**（当时 A～E 五条全在范围内）。2026-09-12「M2-D 整体暂缓」（`milestones/M2-account-runtime.md:5`）是一份**已记录的决策**，M2 因此只走 A/B/C/E 四条，M2 段第 287 行即写「按 M2-A→M2-B→M2-C→M2-E **四条**业务闭环顺序补齐」。**改的是 needle 跟随决策，不是跟随文本。** |
| 4–7 | M3 「候选块」4 条 needle 全缺 | M3 关闭时**撤掉了候选块**，`candidate_block()` 返回 `""` ⇒ 4 条 needle 恒缺。 |
| 8 | M10 缺 `FFmpeg/FFprobe 分发` | 「分发」是 **ADR-0015** 时代的口径（Agent 是 FFmpeg 的唯一入口）。**ADR-0017 第 1、10 条**已取代它：视频合成统一由 Cloud 执行，**FFmpeg 属于 Cloud 部署组件**（`docs/decisions/0017-…:28,40`，并明列「Local Agent 原有/规划中的合成 Executor 与 FFmpeg 打包工作不再复用」）。M10-C4 现写「Cloud Compose Worker 的 FFmpeg/FFprobe **镜像**」。**改的是 needle 跟随现行决策。** |

## 改动清单

| # | 位置 | 改动 | 依据 |
|---|---|---|---|
| 1 | `expected_statuses` | M2/M3 → `DONE`，未开始范围改为 `range(4, 11)` | 上表 1、2 |
| 2 | 状态循环后**新增** | 非 `DONE` 里程碑**必须**有非空候选块，否则报错 | 消除空转（下节） |
| 3 | 新增 `forbid_all()` | 禁用对象检查**只在非空块上运行** | 同上 |
| 4 | M2 段 | `candidate_block(...) or sections[2]` → 显式 `m2_record = sections[2]`；needle `五条`→`四条` | 上表 3 |
| 5 | M3 段 | **删除**候选块禁用检查（2 个 needle）+ 4 条 `require_all` | 见下「删掉的是零覆盖」 |
| 6 | M10 段 | needle `FFmpeg/FFprobe 分发` → `FFmpeg/FFprobe 镜像` | 上表 8 |

### 删掉的是零覆盖，不是有效覆盖

M3 关闭后候选块为空，两组断言各自坏在不同的方向：

- **4 条 `require_all("")`** ⇒ 恒缺 ⇒ **每次运行都必定报 4 条红**。这不是「静默空转」而是
  **恒定的噪音红灯**——而恒定红灯正是训练读者忽略这个门禁的东西（`change.md` §4.5）。
- **禁用对象循环 `forbidden in ""`** ⇒ **恒假** ⇒ **静默通过**。它今天无法发现任何事；
  即使把块放回来并在里面写上 `crawl_result`，也要等块非空之后才有判别力。

两者覆盖都为零，故删除不损失覆盖。M3 现在由**状态词**加**通用验收 needle** 覆盖，
这正是 D-04 对已关闭里程碑的规定。

## Method

```bash
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_product_master_alignment.py
python3 -B -X pycache_prefix=/tmp/pyc-none -m unittest tests.test_verify_product_master_alignment -q
python3 -B -X pycache_prefix=/tmp/pyc-none delivery/active/CHG-20260925-063/evidence/artifacts/t03-mutation-control.py .
```

原始输出：`artifacts/t03-{baseline,postfix}-verify_product_master_alignment.out`、
`artifacts/t03-diff-verify_product_master_alignment.patch`、`artifacts/t03-mutation-control.{py,out}`、
`artifacts/t03-ast-scope-checks.out`、`artifacts/t03-false-pass-proof.out`、
`artifacts/t03-gate-readings.out`。

改后：`Product and Master Plan alignment verification ok` / `exit=0`。
六个校验脚本全部 `exit=0`（`artifacts/t03-gate-readings.out`）。

## Mutation control（AC-08）

`artifacts/t03-mutation-control.py` 在**内存里**逐条变异真实 Master Plan 文本，
要求每条变异产出**恰好**其预期错误集。**两条对照**先立：

```
control: empty text -> milestone set mismatch      # 证明函数读的是传入文本，不是磁盘文件
control: unmutated real text -> 0 errors           # 证明基线本身是干净的
```

| 变异 | 预期读数 | 结果 |
|---|---|---|
| M2 状态 `DONE`→`IN_PROGRESS` | 状态错 + **缺候选块错**（两处，见下） | ok |
| M2 `四条`→`五条` | `M2 capability missing '四条业务闭环顺序补齐'` | ok |
| M3 状态 `DONE`→`NOT_STARTED`（依旧无块） | 状态错 + 缺块错；**且不再出现任何 `M3 candidate` 幽灵错** | ok |
| M8 块注入 `interaction_batch` | 1 条禁用对象错（证明非空块上仍然会报） | ok |
| M9 块清空（仍 `NOT_STARTED`） | 1 条缺块错 + 3 条 `M9 candidate missing`，**禁用检查贡献 0 条** | ok |
| M10 `镜像`→`分发` | `M10 capability missing 'FFmpeg/FFprobe 镜像'` | ok |
| M0 门禁措辞改坏（本 CHG 未动它） | `M0 gate missing …`（证明旧判据仍有判别力） | ok |

**一处预期写错、由实测纠正，登记**：M2 状态变异我最初只预期 1 条错。实跑得 2 条——
把已关闭的里程碑改回未关闭，**同时**触发新增的缺块检查。这不是脚本的 bug：
「重开一个里程碑就必须重新给出候选 CHG 块」正是该检查的意图。**是预期写窄了，已改预期并把该交互记在此处。**

### 空转消除的方向（M9 清空那臂值得单看）

块为空时，三族检查各自的表现是**不对称**的，这正是新增结构检查的理由：

```
require_all      -> 3 条噪音错（每条 needle 各报一次「missing」）
forbidden 循环   -> 0 条            （`needle in ""` 恒假，静默通过）
新增结构检查      -> 1 条，且只有它指出了真正的问题
```

### AC-09：被删 needle 逐条经 AST 证明不再处于断言集合内

`artifacts/t03-ast-scope-checks.out` 用 **AST** 枚举全部 `require_all` / `forbid_all` 调用
的 `(label, needle)` 集合：

```
removed M3 needles still asserted: []   -> 0/6
M3-labelled assertion groups remaining: none
```

**为什么必须用 AST 而不是 grep**：被删的 needle 仍出现在**我写的删除说明注释里**，
grep 分不清断言与散文——T-02 已经踩过一次同一个坑（当时 3 个被删 needle 因注释显示 `hits=1`）。

## 一处新查明的机制：T-04 那条假通过测试，**绿的原因也是空转**

`artifacts/t03-false-pass-proof.out` 用 `HEAD` 版脚本对**未变异**的 Master Plan 文本求值：

```
M3 candidate missing 'source_content'
M3 candidate missing 'Scheduler'
M3 candidate missing '正式任务 Schema'
M3 candidate missing '真实抖音接口'
-> 'M3 candidate' errors present BEFORE any mutation: 4
```

而该测试的断言是 `any("M3 candidate" in error for error in errors)`。
**未变异时该谓词就已经为真**，所以满足它的从来不是那次变异。

先前只查明「变异字符串在 MASTER 中不存在 ⇒ `str.replace` 是空操作」，
**现在补齐了另一半**：断言被**恒定的 `M3 candidate` 噪音**满足了。两个错互相掩盖——
空操作让用例看起来在测禁用对象机制，恒红让断言看起来被变异触发。
**故 T-04 不能只把变异字符串换成存在的那个**：只要断言仍匹配 `M3 candidate` 这个标签，
它在别的红项出现时又会为真。T-04 必须同时改**变异目标**与**断言的判定方式**
（改到 M8/M9 这类**非空块**上，并断言**错误条数与该条消息**，而不是「有某标签」）。

## 与 §14 遗留的关系

- 本任务关闭 CHG-062 遗留第 3 项中 `verify_product_master_alignment.py` 的部分。
- 遗留第 7 项（`verify_product_master_alignment.py` 要求 active CHG 的 §7 为字面 `None.`、
  不接受「非阻塞」档位）**本任务不动**——它属形状限制，与 D-04 的分层无关。
- 本任务**没有**为 M3 补新的内容断言。若日后要恢复对 M3 的内容覆盖，应在
  `milestones/M3-content-discovery-v2.md`（M3 的真实闭环记录）那一层做，而不是回到
  Master Plan 的候选块——**候选块属于未关闭的里程碑**，这条约定已写进脚本注释。
