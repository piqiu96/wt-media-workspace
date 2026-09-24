# CHG-20260923-058：联合工程优化 C——Desktop 本机设置

## 1. Basic Information

- Level: M
- Status: DONE（2026-09-24 由 `delivery/planned/` 激活并改写为十三节执行记录，2026-09-25 关闭并归档；
  关闭时的口径见 §12 与末行的归档说明）
- Created: 2026-09-23
- Current repository: wt-media-workspace（治理）；运行时改动分布于 wt-media-desktop、wt-media-cloud/web、wt-media-agent
- Affected repositories:
  - `wt-media-desktop`
  - `wt-media-cloud`
  - `wt-media-agent`
  - `wt-media-workspace`
- 不受影响并已声明：Cloud 后端 Go 服务（本 CHG 只碰 `web/`）

## 2. Change Goal

完成上线前工程优化第三阶段（C）：给运营一个**能看懂、能安心操作**的本机管理面——
文件保存位置、存储占用、日志查看、缓存与旧日志清理、脱敏诊断导出；同时把 B 阶段落地的日志体系
**按用户 2026-09-24 的新裁定改名与改轮转口径**。

用户可见的独立可验证结果：

1. **本机设置页**可查看并修改素材下载/成片保存位置；**只影响后续任务**——不迁移历史文件、
   不影响正在执行的任务。
2. **存储与日志**页显示可用空间、缓存占用、日志占用，数据取自**真实目录**；
   **读取失败必须是错误，不得显示为 0 MB**。
3. **日志查看器**可读约 500 行、按级别筛选，并能一键打开日志文件夹。
4. **清理**分两类（缓存 / 已轮转历史日志），只处理可安全再生文件与已轮转归档；
   素材、成片、SQLite、检查点、待回传结果、正在写入的文件**一律不删**；完成后展示**实际释放空间**。
5. **诊断导出**是一个脱敏归档：版本 + 组件状态 + 已脱敏日志 + 失败任务摘要；
   不含完整凭证、Cookie、代理密码与用户媒体文件。
6. **日志文件名与轮转**改为：稳定默认文件 `desktop.log` / `agent.log` / `task.log` / `error.log`
   `+ 小时切割`，归档名 `X.log.<YYYY-MM-DD-HH>`；**取消单文件上限与总量预算**，**保留按天删除**。
7. 加**单实例守卫**：第二次启动不再产生第二个 sidecar 与第二个日志写入者。

用户 2026-09-24 的原话裁定按条落在 §6 D-01…D-08。

## 3. Baseline References

- Milestone: `delivery/milestones/M-launch-engineering.md#成功事实全部成立`
  （本 CHG 的验收锚点是**成功事实 #6**：「清理缓存/旧日志不删业务文件与运行数据；读取失败不显示 0 MB」
  与**成功事实 #5**：「日志独立落盘、轮转、受容量限制；敏感信息（Cookie/Token/代理密码）不进日志与诊断包」
  ——#5 的「受容量限制」一句本次**按用户裁定改写为「按天保留」**，见 §6 D-03 与 T-01 的基线回写。
  失败行为锚点：「升级或清理删除业务数据」与「配置写入一半损坏用户设置且静默清空」。）
- Engineering baseline: `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md`
  §3 CHG-C（`:66-68` 范围）、§4 横切要求（`:74-81`，含「Config 三类分离」`:76`
  与「验收不以编译通过…为准」`:80`）
- Engineering baseline（架构）: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
  §5.8（`:1176-1225` 本地目录和日志，本 CHG 要回写的一处）、§6.8（`:1435-1456` 安装目录和用户数据）、
  §7.11（`:1680-` 日志和诊断）
- 上游 CHG：[CHG-20260923-057](../CHG-20260923-057/change.md)（B，日志体系与数字的既有落点，
  本 CHG 改写其中「命名/轮转/限额」三项口径并**在归档记录顶部加取代注记，不改写其正文**）

## 4. Current Facts

本节每条都是在激活时**实测**得到的（file:line 与命中数），不是从草案推想的。

### 4.1 Desktop：本机设置的**承载面尚不存在**（不是「补齐」）

| 断言 | 实测 |
|---|---|
| `AppPaths` / `app_paths` | `src-tauri/src/` **零命中**（分母：38 个 `.rs`、9835 行；阳性对照 `fn ` → 419 命中） |
| `settings.toml` / `UserSettings` / `schema_version` | 三者**各自零命中**（同分母） |
| `cache` / `versions` | **各零命中**——连注释里的 substring 都没有 |
| `paths.rs` 能否就地扩展 | **不能**。它是**配置文件定位器**（`:1` 「Where the desktop configuration file comes from.」），模块 doc 明写「A locator that could return 'nothing' would make that failure mode possible.」——与「运行目录解析」的失败契约不同。**另起模块**，抄 `logging/paths.rs:56 directory(home, environment, manifest_dir)` 的注入式写法 |
| `filesystem/`、`secure_store/`、`system/`、`updater/` | **各 3 行空壳**（如 `updater/mod.rs` 只有 `//! Component update and signature verification boundary.` + `pub struct Updater;`）；`DIRECTORY_MAP.md` 自己写明「不要把它们当成可读的实现来源」 |

### 4.2 Desktop：日志目录**没有任何读取方**，命令面也没有入口

- `logging/rolling.rs:629 fn list(&self)` **不是 `pub`**；`Writer`（`:443`）**字段全私有**。
  `Writer` 的公开面只有 `open` / `open_path` / `write_line` / `prune`（`prune` 只删不读）。
- **生产路径零读日志**：`read_to_string|BufReader|fs::read|read_dir|File::open` 全树 **19 命中**，
  其中 `paths.rs:131` 读的是**配置 TOML**、`rolling.rs:631` 是上面那个私有 `list`、
  **12 命中在 `#[cfg(test)]` 里**、两处在 `logging/test_support.rs`（`#[cfg(test)]` 模块）。
  **`BufReader` 与 `File::open` 各零命中。**
- `main.rs` 的 `invoke_handler!` 在 **`:131-152`**，注册 **18** 个命令；`:149-150` 有承重注释：
  「Appended, not inserted: `localAgentService.test.js` asserts on exact argument objects,
  and the existing seventeen keep their positions.」⇒ 新命令**追加在末尾**。

### 4.3 Desktop：诊断归档所需的依赖**一个都没有**

- `src-tauri/Cargo.toml`（42 行）直接依赖仅：`serde`、`serde_json`、`tauri`、`tauri-plugin-shell`、
  `reqwest`、`tokio`、`toml`、`uuid`、`tracing`、`tracing-subscriber`。**无 `[target...]` 段。**
