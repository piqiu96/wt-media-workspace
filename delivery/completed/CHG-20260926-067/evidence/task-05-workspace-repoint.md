# T-05 证据：workspace 回指 cloud `bin/control.sh`（跨仓红窗收口）

- CHG: `CHG-20260926-067`
- Task: T-05（`change.md` §8）
- 日期: 2026-09-26
- 锚: 开工前 workspace HEAD `cf148af`（T-04 的记录提交）；cloud HEAD `e2ba4d8`
- 提交: 本 Task 单提交（workspace 侧）

> 本 Task 的**主要产出是一次更正**：T-04 的回指扫描报了假阴性。红窗本身只有 3 行代码。

## 1. 改动文件

| 文件 | 改动 |
|---|---|
| `scripts/verify_m3_acceptance.py` | 三处改指（§2）：`:561`、`:566`、`:1738` |
| `scripts/local-control.sh` → `bin/control.sh`、`test-local-control.sh` → `test-control.sh` | **T-01 已建全**，本 Task 只复核（§4），未改动 |
| T-04 的记录三件 | 回改那条假读数（§3）：产物、`evidence/task-04-cloud-layout.md` §8、`change.md` T-04 行与 `checkpoint.md` 对应行 |

## 2. 三处改动（逐行）

```text
:561  - subprocess.run(["bash", "scripts/start.sh"], cwd=str(CLOUD_ROOT), check=True,
      + subprocess.run(["bash", "bin/control.sh", "start"], cwd=str(CLOUD_ROOT), check=True,
:566  - record("G2.1", phase, "bringup", "scripts/start.sh -> cmd/server", …)
      + record("G2.1", phase, "bringup", "bin/control.sh start -> cmd/server", …)
:1738 - record("11.4", phase, "teardown", "停止 scheduler/worker/Vite/代理 + scripts/stop.sh", …)
      + record("11.4", phase, "teardown", "停止 scheduler/worker/Vite/代理 + bin/control.sh stop", …)
```

- 计划只点名 `:561` 与 `:1738`；**实测同文件另有 `:566`** 也把旧路径写进了 `record` 标签，一并改。三处都
  在「会被执行的引用」面上，留着任何一处都是指向已不存在路径的活体指针。
- **与旧脚本的一处行为差异，如实记**：旧 `start.sh` 的探针地址带 `${…:-127.0.0.1:18080}` 自带兜底，
  新的 `bin/control.sh` 只读 `WT_MEDIA_CLOUD_HTTP_ADDR`。实测该变量在 `scripts/local-env.sh:9` **带默认值
  导出**，故 `set -u` 下不会踩空——**这一点是读出来的，不是推断的**（本 Task 改的正是那个调用点，若它为空
  则 T-04 的 15 臂早就红了）。
- `check=True` 与新脚本相容：T-04 臂 7 实测「再 `start` 得 `already running` `exit=0`」。
- `:557` 读的 `CLOUD_ROOT/.cache/wt-media-cloud.pid` 与新脚本默认落点**同一个文件**，无需改。

## 3. T-04 假阴性更正（本 Task 的实质工作）

`t04-cloud-sweep.out` 的形态 A／C／D 报「改写后 0」。**T-05 复扫得 2**，两条都在
`bin/control.sh:4-5`（本 CHG 新建的文件）的表头。原因不是判据形态，是**分母**：

| 读数 | 值 | 说明 |
|---|---|---|
| `git ls-tree -r 0db02ab \| wc -l` | 500 | 开工前 cloud 已跟踪 |
| `git ls-files \| wc -l`（扫描时刻） | **497** | 三个删除已 `git rm` 进索引 ⇒ 立即消失；= 产物自报的分母 |
| `git ls-files \| wc -l`（`e2ba4d8` 后） | 500 | 497 ＋ 那三个新增 |

三个新增（`bin/control.sh`、`scripts/dev/.gitkeep`、`scripts/verify/.gitkeep`）当时**未跟踪**，而四形态
**都没带 `--untracked`** ⇒ 被扫集合里没有它们，命中的两条恰在其中之一。机制在合成仓里**再现**过（同内容
两份、一跟踪一未跟踪：默认 `git grep` 只命中前者，`--untracked` 才命中两者；见 `t05-pointer-sweep.out` 末节）。

- 两条命中的性质：**过去时叙述**（说明该文件合并了哪三个脚本），按「路径判修、叙述判留」**判留不改**。
- 更正落三处：产物文末「更正一」（含验算与作废标记）、`task-04-cloud-layout.md` §8（改为「已作废（假阴性）＋
  更正读数」）、`change.md` T-04 行与 `checkpoint.md` 对应行；分析正文在 §14 第 24 项。
