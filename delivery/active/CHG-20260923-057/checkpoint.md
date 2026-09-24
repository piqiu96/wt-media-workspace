# Checkpoint — CHG-20260923-057

- 状态：IMPLEMENTING（2026-09-24 激活）。
- 性质：联合工程优化 B——Paths、Logger 和运行目录。Level M，跨两仓（agent / desktop）+ 治理回写。
- 权威：用户 2026-09-24《CHG-057 日志治理裁定补充说明》十三节。它**推翻**了本 CHG 草案的三处：
  Agent 日志改「三文件纯文本」而非 JSON、Desktop 后端只用官方 `tracing-subscriber`（无自写降级路径）、
  **不发 `X-Operation-Id`**（跨端 `operation_id` 本轮不交付）。

## Completed

- 2026-09-24 T-17：**Desktop 进程内会话 `operation_id`**（`wt-media-desktop` `9051480`，1 个 commit）——
  一次 Agent 会话一个 id：`start` 生成并在**存下 child 之后**登记、`stop` 在**记完「已停止」之后**清除，
  存在 `state.rs` 里 `AgentProcess` **旁边**（两者回答同一个问题：有没有一个会话在跑）。id 只作为**字段**
  落在 `agent.supervisor` 的记录上：会话内的记录带 `operation_id=`，会话外的**一律不带这个字段**——
  不能写成 `operation_id=None`，那是对「这条记录属于哪个会话」的**错误回答**，也会改掉今天已有的行形状；
  这就是 `lifecycle!` 宏有**两个 `event!` 分支**的原因。**不加新 target**（`OWNED_TARGETS` 仍恰 3）、
  **不发 Header**、**不进 sidecar 环境**（裁定九/D-10）——三条各有一个变异去打（M1 query / M2 Header /
  M3 环境变量），M3 打掉的是**既有**用例 `vars.len() == 3`。
  出站头的基准是**桩套接字实际收到的字节**（`authorization`/`accept`/`host` 逐字，`host` 由 hyper 在 send
  时加、`build()` 看不到），不是 `build()` 推断的集合。`begin`/`ended` 再从 `start`/`stop` 拆出一层：
  spawn 之后与 kill 之后的动作是**可以测的**，不该藏在要 `AppHandle`/`CommandChild` 才能进的函数里。
  **变异 R1–R3 + M1–M5 全部 KILLED**（R2/R3 成对：只回退登记或只回退清除，另一个方向仍会绿）；
  **两个诚实幸存者**：`start` 里的 `begin(...)` 与 `stop` 里的 `ended(...)` 各一行调用点，单测进不去
  ⇒ **只由真机臂覆盖**（会话 A 三条同 id、stop 之后那条**无字段**就是它们跑过的证据），未写假替身。
  **真机臂**复用 T-16 的探针页套路：两个会话、六条记录、5 条带 id（两个不同值）、1 条不带（stop 之后的
  health），探针打印的返回值里**一条都不含 id**；脚手架逐项还原（`index.html` sha256 逐字相同、
  5174/18767 无残留、无残留进程），未碰 `:8765`/`:18080`/`:54345`。
  测试 166 → **175**；build **9 → 9**、clippy **13 → 13**；`rustfmt` 新增行 **0 处**差异
  （`state.rs` 整文件干净；`commands/agent.rs` 既有脏行 9 → 8，未整文件重排）。
  **另登记三条**：退出报告**有意不带 id**（`drain` 在进程退出时写，那时会话可能已被清除，同一记录类型
  「有时带有时不带」比一律不带更误导）；`already_running` 带 id 只在单测表里（真机臂时序没走到）；
  两侧 id **不相关**（T-21 的 id 是请求级，不做串联）。见 `evidence/task-17-desktop-operation-id.md`。

- 2026-09-24 T-16：**三个既有 emit 点改道 + 生命周期补点**（`wt-media-desktop` `5eb7d0c` 纯重命名 +
  `b02130c` 改道，**2 个 commit**）——① `drain::report_exit` 由 `eprintln!` 改走 `agent.supervisor`
  记录（**恰一条**，按裁定五**保留末 20 行尾**，`single_line` 把整份报告转义成一行）；② `CommandEvent::Error`
  分支补一条 `warn!`（读失败是 Desktop 的问题，只缓冲则进程未退出时永不为人所见）；③ 两处 `println!`
  改走 `webview` 记录（空 stack 不产生记录）；④ Agent 启停与健康补五处生命周期记录，
  health 响应体**只在 DEBUG**、**失败记录不带尾行**（尾行只在前端拿到的返回串与那条退出记录里）。
  **`CommandEvent` 是 `#[non_exhaustive]`，测试构造不出来** ⇒ 把「一行是什么」压成 `Heard`/`classify`/`heard`，
  `follow` 里只剩收流。**命令体也拆了**（`health`/`start`/`stop` 三个自由函数）：与 T-15 拆 `plan` 同一形态的
  理由——命令体吃 `State`，测试造不出来。**变异 13 个全部 KILLED**：3 个是**回退到改动前的旧形态**
  （R1 `eprintln!` / R2 普通行也发射 / R3 读失败不记），10 个是新形态，每个都**点名打掉了自己的用例**；
  M4（启动记录降 DEBUG）与 M7（`capture_at` 忽略级别）是**成对**的，各自只让一侧红。
  **真机取证被一个环境事实改写**：debug 二进制带 `cargo:rustc-cfg=dev` ⇒ 窗口加载的是 **`devUrl`
  （`127.0.0.1:5174`）而不是 dist**，开发机没起 Vite 时窗口**整页空白、连静态 HTML 都不渲染**，
  按计划原样「真实启动即可驱动命令层」**不成立**（T-15 三臂只断言 Rust 侧记录，未受影响）。
  改用**探针页**：把一页只调 `__TAURI_INTERNALS__.invoke` 的 HTML 挂在 5174（当场核查为空闲），真实启动
  后一次跑齐 start→start→health→stop→stop，五个生命周期记录与前端返回值**逐条对应**；同一轮里
  sidecar 打印的那 1 行**只**出现在退出报告的尾行里（不成为独立记录），前端那条失败串**带**尾行、
  日志那条**不带**——裁定五的分工在真实进程里对照成立。脚手架逐项还原（`index.html` 的 `shasum`
  与备份逐字相同、5174/18766 无残留、五个进程全部结束），全程未碰 `:8765`/`:18080`/`:54345`。
  测试 153 → **166**；build 警告 **9 → 9**、clippy **13 → 13**（13 条逐条列过，无一条落在本 Task 新增代码上）。
  **三条新登记**（见 `Next`）：AC-09 的真机分母是 **1 行**不是 50、`start` 的 spawn 失败分支在本地这棵树
  **够不着**、`already_running` 在 sidecar 自己死掉之后**仍会说「已在运行」**。
  见 `evidence/task-16-desktop-emit-points.md`。

