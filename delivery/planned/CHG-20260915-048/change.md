# CHG-20260915-048：M3-D 统一挖掘策略配置

- Status: DISCUSSION
- Level: M
- Milestone: `delivery/milestones/M3-content-discovery-v2.md#m3-d-挖掘策略配置`
- 日期：2026-09-15
- 基线：`docs/product/M3-content-mining-v2.md`；ADR-0013。
- 当前仓库：wt-media-workspace；未开始运行时代码实施。

## 独立目标与前置

独立用户目标和成功事实以对应闭环卡为准，不扩展至其他阶段。

前置：M3-C / CHG-20260915-046、047；V2-Q02/04/05 的相关产品选择已确认。

范围：discovery_strategy keyword/author、content_channel 引用、策略表单、周期配置、启停、执行记录入口。

> 2026-09-23 更正：本条原表述中的作者侧已随 C2/E2 暂停——本期只交付 keyword，`author` 取值与字段保留但不交付；见 docs/product/M3-content-mining-v2.md 与 evidence/m3-e3-acceptance-20260923/。

## 明确不做

定时器放入策略类、两套策略表、其他平台接入、自动转素材选项、通用规则或调度引擎。

> 2026-09-23 更正：本条原表述「自动转素材选项」已失效——自动转素材是本期已交付能力（`auto_material` 开关、`material_rule` 的 `AND`/`OR`、`like_threshold`、`favorite_threshold`；阈值 ≤0 不参与判定）；见 docs/product/M3-content-mining-v2.md 与 evidence/m3-e3-acceptance-20260923/。

## 顺序任务

### Task 1：确定业务与触发配置

- 工作：记录已确认的频率/时区/首触发/作者首轮规则，定义策略规则与关联触发设置职责。
- 验收：字段可追溯到决策；尚未决定的首次模式不先固化为产品。

### Task 2：交付关键词配置

- 工作：统一模型与受控渠道能力，关键词列表、名称、周期、启停和读回。
- 验收：不支持渠道或非法配置不可保存启用；保存不执行外部抓取。

### Task 3：交付作者配置及共用生命周期

- 工作：稳定作者身份、同一编辑/启停/权限框架；历史任务保留快照。
- 验收：两类策略不是两套独立模型；编辑不改历史；记录入口空态准确。

### Task 4：配置验收

- 工作：两类策略创建编辑启停和角色拒绝；明确阶段执行尚未就绪。
- 验收：D 只证明配置闭环；不得显示已执行或以 D 通过替代 E 自动执行验收。

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

