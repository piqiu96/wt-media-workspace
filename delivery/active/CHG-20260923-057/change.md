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

- Desktop：**起点 68**（CHG-060 checkpoint「测试 **63 → 68**」为终点；其 `task-02-csp.md` 里的 63 是 T-03 加 5 条**之前**的中途数）。
  T-10 后仍 **68**（依赖引入不改测试），T-11 后为 **78**，T-12 后为 **116**（只增不减）。
  本仓是**二进制 crate**（`Cargo.toml:2`，无 `[lib]`）⇒ `cargo test --lib` **不成立**，用 `--workspace`
  或 `--bin wt-media-desktop-shell <filter>`（CHG-060 已记录）。
- Agent：`bash scripts/test.sh`（`python -m unittest discover -s tests`），**起点 253 tests OK**（与 CHG-056/060 一致）；
  T-09 后为 **354**，T-19 后为 **365**（只增不减）。
- 应用 `.cargo/config.toml`：`retry = 10`、`timeout = 600`、`low-speed-limit = 1`、`multiplexing = false`
  ⇒ 网络已知不稳，依赖引入必须先跑 `cargo fetch` 探明（T-10）。
  **T-10 实测的真根因不是「不稳」**：本机**直连** `index.crates.io` 的 TLS 证书被劫持
  （`issuer=Let's Encrypt CN=YE1`、`notAfter=Sep 20 2026`、主题名不匹配，早于施工日 4 天即过期），
  而经开发者本机代理 `127.0.0.1:7897` 取 `config.json` 与 `.crate` 归档均 200。
  `curl` 与 `cargo` 都不读 macOS 的 `scutil --proxy`，故两者都走了那条坏路。修法是**调用时带
  `HTTPS_PROXY=http://127.0.0.1:7897`**（仍是官方后端，不是换实现）；**不写进仓库配置**，
  以免把某台机器的 localhost 代理固化进出货产物。后续如需 registry 访问同样要带它。
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
| Q-06 | **T-13 定下的两条稳定事实**（回写用）：①target 词汇表 `{agent.supervisor, desktop.startup, webview}`，`agent.supervisor` 的运行级别**永不比 INFO 更严**；②Desktop 记录为**单行纯文本**，时间戳 `%Y-%m-%dT%H:%M:%SZ`（UTC，因为 T-12 的文件名已按 UTC 分档），与 Agent 的本地时间无 `Z` 是**有意**差异。三条都有机器守（枚举断言 + 变异 6/8/11/12）。要改口径请一句话。 | NO |
| Q-07 | **Agent 侧脱敏的三处实测发现**（T-13 差分表 20 行跑出来的，**其中两处是真泄漏**）：①`_KEYED` 的 `[^\n]*` + `re.sub` 从整段匹配之后续扫 ⇒ 一行里的**第二个凭据永不进扫描**（实测 `token=aaa password=bbb` → `token=*** password=bbb`）；②`_is_cookie_key` 只认单数 `cookie`，而词表里有复数 `cookies` ⇒ 复数键走通用路径，**只掩第一个值**（`cookies: a=1; b=2` → `cookies: ***; b=2`）；③`_KEYED` 的 `["']?` 被消费掉而回显只拼 `key+separator` ⇒ **JSON 键的闭引号丢失**，该行不再是合法 JSON。T-06 已提交（`b66d7f5`/`70c1f93`），按「一仓一 commit」不在 T-13 里改。
**已由用户裁定开 Agent 侧独立 Task **T-20**（§8 有行）**：把这张 20 行差分表做成用例 + 一条变异 + 真实启动取证，
自己的 commit 与 evidence。**`Blocking = NO`（不挡 T-14…T-18），但 DONE Gate 前必须落地**——两处真泄漏直接
咬成功事实 #5「敏感信息不进日志」。**T-13 之后又实测出第四处**（T-13 那张 20 行表看不见：形似键 `mytoken=`
吞掉整行致遮蔽静默关闭），一并归 T-20 修；本条的行文按**旧行为**描述，T-20 落地后本条须整体改写（T-18）。 | NO |

无阻塞项（`Blocking = NO`）：Q-01…Q-07 均已按上述口径实施或登记，用户可在任一 checkpoint 用一句话改判。
`Q-08` 这个 ID 在 §8 的 T-19 行与 §10 的 AC-11b 里被引用（指「T-02 实测 AC-11 的『不误连外部服务』那半今天无规则在守」），
其定义即上面 **Q-05** 的内容；**保留原引用不改**，在此登记以免读者以为漏了一行。

## 8. Implementation Tasks