- 2026-09-24 T-15：**Desktop 接进 `main`（唯一初始化入口）**（`wt-media-desktop` `a312aa0`，1 个 commit）——
  新增 `logging/setup.rs`：`plan()` 承担**全部决定**（`levels`/`limits`/`directory: Result<PathBuf, String>`/
  `configured_level`/两个 `Environment`，全部参数注入），`install(plan, secrets)` 只剩装配与
  `set_global_default`，**连 `&DesktopConfig` 都不再拿**。**这条拆分是本 Task 第一个变异逼出来的**：
  M1 把 `install` 里的环境改成 `config.environment`（错误的一侧）时**整套 152 条用例全绿**——
  subscriber 每进程只能装一次，留在 `install` 里的判断只能靠启动程序才够得着。拆出 `plan` 后
  N1/N2/N6/N7 四个变异各自转红。
  **环境取构建期**（`bootstrap::build_environment()`）：出货文件恒声明 production 且 `load_with` 取更严一侧
  ⇒ 取生效环境会让开发态目录与开发 DEBUG **永不可达**；代价（进程内两种「环境」并存）由摘要同时写出两者抵消
  （`环境 production（构建 development）`）。token 生成提前到日志之前，sink 才能拿它的值做掩码。
  **变异两轮 22 个**（控制行两次先绿）：第一轮 12 个中 M3/M4 起初存活——正向臂与期望值**都从 `filter_of` 推导**
  （与 T-14 的 M6 同一形状的通病，第二次出现）⇒ 新增 `PINNED_LEVELS` **手写对表** + `join(" ")` 绑回
  `LOG_LEVELS`，N3/N4/N5 转红。**三个幸存者逐条登记**：`main` 的两个实参（N8 token / N9 环境）与
  「已被装过」那条臂（N10，本程序内**不可达**）——N9 由**臂 1 的真实启动**守（目录与级别两处可分辨事实），
  N8 是**无处可验**（真实启动的 grep 分母为 0：今天没有记录携带 token），N10 无守，不谎称已覆盖。
  **真机三臂**：① 开发态布局下 stderr 与 `src-tauri/.local/logs/desktop-20260924-1.log`（249 字节）
  **都有摘要且文件首条即摘要**（AC-02）；② 用普通文件占住 `<repo>/.local/logs` → **仍启动、摘要在 stderr、
  不 panic、占位文件不被改**（AC-05 第二臂）；③ `level="warn"` 臂 **0 条 stderr 记录、不建文件**，
  对照臂 `level="info"` 1 条记录 + 255 字节文件——**实测后果比计划写的更宽**：两层共用同一个 filter，
  严于 INFO 的级别**连 stderr 一起静默**（计划只预测「不建文件」），如实登记并可能进 §7。
  测试 147 → **153**；build 警告 **93 → 9**、clippy **97 → 13**——**与四处登记的待验期望 4/10 不符**，
  差 5 条逐条点名（`rolling` 的 `SHIPPED`/三个 `DEFAULT_*`/`open_path` 现在**只在测试里**被引用，
  根因是 T-14 按计划把配置文件变成四个数字的来源），另 4 条是既有桩 ⇒ 本 Task 新增代码 **0 条 lint**；
  反证三条（计数降了 84 条说明接线到位、臂 1 真的建出文件、clippy 的 13−9 全是既有项）写在证据里。
  见 `evidence/task-15-desktop-main-wiring.md`。

- 2026-09-24 T-14：**Desktop `[logging]` 配置 + 校验 + 出货资源**（`wt-media-desktop`，1 个 commit）——
  出货 TOML 补 `[logging]`（`level = "auto"`、20MB / 14 天 / 100MB）；`Logging` 与其余六节同款
  `deny_unknown_fields`、**无** `#[serde(default)]`；`validate()` 五条检查**只点名键、不回显值**；
  `LOG_LEVELS`/`LOG_LEVEL_AUTO` 常量 `pub` 给 T-15 的 subscriber 复用（不许再手写第二份词表）。
  **先红**：表的第 4 列（报错必须点名的键）+ 每行先断言 `PRODUCTION_TOML.contains(from)` ⇒
  在 `[logging]` 写进出货文件之前，表自己先报 `row "unusable log level" matches nothing`。
  **变异 9/9 红**（控制行 147 passed 先绿），**两个缺口当场补掉**：
  ①M6「词表删掉 trace」**起初存活**——正向臂与报错文案都从 `LOG_LEVELS` 推导，改小数组时两侧一起变，
  故把常量本身用手写值钉死（`len == 6` + `join(" ")` 逐字 + `auto` 不在表内；用 `join` 而不是数组比较，
  因为后者在长度变化时**编不过**，而编不过的变异什么都证明不了）；②M9「撤掉 `Logging` 的
  `deny_unknown_fields`」起初存活——既有用例把未知键放在**顶层**，只被顶层 derive 拒掉，
  每个子结构的那行 derive 都无人守 ⇒ 改为**逐节枚举**（顶层 + 七个节头）。
  三处超出计划原文的检查逐条登记：`retention_days <= 0`（TOML 能装负数）、
  `total_bytes >= max_file_bytes`（更小的总量不可满足）、逐节 `deny_unknown_fields`。
  测试 144 → **147**；build 警告 **93 → 93**、clippy **97 → 97**（新常量被 `validate()` 引用，不入 `dead_code`）
  ⇒ **T-15 的待验期望起点未被本 Task 移动，仍是 93 → 4 / 97 → 10**。
  见 `evidence/task-14-desktop-logging-config.md`。

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

- 2026-09-24 T-08：Agent **聚合健康检查**（`wt-media-agent` `87b1264`）——架构基线 §5.6 的双端点。
  `/healthz` 逐字冻结（单测逐字断言 + 两臂真实进程各量一次，机器守而不是约定）；
  新增 `GET /api/v1/health` 返回 Agent 版本/状态 + Cloud/BitBrowser/Storage 状态。
  裁定那两条禁令都落成**机制**而非承诺：
  ①「不得触发任何对外写请求」——Cloud 侧只有写接口（`clients/cloud/client.py` 无一只读），故探针是
  `socket.create_connection` 到 host:port 后**立刻关闭**，真机实测 `connections=1 received=b''`
  （连上了、一个字节没发）；代价写进契约与 docstring：**连上即 `normal`，token 被拒也仍是 `normal`**，
  那是可达性不是健康，更宽的问题归 `/api/v1/status`。空/非 http(s)、端口非数字 → `unknown`。
  ②「不得因依赖不可用而抛」——每个依赖各自降级（`BitBrowserError`→`unreachable`、
  Cloud `OSError`/存储失败→`abnormal`、未预期的失败→**`unknown` 且留 traceback**），响应恒 200；
  常规不可用只记一行警告不留 traceback（Desktop 轮询不该把 `agent.log` 灌满）。
  `CheckpointStore.probe()` 读一行 `task_checkpoints`：能开文件 ≠ 能干活（未迁移的库要报坏），
  库文件不存在即失败且**绝不创建**（那等于自己造出被验对象），且是本类唯一显式 close 的连接。
  测试 **345 OK**（T-07 后 320 → +25）。新类的「先红」只是 ImportError ⇒ 改量**变异**：
  12 个变异控制行先绿、**全部转红**。**两处自查出的假绿**：①AST「探针不走 HTTP 客户端」检查对
  `from urllib import request` 只取 `node.module`，deny-list 永远匹配不上——**是变异把它救回来的**；
  ②真机探针的就绪判断误用宽 catch 的 `get()` ⇒ 首次连接被拒也当「起来了」，臂 A 全跑在没人服务的端口上。
  真机两臂（真实入口、scratch 端口/临时树）**20/20**：臂 A 全 `normal` + `/healthz` 逐字 + BitBrowser 侧
  只有 `POST /group/list`（读）；臂 B 三依赖全灭仍 200 + `abnormal/unreachable/abnormal`。
  **登记一处范围外事实**：存储不可用时**既有的** `/api/v1/status` **确实抛**（处理函数异常 → 连接被关、
  无响应，实测 `status=-1`），与聚合的 200 构成同进程对照；不在本 Task 改动范围（裁定只约束聚合端点），
  **只如实登记、不改它**。契约 +`/api/v1/health` 与 `AggregateHealth`/`DependencyStatus`，版本 `2026.09.24.1`。
  见 `evidence/task-08-health.md`。

