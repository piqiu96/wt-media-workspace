# Desktop × Agent 联合上线工程优化程序（Program）

- 日期：2026-09-23
- 状态：用户已批准执行（会话内裁定：融合方案一、先执行 CHG-A）。A、B 两阶段已于 2026-09-24 归档 `DONE`；**C 已于 2026-09-25 归档 `DONE`**；**D 已于 2026-09-25 归档 `DONE`**——四个阶段全部关闭，本程序结束
- 性质：上线前工程加固程序，不属 M2/M3 里程碑范围（先例：CHG-20260923-055 里程碑外工程 CHG）
- 承载 CHG：[CHG-20260923-056](../../../delivery/completed/CHG-20260923-056/change.md)（A，**2026-09-24 归档 DONE**）、[CHG-20260923-057](../../../delivery/completed/CHG-20260923-057/change.md)（B，**2026-09-24 归档 DONE**）、[CHG-20260923-058](../../../delivery/completed/CHG-20260923-058/change.md)（C，**2026-09-25 归档 DONE**）、[CHG-20260923-059](../../../delivery/completed/CHG-20260923-059/change.md)（D，**2026-09-25 归档 DONE**）
- 上游基线：ADR-0016（Agent 运行时分层的目录、依赖与配置边界）；架构基线 `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` §5.8

## 1. 问题与目标

`wt-media-desktop` 与 `wt-media-agent` 接近上线，需完成一次联合工程优化，解决六类问题：

1. 服务地址、端口、文件路径和超时等变量写死，修改环境必须改代码。
2. Client 和业务执行代码耦合，自动化测试容易误连真实外部服务。
3. Desktop 和 Agent 缺少清晰的配置、日志、运行目录及初始化规范。
4. 本地开发、自动化测试、Sidecar 和正式安装包缺少可靠隔离。
5. 正式打包、升级回滚和故障诊断尚未形成可持续维护的工程闭环。
6. 运营人员缺少本机文件、缓存和运行日志的查看与安全清理能力。

改造原则：**保留现有稳定功能，按职责收口，尽量少增加抽象**。必须实施真实代码改造，不只是补充架构文档。不重做 Cloud 业务逻辑，不创建第二套任务系统，不引入配置中心、日志数据库、复杂 DI 框架或插件体系。

## 2. 基线融合裁定（2026-09-23 用户裁定，方案一）

用户优化方案与 ADR-0016 的分歧按下述融合执行，**ADR-0016 零修订**：

| 分歧点 | 融合结果 |
|---|---|
| config/logging 目录归属 | 收口在 `runtime/` 下（`runtime/config.py`、`runtime/logging/`），遵循 ADR-0016 第 2 条 |
| 配置文件组织 | `config/`（运行时唯一读取）+ `config_online/`（发布整目录替换）1:1 镜像，单文件 `agent.toml` + environment 字段区分，不按模式选文件 |
| 配置优先级 | **env > file > default**（ADR-0016 第 8 条）；模式区分靠 bootstrap 入口传 context |
| 配置格式 | **TOML**，对齐 Cloud。本表原写「YAML」，2026-09-23 经核实回写：Cloud `config/` 全是 TOML（13 个文件、0 个 YAML），而 Agent 为 `dependencies = []` 零运行时依赖、`uv.lock` 无 YAML 解析器，Python 3.12 起的标准库已自带 `tomllib`。改 TOML 是唯一「对齐 Cloud」且不引入依赖的选项 |
| 开发运行目录 | `.local/{data,logs,versions}`（架构基线 §5.8）；`cache` 子目录**已入基线**——真实需求在 CHG-C 出现（本机设置页的缓存占用与清理，2026-09-25 归档时补进基线）：**只有 Desktop 有 `cache`，Agent 侧没有**；Desktop 装态是 `~/Library/Caches/WTMedia/Desktop`、开发态 `<repo>/.local/cache`，**装机态不在数据根之内**（见架构基线 §5.8） |

新方案的内容全部落地：三类配置分离（部署配置/用户设置/敏感与临时运行上下文）、强类型配置模型、Executor 构造注入 Client、日志脱敏与保留策略、Desktop 用户设置 `settings.toml`。

## 3. 分阶段范围

### CHG-A：结构审计、Config 和 Client 解耦

