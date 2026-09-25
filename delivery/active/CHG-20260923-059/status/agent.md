# CHG-20260923-059 — wt-media-agent 状态

> 本文件是**开工时**的状态快照（下面每条都写于 T-01 之前，保留原文，一字未改）。**关闭时的终态**见末行。

- 起点（2026-09-25 激活时实测）：`bash scripts/test.sh` = **377 tests OK**。
- 本仓范围：T-03 的 Agent 一半（SIGTERM 处理与在飞任务收尾）、T-05（`build_desktop_sidecar.py`
  的 `config_online → 产物/config` 整目录替换）、T-09（`AGENTS.md`/`README.md`/`contracts/*/README.md` 同步）、
  T-10 的 Q-01 过期注释回写（`config_online/agent.toml:17-21`）。
- **不动的既有结论**：按天保留由 `LogBudget` 负责、轮转由标准库 `TimedRotatingFileHandler` 负责——
  这是 C 定型的**有意不对称**（Desktop 侧由 `file-rotate` 一并承担），见 `change.md` §6 D-10。
  本 CHG 只在**退出路径**上动写入者的生命周期，不动轮转与保留规则。
- 起点缺陷（**既有，不是本次引入**）：`local_api/server.py:630` 只捕 `KeyboardInterrupt`，
  SIGTERM 到不了任何清理路径——这正是 T-03 要关的那条。
