# CHG-20260923-058 — wt-media-desktop 状态

> 本文件是**开工时**的状态快照（下面每条都写于 T-02 之前，保留原文，一字未改）。**关闭时的终态**见末行。

- 2026-09-24：尚未开始改动（工作区干净）。起点测试基线 **175 passed / 0 failed**
  （`cargo test --workspace`），全程只增不减。
- 本仓范围：T-02（日志轮转）、T-03…T-07（运行目录、用户设置、只读命令、清理、诊断导出）。
- 起点事实（详见 `../change.md` §4.1–4.3）：
  - `AppPaths`/`settings.toml`/`UserSettings`/`schema_version`/`cache`/`versions` **全树零命中**；
  - `paths.rs` 是**配置文件定位器**（模块 doc 明写不能返回「没有」），**不可就地扩展**——T-03 另起模块；
  - `filesystem/`、`secure_store/`、`system/`、`updater/` 各 **3 行空壳**，不是可读实现；
  - `logging/rolling.rs:629 fn list` 私有，`Writer` 字段全私有，**生产路径零读日志**；
  - `Cargo.toml` **无 zip/tar、无哈希依赖**；`capabilities/default.json` **无 fs 权限**；
  - `main.rs:131-152` 注册 **18** 个命令，`:149-150` 要求新命令**追加在末尾**（前端断言精确参数对象）。
- 待办：T-02 依赖引入（`file-rotate` + `chrono` + `tauri-plugin-single-instance`；
  `cargo fetch` 需 `HTTPS_PROXY=http://127.0.0.1:7897`，**只给该次调用**，不写进仓库配置）。

**终态（2026-09-25 关闭时追加，上文一字未改）**：T-02…T-08 全部 DONE，`cargo test --workspace`
**175 → 336 passed / 0 failed**（单调不降）；命令数 **18 → 27**——T-04 的设置读写 2、T-05 的三条只读 3、
T-06 的两条清理 2、T-07 的诊断导出 1、T-08 的打开位置 1，**全部追加在 `generate_handler!` 末尾**。
起点事实逐条被推翻或落实：`AppPaths` 落在新模块 `src-tauri/src/app_paths.rs`（四个根，**缓存根在数据根之外**，
见架构基线 §5.8）；`settings.rs` 给数据根下的 `settings.toml` 定形（原子替换、坏形态保原文件）；
`storage.rs` / `cleanup.rs` / `diagnostic.rs` 各自成模块；`rolling.rs` 换成 `file-rotate` 薄壳——活文件恒为
`desktop.log`、归档 `desktop.log.<YYYY-MM-DD-HH>`、**按天删由 crate 承担**、**已无单文件上限与总量键**；
新增 `tauri-plugin-single-instance` 单实例守卫（放在链首，先于一切碰日志目录的动作）。
**真机取证（2026-09-25，`package-release-macos.sh` 出的出货包）**：首个实例落盘稳定名 `desktop.log`
（旧的 `desktop-20260924-1.log` 原样留着，不认的名字既不轮转也不删）；把活文件 mtime 推回一小时再启动，
产出归档 `desktop.log.2026-09-24-23`（内容即旧活文件全部 5 条）并**重建** `desktop.log`；
15 天前的 `desktop.log.2026-09-10-00` 被删、1 天前的留下（14 天按归档名时间戳判，与进程是否连续运行无关）；
**直接 exec 第二个副本 → 退出码 0、零日志写入、进程数不变**，同一路径的对照（无同伴时）存活并 +3 行。
未覆盖：`open::that` 那一行与 `main.rs` 的装配一行测不到，逐条列在 `../evidence/task-08-local-settings-ui.md`。
