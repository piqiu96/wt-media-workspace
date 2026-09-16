# Planned delivery index

更新：2026-09-16。当前 active CHG 为 CHG-20260915-044；其余 DISCUSSION 表示执行草案，不自动批准其中待决建议。团队级内容隔离已由 ADR-0014 确认。

## 当前 M3 V2

有效基线：[Product](../../docs/product/M3-content-mining-v2.md)；[M3-content-discovery-v2.md](../milestones/M3-content-discovery-v2.md)。用户确认的方向为内容挖掘自动化入口，关键细节参见 V2-Q01～06。

| 阶段 | 当前草案 | 状态 |
| --- | --- | --- |
| M3-A 内容池基础能力 | [CHG-20260915-044](../active/CHG-20260915-044/change.md) | ACTIVE |
| M3-B 分享链接解析入池 | [CHG-20260915-045](CHG-20260915-045/change.md) | DISCUSSION |
| M3-C1 关键词主动搜索入池 | [CHG-20260915-046](CHG-20260915-046/change.md) | DISCUSSION |
| M3-C2 博主主动搜索入池 | [CHG-20260915-047](CHG-20260915-047/change.md) | DISCUSSION |
| M3-D 统一挖掘策略配置 | [CHG-20260915-048](CHG-20260915-048/change.md) | DISCUSSION |
| M3-E1 关键词任务与真实定时入池 | [CHG-20260915-049](CHG-20260915-049/change.md) | DISCUSSION |
| M3-E2 博主任务与持续入池 | [CHG-20260915-050](CHG-20260915-050/change.md) | DISCUSSION |
| M3-E3 内容挖掘综合验收 | [CHG-20260915-051](CHG-20260915-051/change.md) | DISCUSSION |

按依赖顺序逐项激活，最多一项 active。M3-A 按团队级隔离实施，不做游戏维度或跨团队共享；B 需要真实链接接口；D/E 需要周期、作者首轮及任务部分失败口径。激活前同步根 CURRENT_CONTEXT。

## 已替代的旧 M3 草案

原 [M3-content-discovery.md](../milestones/M3-content-discovery.md) 与以下记录均为 SUPERSEDED；保留历史，不执行、不算已完成，旧编号与 V2 不强行一一映射：

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
