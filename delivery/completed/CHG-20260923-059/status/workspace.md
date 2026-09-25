# CHG-20260923-059 — wt-media-workspace 状态

> 本文件是**开工时**的状态快照（下面每条都写于 T-01 之前，保留原文，一字未改）。**关闭时的终态**见末行。

- 2026-09-25 **激活时（T-01 之前）**：草案由 `delivery/planned/` 移入 `delivery/active/` 并改写为十三节执行记录
  （`change.md`、`evidence/`、`status/`）；`LEDGER.md` 表行由「当前无 active CHG」占位改回 CHG-059；
  `planned/README.md` 的 D 行改 ACTIVE；里程碑状态行注明 D 已激活；
  快照经 `prepare_ai_workspace.py --change CHG-20260923-059` 再生成。
- 本仓范围：激活（T-01 之前）、T-06 的 `release-matrix` 与 skill 部分、T-08（M2 回归记录）、
  T-10（回写与归档收尾）。
- 待办：T-06（五类版本在 `release-matrix` / `contract-map` 里的表示 + Desktop ↔ sidecar 版本兼容校验）、
  T-09 的 skill 改指 `clients/<platform>` + `sync_skills.py`、T-10 的 `config_online/agent.toml`
  过期 Q-01 注释回写。