每项执行序列：`先失败的验证/测试 → 最小实现 → 测试 → diff 检查 → evidence → checkpoint → 独立提交`。
**一仓一 commit；「移动文件」与「改逻辑」绝不进同一 commit。**

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | 建 active 记录并激活（本文件、`checkpoint.md`、`evidence/`、`status/`），LEDGER 加表行，`planned/README.md` B 行改 ACTIVE，快照再生成，两验证器绿 | DONE | `verify_agent_entry.py` + `verify_delivery_governance.py` |
| T-02 | Agent 测试目录隔离（§5.13）：落「不得把检出当运行时目录」的规则 + `scripts/test.sh` 守卫；修 `tests/test_storage_migration_paths.py:46` 对真实检出目录的断言；落隔离助手 `isolated_paths()` | DONE | `evidence/task-02-isolation.md`；改前恰好 1 处命中（红），改后 259 tests OK |
| T-03 | Agent dev/override **真落盘**（推翻 `paths.py:107`，一行行为）；同步删 `config/agent.toml`、`config_online/agent.toml` 的已假注释 | DONE | `evidence/task-03-dev-writes-logs.md`；改前 7 处红；真实 dev 启动 → `agent.log` 114 字节非空，**对照臂无该文件** |
| T-04 | Agent 三文件布局 + 路由（`agent.log` 全量含 traceback / `task.log` 仅 `wt_media_agent.runner.*` / `error.log` ERROR 级不带 traceback） | DONE | `evidence/task-04-three-files-routing.md`；267 tests OK + **四次真实启动**（臂 D 一次给出三条两向证据） |
| T-05 | `error.log` 结构化字段通道（`error_code`/`task_id`/`context`；**缺省放 formatter 而非 `setLogRecordFactory`**——实测后者预置字段会让 `extra=` 必然抛 KeyError；`task_id` 在 `runner.py` 的 **9** 个 task-scoped emit 点加 `extra`，**消息里仍保留**，3 处配已有字面量的 `error_code`） | DONE | `evidence/task-05-error-fields.md`；278 tests OK + **两次真实启动**（真实任务失败按 `error_code`/`task_id` 定位；未注册类型的 WARNING 不进 `error.log`） |
| T-06 | Agent 脱敏（表驱动，15 行两列断言；落点**在 formatter 不在 Filter**——Filter 改 `record.msg` 碰不到 traceback；词表取自 `SENSITIVE_KEY_NAMES`，不另起一份；`AgentConfig.runtime_token` 改 `field(repr=False)`）。**顺带**：实测诊断包 `environment_facts` 的 `cloud_base_url` 可原样带密码（走 `print`→stdout，`drain.rs` 还会尾随 20 行）→ 值统一过 `redact()`；并追平套件里 27 条 `--- Logging error ---`——**点名**是 `test_bootstrap.py`/`test_sidecar_entry.py` 走真实装配却不恢复 logging 状态，修后加机器规则 | DONE | `evidence/task-06-redaction.md`；**293 tests OK**（+1 规则 +1 诊断包用例）；表 `15/15 漏 → 0/15`；诊断包密码 `True → False`；死 handler 泄漏 `245 → 0`、Logging error `27 → 0`；两个提交各自 checkout 均 293 OK |
| T-07 | Agent 保留与轮转：单文件 20MB、14 天、总量上限、**单条截断标 `truncate=true original_size=<n>`**（`BoundedFileHandler` + **三文件共享一个 `LogBudget`** 取代 `RotatingFileHandler`）。**真机实测到一处真缺陷并修**：启动清理此前**空转**——prune 按已注册家族名匹配，而家族名要等 handler 构造才注册（有轮转时才「看起来生效」）→ 先预注册再 prune + 回归测试先红 | DONE | `evidence/task-07-retention.md`；**320 tests OK**；六个界各一次实现变异、各自打掉自己的用例；真机两臂（小界/出厂界）8/8 判据；总量真实上界 `total_bytes + 3×max_bytes` 如实写进 docstring |
| T-08 | `GET /api/v1/health` 聚合健康检查（Cloud/BitBrowser/Storage 各一例不可用 → 200 + `abnormal`/`unknown` 不抛）+ 契约同步；`/healthz` 逐字不变 | DONE | `evidence/task-08-health.md`；**345 tests OK**；12 个变异（控制行先绿）；真机两臂 **20/20**，Cloud 侧实测 `connections=1 received=b''`；契约 `2026.09.24.1` |
| T-09 | 修既有缺陷并锁死唯一入口（**T-07 顺带实测：`-m` 启动时 server 的 logger 名是 `__main__`，HTTP 侧记录看不出组件来源，属本 Task 范围**）：~~①`paths.py:104-106` 已假注释~~（**T-03 已随 docstring 重写完成**）；②删 `server.py` 第二次 `configure_from`；③`state` 改必传（`LocalApiServer` 与 `serve`）；④**新增 R11 AST 规则**（**今天就会红**）；⑤`LOGGER_NAME` 显式写出，`-m` 下记录名不再是 `__main__` | DONE | `evidence/task-09-single-entry.md`；**354 tests OK**；R11 三个反例（含「规则被改成 `return []` 时全红」）；六个变异各自打掉自己的用例；真机 `-m` 探针 11/11，且把 `LOGGER_NAME` 变异回 `__name__` 后 A3/A4 转红 |
| T-10 | Desktop 引入 `tracing` + `tracing-subscriber`（**例外的无失败测试项**） | DONE | `evidence/task-10-desktop-deps.md`；依赖树 **267 → 271，恰好 +4 且具名**（tracing-subscriber 0.3.23 / sharded-slab 0.1.7 / thread_local 1.1.10 / lazy_static 1.5.0）、移除 0；阴性对照：`nu-ansi-term`/`matchers`/`tracing-log`/`tracing-attributes` 全 0（`regex`/`smallvec` **本就在树里**，不计入）；起点 **68 → 68** 逐字不动；clippy **10 → 10**；阻塞根因查明是本机直连 crates.io 证书被劫持（见 §4 平台边界），**经本机代理仍是官方后端**，未换实现 |
| T-11 | Desktop 日志目录解析（纯函数，`home`/`environment` 注入；Production → `~/Library/Logs/WTMedia/Desktop`，Development → `<manifest>/.local/logs`）+ `.gitignore` 补 `.local/` | DONE | `evidence/task-11-desktop-log-paths.md`；**78 tests OK**（68 → +10：4 条纯规则 + 6 条 IO/边界）；测试全程不解析真实 `$HOME`；不可写 → `Err` 不 panic（只读臂**在本机真的跑了**，断言含 `PermissionDenied`）；变异 **8/8 红**且控制臂先绿，并**补上两个探针查出的缺口**（M8 补 stale-probe 用例；M7 量出根因是 `AlreadyExists` 而 `NotADirectory` 是下游，故不是等价变异）；新增 8 个 `dead_code` 警告是本模块的调用方在 T-15，**登记为待验期望**（T-15 接线后应回到 4/10） |
| T-12 | `rolling` writer（`Clock` 注入）：日期翻档、20MB 翻档、**单条截断标 `truncate=true original_size=<n>`**、按天删、按量删、当前文件永不删；命名 `desktop-YYYYMMDD-N.log`，`create_new` 抢名防多实例 | DONE | `evidence/task-12-desktop-rolling.md`；**116 tests OK**（78 → +38）；变异 **25/25 红**、控制行先绿，探针 sha256 核对还原（`c3301b6334b3` 与提交文本一致）；**探针查出并补齐两个缺口**：M13 第一版**编不过**（NO-COMPILE 不算守住，换成可编译的等价变异才红）、M23「翻档记住自己翻过谁」**原本无用例**（补 20B 单文件 + 30B 总量那条才红）；两处 clippy 真意见当场改掉；警告 12 → **43** / clippy 18 → **48**，增量全是本模块 `dead_code`（调用方在 T-15），**T-15 的待验期望据此更新为 43→4 / 48→10**；**如实登记一处未覆盖**：跨午夜的第二个实例（其活文件日期是昨天 ⇒ 会被按天删） |
| T-13 | Desktop 后端装配 + target 白名单（默认 `OFF`，`const OWNED_TARGETS` 枚举断言；`agent.supervisor` 永不比 INFO 更严）+ 格式 + 脱敏 | DONE | `evidence/task-13-desktop-backend.md`；三个新模块 `logging::{redact,targets,backend}`（`assemble` 返回而不安装，测试用线程局部注入）；掩码落在 **sink**（与 T-06 的 formatter 同一处「记录成形后、离开进程前」）；**与 Agent 的差分表 20 行实跑**：17 同 / 3 异，三处根因从 Agent 源码读出，**两处是真泄漏**（一行里第二个凭据、复数 `cookies:` 只掩第一个值）→ 登记 §7 **Q-07**（拟开 Agent 侧 T-20）；外来 target 不入 / 自有 target 入（两向 + 同条对照臂）、落盘后 grep 不到 token 且周围文本仍在、`agent.supervisor` 下限在规则层与 filter 层各一条；**变异 12/12 红**（控制行 76 passed 先绿，逐次 sha256 核对还原），补齐三个缺口（含我自己表测先抓到的一个真 bug）；**144 tests OK**（116 → +28）；build 43 → **93** / clippy 48 → **97**，+50 全是新模块 `dead_code`（`rolling` 的 −1 已查明＝`Date::{year,month,day}` 因 `backend::stamp` 变活）；`cargo fmt` 连带面如实登记（**本仓不是 rustfmt-clean 的**，重排 16 文件已按纯格式量过、备份后还原，全仓格式化不在本 Task） |
| T-14 | Desktop `[logging]` 配置 + 校验 + 出货资源（非法级别、三个 0、总量小于单文件上限先红；报错只点名键不回显值） | DONE | `evidence/task-14-desktop-logging-config.md`；出货 TOML 补 `[logging]`（`level="auto"`、20MB/14 天/100MB），`Logging` 同款 `deny_unknown_fields` 且**无** `#[serde(default)]`；`validate()` 五条检查只点名键；**先红**：表的第 4 列（报错须点名的键）+ 每行先断言 `contains(from)` ⇒ `[logging]` 尚未写进出货文件时表自己报 `row "unusable log level" matches nothing`；**变异 9/9 红**（控制行 147 passed 先绿），**两个缺口当场补齐**——M6「词表删 trace」起初存活（正向臂与文案都从 `LOG_LEVELS` 推导 ⇒ 常量须用手写值钉死）、M9「撤 `Logging` 的 `deny_unknown_fields`」起初存活（既有用例只测顶层 ⇒ 改为逐节枚举）；三处超出计划的检查逐条登记（`retention_days <= 0`、`total_bytes >= max_file_bytes`、逐节 deny）；**147 tests OK**（144 → +3）；build **93 → 93** / clippy **97 → 97**（新常量被 `validate()` 引用，不入 `dead_code`）⇒ T-15 期望起点仍 **93→4 / 97→10** |
| T-15 | 接进 `main`（唯一入口）：插在 `bootstrap::resolve` 之后、启动摘要之前；**stderr 照旧**，目录不可写时仅 stderr 且仍启动 | DONE | `evidence/task-15-desktop-main-wiring.md`；`logging/setup.rs` 拆 `plan()`（全部决定）/`install(plan, secrets)`（只剩装配，**不再持有 `&DesktopConfig`**）——**拆分由第一个变异逼出**：环境取 `config.environment` 时整套 152 条全绿，拆后 N1/N2/N6/N7 各自红；环境取**构建期**；token 生成提前到日志之前；变异**两轮 22 个**（控制行两次先绿），M3/M4 起初存活（期望与实际**都从 `filter_of` 推导**，与 T-14 的 M6 同形）⇒ `PINNED_LEVELS` 手写对表 + `join(" ")` 绑回 `LOG_LEVELS`；**三个幸存者逐条登记**（`main` 的两个实参 + 不可达的「已被装过」臂，N9 由臂 1 的真实启动守、N8 分母为 0）；真机三臂（摘要入 stderr **且**入开发态文件且首条即摘要 / 占住目录仍启动不 panic / `warn` 0 条不建文件 vs 对照 `info` 1 条 255 字节）；**153 tests OK**（147 → +6）；build **93 → 9** / clippy **97 → 13**，与登记的 4/10 不符的 5 条逐条点名（`rolling` 的 `SHIPPED`/三个 `DEFAULT_*`/`open_path` 只在测试里被引用）且新增代码 0 条 lint |
| T-16 | 三个既有 emit 点改道（`main.rs:65`→`desktop.startup`；`drain.rs:158`→`agent.supervisor`；`commands/logging.rs` 先纯重命名 `commands/webview.rs` 单独 commit，再改走 logger `target=webview`）+ Agent 启停与健康检查补点 | DONE | `evidence/task-16-desktop-emit-points.md`；`report_exit` 恰一条该 target 记录且带末 20 行尾；50 行普通 sidecar 输出 → 零条（对照：这 50 行确实在缓冲里）；**166 tests OK**（153 → +13）；变异 **13/13 KILLED**（3 个回退到旧形态 + 10 个新形态）、控制行先绿；真机**探针页**三轮取证；build **9** / clippy **13**（前后相同，逐条点名无一条落在新代码上）；命令体拆 `health`/`start`/`stop` 后只剩 `start` 的 spawn 够不着，如实登记 |
| T-17 | Desktop `operation_id`（**仅进程内**）：断言出站请求头集合与今天**逐字相同**；`sidecar/mod.rs` 的 `assert_eq!(vars.len(), 3)` 仍绿 | DONE | `evidence/task-17-desktop-operation-id.md`；一次会话一个 id（`start` 生成并在存下 child **之后**登记、`stop` 在记完「已停止」**之后**清除），id 是**字段**：会话内带 `operation_id=`、会话外**一律不带**（`lifecycle!` 因此有**两个 `event!` 分支**——写成 `operation_id=None` 是对「这条记录属于哪个会话」的错误回答，且会改掉今天的行形状）；**不加新 target** / **不发 Header** / **不进 sidecar 环境**三条各有一个变异打掉自己（M1 query / M2 Header / M3 环境变量，M3 打的是**既有** `vars.len() == 3`）；**头集合基准是桩套接字实收字节**（`authorization`/`accept`/`host` 逐字，`host` 由 hyper 在 send 时加、`build()` 看不到）而非推断；**175 tests OK**（166 → +9）；变异 **R1–R3 + M1–M5 全 KILLED**（R2/R3 成对）、控制行先绿；**N1/N2 如实 SURVIVED**（`begin(...)`/`ended(...)` 各一行调用点单测进不去）**只由真机臂覆盖**；真机探针页臂：两会话六条记录 5 带 id（两值不同）/1 不带，返回值不含 id；build **9** / clippy **13**（未增）；退出报告**有意不带 id**、`already_running` 带 id 只在单测表里、**两侧 id 不相关**三条已登记 |
| T-18 | 回写与收尾：基线（程序总纲 §3 CHG-B 补数字、架构基线 §5.8/§6.8 补三文件与 Desktop 路径）、入口文档、`[logging]` 注释；`Status: DONE` → `git mv` 归档 → 移除 LEDGER 行 → `--no-active` 冷启动重生成 → **主动扫**失效指针 | TODO | 两验证器绿；扫描报分母 + 阳性对照 |
| T-19 | **测试不误连真实外部服务**（T-02 执行中发现，见 §7 Q-08）：AST 规则——`tests/` 内每次网络客户端构造（`BitBrowserClient` / `CloudAgentClient`）必须注入假 `transport`，`urlopen` 调用必须被 patch；T-02 只覆盖了 AC-11 的后半 | DONE | `evidence/task-19-no-external-services.md`；**365 tests OK**；计划的分母与实测不符（计划 41 处/34 模块，实测 41 = 38 处构造 + 3 处 `urlopen`、**40 模块**）；规则先红报出 5 处真命中且都走标记而非改代码；7 个变异逐个红且三条真断言各有变异能红它；一处真误报（`as urlopen` 绑的是 mock）与**两个自查出的对照缺陷**（读整树报告 → 假理由变红） |
| T-20 | **Agent 侧脱敏**（§7 Q-07 的三处 + T-13 之后新发现的第四处）：把 20 行差分表做成 fixture + 四处缺陷行的**精确串**用例；修复形态两条正则（整尾家族 / 单值家族）；幂等；`SENSITIVE_KEY_NAMES` × {`=`,`:`} 全覆盖 | DONE | `evidence/task-20-agent-redaction.md`；形态：`_TAIL_KEYED`（cookie/authorization，值 = 行尾）+ `_VALUE_KEYED`（其余族，值 = **一个前导词元且匹配在此结束**——`re.sub` 从整段匹配之后续扫，值吃到行尾就会吞掉后面的凭据），两个回调各带族守卫 ⇒ **两趟与顺序无关**；回显改用**原文字前缀**（`key+separator` 拼回会丢掉 JSON 键的闭引号）；`_is_cookie_key` 认 `cookie` **与** `cookies`（词表里两个都有）；`_KEYED`/`_mask_keyed` 删除，接口零变化。**先红**：同一份用例打在修前模块上（`git archive HEAD` + 换 `logging.py`，不碰工作树）→ **FAILED (failures=7)** = 5 个用例，控制臂 **19 OK**；**20 行差分表的期望串是在 Desktop 实现上测量出来的**（临时探针 + `git checkout` + sha256 `a3fad427…` 核对），不是抄它的表；**变异 8 个**（控制行 371 OK 先绿）：M1–M5/M7/M8 **KILLED**（M1 连**既有** T-06 两列表的 7 条一起打掉），**M6（两趟换序）如实 SURVIVED——它本身就是「顺序无关」这条声明的证据**；真机两臂（同源两个副本、scratch 端口 18769、两个死端口、5 次真实 POST）：修后 `agent.log` 三条泄漏针 `bbb`/`b=2`/`password=zzz` 各 **0**（对照：payload 里 1、修前日志里 2；另三个针 `aaa`/`a=1`/`s3cr3tvalue` **两侧都掩**，修前日志**不作对照**，已点名），周围文本 7 项仍在；**371 tests OK**（365 → +6）；`redact.rs` 那句因此变假的注释在 desktop 仓**单独一个 doc commit** `572d1cf`（14 行注释，代码 0 改动，`175 passed` 未增） |
| T-21 | **Agent 侧请求级 `operation_id`**（§8 无任务承接、§5 Scope/Add 要求）：`secrets.token_hex(8)` + contextvar（落在 `runtime/logging.py`）+ 覆写 `handle_one_request` 并 `try/finally` 复位；进 `FMT`/`ERROR_FMT`，`error.log` 位置在 logger 名之后、`error_code` 之前 | TODO | 端口 0 + `http.client` 的真实 HTTP 两条记录各带 16 位十六进制 id 且两 id 不同、请求外不带；变异各自红 |

