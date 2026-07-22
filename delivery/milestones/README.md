# Milestone 业务闭环

本目录保存每个 M 由人工确认的业务闭环基线。

Milestone 不替代 Product、Engineering、MASTER PLAN、AI Spec、CHG 或 Evidence。它只回答：用户按什么顺序操作，以及哪些业务结果和真实外部效果必须同时成立，才能认为该 M 的一段闭环完成。

每张闭环卡只包含：

- 用户目标；
- 前置条件；
- 用户操作顺序；
- 系统与外部动作；
- 成功必须同时满足的事实；
- 失败时禁止出现的假成功；
- 对应 CHG。

CHG 必须引用一张闭环卡，只描述本次差距、修改范围、任务和验证方法，不重复维护完整业务流程。

## Milestone-first 更新规则

Milestone 执行过程中发现的小变更、验收细节、页面口径、操作边界和异常处理，优先回写当前 `delivery/milestones/Mx-xxx.md`。

不要在每个小变更时立即修改 PRD。PRD 是长期产品事实，不承载执行过程中的频繁修订。

执行中产生的事实写入：

- `delivery/active/<CHG>/change.md`
- `delivery/active/<CHG>/evidence/`

按以下规则判断写入位置：

| 变化类型 | 写入位置 |
|---|---|
| 当前 M 执行中发现的业务细节、验收口径、页面文案、按钮语义、异常处理 | 当前 Milestone + 当前 CHG checkpoint/evidence |
| 当前 M 的业务闭环变化、操作顺序变化、成功条件变化、假成功规则变化 | 当前 Milestone；必要时重新拆 CHG |
| 产品目标、用户角色、长期产品能力、全局业务范围变化 | PRD；再同步 Milestone 和 CHG |
| Cloud / Desktop / Agent 职责边界、通信方式、安全原则变化 | Engineering / Decision；再同步 Milestone 和 CHG |
| 代码实现缺陷且不改变业务闭环 | 当前 CHG，不改 Milestone，不改 PRD |

一个 Milestone 完整验收后，再把已经稳定的产品规则按需回写 PRD。未稳定的执行细节不进入 PRD。