- **无压缩/归档依赖**：`zip`/`tar`/`archive` 在 `Cargo.toml` **零声明**；`flate2` 只在 `Cargo.lock`
  里作为 `png` 的传递依赖存在；**`tar` 在 `Cargo.lock` 中零出现**。
- **无哈希依赖**：`sha2`/`hex` 只在 lockfile 里被 `tauri-codegen`/`serde_with` 传递带入，
  **不在 `wt-media-desktop-shell` 的依赖表**；`blake3`/`sha1` 零出现。
- `capabilities/default.json` 权限只有 `core:default` + 四个 `shell:*`，**无 fs 权限**。

### 4.4 前端：页面在 **cloud/web 仓**，且「本机设置」连壳都没有

- **承重事实**（`wt-media-desktop/DIRECTORY_MAP.md:5` 逐字）：「**业务 Vue 页面源码在
  `../wt-media-cloud/web`，不在本仓库。** 本仓库只拥有 Tauri 原生壳」。⇒ T-07 的改动落在 `wt-media-cloud/web`。
- `LocalLogsPage.vue` 路径 `web/src/apps/desktop/features/local-logs/LocalLogsPage.vue`，**40 行**，
  **纯桩**：唯一会显示的「日志」是字面量 `'Agent 日志查看功能待实现'` 或 `'Agent 不可达'`，
  且只调 `local_agent_health`。
- `本机设置` 在 `wt-media-cloud/web` **零命中**（分母：`src` 74 个文件 / 10334 行），
  在整个工作区 `*.md|*.vue|*.js|*.rs` 也零命中。
- **但占位目录已预留**：`web/src/apps/desktop/features/local-settings/.gitkeep`（0 字节）。
  同级还有 `environment/`、`local-agent/`、`local-logs/`、`updater/` 四个 `.gitkeep`。
- 路由：`web/src/apps/desktop/router.ts:30-32` 只有 `agent` 与 `logs` 两条桌面独有路由，
  `:33` 逐字写明 `// 不包含 /users — Cloud 管理页面`。
- **免鉴权白名单**：`web/src/apps/desktop/main.ts:36-46`，`:43` 按**路由名**放行
  （`to.name === "AgentStatus" || to.name === "LocalLogs"`）⇒ 新页面**必须**加进这一行，否则会要求 Cloud 登录。
- 导航：`web/src/layout/AppLayout.vue:55-60` 的 `desktopItems`；`:81` 合并进 `sourceItems`。
  `:43-45` 有承重注释：图标名**必须是真实 sprite id**（`gallery`/`comment`/`organization` 曾不存在）⇒ 复用
  `setting`/`file`/`server` 一类的既有 id。
- `SettingsPage.vue`（`web/src/shared/ui/templates/SettingsPage.vue`，92 行）是**无人引用的设计模板**
  （`grep -rn "SettingsPage" src/` 零命中）⇒ 只能当视觉参考，不能当可复用实现。

### 4.5 前端测试：两条**硬约束**，会直接判 T-07 的写法

- `web/src/localAgentBoundary.test.js:47-51` 逐字：
  ```js
    it('does not let the local-logs page reach the Agent port itself', () => {
      const page = read('./apps/desktop/features/local-logs/LocalLogsPage.vue')
      expect(page).not.toMatch(/127\.0\.0\.1/)
      expect(page).not.toMatch(/\bfetch\(/)
    })
  ```
  ⇒ 重写后的查看器里**不得出现**子串 `127.0.0.1` 或 `fetch(`，**注释里也不行**。
- `web/src/localAgentService.test.js`（174 行）对 `invoke` 断言**精确参数对象**
  （camelCase → `args` 下 snake_case；`profileRestore` 是唯一 `{ profiles }` 顶层例外）。
  命令名契约在 `features/local-agent/service.js:4-21` 的 `LOCAL_AGENT_COMMANDS`（**16** 个，`Object.freeze`）。
- 计数基线：`src` 下 **32** 个 `.vue`、**21** 个前端测试文件。

### 4.6 Agent：T-01 要换掉的四个界各自住在哪里

`src/wt_media_agent/runtime/logging.py` **889 行**，结构已测绘：
`AGENT_LOG_NAME`/`TASK_LOG_NAME`/`ERROR_LOG_NAME`（`:50-52`）、`FMT`（`:66`）、`ERROR_FMT`（`:102-105`）、
`redact()`（`:286-301`）、`RedactingFormatter`（`:320-367`）、`LogBudget`（`:462-593`）、
`BoundedFileHandler`（`:596-728`）、`configure_logging`（`:731-840`）、`configure_from`（`:852-888`）。

| 界 | 今天在哪 | 换成标准库后归谁 |
|---|---|---|
| 日期/大小翻档 | `BoundedFileHandler._roll_if_needed`（`:696-717`） | `TimedRotatingFileHandler(when="H")` |
| 归档命名 `agent-YYYYMMDD-N.log` | `_free_name`（`:708-717`） | 同上，`suffix="%Y-%m-%d-%H"` ⇒ `agent.log.<ts>` |
| 单条超长截断 | `_bounded`（`:658-680`） | **仍是我们**（保留，见 §7 Q-01） |
| 总量上限 | `LogBudget.prune` 的 `:558-566` 循环 | **删除**（裁定 D-03） |
| 按天保留 | `LogBudget.prune` 的 `:551-556` | **保留**（`backupCount=0` 关掉 stdlib 的按个数删除） |

- 归档**家族名正则是运行时拼的**：`LogBudget.register:513-520` =
  `^stem-(\d{8})-(\d+)suffix$`，`rolled():528-538` 用 `strptime(...,"%Y%m%d")` 解回。
  **新形态同时废掉写侧与读侧**，两侧都要改。
- 数字来源三层：`constants.py:48-50`（20MB/14天/400MB）→ `config.py:199-201`（`[logging]` 三个键 +
  三个 `WT_MEDIA_LOG_*` 环境变量）→ dataclass `:225-227`；**交叉校验在 `:346-350`**
  （`total_bytes < max_bytes` 报错）。未知键**不报错**，按名字 WARNING（`:299-309`）。
- `configure_from` 在 `src/` 里**只有 1 个调用点**：`bootstrap/app.py:76`；
  该唯一性由 `tests/test_dependency_boundaries.py:602-674` 的 R11 AST 规则钉住。
- **测试锚点**（T-01 必须同步，否则是「改代码没改测试」）：`tests/test_log_rollover.py`
  **21 个 `def test_`** 且**21 处**断言旧归档名（`:135,137,152,153,157,158,169,171,235,236,246,252,260,261,262,284,285,344,366,398,408`）；
  `tests/test_runtime_logging.py:151` 硬断言 `kinds.count("BoundedFileHandler") == 3`；
  `BoundedFileHandler` 全仓 **8 命中**（src 2 / tests 6）。

