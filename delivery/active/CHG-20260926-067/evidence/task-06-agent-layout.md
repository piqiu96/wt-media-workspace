# T-06 agent 脚本层分层

仓：`wt-media-agent`。日期：2026-09-26。范围：建 `bin/control.sh`、删三个启停脚本、三处端口字面量去值、
三处注释回指、四份文档。**本 Task 无跨仓依赖，也不产生红窗**（理由见 §2）。

## 1. 改动文件

| 类别 | 文件 |
| --- | --- |
| 新建 | `bin/control.sh`（755）、`scripts/dev/.gitkeep`、`scripts/verify/.gitkeep` |
| 删除 | `scripts/start-health.sh`、`scripts/stop-health.sh`、`scripts/health.sh` |
| 改 | `README.md`、`config_online/README.md`、`scripts/README.md`（全文重写）、`DIRECTORY_MAP.md` |
| 改（注释） | `src/wt_media_agent/local_api/server.py:44`、`tests/test_local_api_server.py:154`、`tests/test_runtime_config.py:145` |

`scripts/` 分母 **10 → 7**（`git ls-tree --name-only HEAD scripts/` = 10；`git ls-files scripts/` = 7）。

## 2. 为什么不产生红窗

计划的 T-06 行把「自足」当结论写下来，此处把它验成读数：`scripts/verify-health.sh` 是 `#!/usr/bin/env sh`，
自己内联 `unittest discover`，自己 `"$PYTHON_BIN" -m …server &`，自己 `trap cleanup`
与 10×1s 探活——**它不调用被删的三个脚本中的任何一个**。故删掉那三个不会让任何幸存脚本悬空。
（对照：cloud 的 `verify-health.sh` 会 source `local-env.sh`，所以那边必须保留共享库；agent 没有这个结构。）

## 3. `bin/control.sh`：形状与实现

四仓同形（同文件名、同动词组、同 `status` 语义），实现各随本仓。agent 版由三个旧脚本合并：
`start-health.sh` 的 heredoc 子进程启动体**逐行照搬**（`start_new_session=True` 不变），
PID/日志/探活三件事合一。

- 动词：`start | stop | restart | status | help`。`status` **报两个读数**（`alive=`、`health=`），
  **两项都成立才 exit=0**——这就是「健康检查并入 status」的判据落点，不是把健康检查删掉。
- 覆盖项（脚本级，不进配置文件）：`PYTHON_BIN`、`WT_MEDIA_AGENT_HEALTH_HOST`、`WT_MEDIA_AGENT_HEALTH_PORT`、
  `WT_MEDIA_AGENT_PID_FILE`、`WT_MEDIA_AGENT_LOG_FILE`。
- `bash -n` 与 `sh -n` 都 rc=0；权限 755。
- **实跑 12 臂**：10 条功能臂（含 `status` 运行中 exit=0 与停止后 exit=1 的两个方向、
  `restart` pid 变更 86409→86446、重复 start 幂等、未知动词 exit=2）+ 2 条变异臂。
  逐条读数在 `artifacts/t06-control-arms.out`。臂在**真实健康台**上跑，端口由内核分配、
  PID/日志改到 `/private/tmp`，**不碰本机 18765、不写本仓 `.cache/`**。

### 3.1 变异臂复现了 §14 第 19 项，且危害是三仓共有的

arm11（对照）：替身子进程立刻退出、端口无人应答 → `start` 报 `failed to stay running`，exit=1，窗口关着。
arm12（变异）：**外来进程先占住端口**、替身子进程 2 秒后自杀 → `start` 探到 `/healthz` 有应答即报
`started: 86699`，**exit=0（假成功）**；3 秒后 `status` 读到 `alive=no health=ok`，exit=1。

即 `start` 的探针分不清「自己的子进程活着」与「别人在应答」。cloud（T-04）与 workspace（T-05）各自已测一次，
本处是第三次——**这条危害是三仓同形的，不是某一仓的实现瑕疵**。本 CHG **不修**（§14 登记项）；
修法落点是 `start` 的等待循环里加「pid 存活 ∧ 探针应答」的联合判据。

## 4. 三处端口字面量去值

**端口值一个未改**；去的是 README 里的**复述**。三个数值型事实各自回到它唯一的落点：

