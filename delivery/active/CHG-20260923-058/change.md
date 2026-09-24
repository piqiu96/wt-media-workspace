# CHG-20260923-058：联合工程优化 C——Desktop 本机设置

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING（2026-09-24 由 `delivery/planned/` 激活并改写为十三节执行记录）
- Created: 2026-09-23
- Current repository: `wt-media-workspace`（治理）；运行时改动分布于 `wt-media-desktop`、`wt-media-cloud/web`、`wt-media-agent`
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
- 上游 CHG：[CHG-20260923-057](../completed/CHG-20260923-057/change.md)（B，日志体系与数字的既有落点，
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
| D-04 | **加单实例守卫**（`tauri-plugin-single-instance`），第二次启动把已有窗口召到前台。**理由必须写清**：稳定默认名 `desktop.log` + crate 的 rename-on-roll ⇒ 两个实例会共用一个活文件，一个实例重命名时另一个的句柄还在写被改名的归档。**没有正当的多实例场景**——守卫是**禁止**一个坏状态，不是**启用**一个能力。 | CONFIRMED（用户 2026-09-24：「加实例守卫，需要说明下为何需要多实例什么场景下？」） |
| D-05 | 本 CHG **允许修改 `wt-media-cloud/web`**。 | CONFIRMED（用户 2026-09-24：「允许改 cloud/web（推荐）」） |
| D-06 | 日志改名与轮转改造**折进本 CHG 作为第一个任务 T-01**，不单独开 CHG。 | CONFIRMED（用户 2026-09-24：「折进 CHG-C 第一个任务（推荐）」） |
| D-07 | 脱敏要求与「Desktop 不转存 Agent 业务日志」两条**不变**：它们与轮转正交，且是成功事实 #5 的另一半。 | CONFIRMED（承 CHG-057 D-07/D-08） |
| D-08 | 本 CHG 的基线回写对象**限定为四处活基线 + 两个运行仓入口文档**（清单见 §5 Modify）；CHG-057 的**归档记录正文不改写**，只在其顶部加一段「被本 CHG 取代」的注记（照它自己 T-18 处置 T-01 的先例）。 | CONFIRMED（本次实施口径；依据 `archive-sweep-fix-paths-keep-narration` 的分类：过去时叙述判「留」） |

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
| T-01 | 激活与记录（本文件、`checkpoint.md`、`status/`、`evidence/`），LEDGER 加表行，`planned/README.md` 的 C 行改 ACTIVE，快照再生成，两验证器绿 | IN_PROGRESS | `verify_delivery_governance.py` + `verify_agent_entry.py` |
| T-02 | **日志命名与轮转改造（两侧）+ 基线回写**：Desktop 引 `file-rotate`/`chrono` 取代自写轮转（活文件 `desktop.log`、归档 `desktop.log.<YYYY-MM-DD-HH>`、年龄删除归 crate）；Agent `BoundedFileHandler` → `TimedRotatingFileHandler`（`backupCount=0`）+ 保留截断包装；`LogBudget` 收敛为纯按天；两侧去掉总量与单文件上限；`tauri-plugin-single-instance`；回写四处活基线，并在 CHG-057 归档记录顶部加取代注记 | TODO | 两侧单测计数只增不减；真机取证（稳定名 + 归档名 + 20/15/2 天年龄删除基准 + 第二个实例不产生第二个 writer）；`evidence/task-02-log-rotation.md` |
| T-03 | **Desktop 运行目录解析**：新模块（**不动 `paths.rs`**），data/logs/versions/cache 四个目录 + 开发态 `.local/`；抄 `logging/paths.rs` 的注入式写法（`home`/`environment`/`manifest_dir` 入参，纯函数优先）；不可写时报 `Err` 不 panic | TODO | 纯规则用例 + IO 边界；测试不解析真实 `$HOME`；变异打掉自己；`evidence/task-03-app-paths.md` |
| T-04 | **用户设置持久化**：`UserSettings` + `settings.toml` + `schema_version`，写到用户数据目录；**原子替换**（临时文件 + rename）；**损坏时保留原文件并明确提示**，不得静默清空 | TODO | 先红：损坏输入 ⇒ 原文件仍在 + 明确错误；半写中断 ⇒ 不产生半个文件；`evidence/task-04-user-settings.md` |
| T-05 | **存储与日志只读命令**：可用空间、缓存占用、日志占用、列出日志文件（含两棵树，见 Q-08）；**读取失败必须是错误而非 0 MB**；`logging::rolling` 补公开读取面（列文件 + 读尾部约 500 行 + 级别筛选所需字段） | TODO | 先红：不可读目录 ⇒ `Err`（**不是** 0 MB）；分母与阳性对照齐备；命令追加在 `invoke_handler!` 末尾；`evidence/task-05-storage-read.md` |
| T-06 | **清理闭环**：缓存清理（只处理可安全再生文件）与历史日志清理（只处理**已轮转归档**，正在写入的活文件永不删）；白名单排除素材/成片/SQLite/检查点/待回传结果/正在写入文件；完成后回报**实际释放字节** | TODO | 每个白名单类别各一条「不删」用例 + 一条「删了」对照组；释放字节与实际差值一致；`evidence/task-06-cleanup.md` |
| T-07 | **脱敏诊断导出**：版本 + 组件状态 + 已脱敏日志 + 失败任务摘要，打成单个归档；不得含完整凭证/Cookie/代理密码/用户媒体文件 | TODO | 归档内容逐项枚举；凭据阳性对照（先证明针抓得住）；文件名与大小上限；`evidence/task-07-diagnostic-export.md` |
| T-08 | **前端「本机设置」页 + 日志查看器重写**（`wt-media-cloud/web`）：设置页（保存位置查看/修改、存储与日志、清理、导出）+ `LocalLogsPage.vue` 重写成约 500 行查看器（级别筛选、打开日志文件夹）；路由 + 导航项 + `main.ts:43` 免鉴权名单 + 适配两条既有测试 | TODO | `npx vitest run` 21 文件全绿；`localAgentBoundary.test.js` 的两条禁令（`127.0.0.1`/`fetch(`）不被触碰；`localAgentService.test.js` 的精确参数断言同步；`evidence/task-08-local-settings-ui.md` |
| T-09 | **回写与收尾**：`cache/` 入基线（程序总纲 §2 表最后一行「出现真实需求时再入基线」+ 架构 §5.8 目录树）；本机设置页与命令面的基线语句；`Status: DONE` → `git mv` 归档 → 移除 LEDGER 行 → `--no-active` 冷启动重生成 → **主动扫**失效指针（报分母 + 阳性对照） | TODO | 两验证器绿；扫描报分母 + 阳性对照；`evidence/task-09-writeback-and-archive.md` |

