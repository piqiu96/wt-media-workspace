# CHG-20260923-058 — wt-media-workspace 状态

> 本文件是**开工时**的状态快照（下面每条都写于 T-02 之前，保留原文，一字未改）。**关闭时的终态**见末行。

- 2026-09-24 T-01：草案由 `delivery/planned/` 移入 `delivery/active/` 并改写为十三节执行记录
  （`change.md`、`checkpoint.md`、`evidence/`、`status/`）；`LEDGER.md` 加表行；
  `planned/README.md` 的 C 行改 ACTIVE；快照经 `prepare_ai_workspace.py --change CHG-20260923-058` 再生成。
- 本仓范围：T-01（激活）、T-02 的四处活基线回写 + CHG-057 归档记录顶部的取代注记、
  T-09（`cache/` 入基线、本机设置基线语句、归档与失效指针扫描）。
- 待办：T-02 的基线回写（程序总纲 §3 CHG-B 的 20MB/总量/截断四条 → 按天保留；
  架构基线 §5.8 的 `desktop-YYYYMMDD-N.log` 与 100MB/400MB；里程碑成功事实 #5 的「受容量限制」）。

**终态（2026-09-25 关闭时追加，上文一字未改）**：T-01…T-09 全部 DONE，`Status: DONE`。四处活基线回写完成：
程序总纲 §2 的 `cache` 行改「已入基线」并给出两头真实路径、§3 的 CHG-C 落定口径、架构基线 §5.8 的**四个根**
（**缓存根在数据根之外**）与 §6.8 的缓存条目、里程碑成功事实 #5 与状态行（#5 由 CHG-B 达成、#6 由 CHG-C 达成）。
三个运行仓的入口文档同步：desktop 五个新模块与五个命令文件的行、命令数 18 → 27、`logging/` 按小时切割口径；
agent 的按天保留与**两侧机制有意不对称**；cloud 的「本机设置」页与日志查看器路由（含边界与目录地图）。
本 CHG 记录已 `git mv` 至 `delivery/completed/`，`LEDGER.md` 活动行已移除，`planned/README.md` 的 C 行改 DONE，
快照经 `prepare_ai_workspace.py --no-active` 冷启动重生成（现 `Active CHG: none`）。
回写由 `先失败检查` 钉着落地（8/8 事实进基线、4/4 旧口径清零、5/5 阳性对照在活），归档后**主动扫**失效指针
并逐个 resolve 相对链接，均报分母。详见 `../evidence/task-09-writeback-and-archive.md`。