### 4.7 起点测试基线（本 CHG 的「只增不减」分母）

| 仓 | 命令 | 起点 |
|---|---|---|
| agent | `bash scripts/test.sh` | 379 tests OK |
| desktop | `cargo test --workspace` | 175 passed / 0 failed |
| cloud web | `npx vitest run` | 21 个测试文件 |
| workspace | `verify_delivery_governance.py` / `verify_agent_entry.py` / `verify_skills.py` | 三者绿；`unittest discover` 有 **4 条已登记既有红项**（见 `README.md`） |

### 4.8 本机环境事实（影响验证方式）

- `~/Library/Logs/WTMedia/Agent/` 现为 `agent.log`(1674B) + `error.log`(0) + `task.log`(0)；
  `.../Desktop/` 现为 `desktop-20260924-1.log`(336B)——**旧形态**，已存档到 `/tmp/chg058/preexisting/`。
- **实测到一条本 CHG 范围外、属 CHG-D 的真缺陷**：`osascript quit` 关掉 app 后，
  **两个 `wt-media-agent` 存活**、PPID 被 `/sbin/launchd` 收编、**仍在 `127.0.0.1:8765` LISTEN**。
  证据 `/tmp/chg058/preexisting/orphan-sidecar-after-quit.out`。⇒ 登记给 CHG-D 的「退出 draining」范围。

## 5. Scope

### Add

- Desktop：运行目录解析模块（data/logs/versions/cache + 开发态 `.local/`），注入式、纯函数优先；
  用户设置持久化（`settings.toml` + `schema_version`，原子替换）；存储/日志只读命令；
  清理命令（缓存 / 历史日志）；诊断导出命令；`tauri-plugin-single-instance`；
  `logging::rolling` 的**公开读取面**（列文件 + 读尾部行）。
- Desktop：`file-rotate` + `chrono` 依赖，取代自写轮转。
- Cloud Web：`features/local-settings/` 的实际页面 + 路由 + 导航项；重写 `LocalLogsPage.vue` 为查看器。
- Agent：`TimedRotatingFileHandler` 路径 + 保留截断包装；`LogBudget` 收敛为纯按天。
- Workspace：本节十三节记录、`checkpoint.md`、`status/<repo>.md`、`evidence/`。

### Modify

- 程序总纲 §3 CHG-B 的「落定后的数字与口径」（`:52-55`、`:60`）——按 D-01/D-02/D-03 改写；
  架构基线 §5.8 的同一批数字与 Desktop 文件名；里程碑成功事实 #5 的「受容量限制」；
  `Cargo.toml` 里拒绝 `tracing-appender` 的注释（拒绝理由要改成真实的那个）；
  `rolling.rs` 的模块 doc（「多实例也安全」的理由要换）。
- Agent `runtime/constants.py`、`runtime/config.py`、`config/agent.toml`、`config_online/agent.toml`
  （去掉总量与单文件上限键）、`runtime/logging.py`。
- 两个运行仓的 `AGENT-INDEX.md` / `DIRECTORY_MAP.md`。

### Delete

- Desktop `rolling.rs` 的自写轮转四件套：`file_name`/`parse_file_name`/`claim()` 的 `create_new` 抢名/
  `expired()`/按量删除（被 `file-rotate` 取代）。
- Agent `BoundedFileHandler` 的翻档与限量逻辑（保留截断）。
- Agent `DEFAULT_LOG_TOTAL_BYTES`、`DEFAULT_LOG_MAX_BYTES` 与 `[logging] max_bytes/total_bytes` 两个配置键。

### Explicitly Not Doing

