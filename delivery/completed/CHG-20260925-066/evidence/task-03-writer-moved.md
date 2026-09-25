# T-03 — 修掉归档区唯一的写入者

- CHG: `CHG-20260925-066`
- Task: T-03 修掉唯一的写入者
- 日期: 2026-09-25
- 前置: T-02 已提交（`05c2045`）

## 1. 判定：读取面**不**必须读归档，故读写两侧一并移出

`change.md` §5 的措辞是条件式的：「若读取面必须继续读归档，则只读并以常量声明」。逐条核验后该条件**不成立**：

下表行号是**改动前**的编号（改动后各点整体上移约 5 行，且 P10 段另有增补）。

| 原读点 | 读的是什么 | 实际归属 |
|---|---|---|
| `:1596` `raw/p10-cloud-test.log` | 本轮 shell 产出的日志 | **本轮**产物 |
| `:1615` `raw/p10-m2-regression.log` | 同上 | **本轮**产物 |
| `:1624` `raw/p10-m2-corrected.log` | 同上 | **本轮**产物 |
| `:1656` `raw/p10-flowview-grep.txt` | 同上 | **本轮**产物 |
| `:1645` `screenshots/*.png` | 本轮视觉走查截图 | **本轮**产物 |
| `:1742-1745` `run-manifest.json`／`state.json` | 本脚本自己此前写的 | **本轮**产物 |

⇒ 六处读点全部读的是「本轮产物」，没有一处需要 2026-09-23 那次运行的东西。旧版把产物写在归档包里，
所以「本轮产物」与「归档内容」是同一个目录——这是读写同指一处的**后果**，不是需求。

**结论**：`verify_m3_acceptance.py` 现在**既不读也不写** `delivery/completed/`（唯一残留是对该路径的三行
**注释**，见 §4；注释不是字符串常量，不构成可达路径，属「叙述判留」）。

## 2. 改动

写入面从 `EVIDENCE`（＝归档包）改指 `RUN_DIR = WS_ROOT/.cache/m3-acceptance`
（本仓 `.gitignore` 第 1 行 `.cache/`，故一次运行**不可能**脏化工作树）。

| 原写点 | 现写点 |
|---|---|
| `:304`／`:310`／`:1739` `EVIDENCE.mkdir` | `RUN_DIR.mkdir` |
| `:306` `state.json`／`:311` `run-manifest.json` | `RUN_DIR` 下同名 |
| `:285-289` `raw_dump`（`RAW_DIR.mkdir` ＋ 写入 ＋ 返回相对路径） | `RAW_DIR = RUN_DIR/raw`；返回相对 `RUN_DIR` |
| `:376` **`proc-<component>.log`**（归档区最大文件的产出路径） | `RUN_DIR` 下同名 |
| `:522-523` 基线快照 `02-baseline-snapshot*.md` | `RUN_DIR` 下同名 |
| `:1059` `proc-discovery-scheduler.log`（含 `unlink`） | `RUN_DIR` 下同名 |

附带两处：

- **`:406` `own_artifacts` 去掉两个死项**。原列表含 `scripts/m3-acceptance.sh`——该文件**从未存在过**
  （`git log --all -- scripts/m3-acceptance.sh` 空；阳性对照：对已知被删的
  `delivery/active/CHG-20260714-001/change.md` 跑同一命令返回 `63092e8`）。这一空悬标记**早已登记**在
  `completed/CHG-20260923-055/evidence/20260923-closeout-and-m3-signoff.md:91`（「不删，以免把路径修正扩大成
  验收脚本逻辑重写」）。T-03 正是在重写这一处常量，故一并删除，并同时去掉已不可能再匹配的归档目录项。
  改后 `own_artifacts = ("scripts/verify_m3_acceptance.py",)`：产物全在 `.cache/` 下，工作树里唯一可能
  出现的只有本脚本自身。**实测**：G0.1 在「2 个 dirty 条目」的树上报 `非本轮产物=1`——恰好滤掉了脚本那一条。
