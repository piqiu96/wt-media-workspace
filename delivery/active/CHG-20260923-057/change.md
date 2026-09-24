# CHG-20260923-057：联合工程优化 B——Paths、Logger 和运行目录

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING（2026-09-24 激活；此前为 planned 下的 PLANNED 草案，见 §12）
- Created: 2026-09-23
- Current repository: wt-media-workspace（治理）；运行时改动分布于 wt-media-agent、wt-media-desktop
- Affected repositories: wt-media-agent（主）、wt-media-desktop（主）、wt-media-workspace（治理记录与基线回写）
- 不受影响并已声明：wt-media-cloud

## 2. Change Goal

完成上线前工程优化第二阶段（B）：建立 Desktop 与 Agent **各自独立、可靠、可维护**的日志体系，
满足本地开发、Desktop sidecar、正式上线后的故障定位与长期运行要求。

用户可见的独立可验证结果：

1. Agent 可**脱离 Desktop 独立启动并产生日志**：`agent.log` / `task.log` / `error.log` 三文件真实落盘，
   轮转、按天保留、总量受限，单条超长记录被截断且标出原长度。
2. Desktop **正式启动产生自身日志**：`~/Library/Logs/WTMedia/Desktop/`，记录启动退出、配置加载、
   Agent 启停与健康检查、sidecar 异常退出；**不**转存 Agent 业务日志。
3. Config 与 Logger **各只初始化一次**，由启动流程（bootstrap）负责，server/component/executor 都不得再初始化。
4. 日志目录不可写时降级为仅 stderr，且**不阻断程序启动**。
5. 敏感信息（Cookie / Password / Authorization / Bearer / Refresh / Agent Runtime Token / 代理密码 / 完整 Secret）
   **不进日志**；敏感对象不默认 `Debug` 输出。

**本 CHG 不交付的事项里最重要的一条**：跨端 `operation_id` 串联**不交付**——Desktop **不发**
`X-Operation-Id`、Agent **不消费**任何此类头。两端各自进程内的关联是本 CHG 的全部交付。

## 3. Baseline References

- Milestone: `delivery/milestones/M-launch-engineering.md#成功事实全部成立`
  （本 CHG 的验收锚点是**成功事实 #5**：「日志独立落盘、轮转、受容量限制；敏感信息（Cookie/Token/代理密码）
  不进日志与诊断包」。失败行为锚点：「测试误连真实外部服务产生副作用」——见 T-02。）
- Engineering baseline: `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md`
  §3 CHG-B（范围）；§「改造原则」`:20`；§「敏感信息永不进日志」`:63`；§「验收不以编译通过…为准」`:64`
- Engineering baseline（架构）: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
  §5.8 `:1146-1181`（本地目录和日志）、§5.6 `:1125-1130`（health 双端点）、§5.13 `:1245-1258`（测试隔离）、
  §6.8 `:1399-1413`、§7.11 `:1638-1646`、§8 禁止项 `:1692` 第 20 条「敏感信息进入普通日志」
- Decisions: ADR-0016（Agent 运行时分层与配置目录）；`docs/contracts/ownership.md:15/:20`
  （Local Agent API 归 wt-media-agent；Desktop 不定义正式跨仓契约）
- **用户书面裁定**: 2026-09-24《CHG-057 日志治理裁定补充说明》十三节——本 CHG 的**最高权威**，
  高于程序总纲与任何草案。§6 的 D-01…D-08 逐条来自它。
- 里程碑说明：属上线前联合工程优化里程碑（M-launch-engineering），不属 M2/M3；不改变已验收业务闭环。

## 4. Current Facts

全部为本次**实测**（`file:line` 可核），不是计划推定。**这些事实推翻了本 CHG 草案的多处预想**，故单列。

### 4.1 A 阶段已完成、本 CHG **不再重复**的部分

- Agent 运行目录**已由 CHG-056（A）做完**：`src/wt_media_agent/runtime/paths.py` 已有三态
  （`override`/`dev`/`installed`）+ 懒创建 + 失败降级（`ensure()` 明写 "Never raises"），
  装态已按 §5.8 分 `~/Library/Application Support/WTMedia/Agent/` 与 `~/Library/Logs/WTMedia/Agent/` 两棵树
  （`paths.py:26-27`）。
- sidecar stdout **已由 A 做完**：`src-tauri/src/sidecar/drain.rs` 已持续 drain + `CAPACITY = 200`
  行环形缓冲（`:31`）+ 退出时报告尾 `TAIL_ON_EXIT = 20` 行（`:33`）。

### 4.2 Desktop 日志**从零**（不是「加轮转」）

