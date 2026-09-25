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

## 关闭时的终态（2026-09-25）

- T-01…T-07 全部交付；其中 T-06 的 `scripts/release-versions.sh` + `src-tauri/agent-compat.json`
  + `tests/release-versions.test.sh`（20 臂）让「发布可追溯五类版本」与「Desktop ↔ sidecar pin
  不匹配必拒」都有真机读数；T-07 的 `src-tauri/src/upgrade.rs` 是 `#[cfg(test)]` 的**路径判据**
  （本程序不实现升级器，判据不等于行为）。
- 计数：**336 → 372 passed / 0 failed**（ignored 2 → 5，多的三条是真机臂与包内臂）；编译警告 7 → 7
  （新增 0）。本 CHG 无下降项。
- 「移动文件/改逻辑不同 commit」与 churn 口径逐任务执行并复核：收尾时 `git diff --name-only`
  = **13** 条，逐个核对为 `工作区 == rustfmt(HEAD)`（纯重排，未混进任何提交）。
- 未覆盖/未做按登记收尾：干净机安装（D-09）、Windows／x86_64 构建（Q-03）、
  随包 onefile sidecar 引导器的 SIGTERM 转发（T-03 登记，本机 `dlopen` 被签名拒）、
  「双击启动被篡改的包」（需要 GUI）。