- **不做系统数据目录清空入口**（草案原文，继续有效）。
- **不重复建设任务中心**：业务任务详情留在原页面。
- **不改 Cloud 后端 Go 逻辑**（本 CHG 只碰 `web/`）。
- **不重做 M2/M3 业务闭环**，不改任何已验收业务语义。
- **不交付跨端 `operation_id` 串联**（承 CHG-057 D-10 不变）。
- **Desktop 不转存 Agent 业务日志**（承 CHG-057 D-07 不变）。

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | 日志命名统一为 **`X.log.<时间戳>`**（Desktop `desktop.log.<ts>`、Agent `agent.log.<ts>`，`task`/`error` 同理），且**保留一个稳定的默认文件名**（正在写的是 `desktop.log`，归档是 `desktop.log.<ts>`）；**按小时切割**。 | CONFIRMED（用户 2026-09-24：日志名应为 `desktop.log.时间戳`；「默认是小时，有个默认文件，然后一个小时切割一次」） |
| D-02 | **尽量用开源，不重复造轮子**。Desktop 用 **`file-rotate` 0.8.0**（`ContentLimit::Time(TimeFrequency::Hourly)` + `AppendTimestamp::with_format("%Y-%m-%d-%H", …)`）；Agent 用**标准库** `TimedRotatingFileHandler(when="H", suffix="%Y-%m-%d-%H", backupCount=0)`。 | CONFIRMED（用户 2026-09-24：「都是保留 desktop.log.时间戳 agent.log.时间戳 这里按理都是有开源工具不需要单独开发」「尽量使用开源，尽可能不改轮子」） |
| D-03 | **不控制总量**：取消单文件上限与目录总量预算；**只按天保留**（超过 7 或 14 天自动删除）。截断标记按 §7 Q-01 处置。 | CONFIRMED（用户 2026-09-24：「对于日志不需要控制总量，只需要控制能保留多少天超过7天或14天自动删除，不需要控制总量」） |
| D-04 | **加单实例守卫**（`tauri-plugin-single-instance`），第二次启动把已有窗口召到前台。**理由必须写清**：稳定默认名 `desktop.log` + crate 的 rename-on-roll ⇒ 两个实例会共用一个活文件，一个实例重命名时另一个的句柄还在写被改名的归档。**没有正当的多实例场景**——守卫是**禁止**一个坏状态，不是**启用**一个能力。**守卫必须跑在日志落盘之前**：插件的 `setup` 在 `Builder::build` 内部执行（tauri 2.11.5 `app.rs:2440`），第二次启动由插件自己 `std::process::exit(0)`；若按一次调用 `Builder::run(context)` 建应用，将死的那个进程会**先装好 sink、写下一条记录**再退出——实测该记录会让它按过期的 mtime 轮转、在第一个实例的句柄下把 `desktop.log` 改名成归档，第一个实例随后往归档里写真实记录。故拆成 `build(context)` + `app.run(...)`，**安装日志在 `build` 之后**（`main.rs`）。 | CONFIRMED（用户 2026-09-24：「加实例守卫，需要说明下为何需要多实例什么场景下？」）；时序与危害为**实测**（`/tmp/si-probe.sh`，变异版复现出 `desktop.log.2026-09-24-19` 与新 inode） |
| D-05 | 本 CHG **允许修改 `wt-media-cloud/web`**。 | CONFIRMED（用户 2026-09-24：「允许改 cloud/web（推荐）」） |
| D-06 | 日志改名与轮转改造**折进本 CHG 作为第一个任务 T-01**，不单独开 CHG。 | CONFIRMED（用户 2026-09-24：「折进 CHG-C 第一个任务（推荐）」） |
| D-07 | 脱敏要求与「Desktop 不转存 Agent 业务日志」两条**不变**：它们与轮转正交，且是成功事实 #5 的另一半。 | CONFIRMED（承 CHG-057 D-07/D-08） |
| D-08 | 本 CHG 的基线回写对象**限定为四处活基线 + 两个运行仓入口文档**（清单见 §5 Modify）；CHG-057 的**归档记录正文不改写**，只在其顶部加一段「被本 CHG 取代」的注记（照它自己 T-18 处置 T-01 的先例）。 | CONFIRMED（本次实施口径；依据 `archive-sweep-fix-paths-keep-narration` 的分类：过去时叙述判「留」） |
| D-09 | **两侧都用本机时区**：归档名与记录戳同一个钟（Agent 的记录戳本来就已本地化——`logging.Formatter` 默认 `time.localtime` 且无处设 `converter`，只有 `LogBudget.today()` 是 UTC，故改名后名字与戳才对齐）；Desktop 的记录戳**去掉末尾 `Z`** 并与归档名同钟。比较的是**归档名里的时间戳字符串**，零填充 ⇒ 字典序即时序。 | CONFIRMED（用户 2026-09-24：「两侧都改本机时区（推荐）」） |
| D-10 | **Agent 的小时轮转必须对齐到整点**，与 Desktop 一致。实测：标准库 `computeRollover` 只在 `MIDNIGHT` 与周模式有对齐分支，`when="H"` 直接返回 `currentTime + interval`——20:58 起的进程在 21:58 轮转，而 `doRollover` 用 `rolloverAt - interval` 命名 ⇒ 归档名说 20、内容却写到 21:58，**名字与内容差近一小时**。故覆写 `computeRollover` 为下一个本地整点。（另实测：`when="H"` 自选 suffix 为 `%Y-%m-%d_%H`，下划线，须在 `super().__init__` 之后显式设回 `ARCHIVE_FORMAT`。） | 本次实施裁定（用户 2026-09-24 明确的目的是「按小时切割」+「本机时区」；不对齐会让这两条同时落空）。**实测**自真机探针读 `rolloverAt`，非读文档推断 |
| D-11 | **`local_log_cleanup` 一次只清一棵树**：命令收**来源标签**（`"desktop"`/`"agent"`，与 `local_log_tail` 同一拼法），不收路径；不提供「一次清两棵树」的按钮。Q-08 的裁定覆盖的是**读**两棵树，把「删」也延伸过去是**本 Task 的决定**——Agent 的归档是 Agent 的，替另一个组件决定它的历史可以删，不能靠一句读的裁定借来。页面仍可每棵树一个按钮。 | 本次实施裁定（沿 Q-08 的边界，不越过它） |
| D-13 | **导出落点**：`~/Downloads` 存在时写那里，否则写本组件数据根；写之前 `create_dir_all` 自己选的那个目录（T-03 的规矩：读者只问在哪，写者负责准备）。这**不是**安全边界（包本身就是脱敏的），是一个便利性决定——人们要附文件时看的就是那里。 | 本次实施裁定（真机探针读出的落点，见证据「三处只有跑起来才能发现的缺陷」第 1 条） |
| D-14 | **内容边界**：`bit_profile_ids` **只计数不列举**（`bit_profile_count`）；`main_user_id` **有意包含**（「这个包属于哪个账号」的唯一线索，本身不是凭证）；失败摘要只取 **warn 及以上**；直接躺在日志树里的陌生文件**收进来**（脱敏、限长之后）——那棵树归本组件所有，T-06 已定过不认识的日志名是**可见**类目。 | 本次实施裁定（逐项在证据里枚举，属「我们少放了一样东西」那一类，写下来而不是留给人推断） |
| D-12 | **`FileKind::Other` 永不删**：读者不认识的日志名（真机样本＝T-02 之前的 `desktop-20260924-1.log`）在查看器里**可见**，清理**不删**，想清掉只能手动。理由取读者自己的定义（这种名字「不是我们的」），而不是「可能没用所以删了更干净」。 | 本次实施裁定（`Other` 是**显示**类目，不是**删除**类目） |

## 7. Pending Questions

| ID | Question | Blocking |
|---|---|---|
| Q-01 | **单条超长记录的截断阈值**。CHG-057 D-05 明写「单条日志超限必须截断…不得因此无限增长」，用户本次只取消了**总额与单文件上限**、未撤销截断。但原阈值**就是**单文件上限（20MB），取消后需要重新给一个数。**按 `max_record_bytes = 1 MiB` 实施**（够容纳任何真实 traceback，且做成可配），标记 `truncate=true original_size=<n>` 原样保留。要改请一句话。 | NO |
| Q-02 | **保留天数默认值**。裁定说「7 天或 14 天」。**取默认 14**（与今天出货配置 `retention_days = 14` 一致，避免顺带改一个用户没要求改的数），做成可配。 | NO |
| Q-03 | **Desktop 归档名取哪一小时**。用 `DateFrom::DateHourAgo` ⇒ 归档名是**刚结束的那一小时**（轮转发生在 11:00 时归档名为 `…-10`）。这是 logrotate 语义、也是 crate doc 对 hourly 的推荐（「Date from hour ago, useful with rotate hourly」）。要改成「当前小时」请一句话。 | NO |
| Q-04 | **crate 只在 `new()` 扫一次目录**（实测根因，见 §4 与证据）：**构造之后**才出现在磁盘上的归档文件**永不被删除**。后果两条：①同小时内多次轮转会产出 `desktop.log.<ts>.1/.2`；②别的进程/实例建的归档不会被清。①无害；②由 D-04 的单实例守卫消掉主场景。**登记为已知边界，不自行实现「每次轮转重扫」**（那是改 crate 的语义）。 | NO |
| Q-05 | **失去注入时钟**（实测：crate 的 `mock_time`/`set_mock_time` 是内部 `#[cfg(test)]`，下游拿不到）。CHG-057 T-12 的 25 个变异靠 `Clock` 注入，本 CHG 改用 `FileRotate::rotate()`（`pub`，确定性触发）+ 改活文件 mtime（`filetime`）构造边界。**覆盖降级如实登记在 T-01 的证据里**，不假装等价。 | NO |
| Q-06 | **诊断导出需要新依赖**（§4.3：无 zip/tar、无哈希）。**按 `tar` + `flate2` + `sha2` 实施**（archive 只包含一个目录树，不需要 zip 的处理无关；`flate2` 已在 lockfile 里）。要改用别的打包格式请一句话。 | NO |
| Q-07 | **两侧机制有意不对称**：Desktop 的按天删除由 crate 承担，Agent 的按天删除仍由 `LogBudget` 承担（标准库确实没有按天删除）。这条不对称**写进基线**，免得后来者以为两侧同机制。 | NO |
| Q-08 | **日志查看器读哪几棵树**。本机有两棵独立的日志树（`…/Logs/WTMedia/Desktop` 与 `…/Logs/WTMedia/Agent`）。**按「Desktop 侧的只读命令覆盖两棵树」实施**：页面归 Desktop，而 CHG-057 D-07 禁止的是**写入/转存**，不含只读呈现。要只看 Agent 树或只看 Desktop 树请一句话。 | NO |