- `src-tauri/Cargo.toml` 的 `[dependencies]` **没有** `tracing` / `tracing-subscriber` / `tracing-appender` /
  `log` / `tauri-plugin-log`。仓库根 `Cargo.lock` 里 `tracing 0.1.44`(`:3946`)、`tracing-core 0.1.36`(`:3956`)
  **只是** `h2 0.4.15`(`:1232`)、`hyper-util 0.1.20`(`:1387`)、`softbuffer 0.4.8`(`:3135`) 的传递依赖。
- 全 `src-tauri/src/` 只有 **5 处**裸 emit（这就是今天 Desktop 的全部日志面）：
  `main.rs:65`（启动摘要，`eprintln!`）、`sidecar/drain.rs:158`（sidecar 退出报告，`eprintln!`）、
  `commands/logging.rs:7` 与 `:9`（webview，`println!`）。第 5 处 `config.rs:209` 是注释，不是 emit。
- `src/` 无任何日志初始化入口、无日志文件、无级别概念。
- 启动序（`main.rs`）：`:62` `generate_context!` → `:63` `bootstrap::resolve`（配置落定）→ `:64` `apply_csp`
  → `:65` `eprintln!` 启动摘要 → `:71` token → `:73-82` `.manage` → `:83` `.setup`（空实现）→
  `:94` handler → `:116` shell plugin → `:117` `run`。
- `src-tauri/src/paths.rs` 是**配置文件定位器**（`CONFIG_ENV`、`RESOURCE_NAME`、`Source`、`candidates`、
  `locate`、`file_text`），**没有任何运行目录/日志目录概念**。程序总纲 CHG-A 段提到的 `AppPaths`
  **在 A 的交付里不存在**——本 CHG 只补**日志目录**（见 D-06 与 Q-01）。
- Desktop 仓 `.gitignore`（仓库根，11 行）有 `*.log`，**无** `.local/`。

### 4.3 Agent 日志现状：一个文件，三文件与结构化字段都不存在

- `src/wt_media_agent/runtime/logging.py` 是全仓**唯一**接触 logging 配置的模块（`:80` 的
  `logging.config.dictConfig` 是唯一一次调用）。handler 只有两个：`StreamHandler`（`:42`，stderr）与
  `RotatingFileHandler`（`:50`，`maxBytes = 10 * 1024 * 1024`、`backupCount = 3`）。
- formatter（`:37-38`）：`"%(asctime)s [%(levelname)s] %(name)s: %(message)s"`，datefmt `%Y-%m-%dT%H:%M:%S`。
- **全仓 `task.log` 与 `error.log` 字面量零命中**；`agent.log` 11 处命中全部是「单文件」概念
  （`paths.py:107`、`config/agent.toml:57`、`config_online/agent.toml:54`、4 个测试）。
- 只有 **3 个 logger 在发记录**：`wt_media_agent.runner.runner`（`runner/runner.py:20`）、
  `wt_media_agent.local_api.server`（`local_api/server.py:40`）、`wt_media_agent.runtime.config`
  （`runtime/config.py:37`）。`executors/`、`services/`、`clients/`、`storage/` **零日志调用**——
  故「按 logger 名路由」今天只能区分 runner 与本地 API 两面。
- **无记录字段通道**：全仓无 `extra=`、无 `LoggerAdapter`、无 `setLogRecordFactory`、无 `logging.Filter` 子类。
  `task_id` 只以文本插值出现在 `runner.py:113/:120/:126` 等处的消息串里。
- **`error_code` 无注册表**：只有 `contracts/local-error-codes/v1/bitbrowser.yaml` 的三个码
  （`not_found` / `bitbrowser_identity_unverifiable` / `bitbrowser_response_error`，**无 Python 引用**）、
  DB 列 `error_code TEXT DEFAULT NULL`（`storage/migration.py:55/:69`）、以及 `runner.py:182` 一处硬编码
  `cp.error_code = "executor_error"` 与 `:109` `"no_executor"`、`:124` `"session_invalidated_result_uncertain"`。
- **（起点读数，T-03 已推翻，见 §8）dev 不写日志文件**：`paths.py:107` `return "" if self.origin in {"dev","override"} else str(self.logs_dir / "agent.log")`
  ⇒ 开发态只走 stderr。磁盘实证：`.local/data/local-agent.sqlite3`（36864 字节）与 `.local/data/versions/` 存在，
  **`.local/logs/` 是空的**。T-03 已改为恒写 `<logs_dir>/agent.log`；上面这条留着是为了记住**起点**，
  不是当前行为。当时是推断的那半（「目录空」）已在 T-03 的**对照臂**里实测坐实。

### 4.4 初始化与隔离的既有缺陷（本 CHG 修）