- 三仓结构审计（已完成：Desktop `main.rs` 1570 行承载全部 17 命令、其余模块空壳；Agent `config.py`/`log_setup.py` 零引用死代码、5+ 处 `os.getenv` 散落、入口空壳）。
- Agent：`runtime/`（config/context/paths/environment/logging）+ `bootstrap/{local,cloud}.py` 真实组装 + `clients/`、`services/` 拆分（撤销 `runtimes/`，ADR-0016 第 4 条）+ executors 注入 + `config/`+`config_online/` 落地 + sidecar 受控传参 + AST 边界测试。
- Desktop：拆分 main.rs（bootstrap/config/paths/state/commands）+ 强类型 DesktopConfig（`resources/desktop.<env>.toml` + env 覆盖 + 生产校验）+ AppPaths + AppState + HttpClient 超时 + Cloud 地址链路（DesktopConfig → 受控 command → Vue）+ sidecar 传参。
- Cloud Web：desktop app 两个生产文件（init.js 地址改 invoke、LocalLogsPage healthz 改走 command）+ 两个测试文件（把上两条改成常驻断言）。
- 详见 [CHG-20260923-056 change.md](../../../delivery/completed/CHG-20260923-056/change.md)。

### CHG-B：Paths、Logger 和运行目录

Desktop/Agent 独立运行目录、日志初始化、落盘、轮转、清理及脱敏；`operation_id` 日志关联；测试目录隔离；sidecar stdout 持续消费（不转存全部 INFO）。

落定后的数字与口径（本节是这些数字的**权威落点**；此前它们只在 CHG-053 草案里出现过，而那处自称「来自程序总纲」并不成立）：

- 轮转与保留：**按小时切割**——正在写的恒为稳定默认文件（`agent.log` / `desktop.log`），
  每小时结束的归档名为 `X.log.<YYYY-MM-DD-HH>`（本机时区）；**只按天保留**，默认 14 天，超期自动删除。
  **没有单文件上限、也没有总量预算**：被限定的是历史留多久，不是它有多少。
  两个值都可配（Agent `[logging] max_record_bytes/retention_days`、Desktop `[logging]` 同名两键），
  两侧出货值一致（14 天 / 1 MiB）。多实例靠**守卫**排除（Desktop `tauri-plugin-single-instance`、
  Agent 单绑定 8765），不再靠 `create_new` 抢名。
- 单条超长记录**截断而非丢弃**，尾部标 `truncate=true original_size=<原字节数>`（Agent 与 Desktop 同形，
  默认阈值 1 MiB）。
- Agent 保持**三个纯文本文件**：`agent.log`（全量、唯一含 traceback）、`task.log`（只收
  `wt_media_agent.runner.*`）、`error.log`（只收 ERROR、无 traceback，每行含
  `error_code` / 可选 `task_id` / 可选 `context`）。**不做 JSONL 改造**，
  053 草案的「三个 JSON 日志文件」不采纳。
- Desktop 稳定文件 `desktop.log`（`~/Library/Logs/WTMedia/Desktop`；开发态 `<repo>/.local/logs`），
  只记 Desktop 自身的启动退出、配置加载、Agent 启停与健康检查、sidecar 异常退出；**不转存** Agent 业务日志。

> 2026-09-24（CHG-20260923-058 T-02）用户裁定改写本节前四条：原「单文件 ≤ 20 MB / 总容量受限
> （Agent 400 MB、Desktop 100 MB）/ 按日期分档（UTC）/ 以 `create_new` 抢名保多实例安全」不再成立，
> 改为上面的按小时切割 + 按天保留 + 稳定默认名 + 单实例守卫。裁定原文、设计裁定与例外登记见
> [CHG-20260923-058 change.md §6/§7](../../../delivery/completed/CHG-20260923-058/change.md)。
- `operation_id` 本轮**只在各进程内部**生成，跨端串联不交付（不加 Header、不进 sidecar 环境）。

详见 [CHG-20260923-057 change.md](../../../delivery/completed/CHG-20260923-057/change.md)。

### CHG-C：Desktop 本机设置

目录查看与修改、存储空间、日志查看（约 500 行 + 级别筛选）、缓存清理、历史日志清理、诊断导出（脱敏）。

落定后的口径（本节是这些事实的**权威落点**；2026-09-25 CHG-C 归档时写入，取代立项时的一句话范围）：