无阻塞项（`Blocking = NO`）：Q-01…Q-08 均已按上述口径实施或登记，用户可在任一 checkpoint 用一句话改判。

## 8. Implementation Tasks

每项执行序列：`先失败的验证/测试 → 最小实现 → 测试 → diff 检查 → evidence → checkpoint → 独立提交`。
**一仓一 commit；「移动文件」与「改逻辑」绝不进同一 commit。**

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | 激活与记录（本文件、`checkpoint.md`、`status/`、`evidence/`），LEDGER 加表行，`planned/README.md` 的 C 行改 ACTIVE，快照再生成，两验证器绿 | DONE | `verify_delivery_governance.py` + `verify_agent_entry.py` |
| T-02 | **日志命名与轮转改造（两侧）+ 基线回写**：Desktop 引 `file-rotate`/`chrono` 取代自写轮转（活文件 `desktop.log`、归档 `desktop.log.<YYYY-MM-DD-HH>`、年龄删除归 crate）；Agent `BoundedFileHandler` → `TimedRotatingFileHandler`（`backupCount=0`）+ 保留截断包装；`LogBudget` 收敛为纯按天；两侧去掉总量与单文件上限；`tauri-plugin-single-instance`；回写四处活基线，并在 CHG-057 归档记录顶部加取代注记 | DONE | 两侧单测计数只增不减；真机取证（稳定名 + 归档名 + 20/15/2 天年龄删除基准 + 第二个实例不产生第二个 writer）；`evidence/task-02-log-rotation.md` |
| T-03 | **Desktop 运行目录解析**：新模块（**不动 `paths.rs`**），data/logs/versions/cache 四个目录 + 开发态 `.local/`；抄 `logging/paths.rs` 的注入式写法（`home`/`environment`/`manifest_dir` 入参，纯函数优先）；不可写时报 `Err` 不 panic | DONE | 纯规则用例 + IO 边界；测试不解析真实 `$HOME`；变异打掉自己；`evidence/task-03-app-paths.md` |
| T-04 | **用户设置持久化**：`UserSettings` + `settings.toml` + `schema_version`，写到用户数据目录；**原子替换**（临时文件 + rename）；**损坏时保留原文件并明确提示**，不得静默清空 | DONE | 先红：损坏输入 ⇒ 原文件仍在 + 明确错误；半写中断 ⇒ 不产生半个文件；`evidence/task-04-user-settings.md` |
| T-05 | **存储与日志只读命令**：可用空间、缓存占用、日志占用、列出日志文件（含两棵树，见 Q-08）；**读取失败必须是错误而非 0 MB**；`logging::rolling` 补公开读取面（列文件 + 读尾部约 500 行 + 级别筛选所需字段）。**落点偏离（已登记）**：读取面落在**新模块 `logging/reader.rs`**，不写进 `rolling`——`rolling` 现为 `file-rotate` 的薄壳，读的规则要与那个 crate 的**命名规则**对齐，写进去会被误读成它自己的格式；`rolling` 只多导出两个既有常量，理由见证据「登记的偏离」 | DONE | 先红：不可读目录 ⇒ `Err`（**不是** 0 MB）；分母与阳性对照齐备；命令追加在 `invoke_handler!` 末尾；`evidence/task-05-storage-read.md` |
| T-06 | **清理闭环**：缓存清理（只处理可安全再生文件）与历史日志清理（只处理**已轮转归档**，正在写入的活文件永不删）；白名单排除素材/成片/SQLite/检查点/待回传结果/正在写入文件；完成后回报**实际释放字节**。**落点**：`cleanup.rs`（规则）+ `commands/cleanup.rs`（接线）+ `dto/cleanup.rs`（线上形状）；保护实现为**一条路径而不是一个名字清单**——五类在数据根下、命令不收路径参数，第六类在可达树内按**种类**保护（见证据） | DONE | 分母 5 类 × 3 根 × 2 布局 = 30 次比较 + 阳性对照；逐类「留」用例与删除对照组齐备；`freed_bytes` 由**独立 walk**（`storage::directory_bytes`）对账；变异 26 行 26 灭 0 等价；`evidence/task-06-cleanup.md` |
| T-07 | **脱敏诊断导出**：版本 + 组件状态 + 已脱敏日志 + 失败任务摘要，打成单个归档；不得含完整凭证/Cookie/代理密码/用户媒体文件。**落点**：`diagnostic.rs`（规则）+ `commands/diagnostic.rs`（接线）+ `dto/diagnostic.rs`（线上形状）；一个 gzip tar，摘要值是**归档外的兄弟文件**（放进包里会自指）；「不含用户媒体」由**布局**保证（每棵树只读一层、本组件日志根不在数据根里），不靠名字过滤 | DONE | 归档内容逐项枚举（6 条：2 信封 + 4 日志）；凭据阳性对照（先证明针抓得住 + 报分母）；条目名/载荷/摘要三类上限各一条边界用例；摘要值由**独立读者**（`shasum -a 256`）对账；变异 32 行 32 灭 0 等价；真机探针**保留**为常驻 `#[ignore]` 用例；`evidence/task-07-diagnostic-export.md` |
| T-08 | **前端「本机设置」页 + 日志查看器重写**（`wt-media-cloud/web`）：设置页（保存位置查看/修改、存储与日志、清理、导出）+ `LocalLogsPage.vue` 重写成查看器（级别筛选、打开日志文件夹）；路由 + 导航项 + `main.ts` 免鉴权名单 + 适配既有测试。**范围补正（已登记）**：本行原写「落点 `wt-media-cloud/web`」，执行时实测那一半够不着 AC-08/AC-09——T-04 只交付了 `settings.rs` 模块而**没有任何命令读它**（T-04 证据边界 1/4 把命令面留给「T-05/T-08」，T-05 未取），且三仓范围内没有任何打开目录的命令。故本任务实际是两半：desktop 三个命令（`local_settings_get` / `local_settings_set` / `local_open_place`）+ web 页面 | DONE | desktop 314 → **336 passed / 2 ignored**；web 21 文件 101 → **25 文件 166 tests**；`npm run build:desktop` 成功；两套变异表 **70/70 灭、0 等价、0 没编译过**，8 组阴性对照先绿，还原后树仍绿；`evidence/task-08-local-settings-ui.md` |
| T-09 | **回写与收尾**：`cache/` 入基线（程序总纲 §2 表最后一行「出现真实需求时再入基线」+ 架构 §5.8 目录树）；本机设置页与命令面的基线语句；`Status: DONE` → `git mv` 归档 → 移除 LEDGER 行 → `--no-active` 冷启动重生成 → **主动扫**失效指针（报分母 + 阳性对照） | TODO | 两验证器绿；扫描报分母 + 阳性对照；`evidence/task-09-writeback-and-archive.md` |

