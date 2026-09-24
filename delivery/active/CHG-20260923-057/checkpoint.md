# Checkpoint — CHG-20260923-057

- 状态：IMPLEMENTING（2026-09-24 激活）。
- 性质：联合工程优化 B——Paths、Logger 和运行目录。Level M，跨两仓（agent / desktop）+ 治理回写。
- 权威：用户 2026-09-24《CHG-057 日志治理裁定补充说明》十三节。它**推翻**了本 CHG 草案的三处：
  Agent 日志改「三文件纯文本」而非 JSON、Desktop 后端只用官方 `tracing-subscriber`（无自写降级路径）、
  **不发 `X-Operation-Id`**（跨端 `operation_id` 本轮不交付）。

## Completed

- 2026-09-23：草案建于 `delivery/planned/CHG-20260923-057/`（PLANNED）。
- 2026-09-24 T-01：`git mv` 移入 `delivery/active/`（**不留副本**），改写为十三节执行记录
  （`change.md`、本 `checkpoint.md`、`evidence/`、`status/`），§4 记下实测起点。
- 2026-09-24 T-02：Agent 测试目录隔离（`wt-media-agent` `7382fed`，**test-only，`src/` 零改动**）——
  规则「测试不得把派生根接 `.local`」+ `scripts/test.sh` 前后新增路径守卫 + `isolated_paths()` 隔离助手；
  修掉 `tests/test_storage_migration_paths.py:46` 对真实检出的断言（改注入根，**未删断言**）。
  **先量后改**：实测今天本机与干净克隆都不写 `.local/`，故本 Task 的定位是 **T-03 之前的守卫**，不是修当下泄漏。
  顺带查出 AC-11 被计划高估——「不误连真实外部服务」那半今天**无规则在守**，已拆为 AC-11b 并新增 **T-19**（§7 Q-05）。

- 2026-09-24 T-03：Agent dev/override **真落盘**（`wt-media-agent` `2f07db4`）——`default_log_file` 恒为
  `<logs_dir>/agent.log`（**一行行为**；`logging.py` 零改动，因为 file 分支一直存在、只是永不可达）。
  先红 7 处 → 全套 **259 OK**；真实 dev 启动（临时树 + scratch 端口 18765）→ `agent.log` 114 字节非空，
  **对照臂**（仅回退那一行）同启动下**无该文件**，坐实归因。顺带完成 T-09 ①（已假注释随 docstring 重写删除）。

- 2026-09-24 T-04：Agent **三文件布局与路由**（`wt-media-agent` `305975b`）——`agent.log` 全量且唯一含
  traceback、`task.log` 只收 `wt_media_agent.runner.*`（点边界）、`error.log` 只收 ERROR 且不带 traceback。
  `NoTracebackFormatter` **格式化副本**而非改记录（记录是共享对象、`exc_text` 会被缓存，有专门测试复现该陷阱）。
  全套 **267 tests OK**；**四次真实启动**取证，臂 D 一次给出三条两向证据（真实 traceback 只在 agent.log；
  error.log 收到同一 ERROR 但无栈；非 runner 的 ERROR 不进 task.log）。

- 2026-09-24 T-05：`error.log` **结构化字段通道**（`wt-media-agent` `3a546dc`）——`error_code=` 必现
  （缺省 `none`）、`task_id=`/`context=` 有则现；`_field()` 把值的换行转义，保住「一行一记录」。
  **计划写定的机制被实测推翻**：`setLogRecordFactory` 预置字段会让 `Logger.makeRecord` 拒绝
  `extra={"error_code": …}`（KeyError），两半不可共存 ⇒ 缺省改放 formatter，并把该碰撞写成测试。
  `runner.py` **9 个** task-scoped emit 点加 `extra={"task_id"}`（计划写 8，实测分母 9），3 处配已存在的码；
  `task_id` **仍留在消息里**。全套 **278 tests OK**；两次真实启动：臂 A 真实任务失败在 `error.log`
  按 `error_code`/`task_id` 定位（字段命中 1/0/0），臂 B 未注册类型的 WARNING 不进 `error.log`。

