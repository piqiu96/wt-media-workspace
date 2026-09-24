# CHG-20260923-057 — wt-media-desktop 状态

- 2026-09-24：尚未开始改动（工作区干净）。起点测试基线 **68**（二进制 crate，`cargo test --lib` 不成立）。
- 本仓范围：T-10…T-17。
  - 起点事实（详见 `../change.md` §4.2）：`Cargo.toml` 无 `tracing`/`tracing-subscriber`/`log`/`tauri-plugin-log`；
    `Cargo.lock` 里的 `tracing 0.1.44` 只是 h2/hyper-util/softbuffer 的传递依赖；
    全 `src/` 仅 4 处 emit（`main.rs:65`、`sidecar/drain.rs:158`、`commands/logging.rs:7` 与 `:9`）；
    `paths.rs` 是**配置文件定位器**，无运行/日志目录概念；`.gitignore` 有 `*.log` 但**无** `.local/`。
- 待办：T-10 依赖引入（`cargo fetch` 失败即**阻塞上报**，不换实现）。