> **T-19 的来源**：T-02 执行时逐条核对 AC-11，发现计划把 AC-11 整条映射给 T-02，但 T-02 只交付了
> 「不写真实检出目录」那半——「不误连真实外部服务」**今天没有任何规则在守**（实测：无该规则；
> `54345`/`18080`/`8765` 出现 30 余处但**多为数据**，配注入的假 transport 或断言出货配置值）。
> 该失败行为写在里程碑的成功事实锚点上，故**留在本 CHG 内**而不是丢弃；编号排末位以免打乱既有 T-03…T-18。

> **T-20/T-21 的来源**：用户本次裁定——**开 T-20** 在本 CHG 内修掉 §7 Q-07 的 Agent 侧脱敏缺陷（两处真泄漏
> 直接咬成功事实 #5，`Blocking = NO` 但 DONE Gate 前必须落地），**补 T-21** 交付 §5 Scope/Add 要求而 §8
> 无任务承接的 Agent 侧进程内 `operation_id`（实仓零命中）。二者编号续在 T-19 之后，同 `T-19 的来源` 的理由：
> 不重排既有 T-03…T-18。T-21 的关联范围**仅请求内、处理线程内**（跨线程不传播 contextvar），
> 跨端串联仍**不交付**（裁定九/D-10 不变）。