- **Logger 重复初始化**：`bootstrap/app.py:76` `configure_from(config)` 与 `local_api/server.py:591`
  `configure_from(config)` 是同一进程内两次调用（后者在 `:589` `build_components()` 之后）。
  仅 `wt-media-local-health`（`server.py main`）这条入口走两次；`bootstrap/local.py`、`bootstrap/sidecar.py`、
  `bootstrap/cloud.py` 三条入口只走 `app.py:76` 一次。
- **component 构造器可造第二个初始对象**：`local_api/server.py:65` `self.state = state or LocalAgentState()`
  ——三条生产调用都传了 `state`，故为**潜伏**，未触发。
- **测试依赖真实仓库根**：`tests/test_storage_migration_paths.py:22` `REPO_ROOT = Path(__file__).resolve().parents[1]`，
  `:46` `assertEqual(default_data_dir(), REPO_ROOT / ".local" / "data")`——测试断言**真检出目录**。
- **一处已假的注释**：`runtime/paths.py:104-106` 称「Desktop currently discards the sidecar's stdout and stderr」，
  而 CHG-056 的 `sidecar/drain.rs` 已在持续消费它。
- **裁定的「executor 内初始化 Client」今天已成立**：全仓仅两处 client 构造，都在
  `bootstrap/app.py:81`（BitBrowser）与 `:85`（Cloud），且 `tests/test_dependency_boundaries.py:478`
  的 AST 规则已禁止别处构造。**无需改动。**

### 4.5 基线里的数字空缺（T-18 要补的）

- 架构基线 §5.8 `:1177` 只写 `logs/          # agent.log、task.log、error.log`——**三个文件名在全 docs 树仅此一处**，
  且没写任何轮转/保留/容量/截断数字（对 `轮转|保留天数|容量上限|截断` 全库零命中）。
- 程序总纲 §3 CHG-B（`:46-48`）只有一行范围，**同样没有数字**。
- 唯一下过数字的地方是 **CHG-20260923-053 草案**（Desktop「单文件 20MB / 保留 14 天 / 总占用 100MB」、
  Agent「保留天数与总占用 ~400MB」），但它自称「来自程序总纲」——**该归属不成立**（§3 无数字）。
  故本 CHG 是这些数字的**第一处权威落点**，T-18 回写程序总纲 §3 CHG-B。
- 053 草案同段还写「Agent 三个 **JSON** 日志文件」——**无任何基线背书**，且用户裁定三明写「不调整 JSONL」，
  故**不采纳**（D-02）。记在这里是为了让它不再第三次出现。

### 4.6 测试与工具基线

- Desktop：**68**（CHG-060 checkpoint「测试 **63 → 68**」为终点；其 `task-02-csp.md` 里的 63 是 T-03 加 5 条**之前**的中途数）。
  本仓是**二进制 crate**（`Cargo.toml:2`，无 `[lib]`）⇒ `cargo test --lib` **不成立**，用 `--workspace`
  或 `--bin wt-media-desktop-shell <filter>`（CHG-060 已记录）。
- Agent：`bash scripts/test.sh`（`python -m unittest discover -s tests`），**253 tests OK**（与 CHG-056/060 一致）。
- 应用 `.cargo/config.toml`：`retry = 10`、`timeout = 600`、`low-speed-limit = 1`、`multiplexing = false`
  ⇒ 网络已知不稳，依赖引入必须先跑 `cargo fetch` 探明（T-10）。
- 三个配置结构均 `#[serde(deny_unknown_fields)]`（`config.rs:43,55,67,73,79,86,92`），由 `config.rs:280` 的测试钉住。

## 5. Scope

### Add

- Agent：`runtime/logging` 的**三文件布局**（`agent.log` / `task.log` / `error.log`）、按 logger 名与级别的**路由**、
  `error.log` 的**结构化字段**（`timestamp` / `error_code` / `task_id` / `context` / `message`）、
  **脱敏 Filter**、**按天保留 + 总量上限**、**单条超长截断**（标 `truncate=true original_size=<n>`）。
- Agent：`GET /api/v1/health` 聚合健康检查（`§5.6` 双端点）+ 契约同步。
- Agent：`operation_id`（**进程内**，来自请求上下文，进日志行）。
- Agent：测试目录隔离助手（`tmpdir/data`、`tmpdir/logs`、`tmpdir/runtime`）。
- Desktop：`tracing` + `tracing-subscriber` 后端、日志目录解析、`rolling` writer、
  target 白名单（默认 `OFF`）、`[logging]` 配置段、`main` 的**唯一**初始化入口、`operation_id`（**进程内**）。
