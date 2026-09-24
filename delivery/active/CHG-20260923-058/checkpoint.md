# CHG-20260923-058 Checkpoint

## Completed

- 2026-09-24：草案由 `delivery/planned/` 移入 `delivery/active/` 并改写为十三节执行记录。
- `change.md` §4 的每条现状都是激活时**实测**得到的 file:line 与命中数（不是从草案推想）：
  `AppPaths`/`settings.toml`/`UserSettings`/`schema_version`/`cache`/`versions` 在 Desktop 全为零命中；
  `paths.rs` 是配置文件定位器、**不可就地扩展**；`logging/rolling.rs:629 list` 私有且**生产路径零读日志**；
  Cargo 里**无 zip/tar、无哈希**；`LocalLogsPage.vue` 是 40 行纯桩；`本机设置` 在 `web/src` 零命中但
  `features/local-settings/.gitkeep` 占位已预留；Agent 的四个界各自有明确住处（§4.6）。
- 用户 2026-09-24 的六条裁定落在 §6 D-01…D-06；四条既有裁定按 D-07/§5 原样保留。
- 规格探针先行取得（`/tmp/cratecheck/probe`）：证明 `file-rotate` 0.8.0 给出稳定活文件 +
  `X.log.<YYYY-MM-DD-HH>` 归档 + **真按天删除**（20 天删 / 15 天删 / 2 天留），
  并推翻我此前「没有现成工具能按天删除」的判断。§7 Q-01…Q-08 已把由此产生的代价逐条登记。
- 本机环境已收拢：app / sidecar / cloud / redis 全部停止；旧日志存档 `/tmp/chg058/preexisting/`。
- 顺带实测到 **CHG-D 范围内**的一条真缺陷：`osascript quit` 后两个 `wt-media-agent` 存活、
  PPID 被 launchd 收编、仍占 `127.0.0.1:8765`（`/tmp/chg058/preexisting/orphan-sidecar-after-quit.out`）。

## Current

- T-01 激活中：`checkpoint.md` / `status/` / `evidence/` 已建；LEDGER 与 `planned/README.md` 已改；
  待跑快照重生成与两个验证器，然后提交激活记录。

## Next

- T-02 日志命名与轮转改造（两侧）+ 四处活基线回写（本 CHG 的第一个实现任务，用户裁定 D-06）。

## Blocked

- 无。§7 的 Q-01…Q-08 全部 `Blocking = NO`。

## Recent verification

- 激活时基线：agent `379 tests OK` / desktop `175 passed, 0 failed` / web `21` 个测试文件 /
  workspace 两验证器绿；`unittest discover` 的 **4 条红项为既知**（见 `README.md`），
  判定要用 `git archive HEAD` 的**同集合阳性对照**，不用「看着无关」。