## 9. Repository Checklist

### wt-media-workspace

- [x] T-01：`delivery/active/CHG-20260923-057/`（`change.md`、`checkpoint.md`、`evidence/`、`status/`）；`delivery/planned/CHG-20260923-057/` 移入且**不留副本**
- [x] T-01：`delivery/LEDGER.md` 加裸 id 表行 + 说明段；`delivery/planned/README.md` B 行 → ACTIVE
- [ ] 基线回写：程序总纲 §3 CHG-B（20MB/14d/总量/截断标记/三文件纯文本）、架构基线 §5.8/§6.8（Desktop 日志路径、dev 也落盘）（T-18）
- [ ] 归档收尾与失效指针扫描（T-18）

### wt-media-agent

- [x] T-02 测试隔离；T-03 dev 落盘
- [x] T-04 三文件路由
- [x] T-05 字段通道（**缺省改放 formatter**，理由与实测见证据）；
- [x] T-06 脱敏（**落点在 formatter**；诊断包那处真泄漏一并实测并修；套件 logging 状态隔离补机器规则）；
- [x] T-07 保留/轮转/截断（**启动清理空转**是真缺陷，已修）；
- [x] T-08 `/api/v1/health`（两条禁令落成机制：Cloud 探针只连不发、聚合恒 200 不抛；契约同步）；
- [x] T-09 唯一入口（R11 AST 规则 + 三个反例）、`state` 必传、`-m` 下记录名（`LOGGER_NAME`）；
- [x] T-19 不误连外部服务（AC-11b）
- [x] T-20 脱敏（§7 Q-07 的三处 + 新发现的第四处；两条正则 + 20 行差分表进 fixture）
- [ ] T-21 请求级 `operation_id`（contextvar + `handle_one_request`；三文件位置一致）
- [ ] 入口文档回写（`AGENTS.md`/`DIRECTORY_MAP.md`/`AGENT-INDEX.md`）（T-18）

### wt-media-desktop

- [x] T-10 依赖；T-11 目录解析（**这两项已 DONE**）
- [x] T-12 rolling（**已 DONE**）
- [x] T-13 装配/白名单/脱敏（**已 DONE**）
- [x] T-14 配置；T-15 main；T-16 改道与补点；T-17 operation_id（**四项已 DONE，Desktop 半 T-10…T-17 全部完成**）
- [ ] 入口文档回写（T-18）；`.gitignore` 补 `.local/` **已在 T-11 完成**

### wt-media-cloud