- Desktop：Agent 启停与健康检查的日志发射点（今天一处也不记）。

### Modify

- Agent：`runtime/paths.py`（dev/override 也解析到日志文件）、`runtime/config.py`（`[logging]` 新键与脱敏 repr）、
  `local_api/server.py`（删第二次 `configure_from`、`state` 改必传）、`bootstrap/app.py`（日志初始化留在 bootstrap）、
  `config/agent.toml` 与 `config_online/agent.toml`（已假注释）。
- Desktop：`main.rs`（接日志初始化并改启动摘要的发射方式）、`sidecar/drain.rs`（`report_exit` 改走
  `target=agent.supervisor`）、`commands/agent.rs` 与 `state.rs`（启停/健康检查补点）、
  `resources/desktop.production.toml`、`.gitignore`。
- 两仓 `AGENTS.md` / `DIRECTORY_MAP.md` / `AGENT-INDEX.md` 等入口文档（`drain` 那行「不落盘/不轮转/不脱敏」已变假）。

### Delete

- `commands/logging.rs` 的**文件名**（重命名为 `commands/webview.rs`；**命令名 `log_js_error` 不变**，
  故前端 `web/src/apps/desktop/webviewErrors.js:21` 不动）。纯移动单独一个 commit。
- Agent 侧 `local_api/server.py:38` 的 `configure_from` import 与 `:591` 的调用。

### Explicitly Not Doing

- **不做跨端 `operation_id` 串联**：Desktop **不发** `X-Operation-Id`、Agent **不消费**该头、
  **不进 sidecar 子进程环境**（裁定九：「禁止本次偷偷增加 Header 和消费逻辑」）。
- 不做用户设置 UI 与清理按钮（CHG-C）；不做端口就绪通知与打包校验（CHG-D）。
- 不建 ELK/Loki 等日志平台、不建日志数据库、不做 JSON 日志体系改造、不建第二套任务日志系统。
- Desktop **不代理写 Agent 业务日志**（Agent stdout 不得全量转存 desktop.log）。
- 不引入 `tauri-plugin-log`；不引入 `tracing-appender`（其 rolling 只能按日期切文件，表达不了
  20MB 单文件上限、总量预算与单条截断这三条硬验收）。
- **不自写 tracing 后端、不留降级路径**：`cargo fetch` 失败按**阻塞**上报，不静默换实现（用户批注）。
- 不做大范围业务重构；不改变任何业务闭环、API contract 语义（`/healthz` 字段冻结、`/api/v1/status` 行为不变）。
- 不交付 Desktop 通用运行目录（`AppPaths`）——裁定只固定了日志路径（见 Q-01）。
- 不动开发者的 BitBrowser `:54345`、Cloud `:18080`、dev Agent `:8765`；本 CHG 全程用 scratch 端口。
- 不碰 `wt-media-cloud`。

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | Agent 与 Desktop **各自拥有自己的 Logger**；Logger 初始化**只能有唯一入口**，由 bootstrap/startup 流程负责（main 入口 → 加载配置 → 初始化 Logger → 创建 Runtime → 创建 Components → 启动 Server）。禁止 server 再初始化 Config、component 初始化 Logger、executor/service/client 初始化。Config 亦只初始化一次。 | CONFIRMED（裁定一/二/五） |
| D-02 | Agent **保持三文件**：`agent.log`、`task.log`、`error.log`，**纯文本**（沿用今天的 formatter）。**不调整 JSONL**；**CHG-053 草案的「三个 JSON 日志文件」不采纳**——无基线背书。 | CONFIRMED（裁定三） |
| D-03 | `error.log` 收 ERROR 级事件，但**不是 traceback dump**，每行必含 `timestamp` / `error_code` / `task_id`(可选) / `context`(可选) / `message`；**完整 traceback 进 `agent.log`**。`task.log` 只记任务关键节点（开始/阶段变化/成功/失败/关键业务节点），**不含**高频执行细节、页面点击过程、Playwright debug、HTTP 请求响应全量。 | CONFIRMED（裁定三） |
| D-04 | 级别语义：ERROR 不可忽略失败 / WARN 可恢复异常 / INFO 关键生命周期与业务节点 / DEBUG 开发诊断；**生产默认 INFO、开发 DEBUG**；生产 INFO 不得灌请求响应与调试细节。 | CONFIRMED（裁定四） |
| D-05 | 轮转与限额（默认值）：**单文件 ≤ 20MB**、**保留 ≤ 14 天**、**总容量受限**；**单条日志超限必须截断**，标记 `truncate=true original_size=<原字节数>`，不得因此无限增长。 | CONFIRMED（裁定六） |
| D-06 | Desktop 日志落盘 `~/Library/Logs/WTMedia/Desktop`；开发态 `<repo>/.local/logs`（并给 desktop 仓 `.gitignore` 补 `.local/`）。Desktop 只记：启动退出、配置加载、用户设置异常、Agent 启停、Agent 健康检查、Sidecar 异常退出、更新异常；**不记** Agent 内部任务过程、浏览器操作细节、FFmpeg 执行细节。 | CONFIRMED（裁定七 + 计划裁定④） |
| D-07 | Rust **必须持续消费** sidecar stdout/stderr（防 pipe 阻塞、捕获启动失败、捕获异常退出），但**禁止把 Agent stdout 全量复制进 desktop.log**：Agent 业务日志 → `agent.log`，Agent 生命周期管理 → `desktop.log`（`target=agent.supervisor`）。 | CONFIRMED（裁定八） |
| D-08 | 脱敏禁止项：Cookie / Password / Authorization / Bearer Token / Refresh Token / Agent Runtime Token / 代理密码 / 完整 Secret；**敏感对象禁止默认 Debug 输出**（双道防护：源头避免 + Logger 脱敏）。 | CONFIRMED（裁定十） |
| D-09 | 测试要求：Agent 侧须验「独立启动可产生日志、`.local/logs` 不为空、三类日志路由正确、轮转真实生效、历史清理有效、超长日志截断」；Desktop 侧须验「启动产生 desktop.log、agent.supervisor 信息进入 desktop.log、sidecar stdout 持续消费、Agent 业务日志不重复进入 desktop.log」。**测试禁止使用 `REPO_ROOT/.local/data`**，必须用 `tmpdir/data`、`tmpdir/logs`、`tmpdir/runtime`。 | CONFIRMED（裁定十一） |
| D-10 | `operation_id` 本 CHG **不交付跨端**。Desktop 可**内部生成**、Agent 用**自身上下文**；未来通过 API v2 正式纳入。**禁止本次增加 Header 与消费逻辑。** | CONFIRMED（裁定九） |
| D-11 | 本 CHG **只交付日志目录解析**，不交付 Desktop 通用运行目录（`AppPaths`）——裁定未给该规范，登记为未交付而非发明一份无权威的规范。 | CONFIRMED（本次实施口径） |

