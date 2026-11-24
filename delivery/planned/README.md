<!-- governance: class=index default_load=task -->

# Planned delivery index

本目录保存尚未启动的交付项；DISCUSSION仅为待review草案，PLANNED为已确认待启动项。`DISCUSSION` / `PLANNED` 不自动批准待决建议；按依赖顺序逐项激活，允许多个相互独立的 Active CHG，当前会话只选一个执行（见 `AGENT-INDEX.md` §5）。

| 记录 | 内容 | 状态 |
| --- | --- | --- |
| [CHG-20261124-108](CHG-20261124-108/change.md) / [review清单](CHG-20261124-108/plan.md) | 批次可配置并发、跨批Profile互斥、停止与公开结果 | PLANNED；依赖Active 107；start建单/分组与异常控制 |
| [CHG-20261124-109](CHG-20261124-109/change.md) / [review清单](CHG-20261124-109/plan.md) | 计划目标、全部批次准备与冻结、10%推进、批次快捷操作与结束 | PLANNED；依赖108；冻结/10%推进/快捷处理 |
| [CHG-20260903-034](CHG-20260903-034/change.md) | M2-B 账号检查项 7/8 真实样本校准 | PLANNED，待真实受限账号样本 |
| [CHG-20260915-047](CHG-20260915-047/change.md) | M3-C2 博主主动搜索入池 | 暂停（本期不做，ADR-0013） |
| [CHG-20260915-050](CHG-20260915-050/change.md) | M3-E2 博主任务与持续入池 | 暂停（本期不做，ADR-0013） |
| [CHG-20260923-054](CHG-20260923-054/change.md) | M3 综合验收缺陷与安全问题处置（D1、D2、D3、D6～D10、D-scheduler-2、S-1） | PLANNED；D3 已裁定不阻塞 M3 |

## 发布批次与计划review顺序

1. 先读[107交付范围及执行约定](../completed/CHG-20261124-107/plan.md)：2026-11-25口径已同步，保存不建task/占用；108首次start建单；不再引用旧R1–R6。
2. 按107→108→109逐行核对“业务/页面→API→数据/事务→研发步骤→验收”；纯前端交互明确无新增API，复用接口标明本次增量。
3. 用户review后把批准结论回写PRD/工程设计与Milestone，提供方定版OpenAPI，再将对应change转PLANNED；不因存在可执行清单就直接启动。
4. 运行代码执行仍按依赖合入main、CHG预检、单执行器与独立PR规则；本次不改变Active Ledger或M6验收状态。

M4 剩余 CHG 的执行边界见 [M4 §3.1](../milestones/M4-content-production.md#31-剩余-chg-执行边界)，不在此复制。M4-A 签收补记见 [2026-10-12 签收](../reports/2026-10-12-m4-a-signoff.md)。

已交付、已归档或已废弃的草案由 Git 保存；本目录只列仍未关闭的记录。