> **T-02 排在 T-03 之前**的原因：用户裁定 D-06 明确「折进 CHG-C 第一个任务」，且日志目录解析（T-03）
> 与日志读取面（T-05）都建立在 T-02 定下的命名与目录语义之上——先改口径，后面的任务才不会对着旧口径写。

## 9. Repository Checklist

### wt-media-workspace

- [ ] 激活记录（`change.md`、`checkpoint.md`、`status/`、`evidence/`）、LEDGER、`planned/README.md`
- [ ] T-02 的四处活基线回写 + CHG-057 归档记录顶部的取代注记
- [ ] T-09 的 `cache/` 入基线、本机设置基线语句、归档与失效指针扫描

### wt-media-cloud

- [ ] 只碰 `web/`：`features/local-settings/` 新页面、路由、导航项、`main.ts` 免鉴权名单
- [ ] `LocalLogsPage.vue` 重写为查看器（守住两条禁令）
- [ ] 两条既有前端测试同步（`localAgentBoundary` / `localAgentService`）
- [ ] **不碰** Cloud 后端 Go 代码

### wt-media-agent

- [ ] T-02：`runtime/logging.py` 换轮转、`LogBudget` 收敛、截断保留
- [ ] T-02：`runtime/constants.py` / `runtime/config.py` / 两个 `agent.toml` 去掉总量与单文件上限
- [ ] T-02：21 处旧归档名断言与 `BoundedFileHandler` 断言同步
- [ ] T-02：入口文档（`AGENT-INDEX.md` / `DIRECTORY_MAP.md`）

### wt-media-desktop

- [ ] T-02：`file-rotate` + `chrono`、`rolling.rs` 去自写轮转、单实例守卫、`[logging]` 键收敛
- [ ] T-03…T-07：运行目录、用户设置、只读命令、清理、诊断导出
- [ ] 新命令**追加**在 `main.rs:131-152` 末尾
- [ ] 入口文档（`AGENT-INDEX.md` / `DIRECTORY_MAP.md`）

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | 日志文件名两侧统一为稳定默认文件 + `X.log.<YYYY-MM-DD-HH>` 小时归档 | 单测名表 + 真机目录列表 | TODO |
| AC-02 | 取消单文件上限与总量预算后，**按天保留仍生效** | Desktop 由 crate（20/15/2 天基准）、Agent 由 `LogBudget`；各一条真机/单测两臂 | TODO |
| AC-03 | 脱敏**不回退**：Cookie/Token/授权/代理密码/运行时 token 不进日志 | 沿用 CHG-057 的表驱动用例 + 真机阳性对照（先证明针抓得住） | TODO |
| AC-04 | 单实例守卫：第二个实例不产生第二个 sidecar、不产生第二个日志写入者 | 真机两实例；`desktop.log` 只有一个写入者 | TODO |
| AC-05 | `UserSettings` 落 `settings.toml`（含 `schema_version`），**原子替换**；损坏时**保留原文件并明确提示** | 半写中断 + 损坏输入两条先红用例 | TODO |
| AC-06 | 存储与日志数据取自**真实目录**；**读取失败为错误，不显示 0 MB** | 不可读目录 ⇒ `Err` 的用例（与「返回 0」的正向对照） | TODO |
| AC-07 | 清理只处理可安全再生文件与**已轮转历史日志**；白名单六类一律不删；完成后展示**实际释放空间** | 六类各一条不删用例 + 一条删除对照组 + 释放字节一致性 | TODO |
| AC-08 | 本机设置页可**查看/修改保存位置**，只影响后续任务：不迁移历史、不影响执行中任务 | 前端用例 + 真机操作 | TODO |
| AC-09 | 日志查看器可读约 500 行、按级别筛选、一键打开日志文件夹 | 真机操作 + 前端用例 | TODO |
| AC-10 | 诊断包不含完整凭证、Cookie、代理密码与用户媒体文件 | 归档内容逐项枚举 + 凭据阳性对照 | TODO |
| AC-11 | 不破坏既有基线：三仓测试计数只增不减；M2 业务闭环不被本 CHG 触及 | agent 379 / desktop 175 / web 21 文件为分母；workspace 4 条既有红项按同集合阳性对照判定 | TODO |

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

Current:
- T-01 激活中：LEDGER、`planned/README.md`、快照重生成与两验证器待跑。

Next:
- 跑 `prepare_ai_workspace.py --change CHG-20260923-058` 与两验证器，然后提交激活记录，转入 T-02。

Blocked:
- 无。Q-01…Q-08 全部 `Blocking = NO`。

Recent verification:
- 激活时基线：agent 379 tests OK / desktop 175 passed / web 21 测试文件 / workspace 两验证器绿
  （`unittest discover` 的 4 条红项为既知，待按同集合阳性对照判定）。

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