- 2026-09-24 T-09：**唯一入口、`state` 必传、`-m` 下的记录名**（`wt-media-agent` `1f07cee`）——裁定二的
  「唯一初始化入口」从约定变成机器规则。删掉 `local_api/server.py` 那次重复的 `configure_from`
  （`bootstrap/app.py` 在 `build_components()` 里已经初始化过），新增 **R11**：
  `test_dependency_boundaries.py` 内除 `bootstrap/app.py` 外不得到达 `configure_from`/`configure_logging`，
  **符号拼写与模块拼写两条路径都认**（后者正是 T-08 那条假绿检查栽的地方）。规则今天就会红，
  删掉那行 import 转绿；三个反例在规则被改成 `return []` 时全红。
  **规则第一版太宽**：写成「除 `app.py` 外不得 import `runtime.logging`」时误报了
  `bootstrap/cloud.py:20` 引的纯函数 `redact`——会误报在跑的代码的规则，第一个被削掉的就是它，
  故收窄成点名两个初始化器与两条到达路径。第三个反例（「树里没有初始化器」）第一版与真实违规纠缠，
  改成对**每个文件**都删该行。
  **推翻计划的一处说法**：计划把 `state or LocalAgentState()` 写成「component 构造器成了第二个初始化点」
  ——裁定二的唯一性说的是 **Config 与 Logger**，`LocalAgentState()` 是内存状态，不是初始化点。
  真问题是：忘了传 state 的调用方拿到一个**看起来完全正常**的默认态（`agent_id="local-agent-dev"`、
  `status="idle"`），`/api/v1/status` 于是描述一个**没在跑**的 Agent 且毫无迹象。修法成立、理由改掉。
  同时复核更严重的失效模式**不成立**：`LocalAgentState` 是普通 dataclass、无 `__bool__`/`__len__`，
  传进去的 state 不会被 `or` 丢掉。`state` 在 `LocalApiServer` 与 `serve` 两处都改必传
  （照本文件 `bitbrowser` 的先例），连带 30 个测试构造点显式传 `LocalAgentState()`。
  **两处自查出的问题**：①`test_the_bitbrowser_client_must_be_supplied` 原本靠 `LocalApiServer()`
  断言 TypeError，state 也必传后这个 TypeError 改由 state 触发、测试名就不成立了 → 改为传 state 再断言；
  ②新写的 `serve` 用例第一版**直接调用 `serve(bitbrowser=…)`**，而在默认值还在时那会真的去
  `ThreadingHTTPServer(("127.0.0.1", 8765))` ——**开发者正在跑的 dev Agent 端口**（红跑当场报端口被占）
  → 改为读 `inspect.signature`，判据不许伸向 8765。
  ③`-m` 下的记录名（T-07 登记）：改用显式 `LOGGER_NAME = "wt_media_agent.local_api.server"`，
  它在 import 路径上的取值与 `__name__` **完全一致**，故三条生产入口零变化。
  测试 **354 OK**（T-08 后 345 → +9）。六个变异控制行先绿、各自打掉自己的用例；
  真机 `-m` 探针 **11/11**，把 `LOGGER_NAME` 变异回 `__name__` 后 A3/A4 **转红**
  （实测 `names=['__main__']`）——T-07 登记的缺陷是真的。
  **探针的解析器第一版自己空转**：找 `"]: "` 而真实格式是 `] <name>: `，一个名字都没解析出来，
  A3 因「没有东西可查」而通过；加分母并修解析后才成真检查（本 CHG 第三处「检查自己先坏了」）。
  **如实登记一处测不出差异**：第二次 `configure_from` 没有可观测的独立后果（`configure_logging` 幂等），
  故判据只能是结构性的 R11，不能声称有行为差异。
  见 `evidence/task-09-single-entry.md`。

- 2026-09-24 T-13：**Desktop 后端装配 + target 白名单 + 单行格式 + 脱敏**（`wt-media-desktop`，本 Task 的提交）——
  三个新模块：`logging::redact`（手写扫描器，**零依赖**，次序 `keyed → userinfo → bearer → jwt → known`）、
  `logging::targets`（`OWNED_TARGETS` 3 个 + `SUPERVISION_TARGET` 的 INFO 下限 + `Levels::filter()` 默认 `OFF`）、
  `logging::backend`（`assemble` 装配 `Registry` + 文件/终端两个 layer，**返回而不安装**，测试用线程局部注入）。
  **掩码点选在 sink**（成品行 → writer 的唯一收口），与 T-06 在 Agent 侧实测出的教训同一处：
  `Filter` 改不到 traceback。**与 Agent 的差分表 20 行实跑**：17 行逐字相同、3 行不同，
  三处根因都从 Agent 自己的代码读出——其中 **#13（一行里第二个凭据不掩）与 #16（复数 `cookies:` 只掩第一个值）
  是真泄漏**，登记为 **Q-08**（Agent 侧独立 Task，等你一句话）。
  变异 **12/12 红**，控制行先绿；探针查出并补齐三个缺口（其中 M2 是我自己表测先抓到的真 bug：
  值的尾巴被打印两遍）。`cargo fmt` 连带面如实登记：**本仓不是 rustfmt-clean 的**（重排 16 个文件），
  已逐文件量过是纯格式、备份成 patch + `stash@{0}` 后还原，全仓格式化不在本 Task。
  测试 116 → **144**；build 43 → **93** / clippy 48 → **97**（+50 全是新模块 `dead_code`；
  `rolling` 的 **−1** 已查明＝`Date::{year,month,day}` 因 `backend::stamp` 变活）。
  见 `evidence/task-13-desktop-backend.md`。

- 2026-09-24 T-12：**Desktop 日志文件的有界读写**（`wt-media-desktop` `66f8f02`）——`logging::rolling`：
  `date_of`/`fit`/`rotation`/`expired` 四条**纯规则**（`Clock` 注入）+ `Writer` 一处薄 IO（**永不 panic**）。
  裁定六的四条界（20MB / 14 天 / Desktop 100MB 总量 / 单条截断标记）与计划的五条逐条落成可单测的规则，
  覆盖面按条枚举在证据里。命名 `desktop-YYYYMMDD-N.log`——**每个文件都带日期、含正在写的那个**，因为
  两实例可能同时开着，稳定名会让两者写同一文件再由其中一个改走；`create_new` 抢名字是原子抢占。
  单条超限的标记与 Agent 侧**逐字相同**。测试 78 → 116；变异 25/25 红，并补齐两个探针查出的缺口。
  见 `evidence/task-12-desktop-rolling.md`。