## 7. Pending Questions

| ID | Question | Blocking |
|---|---|---|
| Q-01 | `logs/agent/` 是否要多一层子目录？裁定三写「保持三文件：`logs/agent/` …」，而 §5.8`:1177` 把三个文件**直接**放在 `logs/` 下且裁定说的是「**保持**」。**按不加层实施**（装态 `~/Library/Logs/WTMedia/Agent/{agent,task,error}.log`、dev `<repo>/.local/logs/{…}.log`）。要加层请一句话。 | NO |
| Q-02 | Agent/Desktop 的**总容量上限数字**：裁定六列了「总容量限制」但未给数字。按 053 草案取 **Agent 400MB / Desktop 100MB**，做成 `[logging] total_bytes` 可覆盖，T-18 回写程序总纲 §3 CHG-B。要改请一句话。 | NO |
| Q-03 | Desktop 日志文件名格式：建议 `desktop-YYYYMMDD-N.log`（UTC 日期；本地日期需 `localtime_r`，不安全），`N` 用 `create_new` 防多实例写同一文件。 | NO |
| Q-04 | 裁定七还列了「用户设置异常」与「更新异常」，但 Desktop **没有** settings 命令（`commands/` 只有 account/agent/bind/logging/profile/public_config），`updater/mod.rs` 也**没有任何 emit 与可上报的异常路径**——**无来源可接**。登记为未交付，**不造假发射点**。 | NO |
| Q-05 | **AC-11 的覆盖被计划高估**：计划把 AC-11 整条（含「测试不误连真实外部服务」）映射给 T-02，T-02 执行时实测该半**今天无任何规则在守**。处置：AC-11 拆为 AC-11a（PASS，T-02）/ AC-11b（未覆盖），新增 **T-19** 在本 CHG 内补上这条规则（里程碑的失败行为锚点就写着它，丢弃会使该锚点无人守）。**未静默吸收，也未静默丢弃。** 若要移出本 CHG 请一句话。 | NO |

无阻塞项（`Blocking = NO`）：Q-01…Q-05 均已按上述口径实施，用户可在任一 checkpoint 用一句话改判。

## 8. Implementation Tasks