- **页面在 `wt-media-cloud/web` 构建**（`web/src/apps/desktop/features/local-settings/` 与 `features/local-logs/`），
  路由 `/settings`，路由名 / 免鉴权名单 / 侧边导航三处必须一致。**页面不直连 Agent 的回环端口**——
  窗口的 CSP 挡着，直连只会得到一句「Agent 不可达」，这条由 `localAgentBoundary.test.js` 钉住。
- **命令面新增恰 9 个**（Desktop `src-tauri/src/commands/`，全部**追加**在 `invoke_handler!` 末尾）：
  `local_settings_get` / `local_settings_set` / `local_open_place`、
  `local_storage_usage` / `local_log_files` / `local_log_tail`、
  `local_cache_cleanup` / `local_log_cleanup`、`local_diagnostic_export`。
  页面与命令之间只有这一条通路；参数名在前端是 camelCase、在 Rust 是 snake_case。
- **用户设置**是数据根下的 `settings.toml`（`schema_version` + 同级临时文件 + `rename` 的原子替换；
  损坏时**保留原文件并报错**，不静默清空）。`save_dir` 目前**没有任何消费方**——页面能改它，
  不等于下载会按它落盘。
- **存储与日志的读取面遵守「列表即白名单」**：命令先列目录再按名查找，从不把用户给的字符串拼到路径上；
  **不在 ⇒ 0，读不到 ⇒ `Err`**（不是 0 MB）。日志筛选的语义是**该级别及以上**，未分级的行不受影响。
- **清理只删可安全再生的文件与已轮转的归档**：活文件永不删；数据根下的素材/成片/SQLite/检查点/待回传
  结果都在保护面内；读者认不出的日志名（`Other`）是**显示**类目、不是删除类目。一次只清**一棵**日志树，
  回报的是**实际释放字节**（由一次独立 walk 对账，不是可用空间差值）。
- **诊断导出**是**一个 gzip tar + 一棵目录树**（`summary.json` + `manifest.txt` + `logs/{desktop,agent}/…`），
  摘要值是**归档外的兄弟 `.sha256`**（放进包里会自指）。每条进包的字符串都过脱敏，日志条目**两次**。
  「不含用户媒体」由**布局**保证（每棵树只读一层），不靠名字过滤。

详见 [CHG-20260923-058 change.md](../../../delivery/completed/CHG-20260923-058/change.md)。

### CHG-D：Sidecar、打包、升级与回归

端口就绪通知与实例身份验证、退出 draining、PyInstaller 产物完整性、`config_online → 产物/config` 打包步骤、版本兼容、正式安装包脱离开发环境验证、M2 业务回归。

落定后的口径（本节是这些事实的**权威落点**；2026-09-25 CHG-D 归档时写入，取代立项时的一句话范围）：

- **就绪是两段式**：第一信号是 Agent 在 `bind` + `listen` **之后**打印的 readiness 行，第二信号是 `/healthz`
  真的应答。`[sidecar] start_timeout_ms`（出货 `15000`）从死配置变成这道闸门的真超时。
  **认证失败是致命的第三态**：令牌漂移时 `/healthz` 在 `_check_auth` 之后，答 **401** ⇒ 立即失败，不等到超时。
- **实例身份是活性探针**：`already_running` 只在受管槽位**非空**时才真的问一次 `/healthz`——
  槽位为空时**一个请求都不发**（那个端口上可能是开发机上别人的 Agent）。句柄在而 Agent 不应答 ⇒
  如实报「未在运行」，丢弃句柄并允许重启（这就是 CHG-057 登记的那条实缺陷的关闭）。
- **退出是请停而不是硬杀**：Desktop 的 `RunEvent::Exit` → **SIGTERM** → 宽限（`[sidecar] stop_timeout_ms`，
  出货 `5000`）→ 必要时强杀；**退出报告要能区分**「请停后自己退出」与「被强杀」。Agent 侧在 `serve()` 里
  安置 SIGTERM 处理器并把 `shutdown()` 派到自己的线程，且 `httpd.daemon_threads = False`——
  `ThreadingHTTPServer` 默认 `True` 时 `_Threads` **不登记守护线程**，`server_close()` 的 join 是空转。