- 2026-09-24 T-11：**Desktop 日志目录解析**（`wt-media-desktop` `f1edae6`）——`logging::paths`：
  `directory()` 纯函数（`home`/`environment`/`manifest_dir` 全注入）、`prepare()` 唯一 IO
  （建目录 + **真实写探测**，因为目录已存在时 `create_dir_all` 返回 `Ok`）、`LogDirectoryError` 不 panic。
  两套布局互斥且各有一条「只读一个输入」的断言（M2/M3 证明它能红）。`.gitignore` 补 `.local/`
  （`git check-ignore -v` 回报命中该条）。变异 8/8 红，并补齐两个缺口。
  见 `evidence/task-11-desktop-log-paths.md`。

- 2026-09-24 T-10：**Desktop 引入 `tracing` + `tracing-subscriber`**（`wt-media-desktop` `5194d49`，
  **两行依赖 + 一段说明注释，零源码改动**）——两处都关默认 features（`attributes` 会拖进过程宏；
  `env-filter`/`ansi` 会拖进 matchers、regex、nu-ansi-term）；不引 `tracing-appender`（它的 rolling
  表达不了 20MB 上限、总量预算与单条截断）。依赖树 267 → 271（+4 具名，移除 0），起点 68 条不动。
  见 `evidence/task-10-desktop-deps.md`。

- 2026-09-24 T-19：**测试不误连真实外部服务**（`wt-media-agent` `978155f`，**test-only，生产代码 0 行改动**）——
  新增 `tests/test_no_external_services.py`：两条通道（客户端构造必须注入 `transport`；`urlopen` 必须被
  patch）+ 5 处带非空理由的 `# network-ok:` 标记 + 按文件冻结的标记棘轮，11 条用例。
  修复一处真误报（`as urlopen` 绑的是 mock）并登记两个自查出的对照缺陷（读整树报告 → 假理由变红）。
  `bash scripts/test.sh` → **365 OK**（354 → +11）。见 `evidence/task-19-no-external-services.md`。

- 2026-09-24 T-20：**Agent 侧脱敏四处实测缺陷**（`wt-media-agent` `65725f4` + desktop doc commit `572d1cf`）——
  形态**两条正则按族分治**：`_TAIL_KEYED`（cookie / authorization，值 = 行尾）+
  `_VALUE_KEYED`（其余族，值 = 一个前导词元且**匹配在此结束**）。这条界是关键：`re.sub` 从整段匹配之后
  **续扫**，值吃到行尾就把后面的凭据一并吞掉——`token=aaa password=bbb` 只掩第一个正是这么来的。
  回显改用**原文字前缀**（`key+separator` 拼回会丢掉 JSON 键的闭引号 → 写出 `{"client_secret: "***"}`）；
  `_is_cookie_key` 认 `cookie` **与** `cookies`；两个回调各带族守卫 ⇒ 两趟**与顺序无关**。
  **先红**用「换回修前模块」证（`git archive HEAD` + `git show 978155f:…`，**不碰工作树**）：
  同一份用例 → **FAILED (failures=7)**（7 个失败 = 5 个用例，逐个点名），控制臂 **19 OK**。
  **20 行差分表的期望串是量出来的**（临时探针跑 Desktop + `git checkout` + sha256 `a3fad427…` 核对），
  断言从「两列」换成**整行精确串**（两列看不见形状错）。**变异 8 个**：M1–M5/M7/M8 KILLED
  （M1 连**既有** T-06 两列表的 7 条一起打掉）、**M6（换序）如实 SURVIVED——它就是「顺序无关」的证据**。
  **真机两臂**（同源副本、scratch 18769、两个死端口、5 次真实 POST）：修后三条泄漏针各 0，
  对照 payload 1 / 修前日志 2；**另三个针两侧都掩、修前日志不作对照**（脚本第一版共用对照当场报
  3 条 `CONTROL INVALID`，拆成两组各配能失败的对照）。`371 tests OK`（365 → +6）。
  **一处如实登记的代价**：整尾家族触达行尾 ⇒ `cookies:` 行后的 `group_id=g-1` 一并被掩（真机 8/10），
  **两侧一致**（Desktop 实测同三个串）且触达范围修前修后未变，只登记不改。见 `evidence/task-20-agent-redaction.md`。

- 2026-09-24 T-21：**Agent 请求级 `operation_id`**（`wt-media-agent` `5570906`，1 个 commit）——id 源
  `secrets.token_hex(8)` 在 `local_api/server.py`（`secrets` 已 import，`dependencies = []` 不变）、
  载体是 `runtime/logging.py` 的 `ContextVar`（不用 thread-local：`ThreadingHTTPServer` 每连接一线程，
  thread-local **今天碰巧能用**，请求里任何一段搬到执行器就失效）、边界覆写 `AgentHandler.handle_one_request`
  且 `try/finally` 复位——该位置 **upstream 于 `_check_auth`/`do_OPTIONS`/`send_error`**，故 401/404/
  畸形请求行**构造上**都带 id，且以后新加的 `do_*` 不会忘。字段经 formatter 的 `prepare` 盖上
  （**渲染槽名故意不叫 `operation_id`** ⇒ 调用方 `extra={"operation_id": …}` 不会被静默盖掉），
  无请求时渲染 `""` ⇒ 请求外的行**逐字未变**。`_single_line` 从 `_field` 提出供两者共用；
  `NoTracebackFormatter` 不再自带 `format`（只剩一行 `prepare` 调 `super().prepare`）。
  **先红分两步**（首次红是 ImportError，那种红什么都证明不了）：第 1 步字段机制 → **6 pass / 2 fail**，
  两个失败**恰是两条真 HTTP 用例** ⇒ 接线窟窿在行为上显形；第 2 步接线 → **8 OK**。
  **一个界测不到并如实登记**：`AgentHandler` 未设 `protocol_version`（实为 HTTP/1.0、答完即关，已核）
  ⇒ 按请求与按连接分配在真实 socket 上**产出相同的行**，故 M7（挪到 `handle`）**只**被结构用例
  `test_the_id_is_set_before_the_request_line_is_read` 打掉（该用例 docstring 自陈弱于行为断言，
  并说明它代表的 401/404/畸形请求行没有文件可落）。**变异 9/9 KILLED、0 SURVIVED**（控制行 379 OK
  先绿，锚点不唯一即跳过不算 KILLED）；M2 固定 id、M6 `reset` 改清空、M8 永不复位、M9 id 进响应头
  各自打掉**行为**用例。**真机两臂**（同源、scratch 18771、死端口 18792/18793、各 2 次真实 POST 各 502
  ⇒ 每次请求 **2 条**记录）：修后 4 条带 id、同请求同 id、两次不同、**进程自己的启动行不带**；
  **对照臂（`git archive HEAD src`）同一个针命中 0/5** ⇒ 针会失败；且**去掉该字段后修后每一行与修前
  逐字相等**。**379 tests OK**（371 → +8）。三条登记：① SSE 整条流共用一个 id；② contextvar
  **不跨线程**（实测：同一请求里另起线程写的记录不带 id，`runner.task` 仍靠 `task_id`）；
  ③ `error.log` 的 id 是 D-03 五字段之外的**第六个**可选字段（裁定六）。见
  `evidence/task-21-agent-operation-id.md`。

## Current