- [ ] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Agent 脱离 Desktop 可独立运行并产生日志（裁定十三·1） | 真实独立启动 ✓；**三文件**各收到真实记录（T-04 臂 C 三者均 127 字节）✓；常规启动 `agent.log` 非空（T-03/T-04 臂 A） | PASS |
| AC-02 | Desktop 正式启动产生自身日志（裁定十三·2） | 真实启动（臂 1）后 `src-tauri/.local/logs/desktop-20260924-1.log` 249 字节、**首条记录即启动摘要**且与 stderr 那一行逐字相同（T-15）。**口径**：出货级别（`auto`）下验证；`level` 严于 INFO 时不建文件（惰性建文件，T-12 设计）且**连 stderr 一起静默**（两层共用 filter，T-15 臂 3 实测） | PASS（T-15） |
| AC-03 | Config/Logger **只初始化一次**（裁定十三·3） | Agent 侧已成立：R11 AST 规则（除 `bootstrap/app.py` 外不得到达 `configure_from`/`configure_logging`）+ 三个反例（含规则被改成 `return []` 时全红）；`server.py` 那次重复调用已删。Desktop 侧的 `operation_id` **没有开出第二条初始化/传递通道**：出站头集合与今天**逐字相同**（T-17 在**桩套接字实收字节**上钉死 `authorization`/`accept`/`host`，并断言整份请求不含该 id）、不加新 target（`OWNED_TARGETS` 仍恰 3）、不进 sidecar 环境（既有 `vars.len() == 3`） | PASS（T-09/T-17） |
| AC-04 | 日志不会无限增长（裁定十三·4） | Agent 侧已成立：20MB 翻档 + 14 天删除 + 总量删除 + 单条截断，六个界各一次变异；真机两臂 8/8。**总量口径**：`total_bytes` 在轮转/启动点强制，真实上界 `total_bytes + 3×max_bytes`（出厂 400MB + 60MB），是有界而非逐字节精确（T-07）；Desktop 侧已成立：日期翻档 / 20MB 翻档 / 单条截断（`truncate=true original_size=<n>`）/ 按天删 / 按量删 / 当前文件永不删，变异 **25/25 红**（T-12），**跨午夜的第二个实例**未覆盖（T-12 如实登记） | PASS（T-07/T-12） |
| AC-05 | 日志目录异常不阻断启动（裁定十三·5） | Agent 侧已成立：`configure_from` 降级仅 stderr 且既有单测绿（T-03）；Desktop 侧已成立：用普通文件占住 `<repo>/.local/logs` 后**仍启动**（8 秒后仍存活）、摘要在 stderr、**不 panic**、占位文件未被改动，且原因随摘要一起写出（T-15 臂 2；同形的单测 `an_unusable_directory_is_a_reason_and_not_a_failure`） | PASS（T-03/T-15） |
| AC-06 | 日志可定位问题（裁定十三·6） | 三文件路由已在真实进程两侧证实（T-04）；`error.log` 五字段已在真实任务上证实、`context` 通道就绪但**今日无生产点**（T-05）；`agent.supervisor` 已在真实进程上成立：**五个生命周期记录各自的调用点都跑到过**（启动 / 已在运行 / 健康成功 / 停止 / 未在运行，T-16 臂 C）+ 退出报告（T-16 臂 B）——在此之前「Agent 没在跑」与「在跑但拒绝」在前端只表现为一条失败命令；请求级 `operation_id` 由 **T-21**（Agent 侧进程内）承接，落地前该字段在本条下**未验** | 部分（T-04/T-05/T-16；T-21 待做） |
| AC-07 | 日志不泄露敏感信息（裁定十三·7） | Agent 侧**四处实测缺陷已全部修掉**（T-20）：`token=aaa password=bbb` → `token=*** password=***`、`cookies: a=1; b=2` → `cookies: a=***; b=***`、`{"client_secret": "s3cr3tvalue"}` → `{"client_secret": "***"}`（**仍是合法 JSON**，由 `json.loads` 判定，阳性对照在前）、`mytoken=abcdefghijkl password=zzz` → `mytoken=abcdefghijkl password=***`（形似键不再关掉遮蔽）。**单测**：T-13 的 20 行差分表做成 fixture，期望串是**在 Desktop 实现上测量**的，20/20 一致；四处各一条精确串用例；**变异 8 个里 7 个 KILLED**（M6 换序 SURVIVED，是有意成立的性质）。**真机**：真实进程 + 真实 HTTP 落盘后读回 `agent.log`，三条泄漏针各 0 而对照（payload / 修前日志）各 1 / 2，一个不带敏感形态的值原样通过。T-06 的 15 行两列表、落盘读回、traceback 面同覆盖仍有效。Desktop 侧已成立到模块层与真实进程：target 白名单（外来 target 有对照臂地不入文件）、含 token 的记录走完 sink 后 grep 不到且周围文本仍在（T-13）、真实启动确实建出文件并走完 sink（T-15 臂 1）。**登记两处不声称已覆盖**：①`main` 把 token 交给掩码这一行（T-15 的 N8）**无用例可打**——真实启动的 grep 分母为 0；②`error.log`/`task.log` 两条臂**未在本 Task 重跑**（四个缺陷同在 formatter 路径上，路由未改，但「三文件里的凭据不在」这一点本 Task 只由单测表与 `agent.log` 臂覆盖） | PASS（T-06/T-13/T-15/T-20） |
| AC-08 | Desktop 与 Agent 日志职责清晰（裁定十三·8） | 两向断言，两边各一条对照臂：**Agent 业务日志**进 `agent.log`、不进 `desktop.log`——T-04 三文件路由（真实进程）+ T-16 的 `ordinary_output_reaches_the_buffer_and_no_record`（50 行普通输出 → 该 target 零条记录，**对照**是这 50 行确实在 `drain` 缓冲里，「零条」不来自一个什么都没收到的 drain）；**Desktop 自己的生命周期**（启停、健康、退出）进 `desktop.log` 的 `agent.supervisor`——T-16 五分支真机臂 + 退出报告 | PASS（T-04/T-16） |
| AC-09 | Sidecar stdout 持续消费且**不转存**（裁定十三·9）。**口径按裁定五收窄为「进程存活期间」** | ①**进程存活期间的普通输出零条 desktop 记录**：单测 50 行（对照：50 行在缓冲里）；**真机分母是 1 行而不是 50**（sidecar 只来得及打印 1 行就死了）⇒ 真机只证明「那 1 行没变成记录、且确实到了 drain」，**不**证明规模；②**异常退出另立一臂**：恰**一条**该 target 记录且**含末 20 行尾**（裁定五），尾行在整份 `desktop.log` 里**只出现这一次**（臂 B 逐行核对：`[PYI-…]` 只在退出记录里）；③读失败（`CommandEvent::Error`）也是**一条**记录——进程未退出时的读失败否则永不为人所见；④对照臂：同一次失败，前端拿到的串**带**尾行、记录**不带** | PASS（T-16） |
| AC-10 | 敏感信息不进诊断包（成功事实 #5 后半） | **实测到一处真泄漏并修**：`environment_facts` 的 `cloud_base_url` 原样带密码（`True → False`，URL 仍可读）且走 `print`→stdout（T-06）；`/api/v1/health` 响应面已量（T-08 真机两臂：体里只有 `agent_version`/`agent_status` 与三个依赖的状态词，**没有** `cloud_base_url` 本身、没有 token）；`status` 响应体本 Task **未测**（契约面，已登记） | 部分（T-06/T-08） |
| AC-11a | 测试**不写真实检出目录**（里程碑失败行为） | T-02：规则「不得把派生根接 `.local`」（33/34 模块在扫）+ `scripts/test.sh` 前后新增路径守卫，变异探针证明守卫独立于测试结果 | PASS |
| AC-11b | 测试**不误连真实外部服务**（里程碑失败行为） | T-19：AST 规则（客户端构造必须注入假 transport）。**T-02 期间实测：今天无任何规则在守**，计划把 AC-11 整条映射给 T-02 是乐观的，见 §7 Q-08 | **PASS**（`evidence/task-19-no-external-services.md`：规则先红报 5 处真命中；控制臂先绿、7 个变异逐个红、三条真断言各有变异能红它；规则看不见的四种形态在文件头写明） |

**每项否定结论都要阳性对照，对照臂不出红即记「对照无效」，不得记为通过**（CHG-060 的 AC-08 先例）。

## 11. Evidence

证据落在 `evidence/`，按 `templates/delivery/evidence-record.md` 记录**事实**（命令、期望、实际、PASS/FAIL、commit），
不复述需求。原始输出落 `evidence/artifacts/`。

**约定：证据文件一律不用 `.log` 后缀（用 `.out`）**——两仓 `.gitignore` 都有 `*.log`，CHG-060 已因此让一个
被六处引用的证据静默没入库。

- `evidence/task-01-governance.md`（T-01）
- `evidence/task-02-isolation.md`（T-02）
- `evidence/task-03-dev-writes-logs.md`（T-03）
- `evidence/task-04-three-files-routing.md`（T-04）
- `evidence/task-05-error-fields.md`（T-05）
- `evidence/task-06-redaction.md`（T-06）
- `evidence/task-07-retention.md`（T-07）
- `evidence/task-08-health.md`（T-08）
- `evidence/task-09-single-entry.md`（T-09）
- `evidence/task-19-no-external-services.md`（T-19）
- `evidence/task-10-desktop-deps.md`（T-10）
- `evidence/task-11-desktop-log-paths.md`（T-11）
- `evidence/task-12-desktop-rolling.md`（T-12）
- `evidence/task-13-desktop-backend.md`（T-13）
- `evidence/task-14-desktop-logging-config.md`（T-14）
- `evidence/task-15-desktop-main-wiring.md`（T-15）
- `evidence/task-16-desktop-emit-points.md`（T-16）
- `evidence/task-17-desktop-operation-id.md`（T-17）
- `evidence/task-20-agent-redaction.md`（T-20）
- `evidence/task-XX-<topic>.md`（**T-18 / T-21** 每项一份，随 Task 落地——原句写的「T-03…T-19 每项一份」已按上面的实名清单更正）
- `evidence/test-summary.md`、`evidence/manual-verification.md`（收尾汇总）

## 12. Current Checkpoint

逐 Task 的完整记录（含实测读数与边界）在 `checkpoint.md`；此处只保留骨架。

Completed:

- 2026-09-23 起草（`delivery/planned/CHG-20260923-057/`，PLANNED）。
- 2026-09-24 用户下发书面《CHG-057 日志治理裁定补充说明》十三节，取代草案中的待决项。
- 2026-09-24 T-01：记录移入 `delivery/active/`，改写为十三节执行记录。
- 2026-09-24 T-02：Agent 测试目录隔离落地（`wt-media-agent` `7382fed`，test-only，`src/` 零改动）。
- 2026-09-24 T-03：Agent dev/override 真落盘（`2f07db4`，一行行为），对照组坐实归因。
- 2026-09-24 T-04：Agent 三文件布局与路由（`305975b`），四次真实启动取证。
- 2026-09-24 T-05：`error.log` 结构化字段通道（`wt-media-agent` `3a546dc`），**推翻计划写定的机制**：
  `setLogRecordFactory` 预置字段与 `extra=` 约定不可共存（实测 KeyError），缺省改放 formatter。