- **产物完整性在启动前校验**：读包内 `Contents/Resources/sidecar-manifest.json`，按 SHA-256 比对**要启动的
  那个文件**；失败拒绝启动并说清原因，且**不回退**到 Python 调试路径。没有记录时**工程树容忍、包里拒绝**
  （`cargo test` 的树里没有记录，不这样区分就起不了 Agent）。这份记录写在 sidecar 的 ad-hoc 签名**之后**、
  外层签名**之前**——签名会改写文件，而签名之后写进去的字节不会再被封面盖住。这是**包一致性检查**，
  不是对抗能改包者的安全边界（ad-hoc 签名没有信任锚）。
- **`config_online → 产物/config` 发生在产物上**：由 `scripts/stage-release-config.sh` 整目录替换，
  **不进 `tauri.conf.json` 的 `bundle.resources`**（Tauri 会拒绝匹配不到任何文件的 glob，于是任何还没跑过
  发布步骤的检出都编译不过）。冻结侧的配置目录由**可执行文件的位置**推导（`.app` 里是
  `Contents/Resources/config`，否则可执行文件旁边的 `config/`），命中不了先 WARNING 再回落内置默认值。
- **五类版本各有来源**：Desktop（`tauri.conf.json`）、Agent（包版本）、**前端构建**（workspace 复制产物时
  stamp）、Contract（`config/contract-map.yaml`）、**组件与资源**（`Contents/Resources` 逐文件 sha256 的合并
  摘要，排除记录自身——它是**内容摘要**而不是被人递增的号，没有「谁来 bump」）。出包时写一份
  `versions.json` 进产物、另复制一份到发布目录并进 `SHA256SUMS`；挂载 DMG 后 `--verify` 复算出同一摘要。
  **Desktop ↔ sidecar 用 pin 而不是等值**：`src-tauri/agent-compat.json`，不匹配必拒，**改 pin 即评审**
  （兼容是评审闸门，不是版本号相等）。
- **升级不覆盖是路径判据**（本 CHG **不实现升级器**）：保护的是一组**路径**（数据根下除
  `settings.toml` 与 `versions/` 之外的一切，含 SQLite、检查点、待回传结果），不是一张名字清单。
- **M2 回归的覆盖边界**：链路十三个阶段全绿，其中真 MySQL 与真 BitBrowser 是真读数，
  **实网／实凭据／GUI 三项没有**——不要把这句读成「M2 已在真外部环境重跑」。
- **两条登记过的例外**：①「干净机」安装验收**未做**（D-09，本机是开发机）；
  ②随包 onefile sidecar 的引导器是否把 SIGTERM 转发给真正在服务的进程**未测**（本机 `dlopen` 被签名拒）。
  另有一条未裁定：**Q-05**——M2 链路的 DMG 构建是否改走发布打包、以及 M2 环境里 8765 归谁。

详见 [CHG-20260923-059 change.md](../../../delivery/completed/CHG-20260923-059/change.md)。

## 4. 横切要求（各阶段通用）

- Config 三类分离：部署与运行配置（开发/部署控制）、用户设置（Desktop 页面修改、存用户数据目录）、敏感信息与临时运行上下文（安全存储/启动时生成）。不混进一个文件。
- 依赖方向：`Bootstrap → Config Loader → Validated Config → Clients/Logger/Runtime → 注入 Services/Executors`。Executor 不读环境变量、不初始化 Logger、不创建底层 HTTP Client。
- 两端独立运行：Agent 必须可脱离 Desktop 启动；Desktop 只传必要运行参数与凭证，不接管 Agent 内部配置与 Logger。
- 敏感信息永不进日志：Cookie、Password、Authorization、Bearer/Refresh/Agent Runtime Token、代理密码等。
- 验收不以编译通过、目录创建、类定义完成为准；每阶段交付实际发现问题、修改文件与职责变化、删除或迁移的硬编码、配置加载与验证结果、日志落盘与清理测试结果、真实运行或打包验证证据、未解决风险。
- 模块分工回写：每阶段完成时同步更新各仓 `AGENT-INDEX.md`/`DIRECTORY_MAP.md` 与 workspace 职责基线；`.ai/CURRENT_CONTEXT.md` 由脚本生成，禁手改。

## 5. 来源说明

本程序由用户于 2026-09-23 会话内提供完整优化方案并裁定融合与执行顺序；本文件为其治理沉淀，冲突时以用户原始裁定记录与本文件融合表为准，ADR-0016 保持原有效力。