- T-21 已收尾（`wt-media-agent` `5570906` + 本记录）；**Agent 与 Desktop 两侧代码半都已完成**，
  只剩阶段 3 的 **T-18** 回写与归档收尾。

## Next

- **T-21 的三条登记要进 T-18 的 §7/§10**：① SSE 整条流共用一个 id（有意：id 的单位是「一次请求」）；
  ② 关联**仅请求内、处理线程内**——contextvar 不跨线程（实测），`runner.task` 的记录仍靠 `task_id`；
  ③ 分配边界的**位置**与 `finally` 顺序只有**结构覆盖**（`protocol_version` 未设 ⇒ HTTP/1.0 ⇒
  按请求与按连接在线上不可分，M7 只被结构用例打掉）。
- **T-17 的三条新登记要进 T-18 的 §7/§10**：① 退出报告（`drain::report_exit`）**有意不带 `operation_id`**
  （进程退出时会话可能已被清除，同一记录类型「有时带有时不带」比一律不带更误导）；② `already_running`
  带 id 的形态**只在单测表里**（真机臂每次都先 stop 再 start，槽位总是空的）；③ **两侧的 id 不相关**
  ——Desktop 的 id 标识「一次 Desktop 监督的会话」、T-21 的 id 标识一个请求，来源与粒度都不同，
  本 CHG **不**做跨端对照（D-10 不变）。
- **T-17 的一条环境事实复述**（T-16 已登记，T-17 再次撞上并沿用同一绕法）：debug 二进制带 `cfg(dev)` ⇒
  窗口加载 `devUrl` 而非 `frontendDist`，没有 Vite 时窗口整页空白 ⇒ 真机臂只能靠**探针页替身**驱动命令层，
  真前端未跑。
- **T-16 的三条新登记要进 T-18 的 §7/§10**：① **AC-09 的真机分母是 1 行**不是 50（那 1 行确实是
  sidecar 输出、确实只出现在退出报告的尾行里；规模只由单测证）；② **`start` 的 spawn 失败分支在本地这棵树
  够不着**（随应用提供的 sidecar 存在且能 spawn 成功，只是运行期因 macOS Team ID 起不来 ⇒
  「找不到 sidecar」与「python 回退起不来」两条 `Err` 都到不了）；③ **`already_running` 在 sidecar 自己
  死掉之后仍会说「已在运行」**（托管状态里的 `CommandChild` 不会因进程退出被清掉）——**既有行为**，
  本 Task 只是让它第一次可听见，改它要动 `drain` 与 `AgentProcess` 的耦合，超出 T-16 范围。
- **一条给下一个人的环境事实**（不是缺陷，别当 bug 修）：`cargo build`（debug）带 `cargo:rustc-cfg=dev`
  ⇒ 窗口加载 `devUrl`（`127.0.0.1:5174`）而**不是** `frontendDist`；没起 Vite 时窗口空白到连静态 HTML
  都不渲染。要让真前端在本地跑，得 `npm run dev:desktop`（T-16 用探针页替身取证，真前端未跑）。
- **T-15 的两个新登记要进 T-18 的 §7/§10**：①`level` 严于 INFO 时 **stderr 与文件一起静默**
  （两层共用同一个 filter，实测；计划只预测「不建文件」）；②`main.rs` 的**两个实参无测试守**
  （N8/N9），其中 N9 由臂 1 的真实启动守、N8 分母为 0（无记录携带 token）。
- **Agent 侧脱敏已由 T-20 修完**（`65725f4`，四处实测缺陷全部关闭）：§7 **Q-07** 的三处（一行里第二个
  凭据不掩；复数 `cookies:` 键只掩第一个值；JSON 键的闭引号被吃掉 ⇒ 行不再合法）**加上 T-13 之后新发现的
  第四处 d**（形似键 `mytoken=` 吞掉整行、遮蔽被静默关掉）。**但 Q-07 的行文本身仍按旧行为描述**
  （它把两处列成「实测输出」），**T-18 须整体改写这一行**（关掉它或改写成「已由 T-20 修」），
  否则读者会以为那两处还漏。见 `evidence/task-20-agent-redaction.md` 与 `evidence/task-13-desktop-backend.md` §2/§7。
- **T-20 的两条登记要进 T-18 的 §7/§10**：① **整尾家族的触达是行尾**——`cookies:` 行之后的
  `group_id=g-1` 会与 cookie 头一起被掩（真机 8/10 条记录带它，缺的 2 条正是 `cookies:` 那两条）；
  该行为**两侧一致**（同样三行在 Desktop 实现上实测返回逐字相同的串）、**修前修后触达范围未变**
  （改变的只是掩得全不全），故**只登记、不改任何一侧的答案**——改一侧是有意对「两侧早已一致回答过」
  的问题单方面改答案，不属本 Task。② `error.log`/`task.log` 两条臂**未在 T-20 重跑**：四个缺陷同在
  同一个 formatter 路径上（三文件共用 `redact`），路由未改；但「三文件里的凭据不在」这一点，
  本 Task 只由单测表 + `agent.log` 臂覆盖，**不声称三文件逐条重跑过**。
  （注：T-13 的证据与上一版 checkpoint 把这个 ID 写成 `Q-08`，而 `change.md` §7 里它是 **Q-07**；
  §7 另有一段说明 `Q-08` 这个 ID 早先被 T-19 行与 AC-11b 用作 Q-05 内容的别名。T-18 统一编号时一并收口。）
- **T-15 的待验期望已被实测取代**：登记的「93 → 4 / 97 → 10」**不成立**，实测 **93 → 9 / 97 → 13**，
  差的 5 条是 `rolling` 现在**只在测试里**被引用的项（`SHIPPED`/三个 `DEFAULT_*`/`open_path`），
  根因 T-14 已按计划把配置文件变成四个数字的来源。**这条期望不再作为后续 Task 的判据**，
  T-16/T-17 不再引用它；新增代码的 lint 判据改为「增量逐文件核对、新文件里 0 条真 lint」。
- **访问 crates.io 必须带 `HTTPS_PROXY=http://127.0.0.1:7897`**（T-10 查明的根因：本机直连的证书被劫持）。
- **T-09 新增一项**（T-07 顺带实测）：`python -m wt_media_agent.local_api.server` 使 `getLogger(__name__)`
  得名 `__main__`，真实运行的 HTTP 侧记录看不出组件来源——削弱「日志可定位问题」，属 T-09 范围。
- **T-19 已完成**（`978155f`，test-only）：AC-11b 的 AST 规则——客户端构造必须注入假 `transport`、
  `urlopen` 必须被 patch；**编号排末位**以免打乱 T-03…T-18。它给 T-21 留下一条约束：
  **新测试里不用 `urlopen`**（用 `http.client`），否则会被这条规则判红。
- **定向验证命令一律带 `PYTHONPATH=tests`**：`tests/` 无 `__init__.py`，`python -m unittest tests.<模块>` 对
  6 个 import `support` 的模块（5 个是既有的）报 `ModuleNotFoundError`。既有布局属性，本 CHG 不动布局。
- 阶段 2 Desktop：T-10 ✓ → T-11 ✓ → T-12 ✓ → T-13 ✓ → T-14 ✓ → T-15 ✓ → T-16 ✓ → T-17 ✓（**本阶段完成**）。
- 阶段 2 Agent 补做：T-20 ✓（脱敏，`65725f4`）、T-21 ✓（请求级 `operation_id`，`5570906`）——
  由用户本次裁定新开，**两者均已完成**。