- 2026-09-24 T-06：Agent **脱敏**（`wt-media-agent` `b66d7f5` + `70c1f93`）——掩码落在 **formatter** 而非
  `logging.Filter`：Filter 改 `record.msg` 碰不到 traceback，而凭据最容易出现在 traceback 里；四个 handler
  （stderr + 三文件）共用同一 formatter ⇒ 全部出口一次覆盖。词表由 `SENSITIVE_KEY_NAMES` 生成（不另起一份）。
  表 **15 行**先量后改：同一探针 **15/15 漏 → 0/15**（`gone`/`kept` 两列都断言）。
  `AgentConfig.runtime_token` 改 `field(repr=False)`。
  **顺带实测到诊断包一处真泄漏并修**：`environment_facts()` 的 `cloud_base_url` 可以是
  `https://alice:pw123456@host/api`，原样进 facts（`True`），而它走 `print` → **stdout**、不经任何 handler，
  Rust 侧 `drain.rs` 还会尾随 20 行 ⇒ 有真实外溢路径；值统一过 `redact()`（`True → False`，URL 仍可读）。
  **顺带追平套件 27 条 `--- Logging error ---`**：逐用例插桩点名 **`test_bootstrap.py`（9 条）**与
  **`test_sidecar_entry.py`（1 条）**——都走真实装配（`build_components` 即裁定要求的唯一 Logger 入口）
  却不恢复 logging 状态，之后每条恢复都把死集合原样放回；我的第一个假设（T-05 测试文件只恢复 root）
  **被计数推翻（仍 27）**。修后泄漏 `245 → 0`、噪声 `27 → 0`，并加机器规则
  `test_logging_state_isolation.py`（**先红且恰好点名这两个文件**）。基类还暴露出第二个缺陷：
  两处 `setUp` 覆盖没调 `super().setUp()` ⇒ 7 条用例报错，补上即绿。
  全套 **293 tests OK**；两个提交各自 checkout 亦 293 OK（见 `evidence/task-06-redaction.md`）。

- 2026-09-24 T-07：Agent **保留与轮转**（`wt-media-agent` `f07d9e8`）——裁定六的四个界
  （单文件 20MB、14 天、三文件共享总量 400MB、单条超限截断并标 `truncate=true original_size=<n>`），
  由 `BoundedFileHandler` + `LogBudget` 承接（stdlib 的 `backupCount × maxBytes` 表达不了时间窗、
  总量与单条上限）。三条口径：**日期翻档用「文件覆盖的那一天」命名**、**单条上限即单文件上限**
  （故超长单条既不涨文件也不新开文件）、**预算只在轮转与启动两点强制**。
  测试 **320 OK**（T-06 后 293 → +21 轮转/预算 +6 配置）。
  新类的「先红」只是 ImportError ⇒ 改量**变异**：六个界逐个关掉，各自打掉自己的用例（探针先跑对照行）。
  两处此前**测不到**的地方补了测试：①「当前文件永不被删」原本靠「名字不匹配轮转正则」而非守卫通过
  （新增一例让活跃文件名恰好长得像历史，两向断言）；②**真机两臂实测到一处真缺陷**——
  **启动清理此前空转**（prune 匹配已注册家族名，而家族名要等 handler 构造才注册，只有发生轮转时
  才「看起来生效」）；单元测试之所以绿，是因为它先建了 handler。修：先预注册三个文件再 prune +
  `register` 幂等 + 回归测试（先红）。
  真机两臂（真实入口、scratch 端口 18793、BitBrowser 指向死端口 `:15432`）**8/8 判据**：
  小界臂真的滚出 `agent-20260924-2.log`、真的有 `original_size=3185` 的截断标记、1999 年历史被删、
  预算退掉当日 `task-…-1.log`；出厂界臂同样流量**不滚不截断**（对照），但照样按天删。
  **不准的地方如实写**：总量真实上界是 `total_bytes + 3×max_bytes`（出厂 400MB + 60MB），
  不是逐字节精确（臂 A 实测停在 6500 > 6000）——裁定要的「有界」成立，精确性不成立，
  已写进 `LogBudget` docstring 并用「写 200KB 进去总量仍 ≤ 500+600」的用例钉住。
  走查时补一处并发守卫（三线程共享预算：列出后被改名走 → `FileNotFoundError` 会中断 prune
  并丢记录）→ `_size` 把已消失的文件计 0，配测试（去守卫即红）。
  **顺带实测登记给 T-09**：`-m` 启动时 server 的 logger 名是 `__main__`（HTTP 侧记录看不出组件来源）。
  见 `evidence/task-07-retention.md`。

