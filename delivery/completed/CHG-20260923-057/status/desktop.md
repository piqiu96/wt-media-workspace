# CHG-20260923-057 — wt-media-desktop 状态

> 本文件是**开工时**的状态快照（下面每条都写于 T-10 之前，保留原文）。**关闭时的终态**见末行。

- 2026-09-24：尚未开始改动（工作区干净）。起点测试基线 **68**（二进制 crate，`cargo test --lib` 不成立）。
- 本仓范围：T-10…T-17。
  - 起点事实（详见 `../change.md` §4.2）：`Cargo.toml` 无 `tracing`/`tracing-subscriber`/`log`/`tauri-plugin-log`；
    `Cargo.lock` 里的 `tracing 0.1.44` 只是 h2/hyper-util/softbuffer 的传递依赖；
    全 `src/` 仅 4 处 emit（`main.rs:65`、`sidecar/drain.rs:158`、`commands/logging.rs:7` 与 `:9`）；
    `paths.rs` 是**配置文件定位器**，无运行/日志目录概念；`.gitignore` 有 `*.log` 但**无** `.local/`。
- 待办：T-10 依赖引入（`cargo fetch` 失败即**阻塞上报**，不换实现）。

**终态（2026-09-24 关闭时追加，上文一字未改）**：T-10…T-17 全部 DONE；
`cargo test --workspace` → **175 passed; 0 failed**（起点 63，全程单调不降）；
build **9** 条 / clippy **13** 条，13 条逐条点名、无一条落在新代码上。起点事实逐条被落实：
`tracing`/`tracing-subscriber` 已进依赖树、`src-tauri/src/logging/` 从零建起五个模块、
`paths.rs` 之外新增了日志目录解析（`logging/paths.rs`）、`.local/` 已进 `.gitignore`（T-11）。
**未覆盖项**（Windows 布局、`level` 严于 INFO 时连 stderr 一起静默、若干够不着的分支）见 `../change.md` §7/§10。