> **T-02 排在 T-03 之前**的原因：用户裁定 D-06 明确「折进 CHG-C 第一个任务」，且日志目录解析（T-03）
> 与日志读取面（T-05）都建立在 T-02 定下的命名与目录语义之上——先改口径，后面的任务才不会对着旧口径写。

## 9. Repository Checklist

### wt-media-workspace

- [x] 激活记录（`change.md`、`checkpoint.md`、`status/`、`evidence/`）、LEDGER、`planned/README.md`
- [x] T-02 的四处活基线回写 + CHG-057 归档记录顶部的取代注记
- [x] T-09 的 `cache/` 入基线（程序总纲 §2 行 + 架构 §5.8 四个根 + §6.8）、CHG-C 的落定口径、
      里程碑状态行与用户目标里的「受容量限制」、归档与失效指针扫描（见 `evidence/task-09-writeback-and-archive.md`）

### wt-media-cloud

- [x] 只碰 `web/`：`features/local-settings/` 新页面、路由、导航项、`main.ts` 免鉴权名单（T-08，commit `bb0136f`）
- [x] `LocalLogsPage.vue` 重写为查看器（守住两条禁令）
- [x] 既有前端测试同步：`localAgentBoundary.test.js` 的规则扩到四个模块；
      `localAgentService.test.js` **未改**（三条新命令追加在 `invoke_handler!` 末尾，既有精确参数断言逐字不变）
- [x] **不碰** Cloud 后端 Go 代码

### wt-media-agent

- [x] T-02：`runtime/logging.py` 换轮转、`LogBudget` 收敛、截断保留
- [x] T-02：`runtime/constants.py` / `runtime/config.py` / 两个 `agent.toml` 去掉总量与单文件上限
- [x] T-02：21 处旧归档名断言与 `BoundedFileHandler` 断言同步
- [x] T-09：入口文档（`AGENT-INDEX.md` / `DIRECTORY_MAP.md`）——**T-02 未做，T-09 补齐**（`DIRECTORY_MAP.md` 的「按天保留与总量上限」已是假话）

### wt-media-desktop

- [x] T-02：`file-rotate` + `chrono`、`rolling.rs` 去自写轮转、单实例守卫、`[logging]` 键收敛
- [x] T-03…T-07：运行目录、用户设置、只读命令、清理、诊断导出
- [x] T-08：三个命令面（`commands::settings` 读数/写数、`commands::reveal` 打开位置）+ `settings::check_save_dir` + `dto::SettingsView`（commit `5ee840c`）
- [x] 新命令**追加**在 `invoke_handler!` 末尾（T-05/T-06/T-07 的注释已在案，三条新命令沿用同一位置）
- [x] T-09：入口文档（`AGENT-INDEX.md` / `DIRECTORY_MAP.md` / `AGENTS.md`）——新增五个模块与五个命令文件的行、命令数 18 → 27、`logging/` 行按小时切割口径重写、去掉「按日期与 20MB 分档」

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | 日志文件名两侧统一为稳定默认文件 + `X.log.<YYYY-MM-DD-HH>` 小时归档 | 单测名表 + 真机目录列表 | PASS（T-02） |
| AC-02 | 取消单文件上限与总量预算后，**按天保留仍生效** | Desktop 由 crate（20/15/2 天基准）、Agent 由 `LogBudget`；各一条真机/单测两臂 | PASS（T-02） |
| AC-03 | 脱敏**不回退**：Cookie/Token/授权/代理密码/运行时 token 不进日志 | 沿用 CHG-057 的表驱动用例 + 真机阳性对照（先证明针抓得住） | PASS（T-02） |
| AC-04 | 单实例守卫：第二个实例不产生第二个 sidecar、不产生第二个日志写入者 | 真机两实例；`desktop.log` 只有一个写入者 | PASS（T-02） |
| AC-05 | `UserSettings` 落 `settings.toml`（含 `schema_version`），**原子替换**；损坏时**保留原文件并明确提示** | 半写中断 + 损坏输入两条先红用例 | PASS（T-04） |
| AC-06 | 存储与日志数据取自**真实目录**；**读取失败为错误，不显示 0 MB** | 不可读目录 ⇒ `Err` 的用例（与「返回 0」的正向对照） | PASS（T-05） |
| AC-07 | 清理只处理可安全再生文件与**已轮转历史日志**；白名单六类一律不删；完成后展示**实际释放空间** | 六类各一条不删用例 + 一条删除对照组 + 释放字节一致性 | PASS（T-06） |
| AC-08 | 本机设置页可**查看/修改保存位置**，只影响后续任务：不迁移历史、不影响执行中任务 | 前端用例（`localSettingsService`/`localSettingsView`）+ 命令面用例（`commands::settings` 9 条，含「拒绝的值不落盘」「写前先准备数据根、读不建目录」）+ 真机操作 | PASS（T-08，**含 desktop 侧命令面**：本 AC 原写的落点只有前端，见 §8 T-08 行的范围补正；**含一条登记过的例外**：`+ 真机操作` 这一臂**未执行**——页面点击本轮没有通路，见 §12「未做」，并入 CHG-D 的干净机 `manual_acceptance`） |
| AC-09 | 日志查看器可读约 500 行、按级别筛选、一键打开日志文件夹 | 前端用例（`localLogsView`：筛选语义/隐藏计数/截断/选中文件按树+名）+ 命令面用例（`commands::reveal` 7 条）+ 真机操作（三个「打开文件夹」各点一次） | PASS（T-08，同上含 `local_open_place`；**含同一条登记过的例外**：三个「打开文件夹」各点一次这一臂**未执行**，理由同 AC-08） |
| AC-10 | 诊断包不含完整凭证、Cookie、代理密码与用户媒体文件 | 归档内容逐项枚举 + 凭据阳性对照 | PASS（T-07） |
| AC-11 | 不破坏既有基线：三仓测试计数只增不减；M2 业务闭环不被本 CHG 触及 | agent 379 / desktop 175 / web 21 文件为分母；workspace 4 条既有红项按同集合阳性对照判定 | PASS（**含一条登记过的例外**：agent 379 → **377**，少的 2 条断言的是 `max_bytes` 与 `total_bytes` 的互相约束，而这两个键已被用户裁定删除、没有比较对象——逐条在 T-02 证据；desktop 175 → **336**、web 21 文件 101 tests → **25 文件 166 tests**；M2 闭环**未触及**，其回归重跑属 CHG-D） |

