# Planned delivery index

更新：2026-09-23。当前 active CHG 为 CHG-20260916-052；本目录其余 DISCUSSION 表示执行草案，不自动批准其中待决建议。团队级内容隔离已由 ADR-0014 确认；M3 内容挖掘执行边界已由 ADR-0015 收敛为 Cloud-owned Crawler。

## 当前 M3 V2

有效基线：[Product M3 内容挖掘 V2](../../docs/product/M3-content-mining-v2.md)；[M3-content-discovery-v2.md](../milestones/M3-content-discovery-v2.md)。用户确认的方向为内容挖掘自动化入口；V2-Q01～06 中 Q02 已由 ADR-0014 关闭、Q03 已于 2026-09-23 关闭（`partial_success`）。

| 阶段 | 当前草案 | 状态 |
| --- | --- | --- |
| M3-A 内容池基础能力 | [CHG-20260915-044](../completed/CHG-20260915-044/change.md) | HANDOFF（并入 M3 综合变更，已归档） |
| M3-B 分享链接解析入池 | [CHG-20260915-045](CHG-20260915-045/change.md) | 已实施，真实证据，由 CHG-052 承载 |
| M3-C1 关键词主动搜索入池 | [CHG-20260915-046](CHG-20260915-046/change.md) | 已实施，真实证据，由 CHG-052 承载 |
| M3-C2 博主主动搜索入池 | [CHG-20260915-047](CHG-20260915-047/change.md) | **暂停**（本期不做，后续版本再做） |
| M3-D 统一挖掘策略配置 | [CHG-20260915-048](CHG-20260915-048/change.md) | 已实施，真实证据，由 CHG-052 承载 |
| M3-E1 关键词任务与真实定时入池 | [CHG-20260915-049](CHG-20260915-049/change.md) | 已实施，真实证据，由 CHG-052 承载 |
| M3-E2 博主任务与持续入池 | [CHG-20260915-050](CHG-20260915-050/change.md) | **暂停**（本期不做，后续版本再做） |
| M3-E3 内容挖掘综合验收 | [CHG-20260915-051](CHG-20260915-051/change.md) | DISCUSSION（未开始） |

按依赖顺序逐项激活，最多一项 active。M3-A 按团队级隔离实施，不做游戏维度或跨团队共享；B～E 按 ADR-0015 由 Cloud Scheduler + Cloud Crawler 实施，不依赖 Agent/BitBrowser/Desktop。逐阶段状态与证据指向见 [M3-content-discovery-v2.md](../milestones/M3-content-discovery-v2.md) 第 2.1 节。

## 已替代的旧 M3 草案

原 `delivery/milestones/M3-content-discovery.md`（已移除，链接不再有效）与以下记录均为 SUPERSEDED；保留历史，不执行、不算已完成，旧编号与 V2 不强行一一映射：

- [CHG-20260914-037](CHG-20260914-037/change.md)
- [CHG-20260915-038](CHG-20260915-038/change.md)
- [CHG-20260915-039](CHG-20260915-039/change.md)
- [CHG-20260915-040](CHG-20260915-040/change.md)
- [CHG-20260915-041](CHG-20260915-041/change.md)
- [CHG-20260915-042](CHG-20260915-042/change.md)
- [CHG-20260915-043](CHG-20260915-043/change.md)

## 既有非 M3 记录

- [CHG-20260903-034](CHG-20260903-034/change.md)：账号检查项 7/8 真实样本校准，PLANNED，待授权样本；不重新打开已经验收通过的 M2，不作为 M3 前置。
- [CHG-20260723-023](CHG-20260723-023/change.md)：既有历史规划文件，位于 planned 但正文保留 IN_PROGRESS 标记；不是当前 active。状态整理不属于本次 M3 拆分范围，保留原文件，不能据此宣布 M2 尚未完成。