每项执行序列：`先失败的验证/测试 → 最小实现 → 测试 → diff 检查 → evidence → checkpoint → 独立提交`。
**一仓一 commit；「移动文件」与「改逻辑」绝不进同一 commit。**

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | 建 active 记录并激活（本文件、`checkpoint.md`、`evidence/`、`status/`），LEDGER 加表行，`planned/README.md` B 行改 ACTIVE，快照再生成，两验证器绿 | DONE | `verify_agent_entry.py` + `verify_delivery_governance.py` |
| T-02 | Agent 测试目录隔离（§5.13）：落「不得把检出当运行时目录」的规则 + `scripts/test.sh` 守卫；修 `tests/test_storage_migration_paths.py:46` 对真实检出目录的断言；落隔离助手 `isolated_paths()` | DONE | `evidence/task-02-isolation.md`；改前恰好 1 处命中（红），改后 259 tests OK |
| T-03 | Agent dev/override **真落盘**（推翻 `paths.py:107`，一行行为）；同步删 `config/agent.toml`、`config_online/agent.toml` 的已假注释 | DONE | `evidence/task-03-dev-writes-logs.md`；改前 7 处红；真实 dev 启动 → `agent.log` 114 字节非空，**对照臂无该文件** |
| T-04 | Agent 三文件布局 + 路由（`agent.log` 全量含 traceback / `task.log` 仅 `wt_media_agent.runner.*` / `error.log` ERROR 级不带 traceback） | TODO | 两向断言：该进的不进 = 失败 |
| T-05 | `error.log` 结构化字段通道（`error_code`/`task_id`/`context`，`setLogRecordFactory` 缺省 `None` + `extra={}` 约定；`task_id` 在 `runner.py` 的 emit 点由文本插值改为 `extra`） | TODO | 有 `extra` 出字段、无 `extra` 不抛 |
| T-06 | Agent 脱敏 Filter（表驱动：`Cookie:`/`Authorization:`/`Bearer`/`proxy_password=`/`password=`/`refresh_token=`/本机 runtime token 逐字值；脱敏后周围文本仍在）+ 配置对象脱敏 `__repr__` | TODO | 表里先放今天会漏的用例 → 红 |
| T-07 | Agent 保留与轮转：单文件 20MB、14 天、总量上限、**单条截断标 `truncate=true original_size=<n>`** | TODO | 六向变异：日期翻档/20MB 翻档/截断/按天删/按量删/当前文件永不删 |
| T-08 | `GET /api/v1/health` 聚合健康检查（Cloud/BitBrowser/Storage 各一例不可用 → 200 + `abnormal`/`unknown` 不抛）+ 契约同步；`/healthz` 逐字不变 | TODO | scratch 端口 curl；`/healthz` 与今天逐字比对 |
| T-09 | 修既有缺陷并锁死唯一入口：~~①`paths.py:104-106` 已假注释~~（**T-03 已随 docstring 重写完成**）；②删 `server.py:38`/`:591` 第二次 `configure_from`；③`server.py:65` `state` 改必传；④**新增 AST 边界测试**：`src/` 内除 `bootstrap/app.py` 外不得 import `configure_from`/`configure_logging`（**今天就会红**） | TODO | 新 AST 测试先红后绿 |
| T-10 | Desktop 引入 `tracing` + `tracing-subscriber`（**例外的无失败测试项**） | TODO | `cargo tree` 前后 + 下载清单具名 + 起点 68 仍绿；`cargo fetch` 失败即阻塞上报 |
| T-11 | Desktop 日志目录解析（纯函数，`home`/`environment` 注入；Production → `~/Library/Logs/WTMedia/Desktop`，Development → `<manifest>/.local/logs`）+ `.gitignore` 补 `.local/` | TODO | 测试不解析真实 `$HOME`；不可写目录返回而非 panic |
| T-12 | `rolling` writer（`Clock` 注入）：日期翻档、20MB 翻档、**单条截断标 `truncate=true original_size=<n>`**、按天删、按量删、当前文件永不删 | TODO | 六向变异，逐条 |
| T-13 | Desktop 后端装配 + target 白名单（默认 `OFF`，`const OWNED_TARGETS` 枚举断言；`agent.supervisor` 永不比 INFO 更严）+ 格式 + 脱敏 | TODO | 外来 target 不入文件 / 自有 target 入文件（两向）；落盘后 grep 不到 token |
| T-14 | Desktop `[logging]` 配置 + 校验 + 出货资源（非法级别、三个 0、总量小于单文件上限先红；报错只点名键不回显值） | TODO | `out_of_range_values_are_rejected` 先行红 |
| T-15 | 接进 `main`（唯一入口）：插在 `bootstrap::resolve` 之后、启动摘要之前；**stderr 照旧**，目录不可写时仅 stderr 且仍启动 | TODO | 真实启动：stderr 与开发态日志文件里**都**有摘要 |
| T-16 | 三个既有 emit 点改道（`main.rs:65`→`desktop.startup`；`drain.rs:158`→`agent.supervisor`；`commands/logging.rs` 先纯重命名 `commands/webview.rs` 单独 commit，再改走 logger `target=webview`）+ Agent 启停与健康检查补点 | TODO | `report_exit` 恰一条该 target 记录；50 行普通 sidecar 输出 → 零条 |
| T-17 | Desktop `operation_id`（**仅进程内**）：断言出站请求头集合与今天**逐字相同**；`sidecar/mod.rs` 的 `assert_eq!(vars.len(), 3)` 仍绿 | TODO | 头集合逐字比对 + 环境变量数不变 |
| T-18 | 回写与收尾：基线（程序总纲 §3 CHG-B 补数字、架构基线 §5.8/§6.8 补三文件与 Desktop 路径）、入口文档、`[logging]` 注释；`Status: DONE` → `git mv` 归档 → 移除 LEDGER 行 → `--no-active` 冷启动重生成 → **主动扫**失效指针 | TODO | 两验证器绿；扫描报分母 + 阳性对照 |
| T-19 | **测试不误连真实外部服务**（T-02 执行中发现，见 §7 Q-08）：AST 规则——`tests/` 内每次网络客户端构造（`BitBrowserClient` / `CloudAgentClient`）必须注入假 `transport`，`urlopen` 调用必须被 patch；T-02 只覆盖了 AC-11 的后半 | TODO | 规则先红（拿一个真实构造点造对照），报分母：41 处网络调用点 / 34 个测试模块 |