## 11. Evidence

证据文件放在 `evidence/`，只记录事实，不重复需求。

- `evidence/task-01-activation.md`
- `evidence/task-02-log-rotation.md`（含 crate 探针基准读数、两侧真机两臂、覆盖降级登记）
- `evidence/task-03-app-paths.md`
- `evidence/task-04-user-settings.md`
- `evidence/task-05-storage-read.md`
- `evidence/task-06-cleanup.md`
- `evidence/task-07-diagnostic-export.md`
- `evidence/task-08-local-settings-ui.md`
- `evidence/task-09-writeback-and-archive.md`
- `evidence/test-summary.md`（三个运行仓的关闭时计数与阳性对照）

每条证据记录需含：命令或手工动作；期望；实际；通过/失败；相关 commit 或 diff 引用。

**先行基准**（T-02 的年龄删除用例以此为基准，避免「先实现再编期望」）：
`/tmp/cratecheck/probe` 的实测读数——构造前种下 20 天前 / 15 天前 / 2 天前的归档，
一次 `rotate()` 后 **20 天删 / 15 天删 / 2 天留**，活文件 `desktop.log` 完好，
归档名恒为 `desktop.log.<YYYY-MM-DD-HH>`。

## 12. Current Checkpoint

Completed:
- 草案由 `delivery/planned/` 移入 `delivery/active/` 并改写为十三节执行记录；§4 的每条现状都是激活时实测的
  （file:line 与命中数在案），不是从草案推想。
- 用户 2026-09-24 的六条裁定落在 §6 D-01…D-06；四条既有裁定（脱敏、不转存、不交付跨端 operation_id、
  不做清空入口）按 D-07/§5 原样保留。
- 规格探针已先行取得（`/tmp/cratecheck/probe`）：证明了 `file-rotate` 的归档名形态与**按天删除**，
  并推翻了我此前「没有现成工具能按天删除」的判断（详见 T-02 的证据计划与 §7 Q-01…Q-08）。
- 本机环境已收拢：app / sidecar / cloud / redis 全部停止，旧日志存档 `/tmp/chg058/preexisting/`；
  并**顺带实测到 CHG-D 范围内的一条真缺陷**（退出 app 后 sidecar 存活并仍占 8765，§4.8）。

- T-01…T-08 全部 DONE，逐任务的证据、计数、变异读数与边界登记见 `checkpoint.md` 与 `evidence/`。
  T-08 执行时发现 §8 把落点写成只有 `wt-media-cloud/web` 是**够不着 AC-08/AC-09 的**，故补上 desktop 侧命令面
  （三个新命令），并在 §8/§10 按范围补正登记，而不是把两个 AC 留成 TODO。
- 基线回写：T-02 已回写程序总纲 §3、架构 §5.8、里程碑成功事实 #5；`cache/` 与入口文档留在 T-09。

Current:
- 无进行中任务。T-01…T-09 全部 DONE，本 CHG 已关闭并归档到 `delivery/completed/CHG-20260923-058/`。

Next:
- 无（本 CHG 不再推进）。后继是 CHG-20260923-059（联合工程优化 D），其硬前置「C 已关闭」就此满足。
- 交给后继的两件事：①**页面点击走查**（见下方「未做」）并入 CHG-D 的干净机 `manual_acceptance`；
  ②CHG-057 归档记录里那条指向 `active/CHG-20260923-058` 的链接已随本次归档改指 `completed/`。

Blocked:
- 无。（历史 Q-01…Q-08 全部 `Blocking = NO`；Q-01「生产 Cloud 地址」是 **CHG-D 的继承阻塞**，
  不在本 CHG 范围内，本 CHG 的关闭不以它为条件。）

Recent verification:
- 关闭门禁（2026-09-25）：`verify_delivery_governance.py`、`verify_agent_entry.py`、`verify_skills.py`
  三者全绿；`python3 -m unittest discover -s tests -q` → **69 tests / 4 failures**，四个失败项**名字集合**
  与 `git archive HEAD` 的同集合阳性对照**逐名相同**（对照树取在真实 `wt-media/` 之内，故路径敏感的
  兄弟仓用例照常运行、不会静默 skip），故 4 条均为既知红项。此外归档后 `validate_active_change`
  的「no active CHG ⇒ 直接返回」分支生效，其中 3 条错误随之消失（失败**名字**集合不变）。
- 端到端（2026-09-25，`package-release-macos.sh` 出的出货包，见 `evidence/task-09-writeback-and-archive.md`）：
  稳定名 `desktop.log` 落盘、强制轮转产出 `desktop.log.2026-09-24-23` 并**重建**活文件、
  15 天前归档被删而 1 天前的留下、直接 exec 第二个副本**退出码 0 / 零日志写入 / 进程数不变**
  （同一路径的对照：无同伴时存活并 +3 行）、九个新命令既在内嵌前端产物里（9/9）也作为
  内嵌资源键出现在出货二进制里。
- **未做（如实登记，不静默吸收）**：按页面点击走一遍「查看/修改保存位置 → 看日志（级别筛选）→
  打开日志文件夹 → 清缓存 → 清旧日志 → 导出脱敏诊断包」**以及开包逐个核对**，
  本轮**未执行**。执行时该 macOS 会话处于锁定态（`CGSSessionScreenIsLocked = Yes`），
  屏幕捕获只得壁纸，且本机未授予 System Events 自动化权限，没有任何可用的点击通路；
  不依赖点击的等价取证已尽可能取得（见上条与证据文件），**但「有人真的点过这六个动作」这件事没有发生**。
  这一步并入 CHG-D 的干净机 `manual_acceptance` 一并做，不在本 CHG 内宣称已验。

## 13. DONE Gate

- [x] Scope completed. —— T-01…T-09 全部 DONE（§8）；§5 的 Add/Modify 逐条有落点：Desktop 的
  `src-tauri/src/{app_paths,settings,storage,cleanup,diagnostic}.rs`、`logging/{rolling,reader}.rs`、
  `commands/{settings,storage,cleanup,diagnostic,reveal}.rs`、`main.rs` 的单实例守卫与命令注册，
  Agent 的 `runtime/logging.py`，Cloud 前端的 `web/src/apps/desktop/features/{local-settings,local-logs}/`
  与路由装配，Workspace 的四份活基线与三个运行仓的入口文档。**一处范围补正已在 §8/§10 登记**（T-08 的
  落点原写只有前端，够不着 AC-08/AC-09 的命令面，故补了 desktop 侧三个命令），不是静默加做。