- **P10 的输入缺失时记 `BLOCKED` 而不是回退读归档**。P10 是**转录**阶段：它自己不跑测试，只把 shell 产出的
  `raw/*.log` 与截图转成清单行（旧版 header 记录的执行命令是 `scripts/test.sh`、`npm test --prefix web`、
  `scripts/m2b-local-acceptance.sh` 与一个无头 Chrome 截图代理——**逐个手敲，无驱动脚本**）。
  旧版因此「重跑 P10」并不重跑任何东西，只会把上一次的结论重新盖一个**今天的日期**。新增 `10.0` 前置行，
  任一输入缺失即整段 `BLOCKED` 并 `return`。

## 3. 判据一：写向归档 ＝ 0 处（三层，逐层标覆盖与分母）

原始输出 `artifacts/t03-write-surface.out`（层 3）与本节内联读数（层 1、2）。

### 层 1（**完整**判据）：文件内不存在归档路径字面量

> **0 / 1810** 个字符串常量含 `completed`。

- 分母 ＝ 该文件全部 `ast.Constant` 字符串。
- **阳性对照**：同一判据跑修改前的版本（基线提交 `05c2045`）＝ **2 / 1798**，两处即 `EVIDENCE` 与
  `own_artifacts` 的路径串。⇒ 该判据有判别力，不是空转。
- 为什么这一层是**完整**的：进入归档的路径只能由 (a) 归档字面量拼出，或 (b) 从外部传入。本脚本的
  外部路径输入只有 `WT_MEDIA_CLOUD_ROOT`，且它指向 Cloud **源**仓（见层 2 的残余）。

### 层 2（**枚举**判据）：19 个写操作点逐个归属

    写操作点总数（分母）: 19
    写向归档: 0 处

逐个核验全部 19 处：3 处是 `"rb"` 模式打开或 `urllib` 请求（`:93`／`:102`／`:186`／`:445`，**读**，
不构成写）；其余每一处的接收者都是五个产物常量之一，而 `RUN_DIR`／`RAW_DIR`／`STATE_FILE`／
`MANIFEST_FILE` 都在 `WS_ROOT/.cache/m3-acceptance` 下、`COOKIE_DIR` 在 Cloud 仓 `.cache/` 下。
实测 `str(RUN_DIR).startswith(str(WS_ROOT/"delivery/completed"))` ＝ `False`。

**残余（如实登记）**：`COOKIE_DIR = CLOUD_ROOT/.cache/m3-acc` 是唯一的间接路径——把
`WT_MEDIA_CLOUD_ROOT` 设成归档路径就能让它落进归档。这需要刻意设置一个把整个 Cloud 交互都指错的环境变量，
不属可自然发生的路径，**不修**。

### 层 3（**运行**判据）：跑前跑后三读数 ＋ 阳性对照

`artifacts/t03-write-surface.out`。臂 A ＝ 现树 ＋ 新版脚本；臂 B ＝ 影子树 ＋ 修改前的脚本（基线 `05c2045`）。

| 读数 | 臂 A（新版） | 臂 B（旧版，阳性对照） |
|---|---|---|
| 归档文件数 | `699` → `699` | `0` → **`2`** |
| 归档字节数 | `10740897` → `10740897` | （新增 2 个 2 B 文件） |
| `find -newer` 标记 | **`0` 个** | **`2` 个**（`state.json`、`run-manifest.json`） |
| 路径/字节/mtime 指纹 | 前后**相同** | 前后**不同** |
| 本轮产物落点 | `.cache/m3-acceptance/`（3 文件） | `.cache/` **不存在**——全部写进归档 |

臂 B 是关键：它同时证明①**指纹与 `find -newer` 有判别力**（对真实写入报了「变了」），②**缺陷真实存在过**
（旧版一次 `--phase p10` 就把两个文件写进已归档的 CHG-052 包里）。臂 B 的 `exit=1` 也是 CHG-055 登记过的
后果——旧版读不到旧日志即抛异常，而 `finally` 照旧往归档写。