> **T-19 的来源**：T-02 执行时逐条核对 AC-11，发现计划把 AC-11 整条映射给 T-02，但 T-02 只交付了
> 「不写真实检出目录」那半——「不误连真实外部服务」**今天没有任何规则在守**（实测：无该规则；
> `54345`/`18080`/`8765` 出现 30 余处但**多为数据**，配注入的假 transport 或断言出货配置值）。
> 该失败行为写在里程碑的成功事实锚点上，故**留在本 CHG 内**而不是丢弃；编号排末位以免打乱既有 T-03…T-18。

## 9. Repository Checklist

### wt-media-workspace

- [x] T-01：`delivery/active/CHG-20260923-057/`（`change.md`、`checkpoint.md`、`evidence/`、`status/`）；`delivery/planned/CHG-20260923-057/` 移入且**不留副本**
- [x] T-01：`delivery/LEDGER.md` 加裸 id 表行 + 说明段；`delivery/planned/README.md` B 行 → ACTIVE
- [ ] 基线回写：程序总纲 §3 CHG-B（20MB/14d/总量/截断标记/三文件纯文本）、架构基线 §5.8/§6.8（Desktop 日志路径、dev 也落盘）（T-18）
- [ ] 归档收尾与失效指针扫描（T-18）

### wt-media-agent

- [x] T-02 测试隔离；T-03 dev 落盘
- [ ] T-04 三文件路由；T-05 字段通道；T-06 脱敏；T-07 保留/轮转/截断；T-08 `/api/v1/health`；T-09 缺陷与唯一入口；T-19 不误连外部服务
- [ ] 入口文档回写（`AGENTS.md`/`DIRECTORY_MAP.md`/`AGENT-INDEX.md`）（T-18）

### wt-media-desktop

- [ ] T-10 依赖；T-11 目录解析；T-12 rolling；T-13 装配/白名单/脱敏；T-14 配置；T-15 main；T-16 改道与补点；T-17 operation_id
- [ ] 入口文档回写 + `.gitignore` 补 `.local/`（T-11/T-18）

### wt-media-cloud

