# Planned delivery index

更新：2026-09-27。当前没有 active CHG：M4-A 的 [CHG-20260924-061](../completed/CHG-20260924-061/change.md)（M4-A 素材库、我的素材与原素材懒加载下载）已于 2026-09-27 关闭归档为 `DONE`；台账见 [delivery/LEDGER.md](../LEDGER.md)。此前的 [CHG-20260923-056](../completed/CHG-20260923-056/change.md)～[CHG-20260923-059](../completed/CHG-20260923-059/change.md) 均已归档 `DONE`，属上线前工程加固程序（`docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md），不属 M2/M3 里程碑。本目录 DISCUSSION/PLANNED 表示执行草案，不自动批准其中待决建议。团队级内容隔离已由 ADR-0014 确认；M3 内容挖掘执行边界已由 ADR-0015 收敛为 Cloud-owned Crawler；Agent 的分层、依赖方向与配置目录约定已由 ADR-0016 确认；M4-M5 Cloud 视频生产边界已由 ADR-0017 确认。

## 联合工程优化程序（2026-09-23 立项）

程序总纲：[launch-engineering-optimization-program.md](../../docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md)。按依赖顺序激活，最多一项 active：

| 阶段 | 记录 | 状态 |
| --- | --- | --- |
| A 结构审计、Config 与 Client 解耦 | [CHG-20260923-056](../completed/CHG-20260923-056/change.md) | **DONE（2026-09-24 归档）** |
| B Paths、Logger 和运行目录 | [CHG-20260923-057](../completed/CHG-20260923-057/change.md) | **DONE（2026-09-24 归档）** |
| C Desktop 本机设置 | [CHG-20260923-058](../completed/CHG-20260923-058/change.md) | **DONE（2026-09-25 归档）** |
| D Sidecar、打包、升级与回归 | [CHG-20260923-059](../completed/CHG-20260923-059/change.md) | **DONE（2026-09-25 归档）** |

## M4 Cloud 内容生产

有效基线：[M4 Cloud 内容生产闭环](../milestones/M4-content-production.md)、[第五章：素材生产](../../docs/product/prd/详细文档/第五章_素材生产.md) 与 ADR-0017。M4 当前为 `IN_PROGRESS`；首个独立闭环 M4-A 由 [CHG-20260924-061](../completed/CHG-20260924-061/change.md) 承载并于 2026-09-27 关闭归档为 `DONE`，但该记录把用户签收与八条走查臂登记为**未闭合**。M4-C2～C8 的候选结果、依赖和验收边界见 [M4 §3.1](../milestones/M4-content-production.md#31-剩余-chg-执行边界)；它们尚非正式 CHG。M4 的后续 CHG 必须等 M4-A 的真实验收后再逐项建立。

## 前端交互规范对齐（2026-09-30 立项）

依据基线：[前端交互规范](../../docs/standards/前端交互规范.md)。用户裁定拆开执行：素材库/我的素材由 [CHG-20260930-069](../active/CHG-20260930-069/change.md) 任务 8 承载（走查三轮）；内容池另立草案。`delivery/active` 同一时间只允许一个活跃 CHG，故按下表顺序激活：

| 草案 | 内容 | 状态 |
| --- | --- | --- |
| [CHG-20260930-070](CHG-20260930-070/change.md) | 内容池行操作按状态收敛、「查看→详情」、已转素材行级「素材详情」入口（按钮 ≤5 全平铺；仅交互层，不动后端与契约） | PLANNED（待 CHG-069 关闭后激活） |
| [CHG-20260930-071](CHG-20260930-071/change.md) | 素材状态维度（可用/已暂停/已下架）与使用情况统计（成片数、发布数、最近生产/发布时间、重复风险）——设计图里交互层做不了的那半 | PLANNED（**范围未定**：§4 的 Q-01～Q-06 关闭前不激活，见该记录 §0） |

CHG-20260930-071 与 070、069 的关系：069 任务 9 只落纯交互层，素材库不提供下载、行操作「详情 | 加入我的素材 / 去我的素材」、详情抽屉分标签，这些都**不需要**后端新能力；071 收的是设计图里必须新增数据库字段、投影与契约才能成立的部分（用户 2026-09-30 裁定「先落纯交互层，后端另立 CHG」）。「该素材是否已加入我的素材」已由 069 任务 9 用客户端 join 承担，不属 071。

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
| M3-E3 内容挖掘综合验收 | [CHG-20260915-051](CHG-20260915-051/change.md) | **已由 CHG-052 执行、用户 2026-09-23 签收**；独立验收草案 CHG-051 保持 DISCUSSION、不激活 |

上表「状态」列写的是**程序进度**（这一阶段做没做、由谁承载），**不是记录自身的状态词**——每条记录的状态词在它自己 `change.md` 的 `Status:` 字段，词表见 `MASTER` §3。所以「已实施，真实证据，由 CHG-052 承载」与那份草案自己写 `DISCUSSION`（未开始实施、不激活）并不矛盾：前者说工作已由别处交付，后者说这份草案从未被激活。**记录层**要不要为这些草案补一个终态词，是另一件事，不在本索引内裁定。

按依赖顺序逐项激活，最多一项 active。M3-A 按团队级隔离实施，不做游戏维度或跨团队共享；B～E 按 ADR-0015 由 Cloud Scheduler + Cloud Crawler 实施，不依赖 Agent/BitBrowser/Desktop。逐阶段状态与证据指向见 [M3-content-discovery-v2.md](../milestones/M3-content-discovery-v2.md) 第 2.1 节。

### M3 验收遗留

E3 综合验收已由 `CHG-20260916-052` 执行并经 2026-09-23 补验收口（验收矩阵无 FAIL、无 NOT VERIFIED）。验收期间**只登记未修**的缺陷与安全问题按用户裁定移入 planned：

| 草案 | 内容 | 状态 |
| --- | --- | --- |
| [CHG-20260923-054](CHG-20260923-054/change.md) | M3 综合验收缺陷与安全问题处置（D1、D2、D3、D6、D7、D8、D9、D10、D-scheduler-2、S-1） | PLANNED（未激活） |

其中 D3 是唯一影响验收项的缺陷（基线 §5 的「不重复排队」）；**用户已于 2026-09-23 裁定 D3 不阻塞 M3**——M3 据此签收，D3 仍在 054 内按该记录自身范围处置，不因 M3 关闭而消失。D9、D-scheduler-2 与 S-1 的处置范围需先有用户裁定。

**不在 054 内跟踪**：验收之后从生产形态 DMG 原生应用报出的内容池呈现问题（封面被 CSP 拦截、
标题省略号漏了 `<a>` 渲染分支）已由 [CHG-20260923-055](../completed/CHG-20260923-055/change.md) 单独处置，
**不以缺陷条目重复登记进 054**。二者性质不同：054 收的是 E3 验收期内**已登记未修**的项，
055 收的是验收之后新发现的、且已当轮修复的项。

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

- [CHG-20260923-053](CHG-20260923-053/change.md)：Agent 运行时目录、依赖边界与生产运行能力，**SUPERSEDED（2026-09-23 用户裁定并入联合工程优化程序：Task 1-5→CHG-056、Task 6→CHG-057、Task 7→CHG-059，唯一偏差 sidecar 受控 env 传参见其归档记录）**。原「不改变任何业务闭环、API contract 语义或已有测试含义」约束随 CHG-056 继续有效（`test_sidecar_entry.py` 断言调整除外）。
- [CHG-20260903-034](CHG-20260903-034/change.md)：账号检查项 7/8 真实样本校准，PLANNED，待授权样本；不重新打开已经验收通过的 M2，不作为 M3 前置。
- [CHG-20260723-023](CHG-20260723-023/change.md)：M2-B1 扫描与 Diff 的**草案**，从未激活、无 evidence。其范围已由三个已归档 CHG 交付（`CHG-20260723-022` 主账号确认、`CHG-20260723-025` M2-B1 只读闭环、`CHG-20260723-026` 窗口同步应用与恢复），故标记 `SUPERSEDED`——M2 的完成与否以 `M2-account-runtime.md` 与 `CHG-20260725-031` 的收口矩阵为准，与本记录无关。