| 文件 | 改前 | 改后 | 事实的落点 |
| --- | --- | --- | --- |
| `README.md:17` | `default \`http://127.0.0.1:54345\`` | 删数值 | `config/agent.toml`（`runtime/constants.py` 兜底） |
| `README.md:48-49` | `WT_MEDIA_AGENT_HEALTH_PORT=18765 scripts/start-health.sh` | 改指 `bin/control.sh start\|status\|stop` | **`bin/control.sh` 自己**（例外，见 §4.1） |
| `config_online/README.md:16` | `local Cloud service on \`127.0.0.1:18080\`` | 删数值 | 同目录 TOML |

### 4.1 为什么 agent 是全仓唯一保留端口字面量的地方

`WT_MEDIA_AGENT_HEALTH_PORT` 的默认值 **18765 就是隔离健康台自己的值**，而隔离健康台
**没有配置文件落点**——CHG-20260926-067 已裁定把它挪进 `config/` 会破坏隔离设计（`config/` 是运行时的
唯一读取目录，而这个台的默认值按定义不该由运行时配置决定）。所以这里的脚本默认值**就是**那个落点，
例外写在 `bin/control.sh` 自己的表头里，并在此登记为**唯一例外**。

### 4.2 计划给的判据有一个覆盖缺口（如实登记）

计划写的模式是 `127\.0\.0\.1:[0-9]{2,5}|:[0-9]{4,5}`——**两段都要求数字前有冒号**。
而 `README.md:48` 的形态是 `WT_MEDIA_AGENT_HEALTH_PORT=18765`，**没有冒号**，计划的模式抓不到它。
改前读数可证：那个模式下 `:48/:49` 从未出现。**已补第三种写法** `[0-9]{4,5}` 覆盖 `VAR=值` 形态，
三种写法的改前/改后读数、分母与阳性对照在 `artifacts/t06-doc-port-literals.out`。

三种写法改后读数：冒号两种命中 **0**；裸数值形态命中 3 行，全是**同文件里与本 Task 无关的历史编号**
（`CHG-20260923-056`、`CHG-20260923-059`、`2026-09-25`），**端口事实 0 条**——
这正是计划自己记过的「`[0-9]{4,5}` 会撞 CHG 编号」那一条的现场。

## 5. 三处注释回指（计划只点了两处）

`server.py:44` 与 `test_local_api_server.py:154` 的 `scripts/start-health.sh` → `bin/control.sh`（计划已列）；
**`tests/test_runtime_config.py:145` 是第三处**（计划未列）——它写 `bin/control.sh redirects *its*`，
说的是日志重定向的落点，也是同一批被删名字的活指针。三处都已改，旧名在三文件里 `grep` rc=1（0 命中）。

回指充分性扫描见 `artifacts/t06-pointer-sweep.out`：三个名字在带边界的精确形态下命中 **2 行**，
都在新文件表头（过去时叙述「合并了这三个脚本」，判留），**可解析的活指针 = 0**；
带目录的路径形态去重后同这 2 行；裸 `health\.sh` 形态 10 行全是子串重叠（8 行在幸存的 `verify-health.sh` 上）。
阳性对照同命令同集合 `bin/control.sh` = 6 文件/12 行。

**该产物同时当场复现了 T-04 那个坑**：同一时刻、同一命令，只读已跟踪命中 0，加 `--untracked` 命中 2——
`bin/control.sh` 当时还没 `git add`。产物里每条读数都标了取的是哪个集合。

## 6. 文档：`scripts/README.md` 与 DIRECTORY_MAP

`scripts/README.md` 按四仓同一模板重写：三分类表（运营/开发/验收）、多归属说明、
「新脚本落在哪」（新 dev → `scripts/dev/`、新 verify → `scripts/verify/`、启停与健康**一律**进 `bin/`、
**现存脚本不迁移**）、「本文件不拥有什么」＋**端口例外声明**。补上了计划点名的缺失 `build_desktop_sidecar.py` 行。
`DIRECTORY_MAP.md` 增 `bin/` 行、`scripts/` 行改指 `scripts/README.md`。

## 7. 测试读数

`PYTHONPATH=src .venv/bin/python -B -X pycache_prefix=/tmp/pyc-none -m unittest discover -s tests -q`
→ `Ran 409 tests in 11.590s` / `OK`，rc=0。与激活前基线 `Ran 409 tests` / `OK`（rc=0）**逐字相同**；
耗时 11.488s → 11.590s 属正常抖动。

**归因声明**：本仓工作树有一处**开工前就存在**的未提交改动（`AGENT-INDEX.md`，删掉需求路由表一行，
发生在 CHG-065 提交 `6d740fc` 之后）。本 Task **未触碰**它，但它使本节的读数是「脏工作树上的绿」，
而非「干净提交上的绿」——如实登记，不据此拔高结论。
