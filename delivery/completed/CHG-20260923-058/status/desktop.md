# CHG-20260923-058 — wt-media-desktop 状态

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