## Current

- T-07 已收尾（一个 Agent 提交 + 本记录）；T-08 `/api/v1/health` 待开始。

## Next

- 阶段 1 Agent：T-08 → T-09（T-02…T-07 已完成）。
- **T-08 的题设要重测**：实测 BitBrowser 指向死端口时 `/api/v1/status` **已返回 200 + `unreachable`**，
  不能假设外部依赖不可用会抛。
- **T-09 新增一项**（T-07 顺带实测）：`python -m wt_media_agent.local_api.server` 使 `getLogger(__name__)`
  得名 `__main__`，真实运行的 HTTP 侧记录看不出组件来源——削弱「日志可定位问题」，属 T-09 范围。
- 新增 **T-19**（AC-11b 的 AST 规则：客户端构造必须注入假 `transport`）排在阶段 1 余项之后，编号排末位以免打乱 T-03…T-18。
- **定向验证命令一律带 `PYTHONPATH=tests`**：`tests/` 无 `__init__.py`，`python -m unittest tests.<模块>` 对
  6 个 import `support` 的模块（5 个是既有的）报 `ModuleNotFoundError`。既有布局属性，本 CHG 不动布局。
- 阶段 2 Desktop：T-10 → T-11 → T-12 → T-13 → T-14 → T-15 → T-16 → T-17。
- 阶段 3：T-18 回写与收尾。

## Blockers

- None。裁定十三节已把草案的待决项全部定下；§7 的 Q-01…Q-04 均为 `Blocking = NO`，已按读数实施。

## Recent verification

- Start Gate（2026-09-24）：四仓工作区干净（governance/agent/desktop/cloud 各 `git status --porcelain` 为空）；
  `delivery/active/` 仅 `.gitkeep`；`LEDGER.md` 无表行；快照 `Active CHG: none`。
- 起点测试基线：Desktop **68**（二进制 crate，`cargo test --lib` 不成立）、Agent **253 tests OK**。
- T-01：见 `evidence/task-01-governance.md`。
- T-02：`bash scripts/test.sh` → **259 tests OK，exit=0**（253 → 259，只增不减）。改前规则**红且恰好 1 处命中**
  （`test_storage_migration_paths.py:46`）；阳性对照两处实跑出红（规则内正则；端到端探针模块报出
  `test_zz_probe_forbidden.py:3`）；变异探针下 `scripts/test.sh` `exit=1` 点名路径**而套件打印 `OK`**
  ⇒ 守卫独立于测试结果。见 `evidence/task-02-isolation.md`。
- T-03：`bash scripts/test.sh` → **259 tests OK，exit=0**；**T-02 的规则当场命中了我自己的 T-03 新代码**
  （`test_runtime_logging.py` 里 `<标识符> / ".local"`，1 处）——**未放宽规则**，改测试为经由 `cfg.paths` 断言。
  真实启动：`curl /healthz` 200、`.local/logs/agent.log` 114 字节含监听记录、stderr 同时有同一条；
  对照臂同启动下 `.local/logs/` 是**空目录**（同时实测坐实了 §4 那条「dev 的 `.local/logs` 是空的」起点读数）。
  见 `evidence/task-03-dev-writes-logs.md`。