- 2026-09-24 T-06：Agent 脱敏（`wt-media-agent` `b66d7f5` + `70c1f93`）——掩码落在 **formatter**（Filter 碰不到
  traceback），词表取自 `SENSITIVE_KEY_NAMES`；表 `15/15 → 0/15`；配置对象 `repr=False`。
  **实测到诊断包一处真泄漏并修**（`cloud_base_url` 的密码原样进 `environment_facts`，且走 `print`→stdout）
  并**追平套件 27 条 `Logging error`**：点名 `test_bootstrap.py`/`test_sidecar_entry.py` 走真实装配却不恢复
  logging 状态（我的第一个假设被判错，见证据），修后加机器规则 `test_logging_state_isolation.py`。
- 2026-09-24 T-07：Agent 保留与轮转（`wt-media-agent` `f07d9e8`）——四个界（20MB／14 天／总量／单条截断）
  各一次实现变异，各自打掉自己的用例。**真机两臂实测到一处真缺陷并修**：启动清理此前**空转**
  （prune 匹配的是已注册家族名，而家族名要等 handler 构造才注册），有轮转时才「看起来生效」；
  先注册再 prune + 回归测试先红。**总量的真实上界如实改成 `total_bytes + 3×max_bytes`**
  （是有界，不是逐字节精确）。
- 2026-09-24 T-08：Agent 聚合健康检查（`wt-media-agent` `87b1264`）——`/healthz` 逐字冻结（机器守），
  新增 `/api/v1/health`。两条禁令都落成机制而非承诺：Cloud 探针只 `socket.create_connection` 后立刻关闭
  （真机实测 `connections=1 received=b''`），三依赖全灭时聚合仍 200 + `abnormal`。
  **两处自查出的假绿**：AST「不走 HTTP 客户端」检查对 `from urllib import request` 匹配不上（变异救回）、
  真机探针的就绪判断用了宽 catch 的 `get()` 而空转。另实测登记一处范围外事实：存储不可用时
  `/api/v1/status` **确实抛**（连接被关），与聚合的 200 构成同进程对照，不改它。

- 2026-09-24 T-09：唯一入口与 `-m` 记录名（`wt-media-agent` `1f07cee`）——删掉 `server.py` 那次重复的
  `configure_from`，新增 **R11 AST 规则**（除 `bootstrap/app.py` 外不得到达两个初始化器，符号与模块两条
  拼写都认）＋三个反例；`state` 改必传；`LOGGER_NAME` 显式写出使 `-m` 下记录名不再是 `__main__`。
  **推翻计划的一处说法**：「component 构造器是第二个初始化点」不成立（裁定说的是 Config 与 Logger），
  真问题是 `state or LocalAgentState()` 让忘了传的调用方拿到一个**看起来正常**的默认态，
  `/api/v1/status` 于是描述一个没在跑的 Agent；同时复核更严重的失效模式**不成立**
  （`LocalAgentState` 无 `__bool__`/`__len__`，传进去的不会被丢）。**两处自查出的问题**：
  R11 第一版误报 `bootstrap/cloud.py` 引纯函数 `redact`（会误报在跑的代码的规则活不长）；
  新写的 `serve` 用例第一版**真的去 bind 8765**（dev Agent 端口），改为读签名。

- 2026-09-24 T-10：Desktop 引入 `tracing` + `tracing-subscriber`（`wt-media-desktop` `5194d49`）——
  依赖树 267 → 271（+4 具名、移除 0），阻塞根因是本机直连 crates.io 证书被劫持（经代理仍是官方后端）。
- 2026-09-24 T-11：Desktop 日志目录解析（`wt-media-desktop` `f1edae6`）——`logging::paths`，变异 8/8 红。
- 2026-09-24 T-12：Desktop `rolling` writer（`wt-media-desktop` `66f8f02`）——四条界 + `Writer`，变异 25/25 红。
- 2026-09-24 T-13：Desktop 后端装配 + 白名单 + 格式 + 脱敏（`wt-media-desktop`，本 Task 的提交）——
  `logging::{redact,targets,backend}`；与 Agent 的差分表 20 行实测出 Agent 侧两处真泄漏（§7 Q-07）；
  变异 12/12 红；144 tests OK。
- 2026-09-24 T-14：Desktop `[logging]` 配置 + 校验 + 出货资源（`wt-media-desktop`，本 Task 的提交）——
  出货 TOML 四键（`auto`/20MB/14 天/100MB），`Logging` 同款 `deny_unknown_fields` 且无 `#[serde(default)]`；
  五条检查只点名键；**变异 9/9 红**，两个缺口当场补齐（词表驱动的断言须把常量本身钉死；
  `deny_unknown_fields` 是**按 struct** 写的，用例改为逐节枚举）；147 tests OK；
  build/clippy **93 → 93 / 97 → 97**（新常量被 `validate()` 引用）⇒ T-15 期望起点未移动。

- 2026-09-24 T-15：Desktop 接进 `main`（`a312aa0`）——`logging/setup.rs` 拆 `plan()`/`install(plan, secrets)`；
  **拆分由第一个变异逼出**（环境取 `config.environment` 时整套 152 条全绿，因为 subscriber 每进程只能装一次）；
  环境取**构建期**、token 生成提前到日志之前；变异两轮 22 个，M3/M4 因「期望与实际都从 `filter_of` 推导」
  起初存活 ⇒ `PINNED_LEVELS` 手写对表；三个幸存者逐条登记（`main` 的两个实参 + 不可达臂）；
  真机三臂；153 tests OK；build **93 → 9** / clippy **97 → 13**（与登记的 4/10 不符，差的 5 条逐条点名）。

- 2026-09-24 T-16：Desktop 三个既有 emit 点改道 + 生命周期补点（`wt-media-desktop` `5eb7d0c` 纯重命名 +
  本 Task 的提交）——`report_exit` → `agent.supervisor`（**恰一条、含末 20 行尾**，裁定五）；
  `CommandEvent::Error` 分支补一条记录（否则进程存活期间的读失败永不为人所见）；`commands/logging.rs` →
  `commands/webview.rs`（**纯重命名单独一个 commit**，命令名 `log_js_error` 不变）后两处 `println!` 改走
  `target=webview`；Agent 启停与健康检查补点（health 响应体**只在 DEBUG**、失败记录**不带**那 20 行尾）。
  `CommandEvent` 是 `#[non_exhaustive]`（测试构造不出）⇒ 把「一行是什么」压成三臂纯函数
  `Heard`/`classify`/`heard`；命令体拆 `health`/`start`/`stop`（与 T-15 拆 `plan`/`install` 同形）。
  **变异 13/13 KILLED**（3 个回退旧形态 + 10 个新形态）、控制行先绿；**166 tests OK**（153 → +13）；
  build **9** / clippy **13**（前后相同，13 条逐条点名无一条落在新代码上）。真机取证逼出一条**环境事实**：
  debug 二进制带 `cfg(dev)` 且 `devUrl` = `127.0.0.1:5174` ⇒ 窗口**整页空白**，前端命令一条也到不了；
  改用**临时探针页**（事后逐项还原、`index.html` sha256 核对）跑出五个生命周期分支 + 退出码 255 与
  信号 9 两种状态。未覆盖项逐条登记（`start` 的 spawn 失败分支、真机分母是 1 行不是 50、
  探针页是替身、`already_running` 在 sidecar 死后仍说「已在运行」、`local_agent_status` 未加记录）。