- **T-04 证据的字节预算因此被重新分配**：更正净增约 130 B，同文件里删掉等量旧冗文（如 `「有同一形状的缺陷」`
  与「检查通过」等重复措辞），最终 **9211 / 9216**，未放宽上限。

## 4. `foreign` 清单逐条重算（`:414-421`）

`own_artifacts = ("scripts/verify_m3_acceptance.py",)`。重算方式**不是重读注释，是重查落点**：

| 谁 | 落到哪 | 是否在忽略面内 |
|---|---|---|
| 本脚本（workspace） | `.cache/m3-acceptance/`（`RUN_DIR`／`RAW_DIR`／`STATE_FILE`／`MANIFEST_FILE`） | 是：workspace `.gitignore:1` = `.cache/` |
| 本脚本（cloud） | `.cache/m3-acc/`、`.cache/go-build`、`.cache/go-path`、`.cache/wt-media-cloud.pid`、`.cache/wt-media-%s`、日志 | 是：cloud `.gitignore:1` = `.cache/`；`.pid` 另有 `*.pid` 兜一层 |
| 三个被删脚本名 | 已不在活体面（§5） | — |

**结论：条目仍准确，不改。** 同时如实记一条**本清单管不到的情形**：G0.1 要求 workspace「除本轮产物外干净」，
而跑验收时活动 CHG 自己的记录（`delivery/active/CHG-…/`）必然是脏的 ⇒ 该判据**只能在提交后的干净工作树上
成立**。这不是本 CHG 引入的缺陷（该脚本本就不属六门禁、不在本 CHG 验证项内），登记为观察。

## 5. workspace 侧复核与判据

- `bin/control.sh`（T-01 建）：动词 `start|stop|restart|status|verify|help`（另有 `-h|--help`），`bash -n`
  `exit=0`，端口字面量 `grep -nE '[0-9]{4,5}'` **0 命中**。
- `scripts/test-control.sh`（T-01 建）：`bash -n` `exit=0`；全跑 `exit=0`，一条聚合 `PASS`
  （`usage, dispatch, status wiring, and no-port-literal`）——落 `t05-test-control.out`。
- **回指扫描**（`t05-pointer-sweep.out`）：活体面（`:!delivery`）逐形态 **8 → 5 行**，差 **3** 与 §2 的
  三行编辑逐行对上；余 5 行全在 `config/release-matrix.yaml` 的 `verification:` 历史证据行，按 §5「明确
  不做」判留 ⇒ **可解析指针 = 0**。cloud 同口径 **2 行**（§3）。阳性对照 `bin/control\.sh` 两个仓各
  **23 文件/124 行**、**3 文件**；反向对照排除记录产物后 **0**。

## 6. 本次写坏的读数（一处，留在产物里）

**首版产物是原始 dump，把整份 42 KB 的命中清单直接写进了 `t05-pointer-sweep.out`**，三重后果：①远超记录预算；
②产物自己进了被扫分母（实测 `t05-pointer-sweep.out:205`，形态 D 口径 205 行）；③**把反向对照毒化**——全仓
搜「从未存在过的名字」不再是 0，命中的正是产物里那句对照记录。重做为「按文件计数 ＋ 只逐字列出活体面」的
紧凑版（4.2 KB），并把自指单列成节。**同类既有污染**：`t04-cloud-sweep.out:46` 也引用了对照名，故反向对照
必须带 `:!delivery` 才是干净的。

## 7. 跨仓与红窗

- **红窗关闭**：本条提交后，workspace 再无指向 cloud 已删三个脚本的可解析指针。窗口 = T-04 的 cloud 提交
  （`e2ba4d8`）到本条提交，期间六门禁与单元套件全程绿（见 T-04／T-05 的产物）。
- `config/release-matrix.yaml:114,117,120` 的 5 行按裁定**不改**：`validate_release_matrix()` 只查状态与契约
  版本、不解析命令行；`:117` 的 `start-health.sh`／`stop-health.sh` 是 agent 的，归 T-06（也只处置仓内脚本，
  同样不改该文件）。
- 未跑 `verify_m3_acceptance.py`：它需真实运行实例（mysql／上游／真 `go`），不属六门禁（`AGENT-INDEX.md:209-210`），
  本 Task 只做**语法与引用面**的判据——**如实记：这三行改动的运行期正确性未被本 Task 验证**。
