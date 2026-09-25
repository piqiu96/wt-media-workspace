# CHG-20260923-059 — wt-media-desktop 状态

> 本文件是**开工时**的状态快照（下面每条都写于 T-01 之前，保留原文，一字未改）。**关闭时的终态**见末行。

- 起点（2026-09-25 激活时实测）：`cargo test --workspace` = **336 passed / 0 failed / 2 ignored**。
- 本仓范围：T-01（就绪闸门）、T-02（活性探针）、T-03（退出收尾的 Desktop 一半）、
  T-04（运行期完整性校验）、T-05（`tauri.conf.json` 的 `bundle.resources` + 打包侧）、
  T-06（Desktop 与前端构建版本的来源 + 发布脚本的版本兼容校验）、T-07（升级不覆盖的路径判据）。
- **不动的既有结论**：日志命名与轮转保留（C 已定型，见 `change.md` §6 D-10）；两份出货配置的**值与 CSP**
  （Q-01 裁定，§6 D-08）——只回写 `config_online/agent.toml` 里那段过期的 Q-01 注释。
- 已知边界（开工前就有，登记以免被读成本次引入）：`open::that` 一行与 `main.rs` 的接线行不可断言；
  13 个既有的 rustfmt 脏文件保持脏；本仓**不是 rustfmt-clean**，只对单个文件跑 `rustfmt`。