**运行覆盖的边界（不主张更多）**：9 个写点里，运行时实际走到的是 5 个（`raw_dump`、`save_state`、
`flush_manifest`、`main` 的两处 `mkdir`）；未走到的是 `go_run` 的 `proc-*.log`、基线快照、scheduler 日志、
`:1068` 的 `unlink`——它们需要真跑 Cloud 二进制或连库，**本轮不跑**（会在库里落真数据）。这 4 处由层 1＋层 2
覆盖：它们的路径表达式同样只由那五个常量派生。

## 4. 判据二：AST 判据该按字面量而不是按变量名（T-04 的前置结论）

本 Task 先写了一个「按接收者变量名找写操作」的判据，**它错了两次**，两次都被阳性对照抓住，如实登记：

1. 名字式判据对修改前的版本只报 **3 处**（三个 `EVIDENCE.mkdir`），漏掉 `STATE_FILE`／`MANIFEST_FILE`／
   基线快照 `target` 三处——它们经 `EVIDENCE / "state.json"` 这种**一跳间接**赋值，名字里不含归档字面量。
   ⇒ 名字式判据的命中数**低于**真值，且低得看不出来。
2. 改成「一跳以上的定点传播」后，污染集爆到约 180 个名字（`path`、`name`、`value`、`log`…），因为赋值、
   循环目标与函数参数共用一个名字空间，污染跨函数泄漏；命中数又**高于**真值。⇒ 名字式判据两头都不准。

**结论（供 T-04 实现 `check_archive_readonly` 用）**：判据要锚在**字符串字面量**上（`completed/` 前缀），
再看它是否流向写操作，**不锚在接收者变量名上**。另有一条 T-04 必须处理的负例：修改前的版本里，
`own_artifacts` 那个归档串是**过滤器**不是写目标——只判「字面量出现」会把这类也报出来，故判据必须
真的做「流向写操作」这一步。

## 5. 本 Task 顺带实测的两处（登记 §14）

1. **归档区 15.6% 的字节不在版本控制内。** 归档共 699 文件 / 10,739,451 B，其中 **687 文件 /
   9,062,732 B** 已跟踪，**12 文件 / 1,676,719 B（15.6%）** 被 `.gitignore` 的 `*.log` 与 `__pycache__/`
   两条规则排除——含归档区**最大的单个文件** `proc-discovery-worker.log`（1,587,838 B，正是旧版 `go_run`
   的产出）。对这 12 个文件，「不回改」**不由 git 保证**：被改写时 `git status` 与 `git diff` 都是空的。
   已写入 `delivery/completed/README.md` 的「已知例外」（T-03 增补）。
   - 阳性对照：`git ls-files --others --ignored --exclude-standard delivery/completed` 列出 12 项；
     `git ls-files delivery/completed` 计数 687；两者之和恰为文件系统实测的 699。三个分母互相闭合。
2. **归档字节读数本身会因写记录而变。** T-02 收尾读数是 `10,739,451 B`，本节量得 `10,740,897 B`，
   差 `1,446 B` ＝ T-03 对 `delivery/completed/README.md` 那一段的增补。这不是漂移，是
   「**记录行为本身就是被记录对象的一部分**」（CHG-065 §14 第 20 项、本 CHG §14 第 4 项的同源形态）
   再一次出现——且这次被记录的对象**就是归档目录自身的体量**。

## 6. 本 Task 变更文件

修改：`scripts/verify_m3_acceptance.py`、`delivery/completed/README.md`。
新建：本记录、`artifacts/t03-write-surface.out`。
**未删任何文件**（删除在 T-05）；未改任何归档 CHG 记录的正文；未改三仓任何文件；
`delivery/completed/` 下 699 个文件**内容零改动**（只有本 CHG 自己新建的 `README.md` 在增补）。