- 阶段 3：T-18 回写与收尾（**下一步，仅此一项**）。

## Blockers

- None。裁定十三节已把草案的待决项全部定下；§7 的 Q-01…Q-04 均为 `Blocking = NO`，已按读数实施。

### 工作区里不属本 CHG 的既有改动（**不被本 CHG 提交**）

T-11 收尾时工作区另有一组**与本 Task 无关**的改动，`mtime` 晚于上一提交（14:51 vs 14:49），
内容是对入口文档的一次成体系改写：`AGENT-INDEX.md`（+207/-…）、`AGENTS.md`（大幅删减）、
`CLAUDE.md`、`README.md`、`docs/engineering/specs/agent-workspace-conventions.md`。

**不是本 CHG 写的，因此不并入本 CHG 的记录提交**——「一仓一 commit」与「diff 检查越界改动」都要求
把它们分开。两个验证器在**带这组改动的工作区**上仍报绿（`verify_agent_entry` 0 warning、
`verify_delivery_governance` Active CHG 一致），故不构成阻塞。

登记在此是为了：**T-18 的「入口文档回写」开始前必须先看这组改动是否要保留**，否则会覆盖掉它。

## Recent verification

- T-21：`bash scripts/test.sh` → **379 tests OK**（371 → +8 = 新模块 8 个用例，**只增不减**）；
  `PYTHONPATH=tests python3 -m unittest tests.test_log_operation_id` → **8 OK**。
  **先红分两步**（首次红是 ImportError，按既有规则那种红不算数）：第 1 步字段机制 + 两个 `FMT` 槽位 →
  **6 pass / 2 fail**，两个失败**恰是两条真 HTTP 用例**（`…each_request_gets_its_own_id…`、
  `…the_id_is_set_before_the_request_line_is_read`）；第 2 步加 `handle_one_request` 覆写 → **8 OK**。
  **变异 9 个**（`/tmp/t21_mutate.py`，控制行 379 OK 先绿，逐次改一处、跑完即从 pristine 副本还原，
  锚点不唯一即报 `ANCHOR PROBLEM` 跳过且**不算 KILLED**——M1/M7 第一版锚点就是错的，改对后才有判定）：
  M1 完全不设 id / M2 整进程固定 id / M3 `FMT` 去槽 / M4 `ERROR_FMT` 去槽 / M5 id 挪到 `error_code` 之后 /
  M6 `reset` 改清空 / M7 挪到 `handle`（按连接）/ M8 永不复位 / M9 id 进响应头 →
  **9/9 KILLED、0 SURVIVED**，各自打掉自己的用例并逐个点名。
  **M7 只被结构用例打掉**，这是「分配边界的位置在线上不可分」的实测（`protocol_version` 未设
  ⇒ HTTP/1.0、答完即关，已核），已登记。
  **真机两臂**（`/tmp/t21/real_arm.sh`；scratch 端口 **18771**，BitBrowser/Cloud 指向死端口 18792/18793，
  各 2 次真实 `POST` 各得 `502` ⇒ **每次请求 2 条**记录，比单条更能证明 id 按请求分组）：
  臂 A `WS=/tmp/t21/pre`（`git archive HEAD src`，修前）、臂 B `WS=/tmp/t21/ws`（工作树副本）——
  修后 4 条请求记录带 16 位十六进制 id、同请求同 id（`927a813c8e69b04c`）、两次不同
  （`925cc1c99adc2bce`）、**进程自己的启动行不带**；
  **对照臂同一个针命中 0/5** ⇒ 针会失败；去掉 id 字段后**修后每一行与修前逐字相等**。
  `/tmp/t21/assert_arm.py` → **ALL ASSERTIONS PASS**；跑完 `left listening: 0`，
  全程**未碰** `:8765`/`:18080`/`:54345`。
  跨线程实测（`/tmp/t21/threads.py`）：同一请求里另起线程写的记录**不带** id。
  见 `evidence/task-21-agent-operation-id.md`。

- T-20：`bash scripts/test.sh` → **371 tests OK**（365 → +6 = 新类 6 个用例，**只增不减**）；
  `logging.py` sha256 `d82d52efaa5f63351477abf64ebd4970c365dbd61c4147e643ba3c22db8251cd`（= `65725f4`），
  `git status --porcelain` 空。**先红**在 git 对象上做（`git archive HEAD` + `git show 978155f:…logging.py`，
  不碰工作树）：`/tmp/t20/red` → **FAILED (failures=7)**（7 个失败 = 5 个用例：
  `every_row_matches_the_desktop_reference` 3 条 subTest + `the_three_rows_that_used_to_differ_are_named` +
  `the_json_row_is_still_json` + `the_tail_families_reach_the_end_of_the_line_on_both_sides` +
  `a_lookalike_key_no_longer_hides_the_credential_behind_it`），控制臂 `/tmp/t20/ctl` → **19 OK**。
  **变异 8 个**（`/tmp/t20_mutate.py`，控制行 371 OK 先绿，逐次改一处、跑完即从 pristine 副本还原）：
  M1 值组改回 `[^\n]*` / M2 复数 / M3 回显重建 / M4 守卫丢非敏感半 / M5 守卫丢家族半 / M7 整尾趟不跑 /
  M8 cookie 尾只吃一个词元 → **全部 KILLED 且各自打掉自己的用例**；**M6（两趟换序）SURVIVED**——
  **有意**，它就是「两趟与顺序无关」这条声明的证据，不为它补一条把实现细节写死的用例。
  **真机两臂**（`/tmp/t20/real_arm.sh`；scratch 端口 18769，BitBrowser/Cloud 指向死端口
  18790/18791，5 次真实 `POST` 各得 `502`，body 落 `requests.out` 供对照）：
  `/tmp/t20/assert_arm.py` → **ALL ASSERTIONS PASS**——三条泄漏针 `bbb`/`b=2`/`password=zzz` 在修后
  `agent.log` 里各 **0**、对照 payload **1** / 修前日志 **2**；另三个针 `aaa`/`a=1`/`s3cr3tvalue` **两侧都掩**，
  修前日志**不作对照**（脚本第一版共用对照当场报 3 条 `CONTROL INVALID`，故拆两组）；周围文本 7 项仍在
  （`name=` 10、`start`/`failure` 各 5、`error=` 4、`duration_ms=` 4、`plain-name-with-no-secret` 2、
  `mytoken=abcdefghijkl` 2）；`group_id=g-1` **8/10**（缺的两条正是 `cookies:` 那两条，已登记）。
  跑完 `lsof -nP -iTCP:18769 -sTCP:LISTEN` 为空、无残留进程，全程**未碰** `:8765`/`:18080`/`:54345`。
  Desktop 侧 `cargo test --workspace` → **175 passed**（未增，本 Task 未动 desktop 代码）；
  `572d1cf` 只改注释（过滤注释行后 diff 为空；`redact.rs` 测量时 sha `a3fad427…` → 现值 `c47e5aca…`）。