- 2026-09-24 T-17：Desktop 进程内会话 `operation_id`（`wt-media-desktop` `9051480`，1 个 commit）——
  一次 Agent 会话一个 id（`start` 生成并在存下 child **之后**登记、`stop` 在记完「已停止」**之后**清除），
  存在 `state.rs` 里 `AgentProcess` **旁边**。id 只作为**字段**落在 `agent.supervisor` 的记录上：会话内带
  `operation_id=`、会话外**一律不带**（`lifecycle!` 因此有两个 `event!` 分支——写成 `operation_id=None`
  是对「这条记录属于哪个会话」的**错误回答**，也会改掉今天的行形状）。**不加新 target** / **不发 Header** /
  **不进 sidecar 环境**三条各有一个变异打掉自己（M1 query / M2 Header / M3 环境变量，M3 打的是**既有**
  `vars.len() == 3`）。出站头集合的基准**测量自桩套接字实收字节**（`authorization`/`accept`/`host`，
  `host` 由 hyper 在 send 时加、`build()` 看不到）。`begin`/`ended` 再从 `start`/`stop` 拆一层：
  spawn 之后与 kill 之后的动作是**可以测的**。**变异 R1–R3 + M1–M5 全 KILLED**（R2/R3 成对）、控制行先绿；
  **N1/N2 如实 SURVIVED**（`begin(...)`/`ended(...)` 各一行调用点单测进不去）**只由真机臂覆盖**。
  **175 tests OK**（166 → +9）；build **9 → 9** / clippy **13 → 13**；`rustfmt` 新增行 0 处差异。
  真机探针页臂（T-16 同一套路）：两会话六条记录，5 条带 id（两值不同）、1 条不带（stop 之后的 health
  ⇒ `clear` 真跑过），返回值里一条都不含 id。**三条登记**：退出报告**有意不带 id**、`already_running`
  带 id 只在单测表里、**两侧 id 不相关**（不做跨端串联，D-10 不变）。

- 2026-09-24 T-20：Agent 侧脱敏（`wt-media-agent` `65725f4` + `wt-media-desktop` 的 doc commit `572d1cf`）——
  §7 Q-07 的四处实测缺陷全部修掉：**形态是两条正则按族分治**——`_TAIL_KEYED`（cookie/authorization，
  值 = 行尾）+ `_VALUE_KEYED`（其余族，值 = **一个前导词元且匹配在此结束**）。这一条界是关键：
  `re.sub` 从整段匹配之后**续扫**，值一旦吃到行尾就把后面的凭据一并吞掉、扫描就此停住，
  而 `token=aaa password=bbb` 只掩第一个、第二个原样进日志正是这么来的。回显改用**原文字前缀**
  （`key+separator` 拼回会丢掉 JSON 键的闭引号，写出 `{"client_secret: "***"}`）；
  `_is_cookie_key` 认 `cookie` **与** `cookies`（词表里两个都有）；两个回调各带族守卫 ⇒ 两趟**与顺序无关**。
  **先红**用「把模块换回修前版本」证（`git archive HEAD` + `git show 978155f:…`，不碰工作树）：
  同一份用例 → **FAILED (failures=7)**、控制臂 **19 OK**，7 个失败落在 5 个用例上并逐个点名。
  **20 行差分表的期望串是测量出来的**（临时探针跑 Desktop 实现 + `git checkout` + sha256 `a3fad427…` 核对），
  断言风格从「两列」换成**整行精确串**——两列风格看不见形状错（`{"client_secret: "***"}` 两列都过）。
  **变异 8 个**：M1–M5/M7/M8 KILLED（M1 连**既有** T-06 两列表的 7 条一起打掉），
  **M6（两趟换序）如实 SURVIVED——它本身就是「顺序无关」的证据**，不为它补一条把实现细节写死的用例。
  **真机两臂**（同源两个副本、scratch 端口 18769、两个死端口、5 次真实 POST、`502` 5 次）：
  修后 `agent.log` 三条泄漏针 `bbb`/`b=2`/`password=zzz` 各 0，对照（payload 1 / 修前日志 2）；
  **其余三个针 `aaa`/`a=1`/`s3cr3tvalue` 两侧都掩，修前日志不作对照**（脚本第一版共用对照，
  当场报 3 条 `CONTROL INVALID`，故拆成两组各配能失败的对照）；周围文本 7 项仍在；
  `plain-name-with-no-secret` 原样通过（阴性对照）。**371 tests OK**（365 → +6）。
  **如实登记一处代价**：整尾家族触达行尾 ⇒ `cookies:` 行后的 `group_id=g-1` 一并被掩
  （真机 8/10 条带它），**两侧一致**（Desktop 上实测同三个串）且修前修后触达范围未变，故只登记不改。
  见 `evidence/task-20-agent-redaction.md`。

Current:

- T-20 已收尾（`wt-media-agent` 一个提交 `65725f4` + desktop 一个 doc commit `572d1cf` + 本记录）；
  **Agent 半只剩 T-21**，随后阶段 3 的 T-18 回写与收尾。

Next:

- **T-21（Agent 侧）**：请求级 `operation_id`（`secrets.token_hex(8)` + contextvar + 覆写
  `handle_one_request` 且 `try/finally` 复位），进 `FMT`/`ERROR_FMT`（`error.log` 放在 logger 名之后、
  `error_code` 之前）；测试用端口 0 + `http.client`（**不用 `urlopen`**，避开 T-19 的 AST 规则）。
- **T-20 的两条登记要进 T-18 的 §7/§10**：① 整尾家族的触达是**行尾**，故 `cookies:` 行后的
  `group_id=g-1` 会一并被掩（真机 8/10 条记录带它，缺的 2 条正是 `cookies:` 那两条）——**两侧一致**
  （在 Desktop 上实测同三个串）、修前修后触达范围未变，只登记不改某一侧的答案；
  ② `error.log`/`task.log` 两条臂**未在 T-20 重跑**（缺陷同在 formatter 路径上）。
- **T-17 的三条登记要进 T-18 的 §7/§10**：退出报告**有意不带 id**；`already_running` 带 id 只在单测表里；
  **两侧 id 不相关**（来源与粒度不同，不做跨端对照，D-10 不变）。
- **T-16 的三条登记同样进 T-18 的 §7/§10**：`start` 的 spawn 失败分支够不着；AC-09 真机分母是 **1 行**；
  `already_running` 在 sidecar 死后仍说「已在运行」。另有一条**环境事实**（非缺陷）：debug 二进制带
  `cfg(dev)` ⇒ 加载 `devUrl` 而非 `frontendDist`，没有 Vite 时窗口整页空白，真机臂只能靠探针页替身。
- 之后阶段 3 **T-18** 回写与收尾（含 §7 关掉 Q-07、新增 Q-08、§10 陈旧行修正、
  归档与冷启动重生成、失效指针扫描报分母 + 阳性对照）。

Blockers:

- None。§7 的 Q-01…Q-07 均 `Blocking = NO`，已按读数实施或登记。
  **Q-07（Agent 侧脱敏）已由 T-20 落地修完**（`65725f4`），四处实测缺陷全部关闭；
  但 Q-07 的**行文本身仍按旧行为描述**（它把两处列成「实测输出」），T-18 须整体改写这一行。

Recent verification:

- T-20：`bash scripts/test.sh` → **371 tests OK**（365 → +6，只增不减）；模块 sha256
  `d82d52efaa5f63351477abf64ebd4970c365dbd61c4147e643ba3c22db8251cd` 与 `65725f4` 一致，工作树干净；
  **先红**（修前模块 `cb97e581…`）→ **FAILED (failures=7)**、控制臂 **19 OK**；
  **变异 8 个**（`/tmp/t20_mutate.py`，控制行 371 OK 先绿，逐次改一处跑完即还原）：
  M1–M5/M7/M8 **KILLED**、**M6 SURVIVED（有意）**；
  **真机两臂**（`/tmp/t20/real_arm.sh`，scratch 18769 + 死端口 18790/18791，5 次真实 POST 各 502）：
  `/tmp/t20/assert_arm.py` → **ALL ASSERTIONS PASS**（三条泄漏针各 0、对照 payload 1 / 修前日志 2，
  另一组三个针的对照**已在脚本里点名不成立**；周围文本 7 项仍在；`group_id=g-1` 8/10 条如实登记）；
  跑完 `lsof -nP -iTCP:18769 -sTCP:LISTEN` 为空，全程**未碰** `:8765`/`:18080`/`:54345`。
  Desktop 侧 `cargo test --workspace` → **175 passed**（未增，本 Task 未动 desktop 代码），
  `572d1cf` 只改注释（过滤注释行后 diff 为空）。见 `evidence/task-20-agent-redaction.md`。

- T-17：`cargo test --workspace` → **175 passed; 0 failed**（166 → +9 = `state` 3 + `commands/agent` 5 +
  `http/local_agent` 1，只增不减）；build **9 → 9** / clippy `--all-targets` **13 → 13**（未增）；
  `rustfmt --check --config skip_children=true`：`state.rs` 整文件 0 处差异、`commands/agent.rs` 8 处
  既有脏行（改动前 9，未整文件重排）；**变异 R1–R3 + M1–M5 全 KILLED**（控制行先绿，R2/R3 成对）、
  **N1/N2 如实 SURVIVED**（两行调用点单测进不去，只由真机臂覆盖）；
  真机探针页臂两会话六条记录，5 带 id / 1 不带，脚手架逐项还原（`index.html` sha256 逐字相同、
  5174/18767 无残留、无残留进程、未碰 `:8765`/`:18080`/`:54345`）。
  见 `evidence/task-17-desktop-operation-id.md`。

- T-16：`cargo test --workspace` → **166 passed; 0 failed**（153 → +13 = drain 4 + webview 2 + agent 7）；
  build **9** / clippy **13**（T-15 后也是 9/13，**未增**，13 条逐条列过）；**变异 13/13 KILLED**
  （`/tmp/t16_mutate.py`，3 个旧形态 + 10 个新形态，控制行 166 passed 先绿，逐次 sha256 核对还原）；
  真机三轮（臂 B 真实 sidecar 退出码 255 + 臂 C stub 五个生命周期分支 + 被信号 9 终止），
  全程未碰 `:8765`/`:18080`/`:54345`。见 `evidence/task-16-desktop-emit-points.md`。
- T-15：`cargo test --workspace` → **153 passed; 0 failed**（147 → +6）；build **93 → 9** / clippy **97 → 13**
  ——**与四处登记的 4/10 不符**，差的 5 条逐条点名（`rolling.rs` 的 `SHIPPED`/三个 `DEFAULT_*`/`open_path`
  现在只在测试里被引用；根因是 T-14 把配置文件变成四个数字的来源），另 4 条是既有桩、
  clippy 的 13−9=4 全是既有项 ⇒ 新增代码 0 条 lint；**变异两轮 22 个**（控制行两次先绿，
  第一轮 4 个起初存活、第二轮 3 个幸存且逐条登记守卫方式）；真机三臂（摘要入 stderr **且**入
  开发态文件且首条即摘要 / 占住目录仍启动不 panic / `warn` 0 条不建文件 vs 对照 `info` 1 条）。
  见 `evidence/task-15-desktop-main-wiring.md`。
- T-14：`cargo test --workspace` → **147 passed; 0 failed**（144 → +3）；build **93 → 93** / clippy **97 → 97**
  （测量结果：新常量被 `validate()` 引用、`Logging` 字段由 derive 读写，故无新 `dead_code`）；
  **变异 9/9 红**（控制行 147 passed 先绿），M6/M9 两个缺口当场补齐；
  `rustfmt` 的差异逐行比对后确认只有 7 处**既有脏行**并已还原。见 `evidence/task-14-desktop-logging-config.md`。
- T-13：`cargo test --workspace` → **144 passed; 0 failed**（116 → +28），`logging::` 过滤 76 passed（144 − 76 = 68 = 起点）；
  build 93 / clippy 97（+50 全是新模块 `dead_code`，逐文件核对；`rolling` 的 −1 已查明＝`Date::{year,month,day}` 因
  `backend::stamp` 变活）；**变异 12/12 红**、控制行先绿、逐次 sha256 核对还原；
  **差分表 20 行实跑** Agent vs Desktop（17 同 / 3 异，三处根因从 Agent 源码读出）。
  见 `evidence/task-13-desktop-backend.md`。
- 全套 `bash scripts/test.sh` → **320 tests OK，exit=0**（253 → … → 293 → 320，只增不减）；
  T-02 的 `.local/` 守卫全程不响，`--- Logging error ---` 0 条。
- T-07：六个界各做一次实现变异，**各自打掉自己的用例**（探针先跑未变异对照行）；
  真机两臂（真实入口 + scratch 端口/临时树）8/8 判据；`f07d9e8` 单独 worktree 亦 320 OK。
  见 `evidence/task-07-retention.md`。T-05/T-06 的两向证据见 `evidence/task-05-error-fields.md`、
  `evidence/task-06-redaction.md`。
- T-08：全套 **345 tests OK，exit=0**（320 → 345，只增不减），`.local/` 守卫不响；
  12 个变异**全部转红**且控制行先绿（其中一处检查是变异救回来的，见证据 §1）；
  真机两臂 **20/20**（真实入口 + scratch 端口/临时树），`/healthz` 在两臂里都逐字未变。
  见 `evidence/task-08-health.md`。
- T-09：全套 **354 tests OK，exit=0**（345 → 354，只增不减），`.local/` 守卫不响；
  六个变异各自打掉自己的用例（控制行先绿）；R11 的第三个反例证明「规则被改成 `return []`」时三个反例全红；
  真机 `-m` 探针 11/11，把 `LOGGER_NAME` 变异回 `__name__` 后 A3/A4 转红（`names=['__main__']`）。
  见 `evidence/task-09-single-entry.md`。
- T-19：全套 **365 tests OK，exit=0**（354 → 365，只增不减），`.local/` 守卫不响；
  分母按实测登记（计划 41/34 → 实测 41 = 38 处构造 + 3 处 `urlopen`、**40 模块**）；
  控制臂先绿、7 个变异逐个红，三条真断言各至少有一个变异能红它；
  **两处自查**：一处真误报（`as urlopen` 绑的是 mock，驱动假传输的最干净写法被判成联网）、
  两个对照读整树报告导致任何真实树变动都让它们为假理由变红。
  见 `evidence/task-19-no-external-services.md`。

Blocked:

- None。

Recent verification:

- Start Gate（2026-09-24）：四仓工作区全部干净（governance/agent/desktop/cloud 各 `git status --porcelain` 为空）；
  `delivery/active/` 仅 `.gitkeep`；`delivery/LEDGER.md` 无表行；快照 `Active CHG: none`。
- T-01：见 `evidence/task-01-governance.md`。
- T-02：`bash scripts/test.sh` → **259 tests OK，exit=0**（253 → 259）；改前规则红且**恰好 1 处命中**；
  变异探针下守卫 `exit=1` 而套件打印 `OK`（守卫独立于测试结果）。见 `evidence/task-02-isolation.md`。
- T-03…T-06：见 `evidence/task-03-dev-writes-logs.md`…`evidence/task-06-redaction.md`。
  T-06 的全套为 **293 tests OK，exit=0**；每个 Agent 提交单独 checkout 亦 293 OK。
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