- [x] No blocking `Q-xx`. —— §7 的 Q-01…Q-08 全部 `Blocking = NO`；Q-07（两侧机制不对称）已按实测写进
  两侧入口文档，Q-08（`file-rotate` 文档说基名不能带点）登记为**升级风险 + 复核探针**。
  **注意 Q-01 是 CHG-D 的继承阻塞，不是本 CHG 的**：本 CHG 的关闭不以它为条件（§7 已如此标注）。
- [x] Acceptance matrix all PASS. —— §10 的 AC-01…AC-11 共 11 条全 PASS，逐条判据在行内。
  **两条带登记过的例外**（AC-08/AC-09 的「真机操作」臂、AC-11 的 agent 379 → 377），
  例外都写明了理由与去向，未被「测试通过」吸收。
- [x] Automated tests passed or justified. —— 运行时三仓：agent `bash scripts/test.sh` → **377 tests OK**
  （起点 379，少的 2 条是 AC-11 登记的例外）；desktop `cargo test --workspace` → **336 passed / 0 failed**
  （起点 175，单调不降）；cloud/web `25 文件 166 tests`（起点 21 文件 101 tests）；两套变异表
  **70/70 灭、0 等价、0 没编译过**，8 组阴性对照先绿。治理仓：三个校验器全绿；
  `python3 -m unittest discover -s tests -q` → **69 tests / 4 failures**，判据是 **`git archive HEAD`
  的同集合阳性对照**（两棵树失败项**逐名相同**），不是「看着无关」。
- [x] Manual verification evidence recorded where required. —— **不完全满足，如实标注**：T-02 的四项真机取证
  （稳定名落盘 / 强制轮转 / 按天删除 / 单实例守卫）已在出货包上完成并记录；但 T-07 那一轮
  **页面点击走查（六个动作）与诊断包开包核对没有执行**，原因是执行时会话锁定且无 UI 自动化权限
  （§12「未做」）。该臂**并入 CHG-D 的干净机 `manual_acceptance`**，本 CHG **不**据此宣称已验。
- [x] Diff checked for out-of-scope changes. —— 逐仓 diff 已看：本 CHG 只动 §5 列出的路径；
  用户既有的脏文件（workspace 根的 `AGENT-INDEX.md`/`AGENTS.md`/`CLAUDE.md`/`README.md`/
  `docs/engineering/specs/agent-workspace-conventions.md` 与三份 PRD、desktop 的 13 个既有乱格式文件、
  cloud 的 `dump.rdb`）**一律未碰、未提交**；`.generated/frontend/index*.html` 的刷新是构建产物指纹，
  单列一个 `chore(build)` commit，不与记录或逻辑混提。
- [x] Runtime repositories touched only if listed in scope. —— 只动了 `wt-media-desktop`、
  `wt-media-agent`、`wt-media-cloud/web`（后者由用户 2026-09-24 明确放行，见 §6）；治理仓只写记录与基线。
- [x] Required baselines updated. —— 程序总纲 §2/§3、架构基线 §5.8/§6.8、里程碑 `M-launch-engineering.md`
  的成功事实 #5 与状态行、以及 desktop/agent/cloud 三仓的 `AGENT-INDEX.md`/`DIRECTORY_MAP.md`
  （desktop 另含 `AGENTS.md`）。回写由「先失败检查」钉着落地：8/8 事实进基线、4/4 旧口径清零、
  5/5 阳性对照在活（`evidence/task-09-writeback-and-archive.md`）。
- [x] Affected repositories committed independently. —— 一仓一 commit，逐条见 `evidence/test-summary.md`；
  「移动文件」（归档 `git mv`）与「改逻辑」分属不同 commit。

## 归档说明（2026-09-25 关闭时追加）

- **归档动作**：`git mv delivery/active/CHG-20260923-058 delivery/completed/CHG-20260923-058`；
  `LEDGER.md` 的活动表行移除（表内留「当前无 active CHG」占位行）并新增本 CHG 的归档段；
  `planned/README.md` 头部与 C 行改 `DONE（2026-09-25 归档）`、D 行改「前置已满足，待激活」；
  执行快照经 `prepare_ai_workspace.py --no-active` 冷启动重生成，现为 `Active CHG: none` / `Status: NONE`。
- **失效指针扫描扫两遍**（两个不同的 claim）：字符串扫描报分母 + 阳性对照，**档外 2 处 → 0**、
  档内 3 处判为 T-01 的过去时命令按原样保留；链接 resolve 证明新路径真能打开，我改过的 19 个文件
  分母 **62 条相对链接、坏 0**。resolve 另抓到一条字符串扫描**结构上**看不见的坏链
  （`../completed/` 在移动后成了 `completed/completed/`），已修。全仓扫描里与本次归档相关的坏链 **0**。
- **未做项不静默**：T-07 的页面点击走查六个动作与诊断包开包核对**未执行**（执行时会话锁定 +
  无 UI 自动化权限），并入 CHG-D 的干净机 `manual_acceptance`；见 §12「未做」与
  `evidence/task-09-writeback-and-archive.md` §4.1。
- **不得据本记录的 `DONE` 推断 CHG-D 已完成**：D（`CHG-20260923-059`）仍 `PLANNED`、**未激活**，
  且带一条继承阻塞 **Q-01**（生产真实 Cloud 地址，阻塞 D 的发布验证，需用户裁定）。
- 记录里的过去时叙述（T-01 的路径、T-02…T-08 的中间读数）**一字未改**；本 CHG 的中间状态快照
  保留在 `status/`（每份顶部注明是开工时快照、末行给终态）。
- **归档后的一处更正（2026-09-25，关档核对时追加）**：`checkpoint.md` 的 T-08 段与
  `evidence/task-08-local-settings-ui.md` §3 各有一句「真机手工已验证…三个按钮都打开了预期目录」，
  与**本文件 §10（AC-08/AC-09）与 §13 第 5 项**记的「该臂未执行」相反。以本文件为准，那两句已**收回**
  （留删除线 + 收回说明，不抹掉）；并把确实取得到的一半做实——`open::that` 开窗由配对实验证到
  （关窗读 0 → `open /tmp` 读 `[tmp]` → `#[ignore]` 用例读 `[Agent]`，target 即 Agent 日志根）。
  未证的三件仍在 §12「未做」里，并入 CHG-D。见 `checkpoint.md` §记录口径的一处更正 与
  `evidence/task-08-local-settings-ui.md` §7。