- T-17：`cargo test --workspace` → **175 passed; 0 failed**（166 → +9 = `state` 3 + `commands/agent` 5 +
  `http/local_agent` 1，**只增不减**）；`cargo build` 条目级警告 **9 → 9**、clippy `--all-targets` **13 → 13**
  （**未增**）。`rustfmt --edition 2021 --check --config skip_children=true`：`state.rs` **整文件 0 处差异**，
  `commands/agent.rs` **8 处既有脏行**（改动前 9，因我改动而变长的三行按 rustfmt 写法顺手改掉；**未**整文件重排）。
  变异 **R1–R3 + M1–M5 全部 KILLED**（控制行 175 passed 先绿；R2/R3 成对），**N1/N2 如实 SURVIVED**
  ——`start` 里的 `begin(...)` 与 `stop` 里的 `ended(...)` 各一行调用点单测进不去（要 `AppHandle` / 真
  `CommandChild`），**只由真机臂覆盖**。
  真机臂（探针页 + scratch 端口 18767 的 stub，**不是 8765**）：两个会话、六条 `agent.supervisor` 记录，
  5 条带 id（`1190a95e…` / `f386572a…`，**两个不同值**）、1 条不带（stop 之后的 health ⇒ `clear` 真的跑过）；
  探针打印的六条返回值**一条都不含 id**（id 不出进程）；`stop` 后立即 `start` 得**新 id**（不跨会话复用）；
  退出报告两条**都没有 id**（有意为之）。脚手架逐项还原（`index.html` 的 sha256 `e568216d…` 与备份逐字相同、
  5174/18767 无监听残留、无残留进程、未碰 `:8765`/`:18080`/`:54345`、未向仓库配置写代理）。
  二进制在两次启动前核对过 mtime（晚于最后一次源码改动）。

- T-16：`cargo test --workspace` → **166 passed; 0 failed**（153 → +13 = drain 4 + webview 2 + agent 7；
  agent 那 7 条 = 生命周期全表 1 + 记录文案与返回串 3 + **真实套接字上**的命令体 3，其中 health 成功那条
  发的是真 HTTP 请求（端口 0，内核分配）；`cargo build` 条目级警告 **9 → 9**、clippy `--all-targets`
  **13 → 13**，13 条**逐条列出**（`rolling.rs` 5 + 四个占位 struct 4 + `main.rs:45` + `account.rs` 2 +
  `drain.rs:284`）**无一条落在新增代码上**。
  变异 **13 个全部 KILLED 且各自打掉自己的用例**（3 个旧形态回退 R1–R3 + 10 个新形态 M1–M10，
  控制行 166 passed 先绿，每次从 pristine 副本还原）。
  真机两臂（真实二进制 + **探针页**，因为 debug 构建加载 `devUrl`）：
  臂 B 无 stub → `已启动（sidecar_started）` / 退出码 255 的退出记录（**含** sidecar 那 1 行）/
  `agent unreachable: …`（**不含**尾行）/ `已停止`，前端那条串**含**尾行 ⇒ 裁定五一屏对照成立；
  臂 C 用 stub 占住 scratch 端口 18766 → start / already_running / `[DEBUG] 健康检查成功：{"status":"ok",…}` /
  stopped / not_running 五条，与前端返回值逐条对应。
  脚手架全部还原（`index.html` 的 `shasum` 逐字相同、5174/18766 无监听残留、进程全清）。
  `rustfmt` 只对新文件 `logging/test_support.rs` 整文件跑，四个既有文件只手改。
  见 `evidence/task-16-desktop-emit-points.md`。

- T-15：`cargo test --workspace` → **153 passed; 0 failed**（147 → +6：`setup.rs` 5 条 + 手写对表 1 条；
  环境两向那条在拆分后由 `plan` 承担并改名，是改名不是新增）；`cargo build` 条目级警告 **93 → 9**、
  clippy `--all-targets` **97 → 13**——**与登记期望不符，差的 5 条逐条点名**（`rolling.rs` 的
  `DEFAULT_MAX_FILE_BYTES`/`DEFAULT_RETENTION_DAYS`/`DEFAULT_TOTAL_BYTES`/`SHIPPED`/`open_path`，
  现在只在测试里被引用），另 4 条是既有桩（filesystem/secure_store/system/updater），
  clippy 的 13−9=4 全是既有项（`main.rs:45`、`account.rs` ×2、`drain.rs:212`）⇒ **本 Task 新增代码 0 条 lint**。
  变异 **两轮 22 个**（控制行两次先绿，每次从 pristine 副本还原）：第一轮 12 个（4 个起初存活）、
  第二轮 10 个（拆分后重跑，3 个幸存且**逐条登记守卫方式**）。
  真机三臂（真实二进制、每次先清开发态日志目录）：臂 1 摘要入 stderr **且**入
  `src-tauri/.local/logs/desktop-20260924-1.log`（249 字节，首条即摘要）；臂 2 占住目录仍启动、不 panic；
  臂 3 `warn` 0 条 stderr / 不建文件 vs 对照 `info` 1 条 / 255 字节。
  `rustfmt` 只对新文件 `setup.rs` 整文件跑（新文件无既有脏行），`main.rs` 未跑全文件格式化，
  `git diff -U0` 的删除行只有那一条 `eprintln!`。
  见 `evidence/task-15-desktop-main-wiring.md`。

- T-14：`cargo test --workspace` → **147 passed; 0 failed**（144 → +3：出货值漂移 1 + 级别正向/词表钉死 2；
  原有的 `unknown_key_is_rejected...` 由顶层单点改为**逐节枚举**，用例数不变而覆盖面变宽）。
  `cargo build` 条目级警告 **93 → 93**、clippy `--all-targets` **97 → 97**——**测量结果，不是默认**：
  新增的 `LOG_LEVELS`/`LOG_LEVEL_AUTO` 都被 `validate()`（非测试代码）引用，`Logging` 的字段由 derive 读写，
  故没有新增 `dead_code`；T-15 的期望起点 **93 → 4 / 97 → 10** 未被本 Task 移动。
  变异 **9/9 红**（控制行 147 passed 先绿），M6/M9 两个缺口当场补齐（见 §Completed 的 T-14 条）。
  `rustfmt` 只对本文件跑，**逐行比对**其输出与我的版本：差异只有 7 处**既有脏行**（本仓不是 rustfmt-clean 的，
  T-13 已量化），已全部还原 ⇒ 本 Task 的 diff 里没有一行与 T-14 无关的重排。
  见 `evidence/task-14-desktop-logging-config.md`。

- T-13：`cargo test --workspace` → **144 passed; 0 failed**（116 → +28：redact 8 / targets 8 / backend 12；
  `logging::` 过滤 **76 passed**，144 − 76 = 68 = 起点）；`cargo build` 条目级警告 **43 → 93**、
  clippy `--all-targets` **48 → 97**，增量逐文件核对（redact 32 + backend 13 + targets 5 = +50，别的文件 0 增），
  且 `97 − 93 = 4` 条非 `dead_code` 全是既有项（account ×2、main ×1、drain ×1）——**新模块里 0 条真 lint**。
  那 **−1**（`rolling` 32 → 31）**已查明根因**：临时撤掉 `logging/mod.rs` 的三行 `pub mod` 复现出 T-12 状态
  （build **43** / clippy **48**，与 T-12 证据逐字一致），差的那条是 `` Date::{year, month, day} is never used ``
  ——`backend::stamp` 用了它，正好是「后端真的接上了 `rolling`」的独立证据。
  变异 **12/12 红**（控制行 76 passed 先绿，每次还原都 sha256 核对）；
  差分表 **20 行实跑**（Agent vs Desktop，17 同 / 3 异，三处根因都从 Agent 源码读出）。
  见 `evidence/task-13-desktop-backend.md`。