- T-05：`bash scripts/test.sh` → **278 tests OK，exit=0**（267 → 278，+11，正反成对）；
  **设计前提先实测**：`factory 预置 error_code` + `extra={"error_code":…}` → `KeyError "Attempt to overwrite …"`
  ⇒ 缺省改放 formatter（该碰撞有专门测试）。真实启动两臂（scratch Cloud 17901，`/tmp` 工作树副本）——
  臂 A 真实 `cookie_read_task` 失败：`error.log` 得 `error_code=executor_error task_id=t05-real-1`，
  字段命中分母 `error.log 1 / agent.log 0 / task.log 0`；臂 B 未注册类型：WARNING 进 `agent.log`、
  `error.log` **0 字节**。见 `evidence/task-05-error-fields.md`。
- T-07：`bash scripts/test.sh` → **320 tests OK，exit=0**（293 → 320：+21 轮转/预算、+6 配置）；
  六个界各一次实现变异**各自打掉自己的用例**；真机两臂 8/8；`f07d9e8` 单独 worktree 亦 320 OK。
  **一次「测到了但没测到点上」如实记录**：启动清理的单元测试先建了 handler，故对启动路径的空转是瞎的。
  见 `evidence/task-07-retention.md`。
- T-06：`bash scripts/test.sh` → **293 tests OK，exit=0**（291 → 293：+1 隔离规则、+1 诊断包用例）；
  两个 Agent 提交各自单独 checkout 再跑，**均 293 OK**（提交边界真实）。
  探针四组：脱敏表 `15 → 0`（同一探针改动前后）、诊断包密码 `True → False`、死 handler 泄漏 `245 → 0`、
  `Logging error` `27 → 0`。**一次对照无效如实记录**：`.local/` 守卫的第一次对照把目录建在跑之前
  （BEFORE 里就有它），改为对 `comm` 比较本身做对照并报出 `.local/logs/task.log`。
  见 `evidence/task-06-redaction.md`。
- T-04：`bash scripts/test.sh` → **267 tests OK，exit=0**（259 → 267，+8，两向成对）；
  真实启动四臂（A 常规 / B DEBUG+死 Cloud / C 自建 scratch Cloud 回 11001 / D 不可解析 URL）——
  臂 D：`agent.log` 2406 字节含 `Traceback … ValueError: Invalid IPv6 URL`、`error.log` 101 字节**同一个
  ERROR 但无 traceback**、`task.log` **0 字节**（非 runner 的 ERROR 不进）。见 `evidence/task-04-three-files-routing.md`。

## 执行期间的边界（不得越界）

- 开发者自己的 BitBrowser `:54345`、Cloud `:18080`、dev Agent `:8765` **全程不碰**；所有启动用 scratch 端口。
- `.ai/CURRENT_CONTEXT.md` 由 `prepare_ai_workspace.py` 生成，**禁手改**。
- 运行仓改动只限 `wt-media-agent` 与 `wt-media-desktop`（本记录 §1 已列）；`wt-media-cloud` 不碰。
- 证据文件一律 `.out` 后缀，不用 `.log`（两仓 `.gitignore` 都有 `*.log`）。
- 一仓一 commit；「移动文件」与「改逻辑」绝不进同一 commit。

## 实测起点里最容易被忽略的三条（施工时反复回看）

1. **dev 今天根本不写日志文件**（`paths.py:107` 对 dev/override 返回 `""`）——磁盘上 `.local/logs/` 是空的。
   「日志有轮转」的直觉在此处不成立。
2. **Agent 只有 3 个 logger 在发记录**（runner / local_api.server / runtime.config），
   `executors/`、`services/`、`clients/`、`storage/` 零日志调用——按名字路由今天只能区分两面。
3. **Desktop 全仓只有 5 处裸 emit**，其中 4 处是 emit（第 5 处是注释）——日志面是从零开始，
   不是「给已有日志加轮转」。
