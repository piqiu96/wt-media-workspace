# CHG-20260915-049：M3-E1 关键词任务与真实定时入池

- Status: DISCUSSION
- Level: M
- Milestone: `delivery/milestones/M3-content-discovery-v2.md#m3-e1-关键词自动挖掘`
- 日期：2026-09-15
- 基线：`docs/product/M3-content-mining-v2.md`；ADR-0013。
- 当前仓库：wt-media-workspace；未开始运行时代码实施。

## 独立目标与前置

独立用户目标和成功事实以对应闭环卡为准，不扩展至其他阶段。

前置：M3-D / CHG-20260915-048；V2-Q03/04/06 已形成任务与调度合同。

范围：受控触发、周期防重、crawl_task 四态/快照/统计/日志、Cloud Agent 多词执行、真实入池和恢复。

> 2026-09-23 更正：本条原表述「crawl_task 四态」已失效，业务状态为五态（`pending`/`running`/`success`/`partial_success`/`failed`）；「Cloud Agent 多词执行」亦已由 ADR-0015 纠偏为 Cloud-owned 执行。见 docs/product/M3-content-mining-v2.md 与 evidence/m3-e3-acceptance-20260923/。

## 明确不做

只建任务列表、用手工调用代替定时验收、自动创建 material、partial 第五业务态、可视化调度与任意脚本。

> 2026-09-23 更正：本条原表述「自动创建 material」与「partial 第五业务态」均已失效——自动转素材是本期已交付能力，`partial_success` 已是正式业务状态（五态之一）；见 docs/product/M3-content-mining-v2.md 与 evidence/m3-e3-acceptance-20260923/。

## 顺序任务

### Task 1：定义任务与触发合同

- 工作：四态映射、统计单位、触发身份、计划幂等键、同策略互斥、恢复检查点及日志脱敏。
  > 2026-09-23 更正：本条原表述「四态映射」已失效，业务状态为五态（含 `partial_success`）；见 docs/product/M3-content-mining-v2.md 与 evidence/m3-e3-acceptance-20260923/。
- 验收：先解决部分失败口径；技术 task 与 crawl_task 分离，终态不任意回写。

### Task 2：交付周期到真实内容池

- 工作：调度/受控脚本经同一 Cloud 校验入口创建快照任务，Cloud Agent 查询并复用入池服务。
- 验收：真实周期产生真实来源；Cloud 负责落库；未人工转换零 material；同策略不重复排队。

### Task 3：交付任务列表和详情

- 工作：四态、开始/结束、五项主要计数、错误和执行日志，策略页面关联记录；以这些真实记录提供只读业务流转展示，素材尚未转换时如实显示未转素材，后续 E2 复用。
  > 2026-09-23 更正：本条原表述「四态」与「只读业务流转展示」均已失效——状态为五态；独立的只读业务流转视图本期不交付，已按用户 2026-09-23 裁定移出交付与验收范围（ADR-0013 第 8 条的禁止性约束不变）；见 docs/product/M3-content-mining-v2.md 与 evidence/m3-e3-acceptance-20260923/。
- 验收：统计单位可解释，接口失败不假装作品计数；无结果成功与接口失败可区分。

### Task 4：恢复与闭环验收

- 工作：真实周期+重复触发、Cloud/Agent 重启、限流、提交后回报丢失及部分失败验证。
- 验收：不重复来源/统计；已成功数据不回滚；本地电脑离线仍能执行；不以 ticker 日志判成功。

## Evidence 与提交边界

每项记录输入/角色、预期、实际、PASS/FAIL、环境版本、相关 ID 与脱敏截图。fixture/mock 与真实接口证据分开；HTTP 成功、任务创建、代码存在都不能替代业务读回。

Cloud 负责业务 API/数据库/Web 及正式合同；Agent 负责渠道执行适配；Desktop 复用 Web 不复制业务；Workspace 负责决策、治理索引和 Evidence。按提供方先行与消费者验证顺序，分别在各仓提交。

有待决产品规则或缺真实依赖时不激活；不得为通过验收私自降级范围。若实施设计仍超出该独立闭环，激活前继续拆分，不横跨 A～E 全部实施。

## Checkpoint

- Completed：V2 文档级范围、依赖、任务与验收拆分。
- Current：DISCUSSION，planned；无运行时测试或完成证据。
- Next：解决相关 V2-Q 项，补齐设计/合同，按依赖顺序只激活一项。
- Blockers：前置阶段未验收，相关规则/真实接口条件待核实。
- Verification：本轮仅 Workspace 文档检查，不代表运行链路验证。