- T-12：`cargo test --workspace` → **116 passed; 0 failed**（78 → +38）；`cargo build` 条目级警告
  **12 → 43**、clippy `--all-targets` **18 → 48**，增量**全是 `rolling.rs` 的 `dead_code`**（逐文件核对：
  rolling 31 + paths 8 + 既有存根 4 = 43，没有一条来自别的文件）。
  变异 **25/25 红、控制行先绿**，探针 sha256 核对还原（`c3301b6334b3` 与提交文本一致）。
  **探针查出两个缺口并补齐**：**M13 第一版编不过**（临时值借不到 `&str`）——记成 `NO-COMPILE` 是对的，
  编译失败的变异证明不了任何事，改成可编译的等价变异后转红；**M23 起初全绿**——`rolled_by_us` 只在
  「总量界要删一个今天的文件」时起作用，原有用例要么总量宽、要么删的是昨天的，补了
  `a_file_this_writer_rolled_today_is_reclaimable_under_pressure`（20B 单文件 + 30B 总量，算出第 5 条
  写入时删 `-1` 停在 `-2`）才红。
  **两处 clippy 真意见当场改掉**（`Send + Sync` 是 `Clock` 超 trait 已保证的；测试里 `x + 1 <= 字面量`
  的写法），clippy 条目数 51 → 48。
  **如实登记一处未覆盖**：跨午夜的第二个实例——它在昨天启动、现在还在跑，其活文件日期是昨天，
  而昨天的文件无论谁写的都是历史，故会被按天删。writer 无法区分对端的活文件与历史，不假装解决了。
  见 `evidence/task-12-desktop-rolling.md`。
- T-11：`cargo test --workspace` → **78 passed; 0 failed**（68 → +10）；`cargo build` 条目级警告
  **4 → 12**、clippy `--all-targets` **10 → 18**，**+8 全是新模块的 `dead_code`**（调用方在 T-15）。
  变异 **8/8 红、控制臂先绿**；探针查出两个缺口并补齐：**M8**（`create_new` 与 `create` 只差在
  「崩溃后留下探测文件」这一种情形）补了 stale-probe 用例才红；**M7** 起初看着像等价变异，
  **一量发现不是**——macOS 实测 `create_dir_all` 撞到被文件占住的路径报 `AlreadyExists`，
  绕过它让探测去撞得到的是 `NotADirectory`，故 M7 是把根因换成了下游原因，断言改成实测的 kind 后转红。
  **M6 多红一条的根因也量了**：只读目录里**打开已存在的可写文件是成功的**，只有 `remove_file` 会失败，
  M6 删的恰是那一步 ⇒ 属诚实耦合。只读那一臂在本机**真的跑了**（`--nocapture` 无 skip 行）。
  见 `evidence/task-11-desktop-log-paths.md`。
- T-10：`cargo test --workspace` → **68 passed; 0 failed**（与改前逐字相同，本 Task 按计划不加测试）；
  `cargo tree --no-dedupe` 具名节点 **267 → 271**，**恰好 +4 且具名**、移除 0；阴性对照
  `nu-ansi-term`/`matchers`/`tracing-log`/`tracing-attributes` **全 0**，而 `regex`/`smallvec`
  **改前就在树里**（不计入我们的开销）；clippy 警告 **10 → 10**（用 `git stash` 取改前读数）。
  **一次阻塞先查根因再定性**：`cargo add` 报证书过期——实测直连 `index.crates.io:443` 落在一张
  `CN=YE1`、`notAfter=Sep 20 2026` 且**主题名不匹配**的证书上（被劫持，早于施工日 4 天过期），
  而经开发者本机代理 `127.0.0.1:7897` 取 `config.json` 与 `tracing-subscriber-0.3.20.crate`
  **均 200**。`curl` 与 `cargo` 都不读 macOS `scutil --proxy`，故两者都走了坏路。
  修法 = 调用时带 `HTTPS_PROXY`，**仍是官方后端**（未换实现），且**不写进仓库配置**。
  见 `evidence/task-10-desktop-deps.md`。
- T-19：`bash scripts/test.sh` → **365 tests OK，exit=0**（354 → 365，只增不减）；`.local/` 守卫不响；
  **先量分母再写结论**：计划写「41 处 / 34 模块」，实测 **40 模块 / 38 处客户端构造 / 3 处 `urlopen`**
  ——41 是后两类之和（计划的分类粒度不同），**模块数是真的偏低**，按实测登记。
  规则第一次跑就报出 **5 处真命中**，且**五处都不该改代码**（3 处打的是刚起的 loopback server，
  2 处真实传输就是被测对象）→ 走 `# network-ok:` 标记通道，理由必须非空，按**文件**冻结计数
  （按行号会因上方任何编辑而失效，棘轮红的理由届时没人能处理）。
  变异表：控制臂先绿，**7 个变异逐个红**（真实文件逐次破一处，用 monkeypatch `test_files()` 跑真的那 11 条），
  三条真断言 **A1/A2/A3 各自都有变异能红它**（A1 ← M7 扫描只剩 1 个文件；A2 ← M1/M2/M3/M4/M6；A3 ← M1/M2/M5/M6）。
  **两处自查出的问题**：①一处**真误报**——`with mock.patch.object(urlrequest,"urlopen") as urlopen:`
  之后 `urlopen()` 调的是 mock，规则按函数名判定，把驱动假传输最干净的写法判成联网；改为解析名字在
  该作用域的绑定（`as`/参数/赋值 → local 跳过，import → 照报），并修掉「顺序决定判定」与
  「模块级被兄弟函数的绑定开脱」两个次生问题。②**两个对照读整棵树的报告**，于是 M1/M2/M6 这类
  真实树变动会让它们为**假理由**变红——看起来和控制臂正常工作一模一样；已改成只读自己种的那个文件。
  改后仍会红的只剩 M3/M4，那是把违规种进了同一个文件，属诚实耦合，**如实登记不掩盖**。
  规则看不见的四种形态（经助手到达网络 / 构造了但不调用的外部 URL / `os.system`、裸 socket / 假传输有没被用）
  写在文件头。见 `evidence/task-19-no-external-services.md`。
- T-09：`bash scripts/test.sh` → **354 tests OK，exit=0**（345 → 354，只增不减）；`.local/` 守卫不响；
  六个变异各自打掉自己的用例（控制行先绿）；R11 三个反例（含「规则被改成 `return []` 时全红」）；
  真机 `-m` 探针 11/11 且变异后 A3/A4 红。见 `evidence/task-09-single-entry.md`。
- T-08：`bash scripts/test.sh` → **345 tests OK，exit=0**（320 → 345，只增不减）；`.local/` 守卫不响；
  12 个变异**全部转红**（控制行先绿，探针先跑未变异对照行）；真机两臂 **20/20**；
  契约只用 `ruby -ryaml` 验可解析 + 路径/schema 齐全（本仓**无** openapi 校验器，如实登记）。
  见 `evidence/task-08-health.md`。
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