- [ ] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Agent 脱离 Desktop 可独立运行并产生日志（裁定十三·1） | scratch 端口独立启动 ✓ + `agent.log` 非空 ✓（T-03，含对照臂）；**三文件待 T-04** | 部分（T-03） |
| AC-02 | Desktop 正式启动产生自身日志（裁定十三·2） | 真实启动后读 `desktop.log` 首条记录为启动摘要（T-15） | TODO |
| AC-03 | Config/Logger **只初始化一次**（裁定十三·3） | 新增 AST 边界测试转绿；出站头集合逐字相同（T-09/T-17） | TODO |
| AC-04 | 日志不会无限增长（裁定十三·4） | 20MB 翻档 + 14 天删除 + 总量删除 + 单条截断，逐条变异（T-07/T-12） | TODO |
| AC-05 | 日志目录异常不阻断启动（裁定十三·5） | Agent 侧已成立：`configure_from` 降级仅 stderr 且既有单测绿（T-03）；Desktop 侧待 T-15 | 部分（T-03） |
| AC-06 | 日志可定位问题（裁定十三·6） | 三文件路由 + `error.log` 五字段 + `agent.supervisor` 记录（T-04/T-05/T-16） | TODO |
| AC-07 | 日志不泄露敏感信息（裁定十三·7） | 表驱动脱敏 + 落盘后 grep 不到 token（T-06/T-13） | TODO |
| AC-08 | Desktop 与 Agent 日志职责清晰（裁定十三·8） | 两向断言：**该进的不进 = 失败**（T-04/T-16） | TODO |
| AC-09 | Sidecar stdout 持续消费且**不转存**（裁定十三·9） | 50 行普通 sidecar 输出 → **零**条 desktop 记录（阳性对照）（T-16） | TODO |
| AC-10 | 敏感信息不进诊断包（成功事实 #5 后半） | 诊断包路径本 CHG 不新增采集面；`/api/v1/health` 响应与日志行均不含凭据（T-06/T-08） | TODO |
| AC-11a | 测试**不写真实检出目录**（里程碑失败行为） | T-02：规则「不得把派生根接 `.local`」（33/34 模块在扫）+ `scripts/test.sh` 前后新增路径守卫，变异探针证明守卫独立于测试结果 | PASS |
| AC-11b | 测试**不误连真实外部服务**（里程碑失败行为） | T-19：AST 规则（客户端构造必须注入假 transport）。**T-02 期间实测：今天无任何规则在守**，计划把 AC-11 整条映射给 T-02 是乐观的，见 §7 Q-08 | TODO |

**每项否定结论都要阳性对照，对照臂不出红即记「对照无效」，不得记为通过**（CHG-060 的 AC-08 先例）。

## 11. Evidence

证据落在 `evidence/`，按 `templates/delivery/evidence-record.md` 记录**事实**（命令、期望、实际、PASS/FAIL、commit），
不复述需求。原始输出落 `evidence/artifacts/`。

**约定：证据文件一律不用 `.log` 后缀（用 `.out`）**——两仓 `.gitignore` 都有 `*.log`，CHG-060 已因此让一个
被六处引用的证据静默没入库。

- `evidence/task-01-governance.md`（T-01）
- `evidence/task-02-isolation.md`（T-02）
- `evidence/task-03-dev-writes-logs.md`（T-03）
- `evidence/task-XX-<topic>.md`（T-03…T-19 每项一份）
- `evidence/test-summary.md`、`evidence/manual-verification.md`（收尾汇总）

## 12. Current Checkpoint

Completed:

- 2026-09-23 起草（`delivery/planned/CHG-20260923-057/`，PLANNED）。
- 2026-09-24 用户下发书面《CHG-057 日志治理裁定补充说明》十三节，取代草案中的待决项。
- 2026-09-24 T-01：记录移入 `delivery/active/`，改写为十三节执行记录。
- 2026-09-24 T-02：Agent 测试目录隔离落地（`wt-media-agent` `7382fed`，test-only，`src/` 零改动）。

Current:

- T-03 待开始（Agent dev/override 真落盘，推翻 `paths.py:107`）。T-02 已把它变成安全的改动。

Next:

- T-03 → T-04 → T-05 → T-06 → T-07 → T-08 → T-09（阶段 1 Agent 余项）；
  阶段 2 Desktop T-10…T-17；阶段 3 T-18 收尾；**T-19**（AC-11b 的规则，见 §7 Q-05）排在阶段 1 余项之后。

Blocked:

- None。

Recent verification:

- Start Gate（2026-09-24）：四仓工作区全部干净（governance/agent/desktop/cloud 各 `git status --porcelain` 为空）；
  `delivery/active/` 仅 `.gitkeep`；`delivery/LEDGER.md` 无表行；快照 `Active CHG: none`。
- T-01：见 `evidence/task-01-governance.md`。
- T-02：`bash scripts/test.sh` → **259 tests OK，exit=0**（253 → 259）；改前规则红且**恰好 1 处命中**；
  变异探针下守卫 `exit=1` 而套件打印 `OK`（守卫独立于测试结果）。见 `evidence/task-02-isolation.md`。
- **后续 Task 的定向验证一律带 `PYTHONPATH=tests` 前缀**：`tests/` 无 `__init__.py`，
  `python -m unittest tests.<模块>` 会把仓根而非 `tests/` 放上 `sys.path`，对 34 个模块中 import `support` 的
  6 个（其中 5 个是既有的）报 `ModuleNotFoundError`。这是**既有**布局属性，非 T-02 引入，故本 CHG 不动布局。

## 13. DONE Gate

- [ ] Scope completed.
- [ ] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Manual verification evidence recorded where required.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories touched only if listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.
